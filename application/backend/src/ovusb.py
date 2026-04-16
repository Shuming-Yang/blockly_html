# ovusb.py
"""
[底層] DLL 調用抽象層

Author: OVT AE
Date: 2026-01-07
Description:
"""
# WARNING
# pylint: disable=C0103,C0114,C0115,C0116,R0205,R0917,W0212,W0718
import sys
import ctypes
import os
import time
from enum import Enum
from shared_utils import global_log

# ------- Porting Area - 需要在Port到不同的Project時根據當下的檔案架構與設定架構進行修改使用 ------
I3C_MCU_ID = 0xFC
VENUS_ID = 0x64

def get_dll_dir():
    """自動判定環境並回傳正確的 DLL 目錄路徑"""
    if getattr(sys, 'frozen', False):
        # --- PyInstaller 打包環境 ---
        # sys._MEIPASS 會自動指向 _internal 資料夾 (onedir) 或暫存資料夾 (onefile)
        base_dir = sys._MEIPASS
        return base_dir
    # --- 開發環境 (.py) ---
    # __file__ 是 usb.py 的路徑: .../backend/src/usb.py
    # 回退到 backend/lib
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    # 取得 backend 資料夾路徑
    backend_dir = os.path.dirname(current_script_dir)
    return os.path.join(backend_dir, "lib")

# 直接取得正確路徑
OVAPI_LIB_DIR = get_dll_dir()
# ------- Porting Area - 需要在Port到不同的Project時根據當下的檔案架構與設定架構進行修改使用 ------


class OVAPICmds(Enum):
    OVAPI_VERSION_OVBIF       = 0x1000
    OVAPI_INIT_SCCB           = 0x1110
    OVAPI_CLOSE_SCCB          = 0x1111
    OVAPI_INIT_VIDEO          = 0x1120
    OVAPI_CLOSE_VIDEO         = 0x1121
    OVAPI_INIT_DB             = 0x1130
    OVAPI_CLOSE_DB            = 0x1131
    OVAPI_SET_RES             = 0x1200
    OVAPI_GET_RES_X           = 0x1201
    OVAPI_GET_RES_Y           = 0x1203
    OVAPI_SET_MODE            = 0x1210
    OVAPI_GET_MODE            = 0x1211
    OVAPI_SET_SEQ             = 0x1220
    OVAPI_GET_SEQ             = 0x1221
    OVAPI_GET_RAW_BUF         = 0x1401
    OVAPI_GET_DISPLAY_BUF     = 0x1403
    OVAPI_SET_CALLBACK_ON_RAW = 0x1500
    OVAPI_SET_SCCB_VALUE      = 0x1800
    OVAPI_GET_SCCB_VALUE      = 0x1810
    OVAPI_LOAD_REG_FILE       = 0x3000
    OVAPI_SEND_REG_FILE       = 0x3010
    OVAPI_LOAD_DB_FILE        = 0x3200
    OVAPI_SEND_DB_FILE        = 0x3210
    OVAPI_SEND_FUNC_FILE      = 0x3410
    OVAPI_GET_SCCB_BURST      = 0x1812
    OVAPI_SET_SCCB_BURST      = 0x1802
    OVAPI_GET_SCCB_RAND_BURST = 0x1816
    OVAPI_SET_SCCB_RAND_BURST = 0x1806


