"""
This GENS mode code which be ported from GENS source code.
@@OAX4K dist define

Author: OVT AE
Date: 2024-11-05
"""
# WARNING
# pylint: disable=C0103, C0115, C0412, W0231, W0401, W0611, W0614
from Utility.Entity import Entity
from Utility.Para import *
from Define.Struct import SYSTEM_PLL_CFG
from Utility.Others import get_class_var
from Utility.Reg import REGOBJ
from RegTable.Regdefdist import *
from Define.Para import *


class TPM_REG(REGOBJ):
    def __init__(self, cfg, _uid=0):
        self.base = self.get_baseaddr('TPM', define_dist, 0)
        #print(" SC {:x} {:x}".format(_uid,base))
        self.regtable = cfg.regtable
        self.objr = []


class TPM(Entity):
    """description of class"""
    def __init__(self, chipcfg):
        self.reg = TPM_REG(chipcfg)
        self.setbuf = []

    def start(self):
        self.reg.writereg8(0x14, 0x7f)
