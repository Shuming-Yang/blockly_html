"""
This GENS mode code which be ported from GENS source code.

Author: OVT AE
Date: 2024-11-01
"""
# WARNING
# pylint: disable=C0103, C0115, C0116, C0201, C0206, C0325, C0411, W0401, W0612, W0613, W0614
from Utility.Others import find_file
from Utility.JSONR import jsonReader
from Define.Para import *
import gens_globals
# chip_type_dict={
# 0:'_JUPITER',
# 1:'_UV440',
# 2:'_CHIP',
# 3:'_CHIPDBG',
# }


class CaseCFG(object):
    def __init__(self, cfg):
        self.datadirext = ''
        self.input_files = {}  # key: input_file_item, val: input_file_val
        self.snr_files = {}
        self.fsnr_files = {}
        self.sds_files = {}
        self.fsds_files = {}
        self.hcmds = {}
        self.hcmdlist = []
        self.ispfile = ''

        self.outfile = ''
        self.houtfile = ''          # for host mode
        self.foutfile0 = ''         # first file for flash mode
        self.mntfile = ''
        self.hcmdfile = ''
        self.datadir = cfg.datadirext
        self.testcfg = cfg
        self.regdist = cfg.regdist

    def cfg_parse(self):
        self.datadir = 'gens_data'
        self.datadirext = 'gens_data'
        for item in self.input_files.keys():
            filenamestr = self.input_files[item]
            filename = gens_globals.snr_filename
            self.snr_files[0] = find_file(self.datadir, filename)[0]

            gens_globals.TC_data = {}
            tcase = jsonReader('temp.json')

            tcase.change_elem("SYS-PLL-XCLK", gens_globals.RefCLK)
            tcase.change_elem("SYS-CLKT-DO0CLK", str(gens_globals.do0clk))
            tcase.change_elem("SYS-CLKT-DO1CLK", str(gens_globals.do1clk))
            tcase.change_elem("IN0-EN", "1")
            tcase.change_elem("IN0-SCCB_IDX", "0")
            tcase.change_elem("IN0-CBEN", "0")
            tcase.change_elem("DP0-EN", "1")
            tcase.change_elem("DP0-ISP-YUVOUT-CROPEN", "0")
            tcase.change_elem("DP0-ISP-YUVOUT-SCALE-EN", "0")
            tcase.change_elem("CRYPTO-EN", "0")
            tcase.change_elem("CRYPTO-HST0-EN", "0")
            tcase.change_elem("CRYPTO-SLV0-EN", "0")
            for i in range(4):
                tcase.change_elem("OUT" + str(i) + "-EMBL-OVIPRE-EN", "0")
                tcase.change_elem("OUT" + str(i) + "-EMBL-OVIPOST-EN", "0")
                tcase.change_elem("OUT" + str(i) + "-EMBL-OVIPRE-OUTNUM", "0")
                tcase.change_elem("OUT" + str(i) + "-EMBL-OVIPOST-OUTNUM", "0")
                tcase.change_elem("OUT" + str(i) + "-EMBL-HMAC-INEN", "0")
                tcase.change_elem("OUT" + str(i) + "-EMBL-HMAC-VBYTE", "0")
                tcase.change_elem("OUT" + str(i) + "-EMBL-HMAC-OUTEN", "0")
                tcase.change_elem("OUT" + str(i) + "-HMACOUT", "0")

            if gens_globals.rgbir_en == '1':
                for i in range(int(gens_globals.snrmnum)):
                    dpidx = (i * 2)
                    tcase.change_elem("IN0-SENSOR" + str(i) + "-SET_INDEX", "0")
                    tcase.change_elem("DP" + str(dpidx) + "-EN", "1")
                    tcase.change_elem("DP" + str(dpidx+1) + "-EN", "1")
                    tcase.change_elem("SYS-CLKT-SNRCCLK"+ str(i), gens_globals.SNRCLK)
                    tcase.change_elem("DP" + str(dpidx) + "-INPUT-PORTSRC", "0")
                    tcase.change_elem("DP" + str(dpidx+1) + "-INPUT-PORTSRC", "0")
                    tcase.change_elem("DP" + str(dpidx) + "-INPUT-SEOF_DLYMODE", gens_globals.SEOFDLY)
                    tcase.change_elem("DP" + str(dpidx) + "-INPUT-STRMSRC", str(i))
                    tcase.change_elem("DP" + str(dpidx) + "-INPUT-SNRSRC", str(i))
                    tcase.change_elem("DP" + str(dpidx) + "-INPUT-SERSRC", str(i))
                    tcase.change_elem("DP" + str(dpidx+1) + "-INPUT-STRMSRC", str(i))
                    tcase.change_elem("DP" + str(dpidx+1) + "-INPUT-SNRSRC", str(i))
                    tcase.change_elem("DP" + str(dpidx+1) + "-INPUT-SERSRC", str(i))
                    tcase.change_elem("OUT" + str(dpidx) + "-RTMODE", "3")
                    tcase.change_elem("OUT" + str(dpidx) + "-MTX-CSI-LANE", "4")
                    tcase.change_elem("OUT" + str(dpidx) + "-EN", "1")
                    tcase.change_elem("OUT" + str(dpidx+1) + "-EN", "0")
                    tcase.change_elem("OUT" + str(dpidx) + "-YUV-EN", "0")
                    tcase.change_elem("OUT" + str(dpidx) + "-RAWMV-EN", "1")
                    tcase.change_elem("OUT" + str(dpidx) + "-RAWMV-FORMAT", "0")
                    tcase.change_elem("OUT" + str(dpidx) + "-RAWMV-SEL", "0")
                    tcase.change_elem("OUT" + str(dpidx) + "-YUV-OUTEN", "0")
                    tcase.change_elem("OUT" + str(dpidx) + "-RAWMV-OUTEN", "1")
                    tcase.change_elem("OUT" + str(dpidx) + "-YUV-OUTVC", str(i))
                    tcase.change_elem("OUT" + str(dpidx) + "-RAWMV-OUTVC", str(i))
                    tcase.change_elem("RGBIR-DP" + str(dpidx) + "-RAW-ABMODE", "0")
                    tcase.change_elem("RGBIR-DP" + str(dpidx) + "-RAW-OSEL", "0")
                    tcase.change_elem("RGBIR-DP" + str(dpidx) + "-RAW-AMASK", "1")
                    tcase.change_elem("RGBIR-DP" + str(dpidx) + "-RAW-BMASK", "1")
                    tcase.change_elem("RGBIR-DP" + str(dpidx) + "-RAW-AFRMNUM", "1")
                    tcase.change_elem("RGBIR-DP" + str(dpidx) + "-RAW-BFRMNUM", "1")
                    tcase.change_elem("RGBIR-DP" + str(dpidx) + "-IR-ABMODE", "0")
                    tcase.change_elem("RGBIR-DP" + str(dpidx) + "-IR-OSEL", "0")
                    tcase.change_elem("RGBIR-DP" + str(dpidx) + "-IR-AMASK", "0")
                    tcase.change_elem("RGBIR-DP" + str(dpidx) + "-IR-BMASK", "0")
                    tcase.change_elem("RGBIR-DP" + str(dpidx) + "-IR-AFRMNUM", "1")
                    tcase.change_elem("RGBIR-DP" + str(dpidx) + "-IR-BFRMNUM", "1")
                    tcase.change_elem("RGBIR-DP" + str(dpidx) + "-EXPHBLK", gens_globals.rgbirexphblk)
                    tcase.change_elem("DP" + str(dpidx) + "-RGBIREN", "1")
                    tcase.change_elem("DP" + str(dpidx+1) + "-RGBIREN", "1")
                    tcase.change_elem("DP" + str(dpidx) + "INPUT-SNRSRC", str(i))
                    tcase.change_elem("DP" + str(dpidx+1) + "INPUT-SNRSRC", str(i))
                    tcase.change_elem("DP" + str(dpidx+1) + "-INPUT-IDCEN", "0")
                    tcase.change_elem("DP" + str(dpidx+1) + "-INPUT-LOADEN", "0")
                    if gens_globals.EmbEn == '0':
                        tcase.change_elem("OUT" + str(dpidx) + "-EMBL-EN", "0")
                    else:
                        tcase.change_elem("OUT" + str(dpidx) + "-EMBL-EN", "1")
                        tcase.change_elem("OUT" + str(dpidx+1) + "-EMBL-EN", "0")
                        tcase.change_elem("OUT" + str(dpidx) + "-EMBL-CHN", "0")
                        tcase.change_elem("OUT" + str(dpidx) + "-EMBL-SEIPRE-OUTNUM", gens_globals.TopNum)
                        tcase.change_elem("OUT" + str(dpidx) + "-EMBL-STA-OUTNUM", gens_globals.StatNum)
                        tcase.change_elem("OUT" + str(dpidx) + "-EMBL-SEIPOST-OUTNUM", gens_globals.BtmNum)
                tcase.change_elem("RGBIR-EN", "1")
                tcase.change_elem("RGBIR-TPMODE", "1")
                tcase.change_elem("RGBIR-LNHBLK", "100")
            else:
                for i in range(int(gens_globals.snrmnum)):
                    tcase.change_elem("IN0-SENSOR" + str(i) + "-SET_INDEX", "0")
                    tcase.change_elem("DP" + str(i) + "-EN", "1")
                    tcase.change_elem("SYS-CLKT-SNRCCLK"+ str(i), gens_globals.SNRCLK)
                    tcase.change_elem("DP" + str(i) + "-INPUT-PORTSRC", "0")
                    tcase.change_elem("DP" + str(i) + "-INPUT-SEOF_DLYMODE", gens_globals.SEOFDLY)
                    if gens_globals.snrmnum != '1':
                        tcase.change_elem("DP" + str(i) + "-INPUT-STRMSRC", str(i))
                        tcase.change_elem("DP" + str(i) + "-INPUT-SNRSRC", str(i))
                        tcase.change_elem("DP" + str(i) + "-INPUT-SERSRC", str(i))
                    tcase.change_elem("OUT" + str(i) + "-RTMODE", "3")
                    tcase.change_elem("OUT" + str(i) + "-MTX-CSI-LANE", "4")
                    tcase.change_elem("OUT" + str(i) + "-EN", "1")
                    if gens_globals.output_format == 'YUV422-8':
                        tcase.change_elem("OUT" + str(i) + "-YUV-EN", "1")
                        tcase.change_elem("OUT" + str(i) + "-RAWMV-EN", "0")
                        tcase.change_elem("OUT" + str(i) + "-YUV-FORMAT", "0")
                        tcase.change_elem("OUT" + str(i) + "-YUV-SEL", "0")
                        tcase.change_elem("OUT" + str(i) + "-YUV-OUTEN", "1")
                        tcase.change_elem("OUT" + str(i) + "-RAWMV-OUTEN", "0")
                        tcase.change_elem("OUT" + str(i) + "-EMBL-CHN", "1")
                        tcase.change_elem("OUT" + str(i) + "-YUV-OUTVC", str(i*2))
                        tcase.change_elem("OUT" + str(i) + "-RAWMV-OUTVC", str((i*2)+1))
                    else:
                        tcase.change_elem("OUT" + str(i) + "-YUV-EN", "0")
                        tcase.change_elem("OUT" + str(i) + "-RAWMV-EN", "1")
                        tcase.change_elem("OUT" + str(i) + "-RAWMV-FORMAT", "0")
                        tcase.change_elem("OUT" + str(i) + "-RAWMV-SEL", "0")
                        tcase.change_elem("OUT" + str(i) + "-YUV-OUTEN", "0")
                        tcase.change_elem("OUT" + str(i) + "-RAWMV-OUTEN", "1")
                        tcase.change_elem("OUT" + str(i) + "-EMBL-CHN", "0")
                        tcase.change_elem("OUT" + str(i) + "-YUV-OUTVC", str((i*2)+1))
                        tcase.change_elem("OUT" + str(i) + "-RAWMV-OUTVC", str(i*2))
                    if gens_globals.EmbEn == '0':
                        tcase.change_elem("OUT" + str(i) + "-EMBL-EN", "0")
                    else:
                        tcase.change_elem("OUT" + str(i) + "-EMBL-EN", "1")
                        tcase.change_elem("OUT" + str(i) + "-EMBL-SEIPRE-OUTNUM", gens_globals.TopNum)
                        tcase.change_elem("OUT" + str(i) + "-EMBL-STA-OUTNUM", gens_globals.StatNum)
                        tcase.change_elem("OUT" + str(i) + "-EMBL-SEIPOST-OUTNUM", gens_globals.BtmNum)
                if gens_globals.raw_format == "YUV422":
                    tcase.change_elem("DP" + str(i) + "-BYPISP", "1")
                    tcase.change_elem("DP" + str(i) + "-YUVIN_MODE", "1")
                    tcase.change_elem("DP" + str(i) + "-INPUT-LOADEN", "1")
                    tcase.change_elem("OUT" + str(i) + "-RAWMV-IDCSEL", "1")
                    tcase.change_elem("OUT" + str(i) + "-RAWMV-FORMAT", "13")
            tcase.change_elem("IN0-SENSOR_NUM", gens_globals.snrmnum)
            if gens_globals.snrmnum != '1':
                tcase.change_elem("IN0-SDS_EN", "1")
            # tcase.save_json()


class TestCase(object):
    def __init__(self, cfg):
        self.test_cases = []
        # self._parse(cfg)

    def find_case(self, case_name):
        for test_case in self.test_cases:
            if case_name == test_case.name:
                return test_case

    def _parse_new(self, cfg, spilter='-'):
        test_case = CaseCFG(cfg)
        input_file_item = "sensor0_setting"
        test_case.input_files[input_file_item] = gens_globals.snr_filename
        test_case.cfg_parse()
        yield test_case
