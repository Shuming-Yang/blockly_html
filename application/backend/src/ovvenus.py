# ovvenus.py
"""
[模組] VENUS 硬體行為 - 如果需要使用Thread, 請在上層建立來呼叫 此為純API動作層

Author: OVT AE
Date: 2026-01-12
Description:
"""
import os
import atexit
import time
import ctypes
from ovusb import OvApiDrv
from ovatb import apiOvAtb
from ovmcu import apiOvMcu
from shared_utils import global_log

class apiOvVenus:
# Internal ---------------------------------------------------------------------------------------------
    def __init__(self):
        # 初始化中繼管理層
        self.venus_id = 0x64
        self.fpga_id = 0x40
        self.bit_venus = 0x33
        self.bit_fpga_switch = 0x00
        self.bit_fpga_reset = 0x13
        self._run_status = 0x1
        self._isBusy = False
        self._isUsbInited = False
        self._usb_mgr = OvApiDrv(ignoreKey=True)
        self._dev_mgr = None
        self._venusPofVer = None
        self._venusMcuFwVer = None
        self._venusBaBootLoaderVer = None
        self._venusFpgaChipVer = None
        self._venusBoardVer = None
        self._venusSccbRate = None
        self._mcu_mgr = None
        self._atb_mgr = None
        self._header_set = ""
        # 註冊 atexit 確保 Python 程序結束時一定會執行關閉動作
        atexit.register(self.close)

    def venus_atb_board_init(self):
        if not self._atb_mgr:
            self._atb_mgr = apiOvAtb(self)
        self._dev_mgr = self._atb_mgr

    def venus_mcu_board_init(self):
        if not self._mcu_mgr:
            self._mcu_mgr = apiOvMcu(self)
        self._dev_mgr = self._mcu_mgr

    def venus_cfg_titan(self):
        if self._mcu_mgr:
            self._header_set = self._prepend_titan_config()
            # self._dev_mgr.send_script_content(self._header_set)
        return self._header_set

    def venus_device_init(self, skip_reinit: bool = False):
        # 嘗試初始化 Venus USB 驅動
        ret = -1
        try:
            if self._isUsbInited and skip_reinit:
                ret = 0
            else:
                ret = self._usb_mgr.drv_device_init(1)  # 1:ON, 0:OFF
                if ret == 1:
                    ret = 0
                    self._isUsbInited = True
                    self._log("USB found.")
                else:
                    raise RuntimeError(f"No USB found! {ret}")
        except Exception as e:
            ret = -1
            self._isUsbInited = False
            self._log(f"Error: venus_device_init({skip_reinit}): {e}")
        return ret

    def _prepend_titan_config(self):
        header_path = os.path.join(os.path.dirname(__file__), 'header.ini')
        if os.path.exists(header_path):
            try:
                with open(header_path, 'r', encoding='utf-8') as f:
                    config_lines = f.read()
                return config_lines
            except Exception as e:
                self._log(f"Error loading header.ini: {e}, switching to default configuration.")

        pof = self.venus_get_pof()
        if pof == 0x80241025:
            config_lines = [
                ";enable mcu start",
                "64 700c5120 00",
                "64 60120020 33",
                "sl 300 300",
                "40 03 02 ;40 is 8 bit address + 8 bit data",
                "sl 100 100",
                "40 07 FC ;switch I3C bus to MCU",
                "sl 100 100",
                "64 700C5120 01 ;switch control bus to MCU",
                ";enable mcu end",
                "102 AF1 FC ;enable MCU(fc) 32bit data",
                "sl 10 10"
            ]
        else:
            config_lines = [
                ";; enable mcu start",
                "64 700C5120 00",
                "64 60120020 33",
                "sl 400 400",
                "68 300c 1f ;select GPIO[7:0]",
                "68 3020 f0 ;bit 7:4 is gpio_out[3:0]",
                "68 3022 f8 ;gpio_oen[7:0]",
                "sl 400 400",
                "64 60120020 03",
                "64 700C5120 01",
                "102 AF1 FC ;enable MCU(fc) 32bit data",
                "sl 10 10"
            ]
        return config_lines

    def venus_get_pof(self):
        self._venusPofVer          = self.usbI2cSingleRead(self.venus_id, 0x200A0FF0, self.bit_venus) or 0  # VENUS_POFVER_ADDR
        return self._venusPofVer

    def venus_get_info(self):
        # Venus Information; self._venusPofVer is updated
        self._venusPofVer          = self.usbI2cSingleRead(self.venus_id, 0x200A0FF0, self.bit_venus) or 0  # VENUS_POFVER_ADDR
        self._venusMcuFwVer        = self.usbI2cSingleRead(self.venus_id, 0x200A0FF4, self.bit_venus) or 0  # VENUS_MCUFWVER_ADDR
        self._venusBaBootLoaderVer = self.usbI2cSingleRead(self.venus_id, 0x200A0FF8, self.bit_venus) or 0  # VENUS_BABOOTLOADERVER_ADDR
        self._venusFpgaChipVer     = self.usbI2cSingleRead(self.venus_id, 0x200A0FFC, self.bit_venus) or 0  # VENUS_FPGACHIPVER_ADDR
        self._venusBoardVer        = self.usbI2cSingleRead(self.venus_id, 0x60200018, self.bit_venus) or 0  # VENUS_BOARDVER_ADDR
        self._venusSccbRate        = self.usbI2cSingleRead(self.venus_id, 0x700C5111, self.bit_venus) or 0  # VENUS_SCCBRATE_ADDR
        self._log("Venus Information:")
        self._log(f"_venusPofVer:          0x{self._venusPofVer:08X}")
        self._log(f"_venusMcuFwVer:        0x{self._venusMcuFwVer:08X}")
        self._log(f"_venusBaBootLoaderVer: 0x{self._venusBaBootLoaderVer:08X}")
        self._log(f"_venusFpgaChipVer:     0x{self._venusFpgaChipVer:08X}")
        self._log(f"_venusBoardVer:        0x{self._venusBoardVer:08X}")
        self._log(f"_venusSccbRate:        0x{self._venusSccbRate:08X}")
        # version_buf = ctypes.create_string_buffer(128)
        # self._usb_mgr.ovApiIf.pyGetBaseIFVersion(version_buf)
        # version_str = version_buf.value.decode('utf-8', errors='ignore')
        # self._log(f"pyGetBaseIFVersion (String): {version_str}")

    def _log(self, message):
        """
        支援極高精度時間戳記 (含微秒) 的偵錯打印
        """
        global_log(tag="OVVENUS", message=message)

    def __del__(self):
        """
        當物件被銷毀時確保設備已關閉
        """
        self.close()

