# stream_mgr.py
# pylint: disable=no-member,c-extension-no-member
import threading
import queue
import time
import base64
import json
import winreg
import struct
import win32file # type: ignore
import win32con  # type: ignore
import win32event # type: ignore
import pywintypes # type: ignore
import cv2
import numpy as np
from shared_utils import global_log

# OpenCV 參數
imencode = cv2.imencode
cvtColor = cv2.cvtColor
CV_IMWRITE_JPEG_QUALITY = getattr(cv2, 'IMWRITE_JPEG_QUALITY', 1)
CV_COLOR_BAYER_BG2BGR = getattr(cv2, 'COLOR_BAYER_BG2BGR', 46)
CV_COLOR_YUV2BGR_YUYV = getattr(cv2, 'COLOR_YUV2BGR_YUYV', 85)

# OVT PDMA 核心常數
CYPDMA_CTRL_READ      = 0x08
CYPDMA_CTRL_WRITE     = 0x00
CYPDMA_CTRL_BULK      = 0x00
CYPDMA_CTRL_LASTPKT   = 0x01
CYPDMA_DDR_BASE_ADDR  = 0x80000000


class ImgView:
    def __init__(self, output_callback):
        self.output_callback = output_callback

    def show(self, channel: int, bgr_frame: np.ndarray):
        try:
            ret, buffer = imencode('.jpg', bgr_frame, [int(CV_IMWRITE_JPEG_QUALITY), 80])
            if ret:
                b64_data = base64.b64encode(buffer).decode('utf-8')
                if self.output_callback:
                    self.output_callback(channel, b64_data)
        except Exception as e:
            global_log(tag="IMG_VIEW", message=f"Encode Error: {e}")


class ImgProcess:
    def __init__(self, view_instance: ImgView):
        self.view = view_instance

    @staticmethod
    def _remove_payload(raw_data: bytes) -> bytes:
        chunk_size = 16384
        header_size = 16
        if len(raw_data) <= header_size:
            return b""
        return b"".join([
            raw_data[i + header_size : i + chunk_size]
            for i in range(0, len(raw_data), chunk_size)
        ])

    def handle_frame(self, raw_bytes: bytes, channel: int, width: int, height: int, fmt_type: int, sequence: str = "", mirror: bool = False, flip: bool = False):
        try:
            clean_bytes = self._remove_payload(raw_bytes)
            # 如果是 RAW16 (7) 或是 YUV (2) 每個像素佔用 2 Bytes
            expected = width * height if fmt_type == 5 else width * height * 2
            if len(clean_bytes) < expected:
                global_log(
                    tag="IMG_PROCESS",
                    message=f"Drop: VC{channel} 影像大小不足 (收到 {len(clean_bytes)}, 需要 {expected})"
                )
                return
            bgr_img = None
            if fmt_type == 5: # 8-bit RAW
                img_np = np.frombuffer(clean_bytes[:expected], dtype=np.uint8)
                raw_img = img_np.reshape((height, width))
                cv_code_str = f"COLOR_Bayer{sequence}2BGR" if sequence else "COLOR_BayerBG2BGR"
                cv_code = getattr(cv2, cv_code_str, 46)
                bgr_img = cvtColor(raw_img, cv_code)
            elif fmt_type == 7: # 16-bit / 10-bit Unpacked RAW
                # 告訴 Numpy 這是 16-bit (2 bytes) 的整數陣列
                img_np = np.frombuffer(clean_bytes[:expected], dtype=np.uint16)
                raw_img_16 = img_np.reshape((height, width))
                # 將 10-bit 的數值範圍 (0~1023) 壓縮回 8-bit (0~255) 以供一般螢幕顯示
                # 假設硬體是將 10-bit 放在低位元 我們只需向右位移 2 個 bit (等同於除以 4)
                raw_img_8 = (raw_img_16 >> 2).astype(np.uint8)
                # 先用標準 Bayer 算法硬解 讓畫面出得來 (注意: 因為是 RGBIr 顏色一定會有一點偏差)
                cv_code_str = f"COLOR_Bayer{sequence}2BGR" if sequence else "COLOR_BayerBG2BGR"
                cv_code = getattr(cv2, cv_code_str, 46)
                bgr_img = cvtColor(raw_img_8, cv_code)
            elif fmt_type == 2: # YUV422
                img_np = np.frombuffer(clean_bytes[:expected], dtype=np.uint8)
                yuv_img = img_np.reshape((height, width, 2))
                cv_code_str = f"COLOR_YUV2BGR_{sequence}" if sequence else "COLOR_YUV2BGR_YUYV"
                cv_code = getattr(cv2, cv_code_str, 85)
                bgr_img = cvtColor(yuv_img, cv_code)
            if bgr_img is not None:
                # 實現 Mirror (水平) 與 Flip (垂直)
                if mirror and flip:
                    bgr_img = cv2.flip(bgr_img, -1) # 同時翻轉
                elif mirror:
                    bgr_img = cv2.flip(bgr_img, 1)  # 水平鏡像
                elif flip:
                    bgr_img = cv2.flip(bgr_img, 0)  # 垂直翻轉
                self.view.show(channel, bgr_img)
        except Exception as e:
            global_log(tag="IMG_PROCESS", message=f"Decode Error: {e}")


