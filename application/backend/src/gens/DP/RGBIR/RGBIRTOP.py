# WARNING
# pylint: disable=C0103, C0114, C0116, W0231, W0401, W0612, W0613, W0614
from Utility.Para import *
from Utility.Entity import Entity
from DP.RGBIR.CIP import CIP
from DP.RGBIR.TOPCTRL import TOPCTRL


class RGBIRTOP(Entity):
    """description of class"""
    def __init__(self,chipcfg,uid=0):
        self.tbuf=[]
        self.sobj=[]
        dplist =[chipcfg.oax4k_cfg.dp0,chipcfg.oax4k_cfg.dp1,chipcfg.oax4k_cfg.dp2,chipcfg.oax4k_cfg.dp3]
        rgbir =chipcfg.oax4k_cfg.rgbir
        # chnlist =[rgbir.chn0,rgbir.chn1,rgbir.chn2,rgbir.chn3]
        chnlist =rgbir.chnlist
        for chn in chnlist:
            if chn.en:
                self.module_gen(CIP,chipcfg,chn.index)
                self.module_gen(TOPCTRL,chipcfg,chn.index)

    def module_gen(self,cls,chipcfg,uid=0):
        mdl =cls(chipcfg,uid)
        self.sobj.append(mdl)
        return mdl

    def start(self):
        for obj in self.sobj:
            obj.start()

    def save(self):
        self.tbuf = []
        for obj in self.sobj:
            tmp =obj.save()
            self.tbuf.extend(tmp)
        #pass
        #print(self.tbuf)
        return self.tbuf

    def save_all(self):
        for obj in self.sobj:
            tmp =obj.save_all()
            self.tbuf.extend(tmp)
        #pass
        #print(self.tbuf)
        return self.tbuf
