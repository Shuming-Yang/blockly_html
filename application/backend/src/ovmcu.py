# ovmcu.py
"""
[模組] MCU 硬體行為

Author: OVT AE
Date: 2026-01-07
Description:
"""
import ctypes
import time
from datetime import datetime
import traceback

class apiOvMcu:
# Internal ---------------------------------------------------------------------------------------------
    def __init__(self, parent):
        # 初始化中繼管理層
        self.DWORD_OF_T_RESULT_HEADER = 6
        self.DWORD_OF_T_TCOVIEW = 3
        self.DWORD_OF_T_ERRLOG = 8
        self.PRE_IDX_OFFSET = (self.DWORD_OF_T_ERRLOG - 1) * 4
        self.FW_RESULT_ADDRESS = 0xC00
        self.TEST_CASE_MAX = 10
        self._venus_api = parent
        self._is_busy = False
        self.chip_id = 0xBC
        self.bit = 0x13
        self._resultBurstLength = 48
        self._resultSize = 0x2400
        self._resultArray = (ctypes.c_uint8 * self._resultSize)(*([0] * self._resultSize))
        self._supportHexMode = False
        self._supportCmdMode = False
        self._log("apiOvMcu loaded.")

    def _log(self, message):
        """
        支援極高精度時間戳記 (含微秒) 的偵錯打印
        """
        # %f 會顯示 6 位數的微秒
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        print(f"[{ts}][{'OVMCU':>16}] {message}")

    def _Readu32bytes(self, chip_id=None, addr=None, switch=0):
        if not self._is_busy:
            if not chip_id:
                chip_id = self.chip_id
            if not addr:
                out_data = 0
                return out_data
            self._is_busy = True
            read_data = (ctypes.c_uint32 * 8)()
            self._drv_sccb_read(chip_id, addr, 4, ctypes.cast(read_data, ctypes.POINTER(ctypes.c_uint32)))
            if switch == 1:
                out_data = read_data[3] << 24 | read_data[2] << 16 | read_data[1] << 8 | read_data[0]
            else:
                out_data = read_data[0] << 24 | read_data[1] << 16 | read_data[2] << 8 | read_data[3]
            self._is_busy = False
        else:
            out_data = 0
        return out_data

    def _drv_sccb_read(self, dev_id, addr, length, data):
        if length <= 4:
            bit = self.bit
            self._venus_api._usb_mgr.set_addr_width(bit, dev_id)
            byteNum = self._venus_api._usb_mgr.set_data_width(bit, dev_id)
            self._venus_api._usb_mgr.ovApiIf.pyWriteRegister(0x102, 0xAF1, dev_id, 0xFF)
            mask = self._venus_api._usb_mgr.get_mask(byteNum)
            temp = self._venus_api._usb_mgr.ovApiIf.pyReadRegister(dev_id, addr, mask)
            val = temp & 0xFFFFFFFF
            try:
                data[0] = val
            except Exception:
                data = temp.to_bytes(4, byteorder='big')
            ret = 1
        else:
            self._venus_api._usb_mgr.set_addr_width(0x10, dev_id)
            byteNum = self._venus_api._usb_mgr.set_data_width(0x10, dev_id)
            self._venus_api._usb_mgr.ovApiIf.pyWriteRegister(0x102, 0xAF1, 0, 0xFF)
            self._venus_api._usb_mgr.ovApiIf.pyWriteRegister(0x64, 0x400A0024, 0x00, 0xFFFFFFFF)
            self._venus_api._usb_mgr.ovApiIf.pyWriteRegister(0x64, 0x400A0008, length, 0xFFFFFFFF)
            ret = self._venus_api._usb_mgr.ovApiIf.pyReadRegBurst(dev_id, addr, data, length)
        return ret

    def _drv_sccb_write(self, dev_id, addr, length, data, bit):
        #self._venus_api._usb_mgr.ovApiIf.pyWriteRegister(0x64, 0x400A0024, 0x00, 0xFFFFFFFF)
        #self._venus_api._usb_mgr.ovApiIf.pyWriteRegister(0x64, 0x400A0008, 0x00, 0xFFFFFFFF)
        if length <= 4:
            self._venus_api._usb_mgr.set_addr_width(bit, dev_id)
            byteNum = self._venus_api._usb_mgr.set_data_width(bit, dev_id)
            self._venus_api._usb_mgr.ovApiIf.pyWriteRegister(0x102, 0xAF1, dev_id, 0xFF)
            try:
                temp = data._obj.value
            except Exception:
                try:
                    temp = data[0]
                    d_len = len(data)
                    if d_len == 4:
                        temp = (data[0] << 24) | (data[1] << 16) | (data[2] << 8) | data[3]
                except Exception:
                    try:
                        temp = data.value
                    except Exception:
                        temp = data
            mask = self._venus_api._usb_mgr.get_mask(byteNum)
            ret = self._venus_api._usb_mgr.ovApiIf.pyWriteRegister(dev_id, addr, temp, mask)
        else:
            self._venus_api._usb_mgr.set_data_width(0, dev_id)
            self._venus_api._usb_mgr.ovApiIf.pyWriteRegister(0x102, 0xAF1, 0, 0xFF)
            byteNum = 1
            self._venus_api._usb_mgr.ovApiIf.pyWriteRegister(0x64, 0x400A0028, length, 0xFFFFFFFF)
            self._venus_api._usb_mgr.ovApiIf.pyWriteRegister(0x102, 0xEAF, 300, 0xFFFFFFFF)
            self._venus_api._usb_mgr.ovApiIf.pyWriteRegister(0x102, 0xEAE, 0x101, 0xFFFFFFFF)
            try:
                temps = data._obj[:]
            except Exception:
                try:
                    temps = data[:]
                except Exception:
                    try:
                        temps = next(i for i in data._objects.values())[:]
                    except Exception:
                        try:
                            temps = [data._obj.value]
                        except Exception:
                            try:
                                temps = [data.value]
                            except Exception:
                                temps = [data]
            datas = (ctypes.c_uint32 * (length * byteNum))()
            for i in range(length):
                for j in range(byteNum):
                    datas[i * byteNum + j] = (temps[i] >> (8 * (byteNum - j - 1))) & 0xFF
            ret = self._venus_api._usb_mgr.ovApiIf.pyWriteRegBurst(dev_id, addr, datas, length * byteNum)
        return ret

    def _read_dataarray(self, addr, length):
        """Get MCU data
        """
        if self._is_busy:
            self._log("_read_dataarray(): SCCB is busy")
            return None
        self._is_busy = True
        try:
            read_data = (ctypes.c_uint * (length + 4))()
            self._drv_sccb_read(self.chip_id,
                                addr,
                                length + 4,
                                ctypes.cast(read_data, ctypes.POINTER(ctypes.c_uint)))
            return read_data
        except Exception as e:
            self._log(f"_read_dataarray(): {e}")
        finally:
            self._is_busy = False

    def _burst_mem(self, start_addr, data):
        data_length = len(data)
        max_length = 4
        current_index = 0
        addr = start_addr
        while current_index < data_length:
            if data_length - current_index >= max_length:
                write_length = max_length
            else:
                write_length = data_length - current_index
            write_data = (ctypes.c_uint32 * write_length)()
            for i in range(write_length):
                write_data[i] = data[current_index + i]
            try:
                self._drv_sccb_write(self.chip_id, addr, write_length, write_data, self.bit)
            except Exception as e:
                self._log(f"writeDatas(), _drv_sccb_write({self.chip_id:02X}, {addr:04X}, {write_length}, ,{self.bit:02X}): {e}")
            time.sleep(0.001)
            current_index += write_length
            addr += write_length  # 位址遞增

