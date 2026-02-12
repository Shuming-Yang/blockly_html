"""
This GENS mode code which be ported from GENS source code.

Author: OVT AE
Date: 2024-11-01
"""
# WARNING
# pylint: disable=C0103, C0115
from Utility.OrderClass import Structure


class FW_SYS2(Structure):
    hsize2 = 'DW16'
    vsize2 = 'DW16'
    fmt2 = 'DW8'

    def __init__(self):
        self.hsize2 = 'x'
        self.vsize2 = 'x'
        self.fmt2 = 'x'


class FW_SYS(Structure):
    hsize = 'DW16'
    vsize = 'DW16'
    fmt = 'DW8'
    sys2 = FW_SYS2()
    fmt3 = 'DW8'

    def __init__(self, sys=0):
        self.hsize = 'x'
        self.vsize = 'x'
        self.fmt = 'x'
        self.sys2 = sys
        self.fmt3 = 'x'


class FW_ALGO(Structure):
    hsize = 'DW16'
    vsize = 'DW16'
    fmt = 'DW8'

    def __init__(self):
        self.hsize = 'x'
        self.vsize = 'x'
        self.fmt = 'x'


class FW_CFG(Structure):
    hwctrl = 'DW32'
    sysclk = 'DW32'
    swsafety = ['DW8', 8]
    hwctrl2 = 'DW8'
    fcnum = 'DW8'
    dlycnt = 'DW8'
    rowcnt = 'DW8'
    sys = FW_SYS()

    def __init__(self, sys=0):
        self.hwctrl = 'x'
        self.sys = sys
        self.sysclk = 'x'
        self.hwctrl2 = 'x'
        self.fcnum = 'x'
        self.dlycnt = 'x'
        self.rowcnt = 'x'
        # slef.algo =algo


class ALGO_CFG(Structure):
    algoctrl = 'DW32'
    sys = FW_ALGO()

    def __init__(self, algo=0):
        self.algoctrl = 'x'
        self.sys = algo
        self.en = 0
