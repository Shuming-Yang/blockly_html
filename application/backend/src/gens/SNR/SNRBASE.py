"""
This GENS mode code which be ported from GENS source code.
@@OAX4K dist define

Author: OVT AE
Date: 2024-11-04
"""
# WARNING
# pylint: disable=C0103, C0116, C0200, C0201, C0325, E1101, W0221, W0401, W0614, W0622
import copy
import re
# from enum import auto
from Utility.Others import *
from Define.Para import *


serdes_setting_lane_num_dict = {
    0 : 4,
    1 : 3,
    2 : 2,
    3 : 1
}

MHZ = 1000000

sds_phyclk_dict = {
    3: 400*MHZ,
    2: 800*MHZ,
    1:1200*MHZ,
    0:1600*MHZ,
}

class SNRBASE(object):
    """description of class"""
    def __init__(self):
        self.name = "SNRBASE"
        self.setbuf = []
        self.baseaddr = 0
        self.setlist = []
        self.setdist = {}
        self.regdist = {}
        self.sccb_write_regdist = {}
        self.addrlen = 0
        self.cfg = 0
        self.cfgs = []
        self.broadcast_en = 0
        self.snr_bc_id = 0x6c
        self.snr_sccb_idx = 0
        self.ppl_bitmap = 0             # bit[7:4] mean this setting will be used for which sensor
        self.setheader = 0

    def gen_cfg(self, cfg, setheader, refclk):
        self.setheader = setheader
        self.cfg = copy.deepcopy(cfg)
        self.sensor_setting_parse()
        # print("!!!!!!!!!!!!ab mode {}".format(self.cfg.ab_mode))
        self.get_sensor_timing(refclk)
        self.cfgs = [self.cfg]
        self.cfg_cb()  #defined by super class