# Interface ---------------------------------------------------------------------------------------------
    def is_test_running(self):
        if not self._is_busy and self._venus_api and self._venus_api._usb_mgr:
            state = self._Readu32bytes(chip_id = self.chip_id, addr=0x3000, switch=1)
            if state == 0x05:
                return True
        return False

    def activate_test(self):
        """Activate Test Board to start test"""
        if not self._is_busy and self._venus_api and self._venus_api._usb_mgr:
            self._is_busy = True
            write_data = (ctypes.c_uint32 * 8)()
            write_data[0] = 0
            self._drv_sccb_write(self.chip_id, 0x3000, 1, write_data, self.bit)
            self._is_busy = False
            return 0
        return -1

    def abort_test(self):
        """Activate Test Board to stop test"""
        if not self._is_busy and self._venus_api and self._venus_api._usb_mgr:
            self._is_busy = True
            write_data = (ctypes.c_uint32 * 8)()
            write_data[0] = 1
            self._drv_sccb_write(self.chip_id, 0x3001, 1, write_data, self.bit)
            self._is_busy = False
            return 0
        return -1

    def is_device_mcu(self):
        """Detect if MCU board is connected"""
        if self._is_busy:
            self._log("is_device_mcu(): SCCB is busy")
            return False
        try:
            ret = False
            self._is_busy = True
            self._supportCmdMode = False
            self._supportHexMode = False
            read_data = (ctypes.c_uint32 * 4)()
            target_id = 0x49334355
            self._drv_sccb_read(0xFC, 0x100A, 1, ctypes.cast(read_data, ctypes.POINTER(ctypes.c_uint32)))
            if read_data[0] == target_id:
                ret = True
                self._supportCmdMode = True
            else:
                self._log(f"Device: 0xFC, read_data[0]: {hex(read_data[0])}")
            ctypes.memset(read_data, 0, ctypes.sizeof(read_data))
            self._drv_sccb_read(self.chip_id, 0xF080, 1, ctypes.cast(read_data, ctypes.POINTER(ctypes.c_uint32)))
            if read_data[0] == target_id:
                ret = True
                self._supportHexMode = True
            else:
                self._log(f"Device: 0xBC, read_data[0]: {hex(read_data[0])}")
            return ret
        except Exception as e:
            self._log(f"is_device_mcu(): {e}")
            return ret
        finally:
            self._is_busy = False
            self._log(f"is_device_mcu(): {ret}")

    def readTestResult(self):
        """Read MCU result data.
        """
        try:
            logUnusedIdx = 0
            exact_byte_size = 0
            total_reads = self._resultSize // self._resultBurstLength
            skip_index_threshold = total_reads
            for read_index in range(total_reads):
                address = self.FW_RESULT_ADDRESS + (read_index * self._resultBurstLength)
                # 取得數據 (ctypes array)
                if read_index < skip_index_threshold or read_index == total_reads - 1:
                    ctypes_data = self._read_dataarray(address, self._resultBurstLength)
                    if not ctypes_data:
                        raise RuntimeError("_read_dataarray is None")
                    uint32_array = list(ctypes_data)
                    time.sleep(0.1)
                else:
                    uint32_array = [0] * self._resultBurstLength
                # 填入 result array (取 LSB)
                for i in range(self._resultBurstLength):
                    if i < len(uint32_array):
                        start_index = (read_index * self._resultBurstLength) + i
                        self._resultArray[start_index] = uint32_array[i] & 0xFF
                # 解析 Header
                if read_index == 0:
                    # 解析 rsltCfg
                    # uint32_array[8:12] 是 [int, int, int, int] 轉成 bytes 才能給 int.from_bytes 用
                    cfg_slice = uint32_array[8:12]
                    cfg_bytes = bytes([x & 0xFF for x in cfg_slice])
                    rsltCfg = int.from_bytes(cfg_bytes, byteorder='little')
                    if rsltCfg & 0xFFFFF == 0:
                        self._log("Dumping in Fast Speed Mode")
                        # 解析 logUnusedIdx
                        idx_slice = uint32_array[16:20]
                        idx_bytes = bytes([x & 0xFF for x in idx_slice])
                        logUnusedIdx = int.from_bytes(idx_bytes, byteorder='little')
                        exact_byte_size = 4 * (self.DWORD_OF_T_RESULT_HEADER +
                                               self.DWORD_OF_T_TCOVIEW * self.TEST_CASE_MAX +
                                               self.DWORD_OF_T_ERRLOG * logUnusedIdx)
                        skip_index_threshold = (exact_byte_size // self._resultBurstLength) + 1
            # 處理未使用索引
            if skip_index_threshold < total_reads:
                preIdx = logUnusedIdx + 1
                # 計算範圍，並增加保護避免超出陣列
                start_fill = exact_byte_size + self.PRE_IDX_OFFSET
                end_fill = len(self._resultArray) - self._resultBurstLength
                if start_fill < len(self._resultArray):
                    for i in range(start_fill, end_fill, self.DWORD_OF_T_ERRLOG * 4):
                        # 將 int 轉 bytes 後，逐 byte 填入 c_uint8 陣列
                        # ctypes array 不支援直接 assign bytes object 到 slice
                        b_val = preIdx.to_bytes(4, byteorder='little')
                        for k in range(4):
                            if i + k < len(self._resultArray):
                                self._resultArray[i + k] = b_val[k]
                        preIdx += 1
        except Exception as e:
            self._log(f"readMcuResult Error: {e}")
            self._log(traceback.format_exc())  # 印出詳細錯誤以便除錯
        finally:
            pass

    def write_testcases(self, data=None):
        if self._is_busy:
            self._log("write_testcases(): is busy")
            return None
        self._is_busy = True
        try:
            self._burst_mem(0x4000, data)
        except Exception as e:
            self._log(f"write_testcases(): {e}")
        finally:
            self._is_busy = False

    def send_script_function(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        lines = content.splitlines()
        # 印出前 5 行看看結果
        for line in lines:
            clean_line = line.strip()
            clean_line = clean_line.split(';')[0].strip()
            if not clean_line:
                continue
            self._log(f"處理中: {clean_line}")
            # self._venus_api._usb_mgr.ovApiIf.pyWriteRegister(0x102, 0xAF1, dev_id, 0xFFFFFFFF)
             # 2. 檢查是否以 SL 或 DELAY 開頭
            is_command = clean_line.upper().startswith(('SL', 'DELAY'))
            # is_hex_data = self.is_hex(clean_line)
            # 過濾邏輯：如果是指令 OR 是純16進位數據
            if is_command:
                value = clean_line.split()[1]
                dly_time = int(value, 16) / 1000
                time.sleep(dly_time)
            else:
                dev, addr, data, *_ = clean_line.split()
                mask = 0xFFFFFFFF
                if dev == '40':
                    mask = 0xFF
                elif dev == '64':
                    mask = 0xFF
                else:
                    mask = 0xFFFFFFFF
                self._venus_api._usb_mgr.ovApiIf.pyWriteRegister(int(dev, 16), int(addr, 16), int(data, 16), mask)
