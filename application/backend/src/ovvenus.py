# ovvenus.py
"""
[模組] VENUS 硬體行為 - 如果需要使用Thread, 請在上層建立來呼叫 此為純API動作層

Author: OVT AE
Date: 2026-01-12
Description:
"""
import atexit
import time
from datetime import datetime
import ctypes
import ovusb
import ovatb
import ovmcu

class apiOvVenus:
# Internal ---------------------------------------------------------------------------------------------
    def __init__(self):
        # 初始化中繼管理層
        self.venus_id = 0x64
        self.fpga_id = 0x40
        self.bit_venus = 0x33
        self.bit_fpga_switch = 0x00
        self.bit_fpga_reset = 0x13
        self._isBusy = False
        self._isUsbInited = False
        self._usb_mgr = ovusb.OvApiDrv(ignoreKey=True)
        self._dev_mgr = None
        self._venusPofVer = None
        self._venusMcuFwVer = None
        self._venusBaBootLoaderVer = None
        self._venusFpgaChipVer = None
        self._venusBoardVer = None
        self._venusSccbRate = None
        self._mcu_mgr = None
        self._atb_mgr = None

    def venus_device_init(self):
        # 嘗試初始化 Venus USB 驅動
        try:
            ret = self._usb_mgr.drv_device_init(1)  # 1:ON, 0:OFF
            if ret == 1:
                self._isUsbInited = True
                self._log("USB found. Identifying type...")
        except Exception as e:
            self._log(f"Exception during scan: {e}")

    def set_MCU_connect(self):
        self._mcu_mgr = ovmcu.apiOvMcu(self)
        self._dev_mgr = self._mcu_mgr

    def venus_get_info(self):
        # Venus Information
        self._venusPofVer          = self._usbI2cSingleRead(self.venus_id, 0x200A0FF0, self.bit_venus) or 0  # VENUS_POFVER_ADDR
        self._venusMcuFwVer        = self._usbI2cSingleRead(self.venus_id, 0x200A0FF4, self.bit_venus) or 0  # VENUS_MCUFWVER_ADDR
        self._venusBaBootLoaderVer = self._usbI2cSingleRead(self.venus_id, 0x200A0FF8, self.bit_venus) or 0  # VENUS_BABOOTLOADERVER_ADDR
        self._venusFpgaChipVer     = self._usbI2cSingleRead(self.venus_id, 0x200A0FFC, self.bit_venus) or 0  # VENUS_FPGACHIPVER_ADDR
        self._venusBoardVer        = self._usbI2cSingleRead(self.venus_id, 0x60200018, self.bit_venus) or 0  # VENUS_BOARDVER_ADDR
        self._venusSccbRate        = self._usbI2cSingleRead(self.venus_id, 0x700C5111, self.bit_venus) or 0  # VENUS_SCCBRATE_ADDR
        self._atb_mgr = ovatb.apiOvAtb(self)
        self._mcu_mgr = ovmcu.apiOvMcu(self)
        self._dev_mgr = self._mcu_mgr
        print("\n")
        self._log("Venus Information:")
        self._log(f"_venusPofVer:          0x{self._venusPofVer:08X}")
        self._log(f"_venusMcuFwVer:        0x{self._venusMcuFwVer:08X}")
        self._log(f"_venusBaBootLoaderVer: 0x{self._venusBaBootLoaderVer:08X}")
        self._log(f"_venusFpgaChipVer:     0x{self._venusFpgaChipVer:08X}")
        self._log(f"_venusBoardVer:        0x{self._venusBoardVer:08X}")
        self._log(f"_venusSccbRate:        0x{self._venusSccbRate:08X}")
        print("\n")
        # Venus default configurations
        self._usbI2cSingleWrite(self.venus_id, 0x700C5120, 0x00, self.bit_venus)  # enable PC to control OVTITAN
        self._usbI2cSingleWrite(self.venus_id, 0x60120020, 0x33, self.bit_venus)  # enable OVTITAN I2C
        time.sleep(0.4)
        self._usbI2cSingleWrite(self.fpga_id, 0x03, 0x02, self.bit_fpga_switch)  # enable OVTITAN to control I/O expander chip
        self._usbI2cSingleWrite(self.fpga_id, 0x07, 0xFC, self.bit_fpga_switch)  # enable sensor I3C for MCU
        time.sleep(0.4)
        # 註冊 atexit 確保 Python 程序結束時一定會執行關閉動作
        atexit.register(self.close)
        self._log("apiOvVenus loaded.")

    def _log(self, message):
        """
        支援極高精度時間戳記 (含微秒) 的偵錯打印
        """
        ts = "UNKNOWN_TIME"
        try:
            # 如果 datetime 模組在程式關閉時已被銷毀 (None)，這裡會拋出 AttributeError 或 TypeError
            # 如果 datetime 模組還在，這裡就會正常執行
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        except (AttributeError, TypeError, ImportError, NameError):
            # 捕捉所有可能的「模組已銷毀」錯誤
            ts = "SHUTDOWN_TIME"
        except Exception:
            ts = "ERROR_TIME"
        try:
            print(f"[{ts}][{'OVVENUS':>16}] {message}", flush=True)
        except ValueError:
            # 防止 stdout 已經被關閉
            pass

    def _usbI2cMultiRead(self, Devid, Addr, Length, width):
        """to read I2C from USB library to return value
        """
        if not self._isUsbInited:
            self._log("Venus USB API not inited")
            return None
        if Devid in (0x00, 0xFF):
            self._log(f"Wrong input device id: {Devid}")
            return None
        if self._isBusy:
            self._log("_usbI2cMultiRead(): is busy")
            return None
        self._isBusy = True
        try:
            buffer_size = Length + 4
            data = (ctypes.c_uint * buffer_size)()
            self._usb_mgr.drv_sccb_read(Devid, Addr, buffer_size, ctypes.cast(data, ctypes.POINTER(ctypes.c_uint)), width)
            result = list(data)
            return result
        except Exception as e:
            self._log(f"USB READ Error: {e}")
            return None
        finally:
            # 使用 finally 確保無論發生什麼事都會解除忙碌狀態
            self._isBusy = False

    def _usbI2cMultiWrite(self, DevId, Addr, Length, value, width):
        """
        支援單個或多個數據寫入
        value: 可以是單一整數，也可以是整數列表 [val1, val2, ...]
        """
        if not self._isUsbInited:
            self._log("Venus USB API not inited")
            return 0
        if DevId in (0x00, 0xFF):
            self._log(f"Wrong input device id: {hex(DevId)}")
            return 0
        if self._isBusy:
            self._log(f"_usbI2cMultiWrite is busy: {self._isBusy}")
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
            self._log(f"_usbI2cMultiWrite Error: {e}")
            return 0
        finally:
            self._isBusy = False

    def _usbI2cSingleRead(self, Devid, Addr, width):
        """to read I2C from USB library to return value
        """
        read_list = self._usbI2cMultiRead(Devid, Addr, 1, width)
        if read_list is not None and len(read_list) > 0:
            return read_list[0]
        self._log(f"SingleRead failed at Addr: {hex(Addr)}")
        return 0

    def _usbI2cSingleWrite(self, DevId, Addr, value, width):
        """寫入單一數值：透過呼叫 MultiWrite 達成"""
        self._usbI2cMultiWrite(DevId, Addr, 1, value, width)

    def __del__(self):
        """
        當物件被銷毀時確保設備已關閉
        """
        self.close()