#        print("Sensor setting generate cfgs len {}".format(len(self.cfgs)))
        return self.cfgs

    def start(self):
        pass

    @staticmethod
    def get_key(input_dict,val):
        for key,dat in input_dict.items():
            #print("{} {} {}".format(key,dat,val))
            if dat == val:
                return key
            else:
                continue
        return None

    def __str__(self):
        return  ''.join('['+self.name+']')

    def _setting_parse(self,snrfile,id=0x6c,idchk=1,group_en=0,group_start=0x3208,group_tirg =0xe0):
        datdict={}
        datlist=[]
        mtlen = 0
        idh = 0
        group_flag=0
        with open(snrfile,'r',encoding='UTF-8') as fh:
            for line in fh.readlines():
                raw = line.strip().rstrip()
                if (raw.startswith(';') or raw.startswith('@') or  raw.startswith('SL') or  raw.startswith('sl') ):
                    continue
                if (raw != '' and (re.match(r'^\d',raw) or re.match(r'^[A-Ea-e]',raw) )  ):
                    if len(raw)>=3:
                        #if(len(raw.split(' '))>3):
                        #    newraw = ' '.join(raw.split())
                        #    print(newraw,raw.split())
                        #    raise("too many space ")
                        #print(raw)
                        idin,addr,data = raw.split()[0:3]
                        # print(id,addr,data)
                        idh=int(idin,16)
                        addrh= int(addr,16)
                        if ';' in data:
                            pdata= data.split(';')[0]
                            data = int(pdata,16)
                        else:
                            data = int(data, 16)
                        # print("{:x} {:x}".format(idh,id))
                        if ((idh == id) or (idchk == 0)):
                            # print(idh)
                            if (addrh==group_start and group_en and not (data & group_tirg)):
                                group_flag  = group_flag ^ 1
                                # print("format {:x} {:x}".format(addrh,data))
                            if not group_flag:
                                datdict[addrh] = data
                            datlist.append((addrh, data))
                            if idh == id:
                                mtlen = mtlen + 1
        return (datdict, datlist, mtlen, id)

    def save(self):
        setlen = len(self.setlist)
        len4 = 0
        len2 = 0
        base = self.baseaddr
        header = 0
        if self.broadcast_en:
            tag = 0x10 << self.snr_sccb_idx
            tag |= 0x06
            header = self.snr_bc_id << 24 | tag<<16 | setlen
        else:
            tag = self.ppl_bitmap << 4
            tag |= 0x00
            header = self.sccb_id << 24 | tag<<16 | setlen
        if self.setheader:
            self.setbuf.append((self.baseaddr, header, 4))
            print(f"[SNRTOP] snr id 0x{self.sccb_id:x} header 0x{header:x}")
            base += 4
        if self.addrlen == 0:  # 16bit address
            for i in range(0, setlen - 3, 4):
                addr0, val0 = self.setlist[i]
                addr1, val1 = self.setlist[i + 1]
                addr2, val2 = self.setlist[i + 2]
                addr3, val3 = self.setlist[i + 3]
                data0 = (addr0 << 16) + (val0 << 8) + (addr1 >> 8)
                data1 = ((addr1 & 0xff) << 24) + (val1 << 16) + (addr2)
                data2 = (val2 << 24) + (addr3 << 8) + (val3)
                self.setbuf.append((base + 0, data0, 4))
                self.setbuf.append((base + 4, data1, 4))
                self.setbuf.append((base + 8, data2, 4))
                len4 = len4 + 4
                base = base + 12
            if setlen % 4 != 0:
                if setlen - len4 == 3:
                    addr0, val0 = self.setlist[len4]
                    addr1, val1 = self.setlist[len4 + 1]
                    addr2, val2 = self.setlist[len4 + 2]
                    data0 = (addr0 << 16) + (val0 << 8) + (addr1 >> 8)
                    data1 = ((addr1 & 0xff) << 24) + (val1 << 16) + (addr2)
                    data2 = val2 << 24
                    self.setbuf.append((base + 0, data0, 4))
                    self.setbuf.append((base + 4, data1, 4))
                    self.setbuf.append((base + 8, data2, 4))
                    base = base + 12
                elif setlen - len4 == 2:
                    addr0, val0 = self.setlist[len4]
                    addr1, val1 = self.setlist[len4 + 1]
                    data0 = (addr0 << 16) + (val0 << 8) + (addr1 >> 8)
                    data1 = ((addr1 & 0xff) << 24) + (val1 << 16)
                    self.setbuf.append((base + 0, data0, 4))
                    self.setbuf.append((base + 4, data1, 4))
                    base = base + 8
                elif setlen - len4 == 1:
                    addr0, val0 = self.setlist[len4]
                    data0 = (addr0 << 16) + (val0 << 8)
                    self.setbuf.append((base + 0, data0, 4))
                    base = base + 4
        else:
            for i in range(0, setlen - 1, 2):
                addr0, val0 = self.setlist[i]
                addr1, val1 = self.setlist[i + 1]
                data0 = (addr0 << 24) + (val0 << 16) + (addr1 << 8) + val1
                self.setbuf.append((base + 0, data0, 4))
                len2 = len2 + 2
                base = base + 4
            if setlen % 2:
                addr0, val0 = self.setlist[len2]
                data0 = (addr0 << 24) + (val0 << 16)
                self.setbuf.append((base + 0, data0, 4))
        # print("snr base setbuf len {}".format(len(self.setbuf)))
        if self.setheader:
            self.setbuf.append((base, 0, 4))
        return self.setbuf

    def get_sensor_reg_val(self,char):
        addr,val = self.regdist[char]
        # if addr in (0x380a, 0x380b):
        #     print("get sensor value defualt 0x{:x} : 0x{:x}".format(addr, val))
        if addr in self.setdist:
            val = self.setdist[addr]
            # if addr in (0x380a, 0x380b):
            #     print("get sensor value setting 0x{:x} : 0x{:x}".format(addr, val))
        return val

    def get_sensor_reg_val_by_addr(self, addr, default_val = 0, use_default = 0):
        if addr in self.setdist:
            return self.setdist[addr]
        else:
            found, val = (0, 0)
            for _, (regdist_addr, regdist_val) in self.regdist.items():
                if regdist_addr == addr:
                    # print("addr 0x{:x} not found in sensor setting, use default value 0x{:x}".format(
                    #     addr, regdist_val
                    # ))
                    found, val = (1, regdist_val)
                    break
            if not found:
                if not use_default:
                    raise RuntimeError(f"addr 0x{addr:x} not found in sensor setting and default dict")
                else:
                    # print("Warning!!!,use default value for addr{:x} {:x}".format(addr,default_val))
                    return default_val
            else:
                return val


