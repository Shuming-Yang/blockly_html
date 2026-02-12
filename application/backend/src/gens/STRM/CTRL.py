"""
This GENS mode code which be ported from GENS source code.
@@OAX4K dist define

Author: OVT AE
Date: 2024-11-04
"""
# WARNING
# pylint: disable=C0103, C0115, C0116, C0412, W0201, R0205, W0231, W0401, W0611, W0614
from Utility.Reg import REG8
from Utility.Reg import REG16
from Utility.Reg import REG32
from Utility.Entity import Entity
from Utility.Para import *
from Define.Struct import SYSTEM_PLL_CFG
from Utility.Others import get_class_var
from Utility.Reg import REGOBJ
from RegTable.Regdefdist import *
from Define.Para import *


class CTRL_CFG(object):

    def __init__(self,_chipcfg):
        self.strm_en = 0
        self.cb0_en = 0
        self.cb1_en = 0
        self.cb2_en = 0
        self.cb3_en = 0
        self.pg0_en = 0
        self.pg1_en = 0
        self.dbg_en = 0
        self.dp_rst_release = 0
        self.chiptype = 0
        self.fsin_outen = 0

    def config(self):
        pass


class CTRL_REG(REGOBJ):
    def __init__(self,cfg,_uid=0):
        self.base = self.get_baseaddr('SYSTEM_CTRL', define_dist, 0)
        #print(" SC {:x} {:x}".format(uid,base))
        self.regtable = cfg.regtable
        self.objr = []


class CTRL(Entity):

    """description of class"""
    def __init__(self,chipcfg):
        self.cfg = CTRL_CFG(chipcfg)
        self.reg = CTRL_REG(chipcfg)
        self.setbuf = []
        self.strm_init(chipcfg)
        #dp0 =chipcfg.chip.dp0

    def _dp_rst_release(self,chipcfg):
        pass

    def strm_init(self,chipcfg):
        #dp0=chipcfg.chi
        # print("stream control test")
        self.cfg.chiptype =chipcfg.oax4k_cfg.topctrl.chip_type
        self.cfg.strm_en = chipcfg.oax4k_cfg.topctrl.strm_default
        self.cfg.dbg_en = chipcfg.oax4k_cfg.topctrl.debug_en
        self.cfg.dbg_sel = chipcfg.oax4k_cfg.topctrl.debug_sel
        self.cfg.pg0_en = chipcfg.oax4k_cfg.pg0.en
        self.cfg.pg1_en = chipcfg.oax4k_cfg.pg1.en

        self.cfg.fsin_outen = chipcfg.oax4k_cfg.out0.fsync.out_fsin |\
                              chipcfg.oax4k_cfg.out1.fsync.out_fsin |\
                              chipcfg.oax4k_cfg.out2.fsync.out_fsin |\
                              chipcfg.oax4k_cfg.out3.fsync.out_fsin

    def start(self):
        if self.cfg.strm_en:
            if self.cfg.pg0_en:
                defval = self.reg.readreg8(PGEN0_BASE_ADDR) | BIT0
                self.reg.writereg8(PGEN0_BASE_ADDR, defval, newreg=1)
            if self.cfg.pg1_en:
                defval = self.reg.readreg8(PGEN1_BASE_ADDR) | BIT0
                self.reg.writereg8(PGEN1_BASE_ADDR, defval, newreg=1)

        if self.cfg.dp_rst_release:
            self.reg.writereg32(0x80208054, 0xffffffff, newreg=1, save_force=1)
            self.reg.writereg32(0x80208058, 0xffffffff, newreg=1, save_force=1)  # don't reset isp asil and isp
            # self.reg.writereg32(0x80208058, 0xf3ffffff, newreg=1, save_force=1)  # don't reset isp asil and isp
            self.reg.writereg32(0x80208054, 0, newreg=1, save_force=1)
            self.reg.writereg32(0x80208058, 0, newreg=1, save_force=1)
