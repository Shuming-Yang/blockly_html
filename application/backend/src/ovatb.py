# ovatb.py
"""
[模組] ATB 硬體行為

Author: OVT AE
Date: 2026-01-07
Description:
"""
import ctypes
import time
# import traceback
from shared_utils import global_log
try:
    from fw_bin import FW_BYTES_ATB
except ImportError:
    FW_BYTES_ATB = b''  # 避免找不到檔案時報錯
    print("Warning: fw_bin.py not found.")

class apiOvAtb:
# Internal ---------------------------------------------------------------------------------------------
    def __init__(self, parent):
        # 初始化中繼管理層
        self.TCAL9539_ID = 0xE8
        self.TCAL9539_WIDTH = 0x00
        self.OV195_ID = 0xAA
        self.OV195_WIDTH = 0x10
        self.OAX4K_FW_TCAL9539OUT_B0_ADDR = 0x3010  # Byte value mapping to TI-TCAL9539 Register 0x02
        self.OAX4K_FW_TCAL9539OUT_B1_ADDR = 0x3011  # Byte value mapping to TI-TCAL9539 Register 0x03
        self.OAX4K_FW_TCAL9539DIR_B0_ADDR = 0x3012  # Byte value mapping to TI-TCAL9539 Register 0x06
        self.OAX4K_FW_TCAL9539DIR_B1_ADDR = 0x3013  # Byte value mapping to TI-TCAL9539 Register 0x07
        self.OAX4K_FW_ENFLAG_ADDR = 0x3008  # Refer to OAX4k: enFlag :: ENFLAG_GPIO_ERRPIN (0x10u)         // Sensor error pin bypass
        self.ALLOW_INIT_TASK_GOING = 0x3009 # 1:break, 0:continue
        self.OAX4K_SCCBS_CFG_ADDRESS = 0x8006
        self.OAX4K_FW_RESULT_ADDRESS = 0x4000
        self.TEST_CASE_MAX = 10
        self.DWORD_OF_T_RESULT_HEADER = 6
        self.DWORD_OF_T_TCOVIEW = 3
        self.DWORD_OF_T_ERRLOG = 8
        self.PRE_IDX_OFFSET = (self.DWORD_OF_T_ERRLOG - 1) * 4
        self._venus_api = parent
        self._usb_mgr = parent._usb_mgr
        self.chip_id_binary = 0x48
        self.chip_id_script = 0xFC
        self.bit = 0x10
        self._isBusy = False
        self._oax4k_only = False
        self._connEG195 = True  # Set to enable EG195 workaround as default opt with ATB
        self._resultBurstLength = 128
        self._resultSize = 0x2400
        self._resultArray = (ctypes.c_uint8 * self._resultSize)(*([0] * self._resultSize))
        self._memory_map_addr = {
            'default':0x80200000,
            'fcpSta':0x801C2000,
            'testcases':0x801C8000,
            'Embbed':0x801cB000,
            'setting':0x801B1000,
            'FcpStat':0x801C2000,
            'cmdSta':0x801D3000,
            'testLog':0x801D6000,
            'testLog2':0x801D6000
        }
        self.AD5142_0_ID = 0x44
        self.AD5142_1_ID = 0x46
        self.AD5142_WIDTH = 0x00
        self.endian = 'big'
        self._log("apiOvAtb loaded.")

    def _log(self, message):
        """
        支援極高精度時間戳記 (含微秒) 的偵錯打印
        """
        global_log(tag="OVATB", message=message)

    def _usbI2cMultiRead(self, Devid, Addr, Length, width):
        """to read I2C from USB library to return value
        """
        if not self._venus_api:
            self._log("Error: Venus API not inited")
            return None
        if not self._venus_api._isUsbInited:
            self._log("Error: Venus USB API not inited")
            return None
        if Devid in (0x00, 0xFF):
            self._log(f"Error: Wrong input device id: {Devid}")
            return None
        if self._isBusy:
            self._log("Warning: _usbI2cMultiRead() is busy")
            return None
        self._isBusy = True
        try:
            buffer_size = Length
            data = (ctypes.c_uint * buffer_size)()
            self.__workaround_EG195(0, width)
            # 絕對不要用 ctypes.cast 直接把 data (Array物件) 傳進去 這樣 Driver 裡面的 data[:] = temps 才會成功
            ret = self._usb_mgr.drv_sccb_read(
                Devid,
                Addr,
                buffer_size,
                data,
                width
            )
            self.__workaround_EG195(1, width)
            # 檢查回傳值 (根據 Driver, 1 是成功)
            if ret != 1:
                raise RuntimeError(f"USB READ Failed (ret={ret})")
            data_list = list(data)
            return data_list
        except Exception as e:
            self._log(f"Error: USB READ Error: {e}")
            return None
        finally:
            # 使用 finally 確保無論發生什麼事都會解除忙碌狀態
            self._isBusy = False

    def _usbI2cMultiWrite(self, DevId, Addr, Length, value, width):
        """
        支援單個或多個數據寫入
        value: 可以是單一整數, 也可以是整數列表 [val1, val2, ...]
        """
        if not self._venus_api:
            self._log("Error: Venus API not inited")
            return 0
        if not self._venus_api._isUsbInited:
            self._log("Error: Venus USB API not inited")
            return 0
        if DevId in (0x00, 0xFF):
            self._log(f"Error: Wrong input device id: {hex(DevId)}")
            return 0
        if self._isBusy:
            self._log("Warning: _usbI2cMultiWrite() is busy")
            return 0
        self._isBusy = True
        try:
            # 處理 ctypes 資料結構
            if isinstance(value, (list, bytes, tuple)):
                # 如果是 Python 原生序列, 轉換為 ctypes 陣列
                data_type = ctypes.c_uint32 * len(value)
                data = data_type(*value)
                p_data = ctypes.cast(data, ctypes.POINTER(ctypes.c_uint32))
            elif "Array" in type(value).__name__:
                # 如果已經是 ctypes 陣列 (例如從 _burst_mem 傳進來的)
                # 直接轉換為指標即可
                p_data = ctypes.cast(value, ctypes.POINTER(ctypes.c_uint32))
            else:
                # 單一數值
                data = ctypes.c_uint32(value)
                p_data = ctypes.byref(data)
            self.__workaround_EG195(0, width)
            # 呼叫底層 API
            self._usb_mgr.drv_sccb_write(DevId, Addr, Length, p_data, width)
            self.__workaround_EG195(1, width)
            # 回傳最後寫入的數值或 1 代表成功
            return value[0] if isinstance(value, list) else value
        except Exception as e:
            self._log(f"Error: _usbI2cMultiWrite Error: {e}")
            return 0
        finally:
            self._isBusy = False

    def _usbI2cSingleRead(self, Devid, Addr, width):
        """to read I2C from USB library to return value
        """
        read_list = self._usbI2cMultiRead(Devid, Addr, 1, width)
        if read_list and len(read_list) > 0:
            return read_list[0]
        self._log(f"Error: SingleRead failed at Addr: {hex(Addr)}")
        return None

    def _usbI2cSingleWrite(self, DevId, Addr, value, width):
        """寫入單一數值: 透過呼叫 MultiWrite 達成"""
        self._usbI2cMultiWrite(DevId, Addr, 1, value, width)

    def __workaround_EG195(self, val, width):
        if self._connEG195 and not width & 0xF0:
            # 直接傳遞一個包含數值的 list
            # Driver 的 temps = [data] 或 data[:] = temps 邏輯都能處理它
            self._usb_mgr.drv_sccb_write(
                self.OV195_ID,
                0x1000,
                1,
                [val],
                self.OV195_WIDTH
            )
            time.sleep(0.01)

    def _sccb_write_table(self, table_list):
        for table in table_list:
            w_size = len(table) - 1
            write_data = (ctypes.c_uint32 * 256)()
            if w_size < 256:
                for j in range(w_size):
                    write_data[j] = table[j + 1]
                self._usbI2cMultiWrite(self.chip_id_binary, table[0], w_size, write_data, self.bit)
            else:
                self._log(f'Error: _sccb_write_table length: {w_size} > 255')

    def _burst_mem(self, start_addr, data):
        """--------write memory--------"""
        data_length = len(data)
        max_length = 64
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
                self._usbI2cMultiWrite(self.chip_id_binary, addr, write_length, write_data, self.bit)
            except Exception as e:
                self._log(f"Error: _burst_mem(), _usbI2cMultiWrite({self.chip_id_binary:02X}, {addr:04X}, {write_length}, {self.bit:02X}): {e}")
            time.sleep(0.001)
            current_index += write_length
            addr += write_length  # 位址遞增

    def _mem_map(self, map_addr):
        write_data = (ctypes.c_uint32 * 4)()
        write_data[0] = map_addr & 0xFF
        write_data[1] = (map_addr >> 8) & 0xFF
        write_data[2] = (map_addr >> 16) & 0xFF
        write_data[3] = (map_addr >> 24) & 0xFF
        self._usbI2cMultiWrite(self.chip_id_binary, 0x9644, 4, write_data, self.bit)

    def _updateMemoryAddrMapping(self, item):
        """Re-mapping OAX4k register address
    
        Args:
            address (_type_): _description_
        """
        try:
            if item in self._memory_map_addr:
                self._mem_map(self._memory_map_addr[item])
            else:
                raise RuntimeError(f"{item} not found in self._memory_map_addr")
        except Exception as e:
            self._log(f"Error: _updateMemoryAddrMapping(),{e}")

    def _checkTcal9539Exist(self):
        """Check TI-TCAL9539 exist or not with SCCB bypass mode
        """
        ret = False
        self.set_sccbs_bypass()
        time.sleep(0.1)
        data = self._usbI2cSingleRead(self.TCAL9539_ID, 0x44, self.TCAL9539_WIDTH)
        if data is not None:
            data1 = self._usbI2cSingleRead(self.TCAL9539_ID, 0x43, self.TCAL9539_WIDTH)
        else:
            self.set_sccbs_slave()
            return ret
        self.set_sccbs_slave()
        time.sleep(0.1)
        if data1 and data == 0x00 and data1 == 0xFF:
            ret = True
        return ret

