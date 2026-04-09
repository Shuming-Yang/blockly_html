# stream_mgr.py
# pylint: disable=no-member,c-extension-no-member
import threading
import queue
import time
import base64
import json
import winreg
import struct
from typing import Optional, Any
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
    """
    Image View Handler
    負責接收解析完成的影像與 EMBL 資料，並透過註冊的回呼函式 (Callback) 將其推播至前端 UI 介面。
    """
    def __init__(self, output_callback):
        """
        Initialize ImgView
        初始化影像顯示物件並綁定影像與 EMBL 的回呼函式
        """
        self.output_callback = output_callback
        self.embl_callback = None

    def show_embl(self, channel: int, embl_data: bytes):
        """
        Show EMBL Data
        將原始的 Byte 陣列轉為 Hex 字串陣列並推播至前端
        """
        try:
            if self.embl_callback is not None:
                hex_list = [f"0x{b:02X}" for b in embl_data]
                self.embl_callback(channel, hex_list)
        except Exception as e:
            global_log(tag="IMG_VIEW", message=f"EMBL Error: {e}")

    def show(self, channel: int, bgr_frame: np.ndarray, iq_data: Optional[dict[str, Any]] = None):
        """
        Show Camera Frame
        將 OpenCV 的 BGR 陣列編碼為 JPEG Base64 並推播至前端
        """
        try:
            ret, buffer = imencode('.jpg', bgr_frame, [int(CV_IMWRITE_JPEG_QUALITY), 80])
            if ret:
                b64_data = base64.b64encode(buffer).decode('utf-8')
                if self.output_callback:
                    self.output_callback(channel, b64_data, iq_data)
        except Exception as e:
            global_log(tag="IMG_VIEW", message=f"Encode Error: {e}")