class _OVBaseIF(object):
    """Interface to OVT API (OVBaseIF.dll) 內部使用的 DLL 介面"""
    def __init__(self,dll_folder=None):
        dll_name = 'OVBaseIFX64.dll'
        if dll_folder is not None:
            plugin_folder = dll_folder + '\\platforms'
            os.environ['PATH'] += os.pathsep + dll_folder
            os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_folder
            dll_path = os.path.join(dll_folder, dll_name)
            self.ovt = ctypes.cdll.LoadLibrary(dll_path)
        else:
            self.ovt = ctypes.cdll.LoadLibrary(dll_name)

    def pyInitOVDriver(self, xSize, ySize):
        success =  self.ovt.OVBIF_CmdIF(OVAPICmds.OVAPI_INIT_VIDEO.value, xSize, ySize, 0, 0)
        return success

    def pyInitOVDriverSCCB(self):
        success =  self.ovt.OVBIF_CmdIF(OVAPICmds.OVAPI_INIT_SCCB.value, 0, 0, 0, 0)
        return success

    def pyWriteRegister(self, dev_id, addr, data, mask):
        success = self.ovt.OVBIF_CmdIF(OVAPICmds.OVAPI_SET_SCCB_VALUE.value, dev_id, addr, data, mask)
        return success

    def pyReadRegister(self, dev_id, addr, mask):
        data = ctypes.c_int(-9999)
        _success = self.ovt.OVBIF_CmdIF(OVAPICmds.OVAPI_GET_SCCB_VALUE.value, dev_id, addr, ctypes.byref(data), mask)
        return data.value

    def pyReadRegBurst(self, dev_id, addr_st, pData, dl):
        #data = c_int(-9999)
        success = self.ovt.OVBIF_CmdIF(OVAPICmds.OVAPI_GET_SCCB_BURST.value, dev_id, addr_st, pData, dl)
        return success

    def pyReadRegRandBurst(self, pSid, pAddr, pData, dl):
        #data = c_int(-9999)
        success = self.ovt.OVBIF_CmdIF(OVAPICmds.OVAPI_GET_SCCB_RAND_BURST.value, pSid, pAddr, pData, dl)
        return success

    def pyWriteRegBurst(self, dev_id, addr_st, pData, dl):
        #data = c_int(-9999)
        success = self.ovt.OVBIF_CmdIF(OVAPICmds.OVAPI_SET_SCCB_BURST.value, dev_id, addr_st, pData, dl)
        return success

    def pyWriteRegRandBurst(self, pSid, pAddr, pData, dl):
        #data = c_int(-9999)
        success = self.ovt.OVBIF_CmdIF(OVAPICmds.OVAPI_SET_SCCB_RAND_BURST.value, pSid, pAddr, pData, dl)
        return success

    def pyLoadDBFile(self, fname):
        success = self.ovt.OVBIF_CmdIF(OVAPICmds.OVAPI_LOAD_DB_FILE.value, fname, 0, 0, 0)
        return success

    def pySendDBFile(self, idx):
        idx = max(idx, 1)
        success = self.ovt.OVBIF_CmdIF(OVAPICmds.OVAPI_SEND_DB_FILE.value, idx, 0, 0, 0)
        return success

    def pySendRegFile(self, fname, idx):
        _success = self.ovt.OVBIF_CmdIF(OVAPICmds.OVAPI_SEND_FUNC_FILE.value, fname, idx, 0, 0)

    def pyGetBaseIFVersion(self,pBuf):
        success = self.ovt.OVBIF_CmdIF(OVAPICmds.OVAPI_VERSION_OVBIF.value, pBuf, 0, 0, 0)
        return success

    def pyRegisterCBRawIamge(self, pCBFunc):
        success = self.ovt.OVBIF_CmdIF(OVAPICmds.OVAPI_SET_CALLBACK_ON_RAW.value, pCBFunc, 0, 0, 0)
        return success

    def pyAcquireImage(self, pBuf):
        success = self.ovt.OVBIF_CmdIF(OVAPICmds.OVAPI_GET_DISPLAY_BUF.value, pBuf, 0, 0, 0)
        return success

    def pyAcquireRawImage(self, pBuf, dl):
        success = self.ovt.OVBIF_CmdIF(OVAPICmds.OVAPI_GET_RAW_BUF.value, pBuf, dl, 0, 0)
        return success

    def pyChangeSeq(self,seq):
        success = self.ovt.OVBIF_CmdIF(OVAPICmds.OVAPI_SET_SEQ.value, seq, 0, 0, 0)
        return success

    def pyChangeMode(self,mode):
        success = self.ovt.OVBIF_CmdIF(OVAPICmds.OVAPI_SET_MODE.value, mode, 0, 0, 0)
        return success

    def pyChangeResolution(self,width, height):
        success = self.ovt.OVBIF_CmdIF(OVAPICmds.OVAPI_SET_RES.value, width, height, 0, 0)
        return success

    #use with init ovdr sccb
    def pyCloseOVDriverSCCB(self):
        success = self.ovt.OVBIF_CmdIF(OVAPICmds.OVAPI_CLOSE_SCCB.value, 0, 0, 0, 0)
        return success

    def pyFinishDriver(self):
        success = self.ovt.OVBIF_CmdIF(OVAPICmds.OVAPI_CLOSE_VIDEO.value, 0, 0, 0, 0)
        return success