# Interface ---------------------------------------------------------------------------------------------
    def loadMainFirmware(self):
        """ Operate to download firmware to OAX4k
        """
        if self._venus_api._isUsbInited:
            start_time = time.time()
            try:
                magic = self._usbI2cMultiRead(self.chip_id_binary, 0xB8DC, 4, self.bit)
                if magic == 0x5454564F:
                    self._log("FW is ready, skip load FW")
                    return True
                w_arr = [[0xB8DC, 0x00],
                            [0x8050, 0x01],
                            [0x966C, 0xFF, 0xFF, 0x6A, 0x96],
                            [0x966A, 0x07],
                            [0x966A, 0x06],
                            [0x9644, 0x00, 0x00, 0x18, 0x80, 0xFF, 0x7F],
                            [0x8061, 0x00],
                            [0x8061, 0x81],
                            [0x8061, 0x00],
                            [0x966A, 0x07]]
                self._sccb_write_table(w_arr)
                # path = r'D:\GitHub\DevVerifyGUI\OAX4000_general_eagle_v0.bin'
                # with open(path, 'rb') as f:
                #    FW_BYTES_ATB = f.read()
                if FW_BYTES_ATB:
                    self._burst_mem(0, FW_BYTES_ATB)
                else:
                    self._log("Error: FW_BYTES_ATB is empty.")
                bootFW = [[0x8001, 0x09],
                            [0x8005, 0x06],
                            [0x8050, 0x00]]
                self._sccb_write_table(bootFW)
                for _ in range(500):
                    time.sleep(0.01)
                    data = self._usbI2cSingleRead(self.chip_id_binary, 0xB8DC, self.bit)
                    if data and data == 0x5A:
                        return True
            finally:
                end_time = time.time()
                execution_time = end_time - start_time
                self._log(f'load MainFw bin cost: {execution_time} sec')
                self.set_init_task_continue()
        return False

    def set_init_task_continue(self):
        """Activate Test Board to set init task continue"""
        self._usbI2cSingleWrite(self.chip_id_binary, self.ALLOW_INIT_TASK_GOING, 0, self.bit)

    def is_test_running(self):
        state = self._usbI2cSingleRead(self.chip_id_binary, 0x3000, self.bit)
        if state and state == 0x05:
            return True
        return False

    def activate_test(self):
        """Activate Test Board to start test"""
        self._usbI2cSingleWrite(self.chip_id_binary, 0x3000, 0, self.bit)
        return 0

    def abort_test(self):
        """Activate Test Board to stop test"""
        self._usbI2cSingleWrite(self.chip_id_binary, 0x3001, 1, self.bit)
        return 0

    def is_device_atb(self):
        """Detect if ATB board is connected"""
        try:
            # 檢測擴充晶片是否存在
            is9539Exist = self._checkTcal9539Exist()
            # 讀取 Chip ID
            # 若回傳 None 則 data 變為 0
            data = self._usbI2cSingleRead(self.chip_id_binary, 0x80FD, self.bit) or 0
            if data and data == 0x40:
                if is9539Exist:
                    self._oax4k_only = False
                else:
                    self._oax4k_only = True
                return True
            raise RuntimeError(f"Wrong ID: expected 0x40, got {hex(data)}")
        except Exception as e:
            self._log(f"Error: is_device_atb(): {e}")
            return False

    def readTestResult(self):
        """Read OAX4k result data."""
        try:
            total_reads = self._resultSize // self._resultBurstLength
            logUnusedIdx = 0
            exact_byte_size = self._resultSize * 4
            skip_index_threshold = total_reads
            for read_index in range(total_reads):
                address = self.OAX4K_FW_RESULT_ADDRESS + (read_index * self._resultBurstLength)
                if read_index < skip_index_threshold or read_index == total_reads - 1:
                    # 這裡回傳的是 List[int]
                    read_data_list = self._usbI2cMultiRead(self.chip_id_binary, address, self._resultBurstLength, 0x10)
                    if read_data_list is None:
                        self._log(f"Error: Failed to read at index {read_index}")
                        return None
                else:
                    read_data_list = [0] * self._resultBurstLength
                # --- 填入 Result Array ---
                for i in range(self._resultBurstLength):
                    if i < len(read_data_list):
                        uint32_value = read_data_list[i]
                        start_index = (read_index * self._resultBurstLength) + i
                        self._resultArray[start_index] = uint32_value & 0xFF  # 確保只取最後 8 bits
                if read_index == 0:
                    # read_data_list 是 [int, int...], 我們需要取其中的一段
                    # 假設讀回來的 int 其實只存了 byte (0-255), 我們需要轉成 bytes 才能給 int.from_bytes 用
                    # 處理 rsltCfg
                    cfg_slice = read_data_list[8:12]
                    # 安全轉換: 確保每個數值都在 0-255 之間再轉 bytes
                    cfg_bytes = bytes([x & 0xFF for x in cfg_slice])
                    rsltCfg = int.from_bytes(cfg_bytes, byteorder='big')
                    if rsltCfg & 0xFFFFF == 0:
                        self._log("Dumping in Fast Speed Mode")
                        # 處理 logUnusedIdx
                        idx_slice = read_data_list[16:20]
                        idx_bytes = bytes([x & 0xFF for x in idx_slice])
                        logUnusedIdx = int.from_bytes(idx_bytes, byteorder='big')
                        exact_byte_size = 4 * (self.DWORD_OF_T_RESULT_HEADER +
                                               self.DWORD_OF_T_TCOVIEW * self.TEST_CASE_MAX +
                                               self.DWORD_OF_T_ERRLOG * logUnusedIdx)
                        skip_index_threshold = (exact_byte_size // self._resultBurstLength) + 1
            # 處理未使用的索引標記
            if skip_index_threshold < total_reads:
                preIdx = logUnusedIdx + 1
                # 注意範圍檢查, 避免超出 array 範圍
                start_fill = exact_byte_size + self.PRE_IDX_OFFSET
                end_fill = len(self._resultArray) - self._resultBurstLength
                # 確保 start_fill 不會超過 array 大小
                if start_fill < len(self._resultArray):
                    for i in range(start_fill, end_fill, self.DWORD_OF_T_ERRLOG * 4):
                        # 這裡將 int 轉為 bytes 直接填入 ctypes array 是合法的 (因為是 slice assignment)
                        # 但 ctypes array 存放的是 c_uint8, 所以要確保填入方式正確
                        # resultArray 是 c_uint8 陣列, 這裡直接用 bytes assign 可能會有行為差異, 使用拆解填入
                        b_val = preIdx.to_bytes(4, byteorder='big')
                        for k in range(4):
                            if i + k < len(self._resultArray):
                                self._resultArray[i + k] = b_val[k]
                        preIdx += 1
            return self._resultArray
        except Exception as e:
            self._log(f"Error: readTestResult: {e}")
            # self._log(traceback.format_exc())  # 印出詳細錯誤以便除錯
            return None
        finally:
            pass

    def write_testcases(self, data=None):
        try:
            self._updateMemoryAddrMapping('testcases')
            self._burst_mem(0, data)
            self._updateMemoryAddrMapping('default')
            return 0
        except Exception as e:
            self._log(f"Error: write_testcases: {e}")
            return -1

    def write_txtgroup(self, data=None):
        try:
            self._updateMemoryAddrMapping('setting')
            self._burst_mem(0, data)
            self._updateMemoryAddrMapping('default')
            return 0
        except Exception as e:
            self._log(f"Error: write_testcases: {e}")
            return -1

    def set_sccbs_slave(self):
        """Set OAX4k SCCBS to be slave mode
        """
        self._usbI2cSingleWrite(self.chip_id_binary, self.OAX4K_SCCBS_CFG_ADDRESS, 0x03, self.bit)

    def set_sccbs_bypass(self):
        """Set OAX4k SCCBS to be bypass mode
        """
        self._usbI2cSingleWrite(self.chip_id_binary, self.OAX4K_SCCBS_CFG_ADDRESS, 0x10, self.bit)

    def init_tcal9539(self):
        try:
            if self._checkTcal9539Exist():
                self.set_sccbs_bypass()
                # Initialize TI-TCAL9539
                self._usbI2cSingleWrite(self.TCAL9539_ID, 0x02, 0x00, self.TCAL9539_WIDTH)
                self._usbI2cSingleWrite(self.TCAL9539_ID, 0x03, 0x17, self.TCAL9539_WIDTH)
                self._usbI2cSingleWrite(self.TCAL9539_ID, 0x04, 0x00, self.TCAL9539_WIDTH)
                self._usbI2cSingleWrite(self.TCAL9539_ID, 0x05, 0x00, self.TCAL9539_WIDTH)
                self._usbI2cSingleWrite(self.TCAL9539_ID, 0x06, 0x00, self.TCAL9539_WIDTH)
                self._usbI2cSingleWrite(self.TCAL9539_ID, 0x07, 0x00, self.TCAL9539_WIDTH)
                self._usbI2cSingleWrite(self.chip_id_binary, self.OAX4K_FW_TCAL9539OUT_B0_ADDR, 0x00, self.bit)  # Byte value mapping to TI-TCAL9539 Register 0x02
                self._usbI2cSingleWrite(self.chip_id_binary, self.OAX4K_FW_TCAL9539OUT_B1_ADDR, 0x17, self.bit)  # Byte value mapping to TI-TCAL9539 Register 0x03
                self._usbI2cSingleWrite(self.chip_id_binary, self.OAX4K_FW_TCAL9539DIR_B0_ADDR, 0x00, self.bit)  # Byte value mapping to TI-TCAL9539 Register 0x06
                self._usbI2cSingleWrite(self.chip_id_binary, self.OAX4K_FW_TCAL9539DIR_B1_ADDR, 0x00, self.bit)  # Byte value mapping to TI-TCAL9539 Register 0x07
                self.set_sccbs_slave()
                self.set_sensor_avdd(2.8)
                self.set_sensor_dovdd(1.8)
                self.set_sensor_dvdd(1.1)
                return 0
            self._log("TI-CAL9539 not found")
            return 1
        except Exception as e:
            self._log(f"Error: init_tcal9539(): {e}")
            return -1
        finally:
            pass

    def init_atb_oax4kenflag(self):
        self.set_sensor_error_bypass(0x00)

    def set_sensor_error_bypass(self, val):
        # self._log(f"set_sensor_error_bypass(): {val:02X}")
        self._usbI2cSingleWrite(self.chip_id_binary, self.OAX4K_FW_ENFLAG_ADDR, val, self.bit)

    def set_i2c_route(self, val):
        """Update I2C configurated value to ATB"""
        try:
            if not self._oax4k_only:
                data = self._usbI2cSingleRead(self.chip_id_binary, self.OAX4K_FW_TCAL9539OUT_B0_ADDR, self.bit)
                if data is not None:
                    if val == 1:
                        data &= 0xFFFFFFF3
                    elif val == 0:
                        data |= 0x00000008
                    else:
                        raise RuntimeError(f"val not support {val}")
                else:
                    raise RuntimeError("data is None")
                self.set_sccbs_bypass()
                self._usbI2cSingleWrite(self.chip_id_binary, self.OAX4K_FW_TCAL9539OUT_B0_ADDR, data, self.bit)
                self._usbI2cSingleWrite(self.TCAL9539_ID, 0x02, data, self.TCAL9539_WIDTH)
                self.set_sccbs_slave()
            return 0
        except Exception as e:
            self._log(f"Error: set_i2c_route(): {e}")
            return -1
        finally:
            pass

    def set_mipi_route(self, val):
        """Update MIPI configurated value to ATB"""
        try:
            if not self._oax4k_only:
                data = self._usbI2cSingleRead(self.chip_id_binary, self.OAX4K_FW_TCAL9539OUT_B0_ADDR, self.bit)
                if data is not None:
                    if val == 1:
                        data &= 0xFFFFFFFC
                    elif val == 0:
                        data |= 0x00000003
                    else:
                        raise RuntimeError(f"val not support {val}")
                else:
                    raise RuntimeError("data is None")
                self.set_sccbs_bypass()
                self._usbI2cSingleWrite(self.chip_id_binary, self.OAX4K_FW_TCAL9539OUT_B0_ADDR, data, self.bit)
                self._usbI2cSingleWrite(self.TCAL9539_ID, 0x02, data, self.TCAL9539_WIDTH)
                self.set_sccbs_slave()
            return 0
        except Exception as e:
            self._log(f"Error: set_mipi_route(): {e}")
            return -1
        finally:
            pass

    def set_mclk_source(self, val):
        """Update MCLK configurated value to ATB"""
        try:
            if not self._oax4k_only:
                data = self._usbI2cSingleRead(self.chip_id_binary, self.OAX4K_FW_TCAL9539OUT_B0_ADDR, self.bit)
                if data is not None:
                    if val == 1:
                        data &= 0xFFFFFFEF
                    elif val == 0:
                        data |= 0x00000010
                    else:
                        raise RuntimeError(f"val not support {val}")
                else:
                    raise RuntimeError("data is None")
                self.set_sccbs_bypass()
                self._usbI2cSingleWrite(self.chip_id_binary, self.OAX4K_FW_TCAL9539OUT_B0_ADDR, data, self.bit)
                self._usbI2cSingleWrite(self.TCAL9539_ID, 0x02, data, self.TCAL9539_WIDTH)
                self.set_sccbs_slave()
            return 0
        except Exception as e:
            self._log(f"Error: set_mclk_source(): {e}")
            return -1
        finally:
            pass

    def set_gpio_source(self, val):
        """Update GPIO configurated value to ATB"""
        try:
            if not self._oax4k_only:
                data = self._usbI2cSingleRead(self.chip_id_binary, self.OAX4K_FW_TCAL9539OUT_B0_ADDR, self.bit)
                if data is not None:
                    if val == 1:
                        data &= 0xFFFFFFDF
                    elif val == 0:
                        data |= 0x00000020
                    else:
                        raise RuntimeError(f"val not support {val}")
                else:
                    raise RuntimeError("data is None")
                self.set_sccbs_bypass()
                self._usbI2cSingleWrite(self.chip_id_binary, self.OAX4K_FW_TCAL9539OUT_B0_ADDR, data, self.bit)
                self._usbI2cSingleWrite(self.TCAL9539_ID, 0x02, data, self.TCAL9539_WIDTH)
                self.set_sccbs_slave()
            return 0
        except Exception as e:
            self._log(f"Error: set_gpio_source(): {e}")
            return -1
        finally:
            pass

    def set_fsin_dir(self, val):
        """Update FSIN configurated value to ATB"""
        try:
            if not self._oax4k_only:
                data = self._usbI2cSingleRead(self.chip_id_binary, self.OAX4K_FW_TCAL9539OUT_B0_ADDR, self.bit)
                if data is not None:
                    if val == 1:
                        data &= 0xFFFFFFBF
                    elif val == 0:
                        data |= 0x00000040
                    else:
                        raise RuntimeError(f"val not support {val}")
                else:
                    raise RuntimeError("data is None")
                self.set_sccbs_bypass()
                self._usbI2cSingleWrite(self.chip_id_binary, self.OAX4K_FW_TCAL9539OUT_B0_ADDR, data, self.bit)
                self._usbI2cSingleWrite(self.TCAL9539_ID, 0x02, data, self.TCAL9539_WIDTH)
                self.set_sccbs_slave()
            return 0
        except Exception as e:
            self._log(f"Error: set_fsin_dir(): {e}")
            return -1
        finally:
            pass

    def set_strobe_route(self, val):
        """Update STROBE configurated value to ATB"""
        try:
            if not self._oax4k_only:
                data = self._usbI2cSingleRead(self.chip_id_binary, self.OAX4K_FW_TCAL9539OUT_B0_ADDR, self.bit)
                if data is not None:
                    if val == 1:
                        data &= 0xFFFFFF7F
                    elif val == 0:
                        data |= 0x00000080
                    else:
                        raise RuntimeError(f"val not support {val}")
                else:
                    raise RuntimeError("data is None")
                self.set_sccbs_bypass()
                self._usbI2cSingleWrite(self.chip_id_binary, self.OAX4K_FW_TCAL9539OUT_B0_ADDR, data, self.bit)
                self._usbI2cSingleWrite(self.TCAL9539_ID, 0x02, data, self.TCAL9539_WIDTH)
                self.set_sccbs_slave()
            return 0
        except Exception as e:
            self._log(f"Error: set_strobe_route(): {e}")
            return -1
        finally:
            pass

    def set_sensor_dovdd(self, val):
        """Update SENSOR_DOVDD configurated value to ATB"""
        try:
            num = float(val) * float(100)
            step = int((390 - num) * 8 / 10)
            # self._log(f"set_sensor_dovdd(): {step:02X}")
            self._usbI2cSingleWrite(self.AD5142_0_ID, 16, step, self.AD5142_WIDTH)
            return 0
        except Exception as e:
            self._log(f"Error: set_sensor_dovdd(): {e}")
            return -1
        finally:
            pass

    def set_sensor_avdd(self, val):
        """Update SENSOR_AVDD configurated value to ATB"""
        try:
            num = float(val) * float(100)
            step = int((320 - num) * 11 / 10)
            # self._log(f"set_sensor_avdd(): {step:02X}")
            self._usbI2cSingleWrite(self.AD5142_1_ID, 16 + 1, step, self.AD5142_WIDTH)
            return 0
        except Exception as e:
            self._log(f"Error: set_sensor_avdd(): {e}")
            return -1
        finally:
            pass

    def set_sensor_dvdd(self, val):
        """Update SENSOR_DVDD configurated value to ATB"""
        try:
            num = float(val) * float(100)
            step = int((160 - num) * 32 / 10)
            step = min(step, 255)
            # self._log(f"set_sensor_dvdd(): {step:02X}")
            self._usbI2cSingleWrite(self.AD5142_0_ID, 16 + 1, step, self.AD5142_WIDTH)
            return 0
        except Exception as e:
            self._log(f"Error: set_sensor_dvdd(): {e}")
            return -1
        finally:
            pass

    def send_script_content(self, content):
        lines = content.splitlines()
        for line in lines:
            clean_line = line.strip()
            clean_line = clean_line.split(';')[0].strip()
            if not clean_line:
                continue
            # self._log(f"處理中: {clean_line}")
            # self._usb_mgr.ovApiIf.pyWriteRegister(0x102, 0xAF1, dev_id, 0xFFFFFFFF)
            # 檢查是否以 SL 或 DELAY 開頭
            is_command = clean_line.upper().startswith(('SL', 'DELAY'))
            # is_hex_data = self.is_hex(clean_line)
            # 過濾邏輯: 如果是指令 OR 是純16進位數據
            if is_command:
                value = clean_line.split()[1]
                dly_time = int(value, 16) / 1000
                time.sleep(dly_time)
            else:
                try:
                    dev, addr, data, *_ = clean_line.split()
                except Exception as e:
                    self._log(f"Error: write_script(): {clean_line}, {e}")
                mask = 0xFFFFFFFF
                if dev == '40':
                    mask = 0xFF
                elif dev == '64':
                    mask = 0xFF
                else:
                    mask = 0xFFFFFFFF
                self._usb_mgr.ovApiIf.pyWriteRegister(int(dev, 16), int(addr, 16), int(data, 16), mask)
