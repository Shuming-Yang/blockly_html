"""
This GENS mode code which be ported from GENS source code.

Author: OVT AE
Date: 2024-11-01
"""
# WARNING
# pylint: disable=C0103, C0115, C0116, W0622
# from Utility.Others import find_file


class TestCfg(object):

    def __init__(self):
        self.datadir = 'gens_data'
        self.datadirext = 'gens_data'
        self.regtab = 'regtable.txt'
        self.testfile = ''
        self.testcase = ''
        self.testdir = ''
        self.regdist = {}
        self.regfilenmae = 'OAX4K_Summary_Table.xls'
        self.ispfilename = 'isp_top.xls'
        self.ispxls = ''
        self.ispxls_dir = ''
        self.version = 4007
        self.setmode = 0
        self.bootmode = 2
        self.sdsspliten = 1
        self.chiptype = 0
        self.mnten = 0
        self.mnttype = 0
        self.diffen = 0
        self.dften = 0
        self.setheader = 0
        self.loglevel = 'debug'
        self.log = ''
        self.chip_cfg_file = ''
        self._para_config()

    def _para_config(self):
        self.datadirext = 'Data'
        self.testfile = 'FWR_TS_Default'
        self.testcase = 'Default'
        self.regtab_dir = ''
        self.ispxls_dir = ''

        self.setmode = 0
        self.bootmode = 2
        self.sdsspliten = 1
        self.chiptype = 2
        self.mnten = 0
        self.setheader = 1
        self.mnttype = 1
        self.diffen = 0
        self.dften = 0
        self.chip_cfg_file = ''
        self.testdir = ''
        self.testfile = 'FWR_TS_Default'
        self.loglevel = 'debug'

    def find(self, elem):
        ''' element is specified as tag1_tag2_tag3, where tag2 is a child of tag1 and tag3 is a child of tag2, etc...
            return found text, if not found, return '' '''
        found, elem_val = self.xml_reader.find_text(elem, str)
        if found is True:
            pass
        return elem_val

    def update(self, para='', name='', type=int):
        ret, val = self.xml_reader.find_text(name, type)
        if ret is True:
            return val
        else:
            return para

    def __str__(self):
        ret = []
        return ''.join(ret)