class _SccbDrv:
    """內部使用的基底驅動類別"""
    def _log(self, message):
        """
        支援極高精度時間戳記 (含微秒) 的偵錯打印
        """
        global_log(tag="OVUSB::SCCBDRV", message=message)

    def __init__(self):
        pass

    def drv_device_init(self, _onoff):
        # self._log(f"It's a drv_device_init prototype, onoff={_onoff}")
        return -1

    def drv_sccb_write(self, _dev_id, _addr, _length, _data, _bit):
        # self._log(f"It's a drv_sccb_write prototype, dev_id={hex(_dev_id)}, addr={hex(_addr)}, length={hex(_length)}, data={hex(_data[0])}, bit={hex(_bit)}")
        pass

    def drv_sccb_read(self, _dev_id, _addr, _length, _data, _bit):
        # self._log(f"It's a drv_sccb_read prototype, dev_id={hex(_dev_id)}, addr={hex(_addr)}, length={hex(_length)}, bit={hex(_bit)}")
        pass

    def drv_get_RAW2Buff(self, _buff, _RdLength):
        # self._log(f"It's a drv_get_RAW2Buff prototype, RdLength={hex(_RdLength)}")
        return 0xF2000001

    def drv_change_resolution(self, _width, _height):
        # self._log("It's a drv_change_resolution prototype")
        return -1