class ImgProcess:
    """
    Image Processing Engine
    核心影像處理模組。職責已徹底解耦，分別提供獨立的 EMBL 擷取與 Video 解碼功能。
    """
    def __init__(self, view_instance: ImgView):
        self.view = view_instance
        self.last_embl_time = 0.0
        self.maximized_vc = -1

    @staticmethod
    def remove_payload(raw_data: bytes) -> bytes:
        """剔除 USB 傳輸協議中的 16 bytes 標頭"""
        chunk_size = 16384
        header_size = 16
        if len(raw_data) <= header_size:
            return b""
        return b"".join([
            raw_data[i + header_size : i + chunk_size]
            for i in range(0, len(raw_data), chunk_size)
        ])

    def process_embl(self, clean_bytes: bytes, channel: int, cfg: dict):
        """
        [獨立功能] 處理 EMBL 資料擷取
        直接接收總管傳來的 cfg 字典，進行絕對物理位址的陣列切片。
        """
        now = time.time()
        # 限制推播頻率 (每 0.5 秒更新一次)
        if now - self.last_embl_time < 0.5:
            return
        try:
            # 從共用的 cfg 中安全取出 EMBL 專屬參數
            e_pos = cfg.get('embl_pos', 'top')
            e_frame_bytes = cfg.get('frame_bytes', 0)
            e_display_len = cfg.get('embl_display_len', 1920)
            # 絕對物理位址計算
            if e_pos == "top":
                offset = 0
            else:
                # BOTTOM: 從硬體實際長度往回推
                offset = e_frame_bytes - e_display_len
            if offset >= 0 and offset + e_display_len <= len(clean_bytes):
                self.view.show_embl(channel, clean_bytes[offset:offset + e_display_len])
                self.last_embl_time = now
            else:
                global_log(tag="EMBL_PROCESS", message=f"Offset Error. Rx:{len(clean_bytes)}, Offset:{offset}, Req:{e_display_len}")
        except Exception as e:
            global_log(tag="EMBL_PROCESS", message=f"EMBL Extraction Error: {e}")

    def analyze_basic_iq(self, raw_img_8bit: np.ndarray, bgr_img: np.ndarray) -> dict[str, Any]:
        """進階影像 IQ 數值分析 (僅對放大的畫面執行)"""
        # 明確宣告變數型別，這樣 Mypy 就不會因為塞入 dict 而報錯
        iq_report: dict[str, Any] = {}
        h, w = raw_img_8bit.shape
        total_pixels = h * w
        # Brightness
        mean_brightness = float(np.mean(raw_img_8bit))
        iq_report['Brightness'] = round(mean_brightness, 2)
        # Exposure
        overexposed = int(np.sum(raw_img_8bit > 250))
        underexposed = int(np.sum(raw_img_8bit < 5))
        iq_report['Exposure'] = {
            'Over_Ratio_Pct': round((overexposed / total_pixels) * 100, 2),
            'Under_Ratio_Pct': round((underexposed / total_pixels) * 100, 2)
        }
        # Sharpness
        gray_img = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2GRAY)
        sharpness = float(cv2.Laplacian(gray_img, cv2.CV_64F).var())
        iq_report['Sharpness'] = round(sharpness, 2)
        # Lens Shading
        roi_h, roi_w = max(1, h // 10), max(1, w // 10)
        cy, cx = h // 2, w // 2
        center_mean = np.mean(raw_img_8bit[cy - roi_h//2 : cy + roi_h//2, cx - roi_w//2 : cx + roi_w//2])
        tl_mean = np.mean(raw_img_8bit[0:roi_h, 0:roi_w])
        tr_mean = np.mean(raw_img_8bit[0:roi_h, w-roi_w:w])
        bl_mean = np.mean(raw_img_8bit[h-roi_h:h, 0:roi_w])
        br_mean = np.mean(raw_img_8bit[h-roi_h:h, w-roi_w:w])
        corner_avg = (tl_mean + tr_mean + bl_mean + br_mean) / 4.0
        shading_ratio = (corner_avg / center_mean * 100) if center_mean > 0 else 100.0
        iq_report['Lens_Shading'] = {
            'Center_Lum': round(float(center_mean), 2),
            'Corner_Avg_Lum': round(float(corner_avg), 2),
            'Shading_Ratio_Pct': round(float(shading_ratio), 2)
        }
        return iq_report

    def process_video(self, clean_bytes: bytes, channel: int, width: int, height: int, fmt_type: int, sequence: str, mirror: bool, flip: bool):
        """
        [獨立功能] 處理 Video 影像解碼
        專注於 OpenCV 的色彩空間轉換、矩陣重塑與翻轉。
        """
        try:
            expected = width * height if fmt_type == 5 else width * height * 2
            if len(clean_bytes) < expected:
                # 資料量不足以解碼畫面，直接捨棄
                return
            bgr_img = None
            luma_8bit = None
            if fmt_type == 5: # 8-bit RAW
                img_np = np.frombuffer(clean_bytes[:expected], dtype=np.uint8)
                raw_img = img_np.reshape((height, width))
                luma_8bit = raw_img
                cv_code_str = f"COLOR_Bayer{sequence}2BGR" if sequence else "COLOR_BayerBG2BGR"
                cv_code = getattr(cv2, cv_code_str, 46)
                bgr_img = cvtColor(raw_img, cv_code)
            elif fmt_type == 7: # 16-bit / 10-bit Unpacked RAW
                img_np = np.frombuffer(clean_bytes[:expected], dtype=np.uint16)
                raw_img_16 = img_np.reshape((height, width))
                raw_img_8 = (raw_img_16 >> 2).astype(np.uint8)
                luma_8bit = raw_img_8
                cv_code_str = f"COLOR_Bayer{sequence}2BGR" if sequence else "COLOR_BayerBG2BGR"
                cv_code = getattr(cv2, cv_code_str, 46)
                bgr_img = cvtColor(raw_img_8, cv_code)
            elif fmt_type == 2: # YUV422
                img_np = np.frombuffer(clean_bytes[:expected], dtype=np.uint8)
                yuv_img = img_np.reshape((height, width, 2))
                luma_8bit = yuv_img[:, :, 0] # YUV 格式直接把 Y 通道剝離出來當 Luma 算！
                cv_code_str = f"COLOR_YUV2BGR_{sequence}" if sequence else "COLOR_YUV2BGR_YUYV"
                cv_code = getattr(cv2, cv_code_str, 85)
                bgr_img = cvtColor(yuv_img, cv_code)
            if bgr_img is not None:
                if mirror and flip:
                    bgr_img = cv2.flip(bgr_img, -1)
                elif mirror:
                    bgr_img = cv2.flip(bgr_img, 1)
                elif flip:
                    bgr_img = cv2.flip(bgr_img, 0)
                iq_report = None
                if channel == self.maximized_vc and luma_8bit is not None:
                    iq_report = self.analyze_basic_iq(luma_8bit, bgr_img)
                self.view.show(channel, bgr_img, iq_report)
        except Exception as e:
            global_log(tag="VIDEO_PROCESS", message=f"Video Decode Error: {e}")


class ImgCapture(threading.Thread):
    """
    USB Data Capture Thread
    繼承自 threading.Thread 的獨立執行緒。負責透過 Windows 原生 Win32 API (Overlapped I/O)
    與指定的 USB 設備進行非同步的大量資料傳輸 (Bulk Transfer)，並將重組後的完整 Frame 放入佇列。
    """
    def __init__(self, vid: int, pid: int, data_queue: queue.Queue, vc_configs: dict):
        """
        Initialize Image Capture Thread
        初始化 USB 資料擷取執行緒 綁定 VID PID 與資料佇列
        """
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
        """
        Log Capture Process
        專門用於影像擷取執行緒的日誌輸出
        """
        global_log(tag="IMG_CAPTURE", message=message)

    def _init_native_win32(self) -> bool:
        """
        Initialize Native Win32 Device
        透過 Windows Registry 查詢目標 USB 裝置並使用 Win32 API 建立連線
        """
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
        """
        Build Frame Request Packet
        根據 PDMA 規範動態建立 16 bytes 記憶體讀取請求標頭
        """
        header = bytearray(16)
        header[0] = 0x30 | CYPDMA_CTRL_READ | CYPDMA_CTRL_BULK | CYPDMA_CTRL_LASTPKT
        header[2] = 0x20
        # 動態根據通道計算記憶體位址偏移量
        addr = CYPDMA_DDR_BASE_ADDR + (channel * 0x0C000000) + 0x20
        struct.pack_into('<I', header, 8, addr)
        struct.pack_into('<I', header, 12, req_size)
        return bytes(header)

    def _flush_stale_data(self, read_ov, buf):
        """
        Flush Stale Data
        啟動擷取前強制清空 USB 緩衝區內的過期殘留資料
        """
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
        """
        Capture Thread Main Loop
        持續向啟用通道發送讀取請求 接收並重組資料流後寫入佇列
        """
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
        """
        Monitor Throughput
        定期結算傳輸量 計算 MB/s 後透過特殊通道 -1 寫入佇列
        """
        now = time.time()
        if now - self.last_time >= 1.0:
            mbps = (self.bytes_count / (1024 * 1024)) / (now - self.last_time)
            # 送出一個特殊通道 -1 的訊息
            throughput_str = f"{mbps:.2f} MB/s"
            self.queue.put((-1, throughput_str))
            self.bytes_count = 0
            self.last_time = now


class apiStreamMgr:
    """
    Stream Manager API
    USB 影像串流的總管類別。負責統一管理資料擷取執行緒、影像處理引擎與佇列 (Queue) 的生命週期，
    並提供對外的控制介面 (Start/Stop/Transform/EMBL)。
    """
    def __init__(self):
        """
        Initialize Stream Manager
        初始化串流管理員 控制資料佇列與執行緒的生命週期
        """
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
        """
        Log Stream Manager Output
        串流管理專用的日誌輸出
        """
        global_log(tag="API_STREAMMGR", message=message)

    def set_embl_callback(self, callback):
        """
        Set EMBL Callback
        供外部呼叫 註冊 EMBL 資料解析完畢的事件回呼函式
        """
        self.img_view.embl_callback = callback

    def start_embl(self, vc: int, pos: str, frame_bytes: int, display_length: int) -> int:
        """
        Start EMBL Extraction
        將 EMBL 參數直接整合進 vc_configs 中，與 Video 共享同一個狀態字典
        """
        # 確保該通道的字典存在 (前端保證會先呼叫 toggleStream，所以通常已存在)
        if vc not in self.vc_configs:
            self.vc_configs[vc] = {}
        # 寫入 EMBL 專屬參數與啟用標記
        self.vc_configs[vc]['is_embl'] = True
        self.vc_configs[vc]['embl_pos'] = pos
        self.vc_configs[vc]['frame_bytes'] = frame_bytes
        self.vc_configs[vc]['embl_display_len'] = display_length
        self._log(f"EMBL Configured for VC{vc} -> Pos:{pos}, FrameBytes:{frame_bytes}, DisplayLen:{display_length}")
        return 0

    def stop_embl(self) -> int:
        """
        Stop EMBL Extraction
        清除所有通道的 EMBL 標記，恢復為純 Video 模式
        """
        for vc in self.vc_configs:
            self.vc_configs[vc]['is_embl'] = False
        self._log("EMBL Stopped. Reverting to Video mode.")
        return 0

    def set_bridge_callback(self, callback):
        """
        Set Bridge Callback
        供外部呼叫 註冊影像編碼完畢的事件回呼函式
        """
        self.img_view.output_callback = callback

    def start_stream(self, config_json: str) -> bool:
        """
        Start USB Camera Stream
        解析 JSON 設定參數 初始化並啟動背景的擷取與消費雙執行緒
        """
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
        """
        Update Stream Transform
        更新影像的鏡像與翻轉狀態 供 ImgProcess 即時套用
        """
        self.mirror = mirror
        self.flip = flip

    def _consume_loop(self):
        """
        Consume Queue Loop
        背景消費執行緒，透過讀取 vc_configs 的標記，互斥派發任務
        """
        while self.capture_thread and self.capture_thread.is_alive():
            try:
                item = self.data_queue.get(timeout=1)
                ch = item[0]
                data = item[1]
                # 處理頻寬資訊
                if ch == -1:
                    if self.img_view.output_callback:
                        self.img_view.output_callback(-1, data)
                    continue
                # 統一清洗 Payload
                clean_bytes = self.img_process.remove_payload(data)
                # 取得統一的通道設定
                cfg = self.vc_configs.get(ch)
                if not cfg:
                    continue
                # 互斥派發 (Mutually Exclusive Routing)
                # 只要有 is_embl 標記，就【只】跑 EMBL 擷取！
                if cfg.get('is_embl', False):
                    self.img_process.process_embl(clean_bytes, ch, cfg)
                # 沒有 EMBL 標記，才跑耗資源的 Video 解碼！
                else:
                    seq = cfg.get('sequence', 'BG' if cfg.get('format') == 5 else 'YUYV')
                    self.img_process.process_video(
                        clean_bytes, ch,
                        cfg['width'], cfg['height'], cfg.get('format', 5),
                        seq, self.mirror, self.flip
                    )
            except queue.Empty:
                continue

    def stop_stream(self) -> bool:
        """
        Stop USB Camera Stream
        安全終止 USB 擷取執行緒並釋放所有底層裝置資源
        """
        if self.capture_thread:
            self.capture_thread.is_running = False
            self.capture_thread.join(timeout=2.0)
        return True

    def set_maximized_vc(self, channel: int):
        """設定當前放大的通道索引"""
        if self.img_process:
            self.img_process.maximized_vc = channel