# Interface ---------------------------------------------------------------------------------------------
    def usbI2cMultiRead(self, Devid, Addr, Length, width):
        """to read I2C from USB library to return value
        """
        if not self._isUsbInited:
            self._log("Error: Venus USB API not inited")
            return None
        if Devid in (0x00, 0xFF):
            self._log(f"Error: Wrong input device id: {Devid}")
            return None
        if self._isBusy:
            self._log("Warning: usbI2cMultiRead(): is busy")
            return None
        self._isBusy = True
        try:
            buffer_size = Length + 4
            data = (ctypes.c_uint * buffer_size)()
            self._usb_mgr.drv_sccb_read(Devid, Addr, buffer_size, ctypes.cast(data, ctypes.POINTER(ctypes.c_uint)), width)
            result = list(data)
            return result
        except Exception as e:
            self._log(f"Error: USB READ: {e}")
            return None
        finally:
            # 使用 finally 確保無論發生什麼事都會解除忙碌狀態
            self._isBusy = False

    def usbI2cMultiWrite(self, DevId, Addr, Length, value, width):
        """
        支援單個或多個數據寫入
        value: 可以是單一整數，也可以是整數列表 [val1, val2, ...]
        """
        if not self._isUsbInited:
            self._log("Error: Venus USB API not inited")
            return 0
        if DevId in (0x00, 0xFF):
            self._log(f"Error: Wrong input device id: {hex(DevId)}")
            return 0
        if self._isBusy:
            self._log(f"Warning: usbI2cMultiWrite is busy: {self._isBusy}")
            return 0
        self._isBusy = True
        try:
            # 處理 ctypes 資料結構
            if isinstance(value, (list, bytes, tuple)):
                # 如果是 Python 原生序列，轉換為 ctypes 陣列
                data_type = ctypes.c_uint32 * len(value)
                data = data_type(*value)
                p_data = ctypes.cast(data, ctypes.POINTER(ctypes.c_uint32))
            elif hasattr(value, '_type_') and "Array" in type(value).__name__:
                # 如果已經是 ctypes 陣列 (例如從 _burst_mem 傳進來的)
                # 直接轉換為指標即可
                p_data = ctypes.cast(value, ctypes.POINTER(ctypes.c_uint32))
            else:
                # 單一數值
                data = ctypes.c_uint32(value)
                p_data = ctypes.byref(data)
            # 呼叫底層 API
            ret = self._usb_mgr.drv_sccb_write(DevId, Addr, Length, p_data, width)
            # 回傳最後寫入的數值或 1 代表成功
            return value[0] if isinstance(value, list) else ret
        except Exception as e:
            self._log(f"Error: usbI2cMultiWrite: {e}")
            return 0
        finally:
            self._isBusy = False

    def usbI2cSingleRead(self, Devid, Addr, width):
        """to read I2C from USB library to return value
        """
        read_list = self.usbI2cMultiRead(Devid, Addr, 1, width)
        if read_list is not None and len(read_list) > 0:
            return read_list[0]
        self._log(f"Error: SingleRead failed at Addr: {hex(Addr)}")
        return 0

    def usbI2cSingleWrite(self, DevId, Addr, value, width):
        """寫入單一數值：透過呼叫 MultiWrite 達成"""
        self.usbI2cMultiWrite(DevId, Addr, 1, value, width)

    def reset_venus(self):
        """To reset Venus, provide the API for user-btn click"""
        # venus_device_init is invoked by caller now.
        # if not self._isUsbInited:
        #     self.venus_device_init(skip_reinit = True)
        self.usbI2cSingleWrite(self.fpga_id, 0x200, 0x01, self.bit_fpga_reset)
        self.usbI2cSingleWrite(self.fpga_id, 0x200, 0x300, self.bit_fpga_reset)
        self.usbI2cSingleWrite(self.fpga_id, 0x201, 0x01, self.bit_fpga_reset)
        time.sleep(0.2)
        self.usbI2cSingleWrite(self.fpga_id, 0x200, 0x01, self.bit_fpga_reset)
        self.usbI2cSingleWrite(self.fpga_id, 0x200, 0x300, self.bit_fpga_reset)
        time.sleep(0.2)
        self.usbI2cSingleWrite(self.venus_id, 0x700C5105, 0x01, self.bit_venus)  # Venus Chip Reset
        time.sleep(0.01)
        # self.usbI2cSingleWrite(self.venus_id, 0x700C5120, 0x00, self.bit_venus)
        # self.usbI2cSingleWrite(self.venus_id, 0x700C5120, 0x00, self.bit_venus)
        # self.usbI2cSingleWrite(self.venus_id, 0x60120020, 0x33, self.bit_venus)
        # self.usbI2cSingleWrite(self.fpga_id, 0x03, 0x02, self.bit_fpga_switch)
        # self.usbI2cSingleWrite(self.fpga_id, 0x07, 0xFC, self.bit_fpga_switch)
        # self.usbI2cSingleWrite(self.venus_id, 0x700C5120, 0x00, self.bit_venus)
        self.venus_get_info()

    def is_test_running(self):
        if self._dev_mgr:
            return self._dev_mgr.is_test_running()
        return False

    def Set_Read_Frame(self, idx):
        """Set to read frame
        """
        data = 0x00000000 + idx  # Capture 0xF
        self.usbI2cSingleWrite(self.venus_id, 0x70200004, data, self.bit_venus)

    def Clear_Sequence_Capture(self):
        """Clear Venus to clear captured data
        """
        self.usbI2cSingleWrite(self.venus_id, 0x70200004, 0,  self.bit_venus)
        self.usbI2cSingleWrite(self.venus_id, 0x70200000, 0,  self.bit_venus)

    def Set_Sequence_Capture(self, idx):
        """Set Venus to do sequence capturing
        """
        data = 0x80000000  # Capture buff0
        self.usbI2cSingleWrite(self.venus_id, 0x600a0440, data, self.bit_venus)
        data = 0xC0000000  # Capture buff1
        self.usbI2cSingleWrite(self.venus_id, 0x600a0444, data, self.bit_venus)
        data = 0xC0000000  # Capture buff2
        self.usbI2cSingleWrite(self.venus_id, 0x600a0448, data, self.bit_venus)
        data = 0xC0000000  # Capture buff2
        self.usbI2cSingleWrite(self.venus_id, 0x600a044C, data, self.bit_venus)
        data = 0x0000000F  # Capture RAW12
        self.usbI2cSingleWrite(self.venus_id, 0x70200104, data, self.bit_venus)
        if idx > 0:
            # [16] Sequence captures enable. High active.
            # [15:0] Total requested capture frame number - 1
            data = 0x00010000 + idx - 1  # Capture 0xF
        else:
            data = 0x00000000
        self.usbI2cSingleWrite(self.venus_id, 0x70200000, data, self.bit_venus)

    def read_script_status(self):
        self._run_status = self.usbI2cSingleRead(self.venus_id, 0x700c5120, self.bit_venus)
        return self._run_status

    def load_db_file(self, fname=None):
        if fname is not None:
            # return pointer to the DB file success
            # return = 0 fail
            ret = self._usb_mgr.drv_load_db_file(fname=fname)
        else:
            ret = 0
        return ret

    def send_db_file(self, setting_index):
        return self._usb_mgr.drv_send_db_file(setting_index=setting_index)

    def close(self):
        """
        手動關閉 USB 設備並釋放資源
        """
        if self._isUsbInited:
            try:
                # 執行關閉動作 (0:OFF)
                self._log("USB device closing....")
                self._usb_mgr.drv_device_init(0)
                self._isUsbInited = False
            except Exception as e:
                print(f"[DATETIME UNKNOW][{'OVVENUS':>16}] Error: Exception during close: {e}")

    def activate_test(self):
        """Activate Test Board to start test"""
        if self._dev_mgr and self._isUsbInited:
            return self._dev_mgr.activate_test()
        return -1

    def abort_test(self, test_mode=0):
        """Activate Test Board to stop test"""
        if self._dev_mgr and self._isUsbInited:
            return self._dev_mgr.abort_test(test_mode)
        return -1