# Interface ---------------------------------------------------------------------------------------------
    def reset_venus(self):
        """To reset Venus, provide the API for user-btn click"""
        self._usbI2cSingleWrite(self.fpga_id, 0x200, 0x01, self.bit_fpga_reset)
        self._usbI2cSingleWrite(self.fpga_id, 0x200, 0x300, self.bit_fpga_reset)
        self._usbI2cSingleWrite(self.fpga_id, 0x201, 0x01, self.bit_fpga_reset)
        time.sleep(0.2)
        self._usbI2cSingleWrite(self.fpga_id, 0x200, 0x01, self.bit_fpga_reset)
        self._usbI2cSingleWrite(self.fpga_id, 0x200, 0x300, self.bit_fpga_reset)
        time.sleep(0.5)
        self._usbI2cSingleWrite(self.venus_id, 0x700C5105, 0x01, self.bit_venus)  # Venus Chip Reset
        self._usbI2cSingleWrite(self.venus_id, 0x700C5120, 0x00, self.bit_venus)
        time.sleep(0.5)
        self._usbI2cSingleWrite(self.venus_id, 0x700C5120, 0x00, self.bit_venus)
        self._usbI2cSingleWrite(self.venus_id, 0x60120020, 0x33, self.bit_venus)
        time.sleep(0.4)
        self._usbI2cSingleWrite(self.fpga_id, 0x03, 0x02, self.bit_fpga_switch)
        self._usbI2cSingleWrite(self.fpga_id, 0x07, 0xFC, self.bit_fpga_switch)
        time.sleep(0.4)
        self._usbI2cSingleWrite(self.venus_id, 0x700C5120, 0x00, self.bit_venus)
        time.sleep(0.2)

    def scan_connected_board(self):
        """Scan the connected board with Venus by Venus USB API #TOIMPLEMENT It will be removed in the future"""
        boardType = 0  # 0: None, 1: MCU, 2: ATB
        self._dev_mgr = self._mcu_mgr
        try:
            if self._isUsbInited:
                self._usbI2cSingleWrite(self.venus_id, 0x700C5120, 0x01, self.bit_venus)  # enable PC to control MCU
                self._usbI2cSingleWrite(self.venus_id, 0x60120020, 0x33, self.bit_venus)  # enable OVTITAN I2C
                time.sleep(0.4)
                isMCU = self._dev_mgr.is_device_mcu()
                if isMCU:
                    boardType = 1
                    self._log("Board detected: MCU")
                else:
                    self._usbI2cSingleWrite(self.venus_id, 0x700C5120, 0x00, self.bit_venus)  # enable PC to control OVTITAN
                    self._usbI2cSingleWrite(self.venus_id, 0x60120020, 0x00, self.bit_venus)  # Disable OVTITAN I2C
                    time.sleep(0.4)
                    isATB = self._atb_mgr.is_device_atb()
                    if isATB:
                        boardType = 2
                        self._dev_mgr = self._atb_mgr
                        self._log("Board detected: ATB")
                        self._log("Start auto-load firmware...")
                        self._dev_mgr.loadMainFirmware()
                        self._log("Firmware loaded.")
                    else:
                        raise RuntimeError("Unknow board type")
            else:
                raise RuntimeError("USB not inited")
        except Exception as e:
            self._log(f"scan_connected_board() Error:{e}")
        finally:
            pass
        return boardType

    def is_test_running(self):
        if self._dev_mgr:
            return self._dev_mgr.is_test_running()
        return False

    def Set_Read_Frame(self, idx):
        """Set to read frame
        """
        data = 0x00000000 + idx  # Capture 0xF
        self._usbI2cSingleWrite(self.venus_id, 0x70200004, data, self.bit_venus)

    def Clear_Sequence_Capture(self):
        """Clear Venus to clear captured data
        """
        self._usbI2cSingleWrite(self.venus_id, 0x70200004, 0,  self.bit_venus)
        self._usbI2cSingleWrite(self.venus_id, 0x70200000, 0,  self.bit_venus)

    def Set_Sequence_Capture(self, idx):
        """Set Venus to do sequence capturing
        """
        data = 0x80000000  # Capture buff0
        self._usbI2cSingleWrite(self.venus_id, 0x600a0440, data, self.bit_venus)
        data = 0xC0000000  # Capture buff1
        self._usbI2cSingleWrite(self.venus_id, 0x600a0444, data, self.bit_venus)
        data = 0xC0000000  # Capture buff2
        self._usbI2cSingleWrite(self.venus_id, 0x600a0448, data, self.bit_venus)
        data = 0xC0000000  # Capture buff2
        self._usbI2cSingleWrite(self.venus_id, 0x600a044C, data, self.bit_venus)
        data = 0x0000000F  # Capture RAW12
        self._usbI2cSingleWrite(self.venus_id, 0x70200104, data, self.bit_venus)
        if idx > 0:
            # [16] Sequence captures enable. High active.
            # [15:0] Total requested capture frame number - 1
            data = 0x00010000 + idx - 1  # Capture 0xF
        else:
            data = 0x00000000
        self._usbI2cSingleWrite(self.venus_id, 0x70200000, data, self.bit_venus)

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
                print(f"[DATETIME UNKNOW][{'OVVENUS':>16}] Exception during close: {e}")

    def activate_test(self):
        """Activate Test Board to start test"""
        if self._dev_mgr and self._isUsbInited:
            return self._dev_mgr.activate_test()
        return -1

    def abort_test(self):
        """Activate Test Board to stop test"""
        if self._dev_mgr and self._isUsbInited:
            return self._dev_mgr.abort_test()
        return -1
