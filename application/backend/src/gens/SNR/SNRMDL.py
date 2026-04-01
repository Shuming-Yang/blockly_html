"""
This GENS mode code which be ported from GENS source code.
@@OAX4K dist define

Author: OVT AE
Date: 2024-11-04
"""
# WARNING
# pylint: disable=C0103, C0116, C0201, W0401, W0614, W0622
from Utility.Para import *


class SNRBASE(object):

    """description of class"""
    def __init__(self):
        self.name = "SNRBASE"
        self.setbuf=[]
        self.baseaddr=0
        self.setlist=[]
        self.setdist={}
        self.regdist={}

    def start(self):
        pass

    @staticmethod
    def get_key(dict,val):
        for key,dat in dict.items():
            #print("{} {} {}".format(key,dat,val))
            if dat==val:
                return key
            else:
                continue
        return None

    def __str__(self):
        return  ''.join('['+self.name+']')

    def _setting_parse(self,snrfile,id=0x6c):
        datdict={}
        datlist=[]
        with open(snrfile,'r',encoding='UTF-8') as fh:
            for line in fh.readlines():
                raw = line.strip().rstrip()
                if(raw.startswith(';') or raw.startswith('@')  ):
                    continue
                if raw != '':
                    if len(raw)>=3:
                        #if(len(raw.split(' '))>3):
                        #    newraw = ' '.join(raw.split())
                        #    print(newraw,raw.split())
                        #    raise("too many space ")
                        id,addr,data = raw.split()[0:3]
                        #print(id,addr,data)
                        idh=int(id,16)
                        addrh= int(addr,16)
                        if ';' in data:
                            pdata= data.split(';')[0]
                            data = int(pdata,16)
                        else:
                            data = int(data,16)
                        # print("{:x} {:x}".format(idh,id))
                        if idh == int(id,16):
                            datdict[addrh]  =data
                            datlist.append((addrh,data))
        return (datdict,datlist)

    def save(self):
        setlen = len(self.setlist)
        len4=0
        base=self.baseaddr
        for i in range(0,setlen-3,4):
            addr0,val0=self.setlist[i]
            addr1,val1=self.setlist[i+1]
            addr2,val2=self.setlist[i+2]
            addr3,val3=self.setlist[i+3]
            data0 =(addr0<<16)+(val0<<8)+(addr1>>8)
            data1 =((addr1&0xff)<<24)+(val1<<16)+(addr2)
            data2 =(val2<<24)+(addr3<<8)+(val3)
            self.setbuf.append((base+0,data0,4))
            self.setbuf.append((base+4,data1,4))
            self.setbuf.append((base+8,data2,4))
            len4=len4+4
            base=base+12
        if setlen%4!=0:
            if setlen-len4==3:
                addr0,val0=self.setlist[len4]
                addr1,val1=self.setlist[len4+1]
                addr2,val2=self.setlist[len4+2]
                data0 =(addr0<<16)+(val0<<8)+(addr1>>8)
                data1 =((addr1&0xff)<<24)+(val1<<16)+(addr2)
                data2 =val2<<24
                self.setbuf.append((base+0,data0,4))
                self.setbuf.append((base+4,data1,4))
                self.setbuf.append((base+8,data2,4))
            elif setlen-len4==2:
                addr0,val0=self.setlist[len4]
                addr1,val1=self.setlist[len4+1]
                data0 =(addr0<<16)+(val0<<8)+(addr1>>8)
                data1 =((addr1&0xff)<<24)+(val1<<16)
                self.setbuf.append((base+0,data0,4))
                self.setbuf.append((base+4,data1,4))
            elif setlen-len4==1:
                addr0,val0=self.setlist[len4]
                data0 =(addr0<<16)+(val0<<8)
                self.setbuf.append((base+0,data0,4))
        return self.setbuf

    def get_sensor_reg_val(self,char):
        addr,val = self.regdist[char]
        if addr not in self.setdist.keys():
            print(f" {char} {addr:x}  use default val {val:x}")
        else:
            val =self.setdist[addr]
        return val
