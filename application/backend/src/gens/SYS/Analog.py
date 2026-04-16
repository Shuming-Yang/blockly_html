"""
This GENS mode code which be ported from GENS source code.
@@OAX4K dist define

Author: OVT AE
Date: 2024-11-05
"""
# WARNING
# pylint: disable=C0103, C0115, C0116, C0412, R0205, W0231, W0401, W0611, W0612, W0614, W0622
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

class RX_DESKEW_CFG(object):
    def __init__(self):
        self.byp = 1
        self.datdly = 0
        self.es_sel = 3


class RXPHY_CFG(object):
    def __init__(self):
        self.enlane0 = 1
        self.enlane1 = 1
        self.enlane2 = 1
        self.enlane3 = 1
        self.phymode = 0
        self.rsel = 1
        self.ibsel = 0x0f
        self.rst = 0
        self.dsd0 = RX_DESKEW_CFG()
        self.dsd1 = RX_DESKEW_CFG()
        self.dsd2 = RX_DESKEW_CFG()
        self.dsd3 = RX_DESKEW_CFG()
        self.eqen = 0  # eq ,<1.5G don't need enable


class VLDSHIFT_CFG(object):
    def __init__(self):
        self.shift_en = 1
        self.shift_num = 6


class FPGAPHY_CFG(object):
    def __init__(self):
        self.rxvld0 = VLDSHIFT_CFG()
        self.rxvld1 = VLDSHIFT_CFG()
        self.rxvld2 = VLDSHIFT_CFG()
        self.rxvld3 = VLDSHIFT_CFG()
        self.vuvld = VLDSHIFT_CFG()


class TXPHY_CFG(object):
    def __init__(self):
        self.dislane0 = 0
        self.dislane1 = 0
        self.dislane2 = 0
        self.dislane3 = 0
        self.phymode = 0
        self.pgm_vcm = 2  # according to 2.5G mipi electrical test ,decrease vcm
        self.rst = 0


class TPM_CFG(object):
    def __init__(self):
        self.en = 0


class VM_CFG(object):
    def __init__(self):
        self.en = 0


class ANALOG_CFG(object):
    def __init__(self,_chipcfg):
        self.rx0 = RXPHY_CFG()
        self.rx2 = RXPHY_CFG()
        self.tx0 = TXPHY_CFG()
        self.tx2 = TXPHY_CFG()
        self.fpga = FPGAPHY_CFG()
        self.tpm = TPM_CFG()
        self.vm = VM_CFG()

    def config(self):
        pass

class ANALOG_REG(REGOBJ):
    def __init__(self, cfg, _uid=0):
        self.base = self.get_baseaddr('ANALOG', define_dist, 0)
        # print(" SC {:x} {:x}".format(uid, base))
        self.regtable = cfg.regtable
        self.objr = []