class OvApiDrv(_SccbDrv):
    _inited = False
    _ovApiIf: _OVBaseIF | None = None

    def _log(self, message):
        """
        支援極高精度時間戳記 (含微秒) 的偵錯打印
        """
        global_log(tag="OVUSB::OVAPIDRVE", message=message)

    def __init__(self, ignoreKey=True):
        if not OvApiDrv._ovApiIf:
            try:
                OvApiDrv._ovApiIf = _OVBaseIF(OVAPI_LIB_DIR)
                self.ovApiIf = OvApiDrv._ovApiIf
                if ignoreKey:
                    # Use magic number to ignore key verification
                    self.ovApiIf.ovt.OVBIF_CmdIF(0x33274479, 0x33274479, 0, 0, 0)
                # self._log("OVBaseIFX64.dll is loaded")
            except OSError as e:
                self._log(f"Error: Cannot load OVBaseIFX64.dll: {e}")

    def set_addr_width(self, bit, dev_id):
        flag_16bit = 0  # API automatically detect
        flag_32bit = 0  # API automatically detect
        bit &= 0xF0
        if bit == 0x00:
            # 8bit address
            flag_16bit = 0
            flag_32bit = 0
        elif bit == 0x10:
            # 16bit address
            flag_16bit = dev_id
        elif bit == 0x30:
            # 32bit address, API automatically detect when the address > 0xFFFF
            flag_32bit = dev_id
        self.ovApiIf.pyWriteRegister(0x102, 0xAA0, flag_16bit, 0xFF)
        self.ovApiIf.pyWriteRegister(0x102, 0xAE0, flag_32bit, 0xFF)

    def set_data_width(self, bit, dev_id):
        flag_16bit = 0  # API automatically detect
        flag_32bit = 0  # API automatically detect
        byteNum = 0
        bit &= 0xF
        if bit == 0x0:
            # 8bit data
            byteNum = 1
        elif bit == 0x1:
            # 16bit data
            flag_16bit = dev_id
            byteNum = 2
        elif bit == 0x3:
            # 32bit data, API automatically detect when the data > 0xFFFF
            flag_32bit = dev_id
            byteNum = 4
        self.ovApiIf.pyWriteRegister(0x102, 0xAB0, flag_16bit, 0xFF)
        self.ovApiIf.pyWriteRegister(0x102, 0xAF0, flag_32bit, 0xFF)
        return byteNum

    def get_mask(self, byteNum):
        # byteNum(1,2,3,4) mapping to mask(0xFF,0xFFFF,0xFFFFFFFF,0xFFFFFFFF)
        byteNum = int(byteNum)
        return (1 << (8 * min(byteNum, 4))) - 1

    def drv_device_init(self, onoff):
        ret = -1
        try:
            if onoff == 0:
                ret = self.ovApiIf.pyCloseOVDriverSCCB()
                OvApiDrv._inited = False
                self._log(f"drv_device_init: Device closed. ret:{ret}")
                return ret # 成功關閉
            if onoff == 1:
                # 定義重試次數
                max_retries = 2
                for attempt in range(max_retries):
                    if OvApiDrv._inited:
                        self.ovApiIf.pyCloseOVDriverSCCB()
                        time.sleep(0.1)
                        OvApiDrv._inited = False
                    # 執行初始化
                    ret = self.ovApiIf.pyInitOVDriverSCCB()
                    if ret == 1:
                        # RGBRAW
                        self.ovApiIf.pyWriteRegister(0x102, 0x80, 0x01, 0xffffffff)
                        # 16bit per Pixel
                        self.ovApiIf.pyWriteRegister(0x110, 0x80, 0x16, 0xffffffff)
                        OvApiDrv._inited = True
                        self._log(f"drv_device_init: Init success on attempt {attempt + 1}")
                        return ret
                    # 如果不是最後一次嘗試, 則執行清理並等待重試
                    if attempt < max_retries - 1:
                        self.ovApiIf.pyCloseOVDriverSCCB()
                        time.sleep(0.5)
                        self._log(f"drv_device_init: Retry attempt {attempt + 1}... ret::{ret}")
                # 跑完迴圈仍失敗
                raise RuntimeError(f"drv_device_init: SCCB Init failed after {max_retries} attempts, code {ret}")
            raise ValueError(f"onoff value '{onoff}' is not supported. Use 1 (on) or 0 (off).")
        except Exception as e:
            OvApiDrv._inited = False
            self._log(f"Error: drv_device_init({onoff}): {e}")
            return -1

    def drv_sccb_write(self, dev_id, addr, length, data, bit):
        self.set_addr_width(bit, dev_id)
        byteNum = self.set_data_width(bit, dev_id)
        if dev_id == VENUS_ID or dev_id > 0xFF or dev_id == I3C_MCU_ID:
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
            mask = self.get_mask(byteNum)
            ret = self.ovApiIf.pyWriteRegister(dev_id, addr, temp, mask)
        else:
            self.set_data_width(0, dev_id)
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
            datas = (ctypes.c_int * (length * byteNum))()
            for i in range(length):
                for j in range(byteNum):
                    datas[i * byteNum + j] = (temps[i] >> (8 * (byteNum - j - 1))) & 0xFF
            ret = self.ovApiIf.pyWriteRegBurst(dev_id, addr, datas, length * byteNum)
        return ret

    def drv_sccb_read(self, dev_id, addr, length, data, bit):
        self.set_addr_width(bit, dev_id)
        byteNum = self.set_data_width(bit, dev_id)
        if dev_id == VENUS_ID or dev_id > 0xFF or dev_id == I3C_MCU_ID:
            mask = self.get_mask(byteNum)
            shift = 0
            temp = self.ovApiIf.pyReadRegister(dev_id, addr, mask)
            if dev_id == I3C_MCU_ID and length == 1:
                shift = 4 - length
                shift = shift << 3
            try:
                data._obj.value = temp >> shift
            except Exception:
                try:
                    data[0] = temp >> shift
                except Exception:
                    try:
                        data.value = temp >> shift
                    except Exception:
                        data = temp >> shift
            ret = -1 if temp == -9999 else 1
        else:
            self.set_data_width(0, dev_id)
            datas = (ctypes.c_int * (length * byteNum))()
            ret = self.ovApiIf.pyReadRegBurst(dev_id, addr, datas, length * byteNum)
            datasIter = iter(datas)
            temps = [0] * length
            for i in range(length):
                temp = 0
                for j in range(byteNum):
                    temp |= (next(datasIter) & 0xFF) << (8 * (byteNum - j - 1))
                temps[i] = temp
            try:
                data._obj[:] = temps
            except Exception:
                try:
                    data[:] = temps
                except Exception:
                    try:
                        next(i for i in data._objects.values())[:] = temps
                    except Exception:
                        try:
                            data._obj.value = temps[0]
                        except Exception:
                            try:
                                data.value = temps[0]
                            except Exception:
                                data = temps[0]
        return ret

    def drv_get_RAW2Buff(self, buff, RdLength):
        return self.ovApiIf.pyAcquireRawImage(buff, RdLength)

    def drv_change_resolution(self, width, height):
        return self.ovApiIf.pyChangeResolution(width, height)

    def drv_load_db_file(self, fname):
        try:
            ret = self.ovApiIf.pyLoadDBFile(ctypes.c_char_p(fname.encode('utf-8')))
            return ret
        except Exception:
            return 0

    def drv_send_db_file(self, setting_index):
        return self.ovApiIf.pySendDBFile(idx = setting_index)
