"""
This GENS mode code which be ported from GENS source code.
@@OAX4K dist define

Author: OVT AE
Date: 2024-11-04
"""
# WARNING
# pylint: disable=C0103, C0116, W0231, W0401, W0611, W0614
from Utility.Reg import REG8
from Utility.Reg import REG16
from Utility.Reg import REG32
from Utility.Para import *
from Utility.Entity import Entity
from STRM.CTRL import CTRL


class STRMTOP(Entity):

    """description of class"""
    def __init__(self, chipcfg):
        self.tbuf = []
        self.sobj = []
        self.module_gen(CTRL,chipcfg)
        # self.cfg=mrx_cfg()

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
