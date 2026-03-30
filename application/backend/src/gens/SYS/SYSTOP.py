"""
This GENS mode code which be ported from GENS source code.
@@OAX4K dist define

Author: OVT AE
Date: 2024-11-05
"""
# WARNING
# pylint: disable=C0103, C0116, W0231, W0401, W0611, W0614
from Utility.Reg import REG8
from Utility.Reg import REG16
from Utility.Reg import REG32
from Utility.Para import *
from Utility.Entity import Entity
from SYS.CLK import CLOCK
from SYS.PLL import PLL
from SYS.PAD import PAD
from SYS.Analog import Analog
from SYS.TPM import TPM


class SYSTOP(Entity):
    """description of class"""
    def __init__(self, chipcfg):
        self.tbuf = []
        self.sobj = []
        if chipcfg.oax4k_cfg.topctrl.chip_type >= 2:  # asic setting
            self.pll = self.module_gen(PLL, chipcfg)
        self.clk = self.module_gen(CLOCK, chipcfg)
        self.pad = self.module_gen(PAD, chipcfg)
        self.tpm = self.module_gen(TPM, chipcfg)
        self.analog = self.module_gen(Analog, chipcfg)

    def module_gen(self, cls, chipcfg):
        mdl = cls(chipcfg)
        self.sobj.append(mdl)
        return mdl

    def start(self):
        for obj in self.sobj:
            obj.start()

    def save(self):
        self.tbuf = []
        for obj in self.sobj:
            tmp = obj.save()
            self.tbuf.extend(tmp)
        return self.tbuf

    def save_all(self):
        for obj in self.sobj:
            tmp = obj.save_all()
            self.tbuf.extend(tmp)
        return self.tbuf
