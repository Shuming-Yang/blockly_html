# WARNING
# pylint: disable=C0103, C0114, C0116, C0412, W0231, W0401, W0612, W0614
from Utility.Para import *
from Define.Para import *
from DP.MIPIRX import MIPIRX
from DP.IMGMT import IMGMT
from DP.IDC import IDC
from DP.IDP import IDP
from DP.ISP import ISP
from DP.EMBL import EMBL
from DP.RETIME import RETIME
from DP.MIPITX import MIPITX
from DP.RGBIR.RGBIRTOP import RGBIRTOP
from DP.CRYPTO_TOP import CRYPTO_TOP
from Utility.Entity import Entity


class DPTOP(Entity):
    """description of class"""
    def __init__(self,chipcfg):
        self.tbuf=[]
        self.sobj=[]
        dplist =[chipcfg.oax4k_cfg.dp0,chipcfg.oax4k_cfg.dp1,chipcfg.oax4k_cfg.dp2,chipcfg.oax4k_cfg.dp3]
        inlist=[]
        dpen = 0
        for dp in dplist:
            if dp.en:
                if dp.input.portsrc not in inlist:
                    if dp.input.idcen:
                        self.module_gen(MIPIRX,chipcfg,dp.input.portsrc)
                        #self.module_gen(VIRSNR,chipcfg,dp.input.portsrc)
                        inlist.append(dp.input.portsrc)
        if inlist:
            self.module_gen(IMGMT,chipcfg)
            self.module_gen(IDC,chipcfg)
        if chipcfg.oax4k_cfg.rgbir.en:
            self.module_gen(RGBIRTOP,chipcfg)
        if chipcfg.oax4k_cfg.crypto.en:
            self.module_gen(CRYPTO_TOP,chipcfg)
        if inlist:
            self.module_gen(IDP,chipcfg)
        txlist=[]
        pgen0_init_done=0
        pgen1_init_done=0
        outlist =[chipcfg.oax4k_cfg.out0,chipcfg.oax4k_cfg.out1,chipcfg.oax4k_cfg.out2,chipcfg.oax4k_cfg.out3]
        for out in outlist:
            # print(txlist,out.yuv.outport,out.rawmv.outport)
            # if(out.embl.en):
            self.module_gen(EMBL,chipcfg,out.index)
            if out.en:
                # if(out.yuv.en or out.rawmv.en):
                self.module_gen(RETIME,chipcfg,out.index)
                if out.yuv.outport not in txlist:
                    #print()
                    self.module_gen(MIPITX,chipcfg,out.yuv.outport)
                    txlist.append(out.yuv.outport)
                if out.rawmv.outport not in txlist:
                    self.module_gen(MIPITX,chipcfg,out.rawmv.outport)
                    txlist.append(out.rawmv.outport)
        self.module_gen(ISP,chipcfg)

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
#        print("[DPTOP] setbuf len {}".format(len(self.tbuf)))
        return self.tbuf

    def save_all(self):
        for obj in self.sobj:
            tmp =obj.save_all()
            self.tbuf.extend(tmp)
        #pass
        #print(self.tbuf)
        return self.tbuf
