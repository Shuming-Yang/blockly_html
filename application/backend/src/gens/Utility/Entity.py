"""
This GENS mode code which be ported from GENS source code.

Author: OVT AE
Date: 2024-11-05
"""
# WARNING
# pylint: disable=C0103, C0115, C0116, R0205, W0401, W0611, W0614, W0622
from Utility.Reg import REG8
from Utility.Reg import REG32
from Utility.Reg import REG16
from Utility.Reg import MEM8
from Utility.Para import *


class Dummy_REG(object):
    def __init__(self, base=0x80200000):
        self.objr = []
        self.regbuf = []
        self.R00 = REG8(base + 0x00, 0x0)


class Entity(object):
    """description of class"""
    def __init__(self, _type='REG'):
        self.name = "Entity"
        self.setbuf = []
        #self.type = _type
        #if(_type == 'REG'):
        self.reg = Dummy_REG()
        #else:
        #    self.mem = Dummy_RAM()

    def start(self):
        pass

    @staticmethod
    def get_key(dict, val):
        for key,dat in dict.items():
            # print("{} {} {}".format(key,dat,val))
            if dat == val:
                return key
            else:
                continue

    def __str__(self):
        return ''.join('['+self.name+']')

    def _setting_parse(self, snrfile, id=0x6c):
        datdict = {}
        datlist = []
        with open(snrfile, 'r', encoding='UTF-8') as fh:
            for line in fh.readlines():
                raw = line.strip().rstrip()
                if (raw.startswith(';') or raw.startswith('@')):
                    continue
                if raw != '':
                    if len(raw) >= 3:
                        #if(len(raw.split(' '))>3):
                        #    newraw = ' '.join(raw.split())
                        #    print(newraw,raw.split())
                        #    raise("too many space ")
                        id, addr, data = raw.split()[0: 3]
                        #print(id, addr, data)
                        idh = int(id, 16)
                        addrh = int(addr, 16)
                        if ';' in data:
                            pdata = data.split(';')[0]
                            data = int(pdata,16)
                        else:
                            data = int(data,16)
                        # print("{:x} {:x}".format(idh,id))
                        if idh == int(id, 16):
                            datdict[addrh] = data
                            datlist.append((addrh, data))
        return (datdict,datlist)

    def save_all(self):
        pass

    def save(self):
        self.setbuf = self.reg.objr
        return self.setbuf
        # for addr,val in self.setbuf:
        #   print('{:x} {:x}'.format(addr,val))