class ImgCapture(threading.Thread):
    def __init__(self, vid: int, pid: int, data_queue: queue.Queue, vc_configs: dict):
        super().__init__(name="USB-Capture-Thread", daemon=True)
        self.vid = vid
        self.pid = pid
        self.queue = data_queue
        self.vc_configs = vc_configs
        self.is_running = False
        self.hDevice = None
        self.bytes_count = 0
        self.last_time = time.time()

    @staticmethod
    def _log(message: str) -> None:
        global_log(tag="IMG_CAPTURE", message=message)

    def _init_native_win32(self) -> bool:
        guid = "{28d78fad-5a12-11d1-ae5b-0000f803a8c2}"
        base_reg_path = rf"SYSTEM\CurrentControlSet\Control\DeviceClasses\{guid}"
        target_id = f"VID_{self.vid:04X}&PID_{self.pid:04X}"
        found = False
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, base_reg_path) as class_key:
                for j in range(64):
                    try:
                        dev_inst = winreg.EnumKey(class_key, j)
                        if target_id in dev_inst.upper():
                            found = True
                            final_path = dev_inst.replace("##?#", "\\\\?\\")
                            for p in [final_path, final_path + "\\", final_path + "\\#"]:
                                try:
                                    self.hDevice = win32file.CreateFile(
                                        p,
                                        win32con.GENERIC_READ | win32con.GENERIC_WRITE,
                                        win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
                                        None,
                                        win32con.OPEN_EXISTING,
                                        win32con.FILE_FLAG_OVERLAPPED,
                                        None
                                    )
                                    self._log(f"SUCCESS: Opened {p}")
                                    return True
                                except Exception:
                                    continue
                    except Exception:
                        break
        except Exception as e:
            self._log(f"Init Error: {e}")
            return False
        if found:
            self._log("ERROR: 找到歷史裝置紀錄 但皆無法連線 (Error 2/5)。請確認裝置目前是否確實連接且未被佔用。")
        else:
            self._log("ERROR: 找不到指定的 USB 裝置 請確認 USB 是否插妥。")
        return False

    def _build_frame_request_packet(self, channel: int, req_size: int) -> bytes:
        header = bytearray(16)
        header[0] = 0x30 | CYPDMA_CTRL_READ | CYPDMA_CTRL_BULK | CYPDMA_CTRL_LASTPKT
        header[2] = 0x20
        # 動態根據通道計算記憶體位址偏移量
        addr = CYPDMA_DDR_BASE_ADDR + (channel * 0x0C000000) + 0x20
        struct.pack_into('<I', header, 8, addr)
        struct.pack_into('<I', header, 12, req_size)
        return bytes(header)

    def _flush_stale_data(self, read_ov, buf):
        self._log("Flushing stale USB data...")
        while True:
            win32event.ResetEvent(read_ov.hEvent)
            hr, _ = win32file.ReadFile(self.hDevice, buf, read_ov)
            if hr == 997:
                res = win32event.WaitForSingleObject(read_ov.hEvent, 100)
                if res == win32event.WAIT_OBJECT_0:
                    win32file.GetOverlappedResult(self.hDevice, read_ov, True)
                else:
                    win32file.CancelIo(self.hDevice)
                    break
            elif hr != 0:
                break
        self._log("Flush complete.")

    def run(self):
        self._log("Requesting Frames for active channels...")
        self.is_running = True
        READ_SIZE = 128 * 1024
        buf = win32file.AllocateReadBuffer(READ_SIZE)
        read_ov = pywintypes.OVERLAPPED()
        read_ov.hEvent = win32event.CreateEvent(None, 1, 0, None)
        write_ov = pywintypes.OVERLAPPED()
        write_ov.hEvent = win32event.CreateEvent(None, 1, 0, None)
        active_channels = sorted(list(self.vc_configs.keys()))
        try:
            self._flush_stale_data(read_ov, buf)
            frame_buffer = bytearray()
            while self.is_running:
                # 依序向每個啟用的通道索取影像
                for ch in active_channels:
                    if not self.is_running:
                        break
                    cfg = self.vc_configs[ch]
                    fmt = cfg.get('format', 5)
                    w = cfg.get('width', 1920)
                    h = cfg.get('height', 1080)
                    payload_size = w * h if fmt == 5 else w * h * 2
                    num_blocks = (payload_size + 16367) // 16368
                    req_size = payload_size + num_blocks * 16
                    req_packet = self._build_frame_request_packet(ch, req_size)
                    bytes_left = 0
                    frame_buffer.clear()
                    not_ready_cnt = 0
                    debug_timer = time.time()
                    while self.is_running:
                        if bytes_left <= 0:
                            win32event.ResetEvent(write_ov.hEvent)
                            hr, _ = win32file.WriteFile(self.hDevice, req_packet, write_ov)
                            if hr == 997:
                                win32event.WaitForSingleObject(write_ov.hEvent, 500)
                                win32file.GetOverlappedResult(self.hDevice, write_ov, True)
                            bytes_left = req_size
                            frame_buffer.clear()
                        win32event.ResetEvent(read_ov.hEvent)
                        hr, _ = win32file.ReadFile(self.hDevice, buf, read_ov)
                        nbytes = 0
                        if hr == 997:
                            res = win32event.WaitForSingleObject(read_ov.hEvent, 1000)
                            if res == win32event.WAIT_OBJECT_0:
                                nbytes = win32file.GetOverlappedResult(self.hDevice, read_ov, True)
                            else:
                                win32file.CancelIo(self.hDevice)
                                if len(frame_buffer) > req_size * 0.8:
                                    self._log(f"[WARNING] VC{ch} 影像長度微小誤差 強制出圖 (目前緩衝 {len(frame_buffer)} bytes)")
                                    self.queue.put((ch, bytes(frame_buffer)))
                                    break
                                else:
                                    now = time.time()
                                    if now - debug_timer > 1.0:
                                        self._log(f"[DEBUG] VC{ch} USB Timeout (目前緩衝 {len(frame_buffer)} bytes)")
                                        debug_timer = now
                                bytes_left = 0
                                continue
                        elif hr == 0:
                            nbytes = win32file.GetOverlappedResult(self.hDevice, read_ov, True)
                        if nbytes > 0:
                            chunk = bytes(buf[:nbytes])
                            if len(frame_buffer) == 0 and nbytes >= 16:
                                pkt_len = struct.unpack('<I', chunk[12:16])[0]
                                bCtrl = chunk[0]
                                if pkt_len == 0 and (bCtrl & 0x01) == 0:
                                    not_ready_cnt += 1
                                    if not_ready_cnt % 10 == 0:
                                        self._log(f"[FPGA] VC{ch} Not Ready. 等待 Sensor 畫面中...")
                                    bytes_left = 0
                                    time.sleep(0.05)
                                    continue
                            not_ready_cnt = 0
                            frame_buffer.extend(chunk)
                            bytes_left -= nbytes
                            self.bytes_count += nbytes
                            self._monitor_throughput()
                            if len(frame_buffer) >= req_size:
                                full_frame = frame_buffer[:req_size]
                                self.queue.put((ch, bytes(full_frame)))
                                # self._log(f"[SUCCESS] ★ VC{ch} 影像擷取成功 ({len(full_frame)} bytes)")
                                break
        except Exception as e:
            self._log(f"Capture Loop Error: {e}")
        finally:
            if self.hDevice:
                try:
                    win32file.CancelIo(self.hDevice)
                except Exception:
                    pass
                win32file.CloseHandle(self.hDevice)
                self.hDevice = None
            if read_ov.hEvent:
                win32file.CloseHandle(read_ov.hEvent)
            if write_ov.hEvent:
                win32file.CloseHandle(write_ov.hEvent)

    def _monitor_throughput(self):
        now = time.time()
        if now - self.last_time >= 1.0:
            mbps = (self.bytes_count / (1024 * 1024)) / (now - self.last_time)
            # 送出一個特殊通道 -1 的訊息
            throughput_str = f"{mbps:.2f} MB/s"
            self.queue.put((-1, throughput_str))
            self.bytes_count = 0
            self.last_time = now


