"""
This GENS mode code which be ported from GENS source code.
@@OAX4K dist define

Author: OVT AE
Date: 2024-11-04
"""
# WARNING
# pylint: disable=C0103, C0115, C0200, C0411, W0401, W0611, W0612, W0614, W1514
from Utility.Reg import REG32
from Define.board import *
from collections import OrderedDict


class RegGen(object):
    def __init__(self, cfg, fsp='\\'):
        datadir = cfg.datadir
        self.reg_table = cfg.datadir + fsp + cfg.regtab
        # self._regtable_dist_gen()

    def _regtable_dist_gen(self):
        regbuf = {}
        with open(self.reg_table, 'r') as fh:
            for line in fh.readlines():
                if not line.startswith('###'):
                    addr, data = line.split()
                    # print(addr,data)
                    if int(addr, 16) & 0xffff0000 == ISP_REG_BASE_ADDR:
                        regobj = REG32(int(addr, 16),int(data, 16), endian=1)
                    else:
                        regobj = REG32(int(addr, 16),int(data, 16), endian=0)
                    regbuf[int(addr, 16)] = regobj
        return self._reorder_regtable(regbuf)

    def _reorder_regtable(self, input_dict):
        regdist = OrderedDict()
        keys = sorted(input_dict.keys())
        for key in keys:
            regdist[key] = input_dict[key]
        return regdist