class Analog(Entity):
    """description of class"""
    def __init__(self,chipcfg):
        self.cfg = ANALOG_CFG(chipcfg)
        self.reg = ANALOG_REG(chipcfg)
        self.setbuf= []
        self.analog_init(chipcfg)
        self.topctrl = chipcfg.oax4k_cfg.topctrl

    def analog_init(self,chipcfg):
        in0 = chipcfg.oax4k_cfg.in0
        in1 = chipcfg.oax4k_cfg.in1
        in2 = chipcfg.oax4k_cfg.in2
        in3 = chipcfg.oax4k_cfg.in3
        topctrl = chipcfg.oax4k_cfg.topctrl

        inlist = [in0, in1, in2, in3]
        out0 = chipcfg.oax4k_cfg.out0
        out2 = chipcfg.oax4k_cfg.out2
        if in0.en:
            self.cfg.rx0.phymode = 1 if in0.lane_num == 4 else 0
            self.cfg.rx0.enlane0,self.cfg.rx0.enlane1 = (1, 1)
            self.cfg.rx0.enlane2,self.cfg.rx0.enlane3 = (1, 1) if in0.lane_num == 4 or in1.en else (0, 0)
        if in2.en:
            # self.cfg.rx2.phymode = 1
            self.cfg.rx2.phymode = 1 if in2.lane_num == 4 else 0
            self.cfg.rx2.enlane0,self.cfg.rx2.enlane1 = (1, 1)
            self.cfg.rx2.enlane2,self.cfg.rx2.enlane3 = (1, 1) if in2.lane_num == 4 or in3.en else (0, 0)
        if out0.mtx.csi.lane == 4 and out0.en:
            self.cfg.tx0.phymode = 1
        if out2.mtx.csi.lane == 4 and out2.en:
            self.cfg.tx2.phymode = 1
        self.cfg.tpm.en = chipcfg.oax4k_cfg.sys.ana.tpmen
        self.cfg.vm.en = chipcfg.oax4k_cfg.sys.ana.vmen

        ana_phys = [self.cfg.rx0, self.cfg.rx2]
        for id, inx in enumerate(inlist):
            ana_phys[id//2].ibsel = 0x0c
            ana_phys[id//2].rsel = 0
            if inx.deskew_en:
                ana_phys[id//2].eqen = 1  # tbd, default as 0,when trace is long ,this should be enable
                if id % 2:
                    ana_phys[id//2].dsd2.byp = 0
                    ana_phys[id//2].dsd3.byp = 0
                else:
                    ana_phys[id//2].dsd0.byp = 0
                    ana_phys[id//2].dsd1.byp = 0

    def start(self):
        self.chip_start()
        if self.topctrl.chip_type < 2:
            self.fpga_start()

    def fpga_start(self):
        if self.topctrl.sim_copy_snr:
            self.reg.writereg8(0x8020806e, 0x00, newreg=1)
            self.reg.writereg8(0x80208072, 0x10, newreg=1)
            self.reg.writereg8(0x80208076, 0x40, newreg=1)
            self.reg.writereg8(0x8020807a, 0x60, newreg=1)
        else:
            fpga = self.cfg.fpga
            self.reg.writereg8(0x2c, fpga.rxvld0.shift_en)
            self.reg.writereg8(0x2d, fpga.rxvld0.shift_num)
            self.reg.writereg8(0x30, fpga.rxvld1.shift_en)
            self.reg.writereg8(0x31, fpga.rxvld1.shift_num)
            self.reg.writereg8(0x34, fpga.rxvld2.shift_en)
            self.reg.writereg8(0x35, fpga.rxvld2.shift_num)
            self.reg.writereg8(0x38, fpga.rxvld3.shift_en)
            self.reg.writereg8(0x39, fpga.rxvld3.shift_num)

    def chip_start(self):
        rx0 = self.cfg.rx0
        rx2 = self.cfg.rx2
        r20 = rx0.enlane0 | (rx0.enlane1 << 1) | (rx0.enlane2 << 2)| (rx0.enlane3 << 3) |\
            (rx2.enlane0 << 4) | (rx2.enlane1 << 5) | (rx2.enlane2 << 6)| (rx2.enlane3 << 7)

        tx0 = self.cfg.tx0
        tx2 = self.cfg.tx2
        r56 = tx0.dislane0 | (tx0.dislane1 << 1) | (tx0.dislane2 << 2) | (tx0.dislane3 << 3) | BIT4 | (tx0.phymode << 5)
        r5a = tx2.dislane0 | (tx2.dislane1 << 1) | (tx2.dislane2 << 2) | (tx2.dislane3 << 3) | BIT4 | (tx2.phymode << 5)
        # r0val = self.reg.readreg8(0)
        self.reg.writereg8(0x20, r20)
        self.reg.writereg8(0x56, r56)
        self.reg.writereg8(0x5a, r5a)
        # self.reg.writereg8(0x01, 0, save_force=1)
        # self.reg.writereg8(0x02, 0x3f, save_force=1)  # phy reset
        # self.reg.writereg8(SYS_DELAY_US_REG, 10, save_force=1)
        # self.reg.writereg8(0x00, 0x0f)
        # self.reg.writereg8(0x30, 0x02)  # for uv440 fpga phy
        r3d = self.reg.readreg8(0x3d)
        r3dn = (rx0.dsd0.byp << 0) | (rx0.dsd1.byp << 1)| (rx0.dsd2.byp << 2)| (rx0.dsd3.byp << 3)
        r41 = self.reg.readreg8(0x41)
        r41n = (rx2.dsd0.byp << 0) | (rx2.dsd1.byp << 1)| (rx2.dsd2.byp << 2) | (rx2.dsd3.byp << 3)
        # self.reg.writereg8(0x3d, 0x0f | r3d )
        # self.reg.writereg8(0x41, 0x0f | r41 )
        self.reg.writereg8(0x3d, r3dn, mask=0xf0 )
        self.reg.writereg8(0x41, r41n, mask=0xf0 )
        #self.reg.writereg32(0, 0x0400ffff)
        r5 =  (self.cfg.tpm.en << 2) | (self.cfg.tpm.en << 3) | (self.cfg.vm.en << 0) | (self.cfg.vm.en << 1)
        self.reg.writereg8(0x05, r5, mask=0xf0)

        r23 = 1
        r24 = (rx0.eqen << 6) | (rx0.rsel << 4) | rx0.ibsel
        self.reg.writereg8(0x23, r23)
        self.reg.writereg8(0x24, r24, mask=0xa0)

        r28 =(rx2.eqen << 6) | (rx2.rsel << 4) | rx2.ibsel
        self.reg.writereg8(0x28, r28, mask=0xa0)
        self.reg.writereg8(0x34, rx0.dsd0.es_sel << 6, mask=0x3f)
        self.reg.writereg8(0x35, rx0.dsd1.es_sel << 6, mask=0x3f)
        self.reg.writereg8(0x36, rx0.dsd2.es_sel << 6, mask=0x3f)
        self.reg.writereg8(0x37, rx0.dsd3.es_sel << 6, mask=0x3f)
        self.reg.writereg8(0x38, rx2.dsd0.es_sel << 6, mask=0x3f)
        self.reg.writereg8(0x39, rx2.dsd1.es_sel << 6, mask=0x3f)
        self.reg.writereg8(0x3a, rx2.dsd2.es_sel << 6, mask=0x3f)
        self.reg.writereg8(0x3b, rx2.dsd3.es_sel << 6, mask=0x3f)
        self.reg.writereg8(0x51, tx0.pgm_vcm << 4, mask=0x8f)
        self.reg.writereg8(0x52, tx2.pgm_vcm << 4, mask=0x8f)
        self.reg.writereg8(0, rx0.phymode | (rx2.phymode << 1) | (tx0.phymode << 2) | (tx2.phymode << 3))  # releae pwdn mipir and set lane mode
        self.reg.writereg8(0x01, 0x00, save_force=1)
        self.reg.writereg8(0x02, 0xc0, save_force=1)  # phy release
        self.reg.writereg8(0x5c, 3)  # for vcm issue
        self.reg.writereg8(0x60, 3)