def get_idxlist(data):
    retlist, idx = [], 0
    while data > 0:
        if data&0x01 == 1:
            retlist.append(idx)
        data = data >> 1
        idx += 1
    return retlist

def get_dict_keys(input_dict,value):
    keys = []
    for key, val in input_dict.items():
        if val == value:
            keys.append(key)
    return keys


class SDSBASE(SNRBASE):
    """description of class"""
    def __init__(self):
        super().__init__()
        self.name = "SDSBASE"
        self.module_type = '960'
        self.marker = 'TI'
        self.setbuf = []
        self.baseaddr = 0
        self.cfgbaseaddr = 0
        self.setlist = []
        self.sccbidlist = []
        self.snrsccbid_dict = {}
        self.sersccbid_dict = {}
        self.serlnum_dict = {}
#        self.serlnum_dict = {0:4, 1:4, 2:4, 3:4}
        self.lnum_dict = {}                 # lane num dict
        self.vcmap_dict = {0:{0:0, 1:1, 2:2, 3:3}, 1:{0:0, 1:1, 2:2, 3:3}, 2:{0:0, 1:1, 2:2, 3:3}, 3:{0:0, 1:1, 2:2, 3:3}}
        self.pplinemap_dict = {0:0, 1:0, 2:0, 3:0}      # 4 rx pipeline map to txport0
        self.sccbmap_dict = {0:0, 1:0, 2:0, 3:0}        # 4 ser sccb map to txport0
        self.setdist = {}
        self.regdist = {}
        self.addrlen = 0
        self.mtlen = 0
        self.phyclk = 0
        self.txport_num = 1
        # sensor broadcast sccb id
        self.sds_bc_port = 0
        self.snr_bc_id = 0x6c

    def gen_map_dict(self, bitmap):
        _portmap_dict = {}
        _portmap_dict[0] = bitmap>>0 & 0x01
        _portmap_dict[1] = bitmap>>1 & 0x01
        _portmap_dict[2] = bitmap>>2 & 0x01
        _portmap_dict[3] = bitmap>>3 & 0x01
        return _portmap_dict

    def get_sensor_reg_val(self, char):
        id, addr, val = self.regdist[char]
        key = id << 2 + addr
        if key not in self.setdist.keys():
            # print(" {} {:x}  use default val {:x}".format(char,addr,val))
            pass
        else:
            val = self.setdist[key]
        return val

    #  XX XX XX
    def _setting_parse(self, sdsfile, automode):
        datdict = {}
        datlist = []
        mtlen = 0
        idh = 0
        txportid = 0
        rxportid = 0
        rxportidlist = []
        txportidlist = []
        with open(sdsfile, 'r', encoding='UTF-8') as fh:
            for line in fh.readlines():
                raw = line.strip().rstrip()
                if (raw.startswith(';') or raw.startswith('@') or raw.startswith('TAG')):
                    continue
                if raw.startswith('SL'):
                    data = raw.split()[1]
                    if ';' in data:
                        pdata = data.split(';')[0]
                        data = int(pdata, 16)
                    else:
                        data = int(data, 16)
                    idh = 0xff
                    addrh = data>>8
                    data  &= 0xff
                    datlist.append((idh, addrh, data))
                    mtlen = mtlen + 1
                    continue
                if raw != '':
                    if len(raw) >= 3:
                        idin, addr, data = raw.split()[0:3]
                        # print("id:%s addr:%s data:%s" % (id,addr,data))
                        idh = int(idin, 16)
                        addrh = int(addr, 16)
                        if ';' in data:
                            pdata = data.split(';')[0]
                            data = int(pdata, 16)
                        else:
                            data = int(data, 16)
                        mtlen = mtlen + 1
                        datdict[(idh << 2) + addrh] = data
                        datlist.append((idh, addrh, data))
                        if idh not in self.sccbidlist:
                            self.sccbidlist.append(idh)
                        if automode:
                            if addrh==0x20 and idh==self.sccbidlist[0] and self.module_type=='960':
                                self.pplinemap_dict = self.gen_map_dict(data)
                                continue
                            if addrh==0x0c and idh==self.sccbidlist[0] and self.module_type=='960':
                                self.sccbmap_dict = self.gen_map_dict(data>>4)
                                continue
                            if addrh==0x1f and idh==self.sccbidlist[0]:                 # get tx port phyclk
                                self.phyclk = sds_phyclk_dict[data&0x3]
                                continue
                            if addrh==0x4c and idh==self.sccbidlist[0]:                 # get rx port index
                                rxportidlist = get_idxlist(data&0xf)
                                continue
                            if addrh==0x5c and idh==self.sccbidlist[0]:                 # ser alias sccb id
                                for rxportid in rxportidlist:
                                    self.sersccbid_dict[rxportid] = data
                                continue
                            if addrh == 0x65 and idh==self.sccbidlist[0]:               # snr alias sccb id
                                for rxportid in rxportidlist:
                                    self.snrsccbid_dict[rxportid] = data
                                continue
                            if addrh==0x72 and idh==self.sccbidlist[0]:
                                tempdict = {}
                                tempdict[0] = data & 0x3
                                tempdict[1] = (data>>2) & 0x3
                                tempdict[2] = (data>>4) & 0x3
                                tempdict[3] = (data>>6) & 0x3
                                for rxportid in rxportidlist:
                                    self.vcmap_dict[rxportid] = tempdict
                                continue
                            if addrh==0x32 and idh==self.sccbidlist[0]:
                                txportidlist = get_idxlist(data&0x3)
                                continue
                            if addrh == 0x33 and idh == self.sccbidlist[0]:
                                for txportid in txportidlist:
                                    self.lnum_dict[txportid] = serdes_setting_lane_num_dict[data>>4]
                                continue
                            if addrh==0x02 and idh in self.sersccbid_dict.values():
                                rxidxs = get_dict_keys(self.sersccbid_dict, idh)
                                for rxidx in rxidxs:
                                    self.serlnum_dict[rxidx] = ((data>>4) & 0x03) + 1
                                    # print("[SDSSER] ser{} lane num {} data {}".format(rxidx, ((data>>4) & 0x03) + 1, data))
                                continue
            datlist.append((0x00, 0x00, 0x00))
        # print("SDS _setting_parse, len:%d" % mtlen)
        return (datdict, datlist, mtlen, self.sccbidlist[0])

    def save(self):
        header = 0
        # save serdes setting or broadcast before setting
        tag = 0x10 << self.snr_sccb_idx
        if self.broadcast_en:
            tag |= 0x05
            header = self.addrlen<<24 | tag<<16 | self.mtlen
        else:
            tag |= 0x01
            header = self.sccb_id<<24 | tag<<16 | self.mtlen
        if self.setheader:
            self.setbuf.append((self.baseaddr, header, 4))
            self.baseaddr += 4
            print(f"[SNRTOP] serdes {self.index} header 0x{header:x}")
        for i in range(len(self.setlist)):
            dtup = self.setlist[i]
            tmpval = dtup[0]<<24 | dtup[1]<<8 |  dtup[2]
            self.setbuf.append((self.baseaddr, tmpval, 4))
            self.baseaddr += 4
        # save serdes broadcast after setting
        if self.broadcast_en:
            tag = 0x10 << self.snr_sccb_idx
            tag |= 0x01
            header = self.sccb_id<<24 | tag<<16 | self.mtlen1
            self.baseaddr = serdes_base_dict[self.index+1]
            self.setbuf.append((self.baseaddr, header, 4))
            print(f"[SNRTOP] serdes {self.index} header 0x{header:x}")
            for i in range(len(self.setlist1)):
                dtup = self.setlist1[i]
                tmpval = dtup[0]<<24 | dtup[1]<<8 |  dtup[2]
                self.baseaddr += 4
                self.setbuf.append((self.baseaddr, tmpval, 4))
        # for tup in self.setbuf:
        # print("[DEBUG] addr 0x{:x} val 0x{:x}".format(tup[0], tup[1]))
        return self.setbuf
