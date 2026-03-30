"""
This GENS mode code which be ported from GENS source code.
@@OAX4K dist define

Author: OVT AE
Date: 2024-11-04
"""
# WARNING
# pylint: disable=C0103, C0116, C0200, C0206, C0201, C0412, W0401, W0611, W0614
import os
from Utility.Reg import REG8
from Utility.Reg import REG16
from Utility.Reg import REG32
from Utility.Para import *
from Define.Para import *
from Utility.Entity import Entity
from SNR.SNRPARSE import SNRPARSE

class SNRTOP():

    """description of class"""
    def __init__(self,cfg):
        self.tbuf=[]
        self.tdist={}
        self.sobj=[]
        self.sdsobj = []
        self.snrlist=cfg.snr_files
        self.sdslist =cfg.sds_files
        self.snrcfgs =[]
        self.parse_snr_serdes_setting(cfg)

    def module_gen(self,cls,file,chip):
        mdl =cls(file,chip)
        # self.sobj.append(mdl)
        return mdl

    def _parse_sensor_rev(self,_idx,_file):
        return None

    def _parse_sensor_setting(self,chip):
        key = 0
        val = 'gens_data\\'+self.snrlist
        snr_rev='OX08B10'
        # print(key,val,snr_rev)
        #self.tbuf.append((key,snr_rev,val))
        self.tdist[key]=(snr_rev,val)
        snr = self.module_gen(SNRPARSE,val,chip)
        self.sobj.append(snr)
        # print("[SNRTOP] ", self.sobj)

        #print(self.tdist)
        # for i in range(len(self.tdist)):
        #     self.module_gen(sensor_type_dict[name.upper()],i,file,chip)

    def _parse_serdes_setting(self,chip):
        pass

    def parse_snr_serdes_setting(self,chip):
        self._parse_sensor_setting(chip)
        self._parse_serdes_setting(chip)

    # def gen_sdscfg(self,chip):
    #     self._parse_serdes_setting(chip)
    #     for i in range(len(self.sobj)):
    #         self.snrcfgs.append(self.sobj[i].gen_cfg())

    def get_snrs(self):
        snrdict ={}
        snrlen = len(self.tdist)
        snrkeys = sorted(self.tdist.keys())
        for i in range(snrlen):
            snrdict[snrkeys[i]] =self.sobj[i]
        # print("[SNRTOP] ", snrdict)
        return snrdict

    def save(self):
        # if(self.set_save):
        self.tbuf = []
        return self.tbuf

    def start(self):
        pass