class apiStreamMgr:
    def __init__(self):
        self.data_queue = queue.Queue(maxsize=10)
        self.vc_configs = {}
        self.img_view = ImgView(None)
        self.img_process = ImgProcess(self.img_view)
        self.capture_thread = None
        self.consumer = None
        self.mirror = False
        self.flip = False

    @staticmethod
    def _log(message: str) -> None:
        global_log(tag="API_STREAMMGR", message=message)

    def set_bridge_callback(self, callback):
        self.img_view.output_callback = callback

    def start_stream(self, config_json: str) -> bool:
        try:
            configs = json.loads(config_json)
            self.vc_configs = {int(c['channel']): c for c in configs}
            self.capture_thread = ImgCapture(
                0x05A9, 0x8166, self.data_queue, self.vc_configs
            )
            if not self.capture_thread._init_native_win32():
                return False
            self.capture_thread.start()
            self.consumer = threading.Thread(target=self._consume_loop, daemon=True)
            self.consumer.start()
            self._log("Stream successfully started.")
            return True
        except Exception as e:
            self._log(f"ERROR: {e}")
            return False

    def update_transform(self, mirror: bool, flip: bool):
        """提供給 Bridge 呼叫的 API"""
        self.mirror = mirror
        self.flip = flip

    def _consume_loop(self):
        while self.capture_thread and self.capture_thread.is_alive():
            try:
                item = self.data_queue.get(timeout=1)
                ch = item[0]
                data = item[1]
                # 判斷是否為頻寬資訊
                if ch == -1:
                    if self.img_view.output_callback:
                        self.img_view.output_callback(-1, data)
                    continue
                # 影像處理邏輯...
                cfg = self.vc_configs.get(ch)
                if cfg:
                    seq = cfg.get('sequence', 'BG' if cfg['format'] == 5 else 'YUYV')
                    # 傳入當前的 mirror 與 flip 狀態
                    self.img_process.handle_frame(data, ch, cfg['width'], cfg['height'], cfg['format'], seq, self.mirror, self.flip)
            except queue.Empty:
                continue

    def stop_stream(self) -> bool:
        if self.capture_thread:
            self.capture_thread.is_running = False
            self.capture_thread.join(timeout=2.0)
        return True


if __name__ == "__main__":
    mgr = apiStreamMgr()
    mgr.set_bridge_callback(lambda ch, data: print(f"=== [OPENCV SUCCESS] CH{ch} BASE64 IMG READY! Len: {len(data)} ==="))
    test_cfg = json.dumps([
        {"channel": 0, "format": 5, "width": 1920, "height": 1080},
        {"channel": 1, "format": 2, "width": 1920, "height": 1080}
    ])
    if mgr.start_stream(test_cfg):
        try:
            time.sleep(30)
        except KeyboardInterrupt:
            pass
        mgr.stop_stream()
