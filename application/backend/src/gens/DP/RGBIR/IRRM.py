# WARNING
# pylint: disable=C0103, C0114, C0115, C0116, W0231, W0401, W0614
from Utility.Reg import REGOBJ
from Utility.Entity import Entity
from Utility.Para import *

from RegTable.Regdefdist import define_dist


class CIP_CFG(object):
    def __init__(self,chipcfg):
        pass

    def config(self):
        pass


class CIP_REG(REGOBJ):
    def __init__(self,cfg,uid=0):
        base =self.get_baseaddr('RGBIR_CIP',define_dist,uid)
        self.R0=cfg.regtable[base+0]
        self.objr=[]


class CIP(Entity):
    """description of class"""
    def __init__(self,chipcfg,uid=0):
        #self.cfg=mrx_cfg()
        self.cfg =CIP_CFG(chipcfg)
        self.reg =CIP_REG(chipcfg,uid)
        self.setbuf=[]

    def start(self):
        self.reg.R0.update(0x12345678)
