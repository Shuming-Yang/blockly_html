"""
This GENS mode code which be ported from GENS source code.

Author: OVT AE
Date: 2024-11-01
"""
# WARNING
# pylint: disable=C0103, C0115, C0116, C0200, C0209, C0325, W0212, W0401, W0612, W0613, W0614, W0622, W0707, W0107, W0715, W1308, W1514, C0411, C1803
# from re import L
# from typing_extensions import runtime
# from typing_extensions import runtime
from Utility.JSONR import jsonReader
from Utility.Para import *
from Utility.Others import *
from DP.DPTOP import DPTOP
from SYS.SYSTOP import SYSTOP
from SNR.SNRTOP import SNRTOP
# from SNR.SNRBASE import SNRBASE
from STRM.STRMTOP import STRMTOP
from FW.CFWST import *
from Define.Struct import *
from Define.fwstruct import *
import os
# import sys
import re
from Define.Para import *
import copy
# import time
from pathlib import Path
from RegTable.Regdefdist import *
# from collections import OrderedDict
import gens_globals
# from there import print as printk


def cfw_struct_init():
    objlist = []
    oviemblist0 = [OVIEMBL_CTRL_CFG(), OVIEMBL_CTRL_CFG()]
    oviemblist1 = [OVIEMBL_CTRL_CFG(), OVIEMBL_CTRL_CFG()]
    oviemblist2 = [OVIEMBL_CTRL_CFG(), OVIEMBL_CTRL_CFG()]
    oviemblist3 = [OVIEMBL_CTRL_CFG(), OVIEMBL_CTRL_CFG()]
    dpobjlist0 = [CRYPTO_REG_CFG(), RGBIR_REG_CFG(), EMBL_REG_CFG(oviemblist0), PPLN_REG_CFG()]
    dpobjlist1 = [CRYPTO_REG_CFG(), RGBIR_REG_CFG(), EMBL_REG_CFG(oviemblist1), PPLN_REG_CFG()]
    dpobjlist2 = [CRYPTO_REG_CFG(), RGBIR_REG_CFG(), EMBL_REG_CFG(oviemblist2), PPLN_REG_CFG()]
    dpobjlist3 = [CRYPTO_REG_CFG(), RGBIR_REG_CFG(), EMBL_REG_CFG(oviemblist3), PPLN_REG_CFG()]

    serstrmlist0 = [SERSTREAM_CTRL(), SERSTREAM_CTRL(), SERSTREAM_CTRL(), SERSTREAM_CTRL()]
    serstrmlist1 = [SERSTREAM_CTRL(), SERSTREAM_CTRL(), SERSTREAM_CTRL(), SERSTREAM_CTRL()]
    serstrmlist2 = [SERSTREAM_CTRL(), SERSTREAM_CTRL(), SERSTREAM_CTRL(), SERSTREAM_CTRL()]
    serstrmlist3 = [SERSTREAM_CTRL(), SERSTREAM_CTRL(), SERSTREAM_CTRL(), SERSTREAM_CTRL()]

    dp0 = DP_REG_CFG(dpobjlist0)
    dp1 = DP_REG_CFG(dpobjlist1)
    dp2 = DP_REG_CFG(dpobjlist2)
    dp3 = DP_REG_CFG(dpobjlist3)
    sds0 = SDS_REG_CFG(serstrmlist0)
    sds1 = SDS_REG_CFG(serstrmlist1)
    sds2 = SDS_REG_CFG(serstrmlist2)
    sds3 = SDS_REG_CFG(serstrmlist3)
    sccb0 = SCCB_REG_CFG()
    sccb1 = SCCB_REG_CFG()
    safe = SAFETY_REG_CFG()
    sys = SYSTEM_REG_CFG()
    ctrl = CONTROL_REG_CFG()
    objlist = [dp0, dp1, dp2, dp3, sds0, sds1, sds2, sds3, sccb0, sccb1, safe, sys, ctrl]
    return objlist


class OAX4K_CFG(object):
    def __init__(self, chip_type=0):
        self.sccb0 = SCCB_CFG(0)
        self.sccb1 = SCCB_CFG(1)
        self.sds0 = SDS_CFG()
        self.sds1 = SDS_CFG()
        self.sds2 = SDS_CFG()
        self.sds3 = SDS_CFG()
        self.in0 = INPUT_CFG(0)
        self.in1 = INPUT_CFG(1)
        self.in2 = INPUT_CFG(2)
        self.in3 = INPUT_CFG(3)
        self.dp0 = DATAPATH_CFG(0)
        self.dp1 = DATAPATH_CFG(1)
        self.dp2 = DATAPATH_CFG(2)
        self.dp3 = DATAPATH_CFG(3)
        self.crypto = CRYPTO_TOP_CFG()
        self.rgbir = RGBIR_CFG()
        self.pg0 = PGEN_CFG(0)
        self.pg1 = PGEN_CFG(1)
        self.out0 = OUTPUT_CFG(0, chip_type)

        self.out1 = OUTPUT_CFG(1, chip_type)
        self.out2 = OUTPUT_CFG(2, chip_type)
        self.out3 = OUTPUT_CFG(3, chip_type)
        self.out0.crypto_slv = self.crypto.slv0
        self.out1.crypto_slv = self.crypto.slv1
        self.out2.crypto_slv = self.crypto.slv2
        self.out3.crypto_slv = self.crypto.slv3
        self.sys = SYSTEM_CFG(chip_type)
        # self.fw = CFW_REG_CFG(cfw_struct_init())
        self.fw = CFW_REG_CFG()
        self.algo = ALGO_CFG(FW_ALGO())
        self.safe = SAFETY_CFG()
        self.topctrl = TOPCTRL_CFG(chip_type)
        # self.analog = ANALOG_CFG(chip_type)
        self.mnt = MONITOR_CFG()
        # self.safe = SAFETY_CFG()
        # self.hcmdctrl = HCMDCTRL_CFG()


class CHIPCFG(object):
    def __init__(self, cfg):
        self.xmlcfg = cfg
        self.chiptype = cfg.testcfg.chiptype
        self.bootmode = cfg.testcfg.bootmode
        self.sdsspliten = cfg.testcfg.sdsspliten
        self.setheader = cfg.testcfg.setheader
        self.jsonfile = jsonReader('temp.json')

        self.oax4k_chipvar_dict = {}
        self.regtable = cfg.regdist
        self.snr_files = gens_globals.snr_filename
        self.fsnr_files = cfg.fsnr_files
        self.sds_files = cfg.sds_files
        self.oax4k_cfg = OAX4K_CFG(self.chiptype)
        self.snrtop = 0  # used to store instantiated SNRTOP while parsing sensor setting file, and the obj will be copied to OAX4K_CFG
        self.oax4k_dup = copy.deepcopy(self.oax4k_cfg)
        self._parse_chipcfg_xml()
        self._chip_init(cfg)
        pass

    def update(self, name, type=int):
        found, val = self.jsonfile.find_text(name, type)
        return found, val

    @staticmethod
    def clkfreq_autoconvt(freq):
        if (freq < 1000):
            rfreq = freq * 1000000
        else:
            rfreq = freq
        return rfreq

    def _oviembl_cfg_validity_chk(self, ovi, out, loc):
        linenum = ovi.outnum
        outidx = out.index

        outchn = out.yuv if (out.embl.chn) else out.rawmv

        oax4k_embl_sram_cap_dict = {
            0: (3840, 4096),
            1: (1920, 3968),
            2: (2560, 3968),
            3: (1920, 3968),
        }

        embl_max_sram_cap_byte, sta_max_sram_cap_byte = oax4k_embl_sram_cap_dict[outidx]

        if (out.embl.chn):
            if (outchn.format == 4):  # rgb888
                byte_rate = 3
            elif (outchn.format < 4):  # yuv422
                byte_rate = 2
            else:  # yuv420
                byte_rate = 1.5

        else:
            if (outchn.format <= 3):  # raw8,raw10,raw12,raw14
                byte_rate = 1
            else:
                byte_rate = 2

        if ("sta" in loc):
            if (out.embl.chn):
                if (outchn.format in [0, 1, 3, 4, 5, 6]):
                    bit12_byte2 = 2
                else:
                    bit12_byte2 = 1
            else:
                if (outchn.format in [12]):
                    bit12_byte2 = 2
                else:
                    bit12_byte2 = 1

            embl_max_line_cap_byte = outchn.hsize * linenum * byte_rate/bit12_byte2 / (2 if (out.embl.tagen) else 1) - 4 - 64  # 64 for crc calculation timing
            embl_acutal_max_byte = min(sta_max_sram_cap_byte, embl_max_line_cap_byte)
            pass
        else:
            embl_max_line_cap_byte = outchn.hsize * linenum * byte_rate / (2 if (out.embl.tagen) else 1) - 4 - 64  # 64 for crc calculation timing
            embl_acutal_max_byte = min(embl_max_sram_cap_byte, embl_max_line_cap_byte)
            pass

        max_valid_byte = embl_acutal_max_byte

        # pass
        # total_len = sum(lenlist)
        if (linenum):
            if ("ovi" in loc):
                total_len = ovi.len
            elif ("sei" in loc):
                total_len = ovi.vldbyte
            else:
                total_len = 0  # ovi.total_vldbyte*12//8

            print(" embl {} {} max valid byte {} len {}".format(outidx, loc, max_valid_byte, total_len))
            if (total_len > max_valid_byte):
                # pass
                # print("embl{} {}chain len must be 4x and large than 32,acutal {} ,change to {} ".format(outidx,loc,total_len,max(int_inc(sum(lenlist),4),32)))
                raise RuntimeError("out{} {} len out of range acutal {} ,max{} ".format(outidx, loc, total_len, max_valid_byte))
                # raise RuntimeError()
        pass

    def _chip_init_emblchn_check(self):
        out0 = self.oax4k_cfg.out0
        out1 = self.oax4k_cfg.out1
        out2 = self.oax4k_cfg.out2
        out3 = self.oax4k_cfg.out3
        outlist = [out0, out1, out2, out3]

        for out in outlist:
            if (out.embl.en and out.en and (out.yuv.en or out.rawmv.en)):
                if (out.embl.ovipre.en):
                    self._oviembl_cfg_validity_chk(out.embl.ovipre, out, "ovipre")
                    pass
                if (out.embl.ovipost.en):
                    self._oviembl_cfg_validity_chk(out.embl.ovipost, out, "ovipost")

                if (out.embl.seipre.outnum and out.embl.seipre.innum):
                    self._oviembl_cfg_validity_chk(out.embl.seipre, out, "seipre")
                    pass
                if (out.embl.seipost.outnum and out.embl.seipost.innum):
                    self._oviembl_cfg_validity_chk(out.embl.seipost, out, "seipost")
                    pass
                if (out.embl.sta.outnum and out.embl.sta.innum):
                    self._oviembl_cfg_validity_chk(out.embl.sta, out, "stapost")
                    pass
                pass
        pass

    def _chip_init_clock_check(self):
        if (self.oax4k_cfg.topctrl.chip_type >= 2):
            pll = self.oax4k_cfg.sys.pll
            clkt = self.oax4k_cfg.sys.clkt
            if (pll.sys_clk0 > 500000000 or pll.sys_clk1 > 500000000):
                raise RuntimeError("sys pll out out of range{} {} ".format(pll.sys_clk0, pll.sys_clk1))
            if (pll.tx0_clk0 > 500000000 or pll.tx0_clk1 > 500000000):
                raise RuntimeError("mipi pll0 outfreq out of range{} {} ".format(pll.tx0_clk0, pll.tx0_clk1))
            if (pll.tx1_clk0 > 500000000 or pll.tx1_clk1 > 500000000):
                raise RuntimeError("mipi pll0 outfreq out of range{} {} ".format(pll.tx1_clk0, pll.tx1_clk1))

            if (pll.xclk > 50000000 or pll.xclk < 6000000):
                raise RuntimeError("input freq out of range{} ".format(pll.xclk))
            cbclks = [clkt.cb0clk, clkt.cb1clk, clkt.cb2clk, clkt.cb3clk]

            for i in range(len(cbclks)):
                if (cbclks[i] > 180000000):
                    raise RuntimeError("cb{} freq{} out out of range  ".format(i, cbclks[i]))

            feclks = [clkt.fe0clk, clkt.fe1clk, clkt.fe2clk, clkt.fe3clk]
            for i in range(len(feclks)):
                if (feclks[i] > 230000000):
                    raise RuntimeError("fe{} clk freq{} out out of range  ".format(i, feclks[i]))
            doclks = [clkt.do0clk, clkt.do1clk]
            outs = [self.oax4k_cfg.out0, self.oax4k_cfg.out1, self.oax4k_cfg.out2, self.oax4k_cfg.out3]
            rtmode0 = self.oax4k_cfg.out0.rtmode
            rtmode2 = self.oax4k_cfg.out2.rtmode
            for i in range(len(doclks)):
                if (doclks[i] > 160000000):
                    raise RuntimeError("do{} clk freq{} out out of range  ".format(i, doclks[i]))
                if (doclks[i] > 94000000):  # dphy 1.2 when 1.5g+
                    for out in outs[i:2*(i+1)]:
                        if (out.en and not out.mtx.csi.deskew and out.index == 0):
                            out.mtx.csi.deskew = 1
                            # raise RuntimeError(" deskew should enable when out{}  PHYCLK {} Large than 1.5G ".format(out.index, doclks[i]))
                        if (out.en and not out.mtx.csi.deskew and out.index == 1 and rtmode0 in [0, 1, 5]):
                            out.mtx.csi.deskew = 1
                        if (out.en and not out.mtx.csi.deskew and out.index == 2 and rtmode0 not in [3]):
                            out.mtx.csi.deskew = 1
                        if (out.en and not out.mtx.csi.deskew and out.index == 3 and rtmode0 not in [3,4] and rtmode2 in [0, 1, 5]):
                            out.mtx.csi.deskew = 1
            if (clkt.dpclk > 2300000000):
                raise RuntimeError("dp clk out of range{} ".format(clkt.dpclk))
            if (clkt.dpclk / clkt.do0clk > 4 or clkt.dpclk / clkt.do1clk > 4):
                raise RuntimeError("dp should < 4x doclk {} {} {} ".format(clkt.dpclk, clkt.do0clk, clkt.do1clk))
            if (clkt.secuclk > 1800000000):
                raise RuntimeError("secuclk clk out of range{} ".format(clkt.secuclk))
            if (clkt.perpclk > 1000000000):
                raise RuntimeError("peripheral clk out of range{} ".format(clkt.perpclk))
            if (clkt.sysclk > 2100000000):
                raise RuntimeError("sys clk out of range{} ".format(clkt.sysclk))
            pass
            print("cbclk {} feclk {} doclk {} dpclk {} sysclk {} ".format(cbclks, feclks, doclks, clkt.dpclk, clkt.sysclk))
            print("sys pll: {} {}  mtxpll0:{} {} mtxpll1:{} {} ".format(pll.sys_clk0, pll.sys_clk1, pll.tx0_clk0, pll.tx0_clk1, pll.tx1_clk0, pll.tx1_clk1))

    def _chip_init(self, cfg):
        topctrl = self.oax4k_cfg.topctrl
        chip_pre_vvs = get_class_var(self.oax4k_cfg)
        chip_ls = get_class_list(self.oax4k_cfg)
        # print(chip_ls)
        prechip_bufl_vars = get_class_listvar_new(self.oax4k_cfg, chip_ls, chip_obj_dict)
        self._chip_init_sys(cfg)
        self._chip_init_sds(cfg)
        self._chip_init_input(cfg, topctrl.snr_auto_mode)
        self._chip_init_rgbir(cfg)
        self._chip_init_internal(cfg)
        self._chip_init_output(cfg)
        # if topctrl.check_timing:
        self._chip_init_idc_timing_check()
        self._chip_init_timing_check()
        self._chip_init_clock_check()
        self._chip_init_timing_check_out()
        self._chip_init_emblchn_check()
        chip_post_vvs = get_class_var(self.oax4k_cfg)
        chip_ls = get_class_list(self.oax4k_cfg)
        postchip_bufl_vars = get_class_listvar_new(self.oax4k_cfg, chip_ls, chip_obj_dict)
        for (preobj, preclist), (postobj, postclist) in zip(prechip_bufl_vars, postchip_bufl_vars):
            self.varlist_intl_check(self.oax4k_cfg, preclist, postclist)

    def _chip_init_sds(self, cfg):
        self.snrtop = SNRTOP(self)
        sds_list = [self.oax4k_cfg.sds0, self.oax4k_cfg.sds1, self.oax4k_cfg.sds2, self.oax4k_cfg.sds3]
        inobjs = [self.oax4k_cfg.in0, self.oax4k_cfg.in1, self.oax4k_cfg.in2, self.oax4k_cfg.in3]
        for inobj in inobjs:
            if inobj.sds_en:
                sdstxport = sds_list[inobj.sds_index].txports[inobj.sds_txport]
                sdstxport.sccb_idx = inobj.sccb_idx

    def _output_chn_tm_chk(self, chnlist, do):
        out_total_bw = 0
        dohts_s = []
        dohsize_s = []
        vldwd_s = []
        dohblk_s = []
        vcid_s = []
        outinfo_s = []
        rt_fifo_sram_size = 1920 * 16

        doobjs = [self.oax4k_cfg.out0, self.oax4k_cfg.out1, self.oax4k_cfg.out2, self.oax4k_cfg.out3]
        outclks = [self.oax4k_cfg.sys.clkt.do0clk, self.oax4k_cfg.sys.clkt.do1clk]
        dpclk = self.oax4k_cfg.sys.clkt.dpclk
        idphblk = self.oax4k_cfg.topctrl.idp_hblk

        fix_total_bw = 0
        fix_max_hts = 0
        fix_hsizes = []
        fix_htss = []
        fix_hblks = []
        fix_bws = []

        for chn in chnlist:
            if (chn.en and not chn.byptc and chn.outen):
                if ((chn.index == 1 and yuv_sel_dist[chn.sel] == 'PGEN0') or (chn.index == 0 and raw_sel_dist[chn.sel] == 'PGEN1')):
                    pass
                else:
                    # actual_outhts = chn.hts*outclks[chn.outport//2]/outclks[0]
                    fix_actual_outhts = (chn.hsize+idphblk)*outclks[0]/dpclk
                    # fix_actual_outhts = outhts*outclks[chn.outport//2]/outclks[0]
                    if chn.txfmt != 0xff:
#                        chn.format = chn.txfmt
                        rawformat, hmul = get_dict_key(output_raw_format_dict, chn.txfmt) if (raw_sel_dist[chn.sel] != 'ISPMV') else get_dict_key(output_yuv_format_dict,
                                                                                                                                                  chn.format)
                    else:
                        rawformat, hmul = get_dict_key(output_raw_format_dict, chn.format) if (raw_sel_dist[chn.sel] != 'ISPMV') else get_dict_key(output_yuv_format_dict,
                                                                                                                                                   chn.format)
                    format_name, hmul = get_dict_key(output_yuv_format_dict, chn.format) if (chn.index) else (rawformat, hmul)
                    byterate, vldwd = rt_byterate_dict[format_name]
                    dpobj = doobjs[chn.rtidx].dpbuf[0]
                    # fix_max_hts= max(fix_max_hts,actual_outhts)
                    if (dpobj.input.fixen):
                        # fix_total_bw =fix_total_bw+(chn.hsize+50) *vldwd/8
                        fix_bws.append((chn.hsize * byterate) * vldwd / 8)
                        fix_htss.append(fix_actual_outhts)
                        fix_hsizes.append(chn.hsize)
                        fix_hblks.append(50 if (chn.hblk_balance == 0) else (chn.hblk_odd + chn.hblk_even) / 2)

        if (fix_htss != []):
            fix_max_hts = max(item for item in fix_htss)
            fix_max_bw_sig = 0
            fix_total_bw = 0
            fix_total_bw1 = 0
            total_hsize = sum(fix_hsizes)
            total_hts = (total_hsize + idphblk * (len(fix_hsizes) - 1)) * outclks[0] / dpclk
            # print("!!!total_hsize total_hts ",total_hsize,total_hts,fix_max_hts)
            for size, hts, vldbw, hblk in zip(fix_hsizes, fix_htss, fix_bws, fix_hblks):
                # hts_bw= vldbw*fix_max_hts/hts
                hts_bw = vldbw * total_hts / hts
                hts_bw1 = vldbw * fix_max_hts / hts
                fix_max_bw_sig = max(hts_bw1, fix_max_bw_sig)
                fix_total_bw = fix_total_bw + hts_bw + hblk
                fix_total_bw1 = fix_total_bw1 + hts_bw1 + hblk

        for chn in chnlist:
            if (chn.en and not chn.byptc and chn.outen):
                # print(chn.rtidx,chn.outport,chn.outchn,"!!!!!")
                actual_outhts = chn.hts*outclks[chn.outport//2]/outclks[0]
                dohts_s.append(actual_outhts)
                vcid_s.append(chn.outvc)
                outinfo_s.append((chn.outvc, actual_outhts, chn.vts * 2, chn.hsize, chn.vsize, chn.format, chn.fps))
                dohblk_s.append(50 if (chn.hblk_balance == 0) else (chn.hblk_odd + chn.hblk_even) / 2)
                if chn.txfmt != 0xff:
                    rawformat, hmul = get_dict_key(output_raw_format_dict, chn.txfmt) if (raw_sel_dist[chn.sel] != 'ISPMV') else get_dict_key(output_yuv_format_dict,
                                                                                                                                              chn.format)
                else:
                    rawformat, hmul = get_dict_key(output_raw_format_dict, chn.format) if (raw_sel_dist[chn.sel] != 'ISPMV') else get_dict_key(output_yuv_format_dict,
                                                                                                                                               chn.format)
                format_name, hmul = get_dict_key(output_yuv_format_dict, chn.format) if (chn.index) else (rawformat, hmul)
                byterate, vldwd = rt_byterate_dict[format_name]
                bufline = rt_fifo_sram_size * 2 / chn.hsize / byterate
                if (doobjs[chn.rtidx].sram_merge):
                    bufline = bufline * 2

                if ((chn.index == 1 and yuv_sel_dist[chn.sel] == 'PGEN0') or (chn.index == 0 and raw_sel_dist[chn.sel] == 'PGEN1')):
                    pass
                else:
                    dpobj = doobjs[chn.rtidx].dpbuf[0]
                    embl = doobjs[chn.rtidx].embl
                    preemblnum = 0
                    if (embl.chn == chn.index and embl.en):
                        preemblnum = embl.ovipre.outnum
                    if (dpobj.input.fixen):
                        tx_csi_bw_ratio = 0.86
                        # tx_out_ratio = (chn.hsize * vldwd / 8 / fix_total_bw) / (fix_total_bw / fix_max_hts / doobjs[chn.outport].mtx.csi.lane / tx_csi_bw_ratio)
                        fix_actual_bw0 = total_hts * do.mtx.csi.lane
                        fix_actual_bw1 = fix_max_hts * do.mtx.csi.lane
                        fix_actual_bw2 = fix_max_hts * do.mtx.csi.lane
                        tx_out_ratio = fix_actual_bw0 * tx_csi_bw_ratio / fix_total_bw
                        tx_out_ratio1 = fix_actual_bw1 * tx_csi_bw_ratio / fix_max_bw_sig
                        tx_out_ratio2 = fix_actual_bw2 * tx_csi_bw_ratio / fix_total_bw1
                        # print("!!!!!!!!!!!", tx_out_ratio, tx_out_ratio1, tx_out_ratio2)
                        # rrrr = (fix_total_bw / fix_max_hts / doobjs[chn.outport].mtx.csi.lane / tx_csi_bw_ratio)
                        fix_outhts = (chn.hsize+self.oax4k_cfg.topctrl.idp_hblk) * outclks[chn.outport // 2] / dpclk * tx_out_ratio
                        buf_line_remain = 0
                        buf_line_remain1 = 0
                        buf_line_remain2 = 0
                        if (self.oax4k_cfg.topctrl.rtfix_mode):  # large buf mode
                            if (tx_out_ratio < 1):
                                buf_line_remain = int_inc((1 - tx_out_ratio) * dpobj.input.rd_start / 2, 2)  # //actual buffline 2
                            if (tx_out_ratio1 < 1):
                                buf_line_remain1 = int_inc((1 - tx_out_ratio1) * dpobj.input.rd_start / 2, 2)  # //actual buffline 2
                            if (tx_out_ratio2 < 1):
                                buf_line_remain2 = int_inc((1 - tx_out_ratio2) * dpobj.input.rd_start / 2, 2)  # //actual buffline 2
                                # print("##@@@@@@@@@@@@@@@@@", fix_actual_bw0, fix_total_bw, fix_max_hts, tx_out_ratio, buf_line_remain, bufline)
                            if (buf_line_remain > bufline or buf_line_remain1 > bufline or buf_line_remain2 > bufline):
                                raise RuntimeError("out{}  buf_line_occupy {} max bufline only {}".format(do.index, buf_line_remain, bufline))
                        else:
                            if (tx_out_ratio < 1):
                                raise RuntimeError("out{}  fix_total_bw {} fix_ideal_bw only {}".format(do.index, fix_total_bw, fix_actual_bw0 * tx_csi_bw_ratio))
                        # if (fix_outhts < chn.hsize):
                        #     buf_line_remain= (chn.hsize-fix_outhts)/chn.hsize*(dpobj.input.rd_start-2) #//actual buffline 2
                        #     print("out{} hts {} outhts{} buf_line_occupy {} max bufline only {} rdst{} buf line {}".format(do.index,
                        #                                                                                                            fix_outhts,
                        #                                                                                                            actual_outhts,
                        #                                                                                                            buf_line_remain,
                        #                                                                                                            bufline,
                        #                                                                                                            dpobj.input.rd_start,
                        #                                                                                                            buf_line_remain1))
                            # if(buf_line_remain>bufline or buf_line_remain1 > bufline):
                if (chn.sbsen):
                    dohsize_s.append(chn.hsize*2*byterate)  # need check # need check
                    # dpobj = doobjs[chn.rtidx].dpbuf[0]
                    if (dpobj.input.vsdly_en):
                        if (bufline < dpobj.input.vsdly_max - 6):  # tbd, it's better to decrease pre embedded line number?
                            raise RuntimeError("RT buf line is too small {} dp need {} ".format(bufline, dpobj.input.vsdly_max - 6))
                else:
                    dohsize_s.append(chn.hsize*byterate)  # need check
                vldwd_s.append(vldwd)
        if (dohts_s != []):
            max_hts = max(item for item in dohts_s)
            for size, hts, vldbw, hblkavg, outinfo in zip(dohsize_s, dohts_s, vldwd_s, dohblk_s, outinfo_s):
                out_total_bw = out_total_bw + (size + hblkavg) * max_hts / hts * vldbw / 8
                print("size {}, hblkavg {}, max_hts {}, hts {}, vldbw {}".format(size, hblkavg, max_hts, hts, vldbw))
                print("out{} toatl bw {:6} maxbw {:6} lanenum {} vldbw {:2}  hblk {}--VCID,HTS,VTS,HZ,VZ,FMT,FPS-- {} ".format(
                    do.index, out_total_bw, max_hts*do.mtx.csi.lane, do.mtx.csi.lane,
                    vldbw, hblkavg, outinfo))
            if (do.mtx.csi.deskew):
                tx_csi_bw_ratio = 0.86
            else:
                tx_csi_bw_ratio = 0.94
            if (out_total_bw > max_hts * do.mtx.csi.lane * tx_csi_bw_ratio):
                raise RuntimeError("output bw is too low {} {} ".format(out_total_bw, max_hts * do.mtx.csi.lane * tx_csi_bw_ratio))
#            print("max hts {}, lane num {}, ratio {}".format(max_hts, do.mtx.csi.lane, tx_csi_bw_ratio))
        if (vcid_s != []):
            uniq_vcids = set(vcid_s)
            if (len(uniq_vcids) != len(vcid_s)):
                raise RuntimeError("currrent output {} have same output VC".format(do.index))

    def _chip_init_timing_check_out(self):
        # print("chip init timing check output")
        out0 = self.oax4k_cfg.out0
        out1 = self.oax4k_cfg.out1
        out2 = self.oax4k_cfg.out2
        out3 = self.oax4k_cfg.out3
        rt0mode = out0.rtmode
        rt2mode = out2.rtmode
        chnlist0 = []
        chnlist1 = []
        chnlist2 = []
        chnlist3 = []

        outs = [out0, out1, out2, out3]

        for out in outs:
            if (not out.en):
                out.yuv.en = 0
                out.rawmv.en = 0
            out.yuv.sbsen = 0
            out.yuv.index = 1
            out.rawmv.sbsen = 0
            out.rawmv.index = 0
            out.yuv.rtidx = out.index
            out.yuv.outport = out.index
            out.rawmv.rtidx = out.index
            out.rawmv.outport = out.index
            out.rawmv.outchn = 1
            out.yuv.outchn = 0
            out.sram_merge = 0

            if (out.yuv.en ^ out.rawmv.en):
                out.sram_merge = 1
                print("enable sram merge for out{} ".format(out.index))
            if (out.en and out.embl.en and (out.yuv.en | out.rawmv.en)):
                self._chip_init_ovitm_check(out)
        if (rt0mode in [2, 3, 4] and not out0.en):
            raise RuntimeError("out0 should enable when rtmode set to {}".format(rt0mode))
        if (rt0mode in [4] and not out2.en):
            raise RuntimeError("out2 should enable when rtmode set to {}".format(rt0mode))

        if (out0.en):
            if (rt0mode == 0):  # tx0 out rt0 yuv and raw
                chnlist0 = [out0.yuv, out0.rawmv]
            elif (rt0mode == 1):  # tx0 out rt01 yuv sbs and rt 0raw
                out0.yuv.sbsen = 1
                chnlist0 = [out0.yuv, out0.rawmv]
            elif (rt0mode == 2):  # tx0 out rt01 yuv +raw through vc
                chnlist0 = [out0.yuv, out0.rawmv, out1.yuv, out1.rawmv]
            elif (rt0mode == 3):  # tx0 out rt0123 yuv +raw through vc
                chnlist0 = [out0.yuv, out0.rawmv, out1.yuv, out1.rawmv, out2.yuv, out2.rawmv, out3.yuv, out3.rawmv]
            elif (rt0mode == 4):  # tx0 out rt0123 yuv vc
                chnlist0 = [out0.yuv, out1.yuv, out2.yuv, out3.yuv]
            elif (rt0mode == 5):  # tx0 out rt0,1 yuv
                chnlist0 = [out0.yuv, out1.yuv]
            for chn in chnlist0:
                chn.outchn = chnlist0.index(chn)
                chn.outport = 0
            if (chnlist0 != []):
                out0.chnlist = chnlist0
                self._output_chn_tm_chk(chnlist0, out0)

        #if (((out2.en or out3.en) and rt0mode != 3)):
        #    if (self.oax4k_cfg.sys.clkt.do0clk < self.oax4k_cfg.sys.clkt.do1clk):
        #        raise RuntimeError("do1clock can't large than do0clk")
        #    pass
        pass

    def _chip_init_timing_check_input(self, di, dp):
        clkt = self.oax4k_cfg.sys.clkt
        ins = [self.oax4k_cfg.in0, self.oax4k_cfg.in1, self.oax4k_cfg.in2, self.oax4k_cfg.in3]
        dps = [self.oax4k_cfg.dp0, self.oax4k_cfg.dp1, self.oax4k_cfg.dp2, self.oax4k_cfg.dp3]
        dos = [self.oax4k_cfg.out0, self.oax4k_cfg.out1, self.oax4k_cfg.out2, self.oax4k_cfg.out3]
        cbclks = [clkt.cb0clk, clkt.cb1clk, clkt.cb2clk, clkt.cb3clk]
        feclks = [clkt.fe0clk, clkt.fe1clk, clkt.fe2clk, clkt.fe3clk]

        if (di.en):
            snrs = di.sensor_buf
            pclk = int(di.phyclk / 16)
            lanenum = di.lane_num
            print("input lane num phyclk {} {}".format(pclk, lanenum))
            for snr in snrs:
                # if snr.not_check_timing:
                #     return
                # pclk = int(snr.strm.phyclk /16)
                fmt = get_dict_key(input_format_dict, snr.strm.format)
                # if (pclk > cbclks[di.index]):
                #     raise RuntimeError("MIPI{} PCLK {} large than sync clk {}".format(di.index, pclk, cbclks[di.index]))
                if (di.pix_width):
                    if (pclk*di.lane_num*16 > feclks[dp.index]*input_format_vldbit_dict_new96[fmt]):
                        raise RuntimeError("input {} lane num{} PCLK {} large than feclk {} vldbit{}".format(di.index,
                                                                                                             di.lane_num,
                                                                                                             cbclks[di.index],
                                                                                                             feclks[dp.index],
                                                                                                             input_format_vldbit_dict_new[fmt]))
                    elif (pclk*di.lane_num*16 > clkt.dpclk*input_format_vldbit_dict_new96[fmt]):
                        raise RuntimeError("dpclk is too slow ")
                    else:
                        pass
                    if(cbclks[di.index]*di.lane_num*16 > feclks[dp.index]*input_format_vldbit_dict_new96[fmt]):
                        raise RuntimeError("input {} lane num{} CBCLK {} large than feclk {} vldbit{}".format(di.index,
                                                                                                              di.lane_num,
                                                                                                              cbclks[di.index],
                                                                                                              feclks[dp.index],
                                                                                                              input_format_vldbit_dict_new96[fmt]))
                    else:
                        pass
                else:
                    if (pclk*di.lane_num*16 > feclks[dp.index]*input_format_vldbit_dict_new[fmt]):
                        raise RuntimeError("input {} lane num{} PCLK {} large than feclk {} vldbit{}".format(di.index,
                                                                                                             di.lane_num,
                                                                                                             cbclks[di.index],
                                                                                                             feclks[dp.index],
                                                                                                             input_format_vldbit_dict_new[fmt]))
                    elif (pclk*di.lane_num*16 > clkt.dpclk*input_format_vldbit_dict_new[fmt]):
                        raise RuntimeError("dpclk is too slow")
                    else:
                        pass
                    if (cbclks[di.index]*di.lane_num*16 > feclks[dp.index]*input_format_vldbit_dict_new[fmt]):
                        raise RuntimeError("input {} lane num{} PCLK {} large than feclk {} vldbit{}".format(di.index,
                                                                                                             di.lane_num,
                                                                                                             cbclks[di.index],
                                                                                                             feclks[dp.index],
                                                                                                             input_format_vldbit_dict_new[fmt]))
                    else:
                        pass
                if (cbclks[di.index] > feclks[dp.index]):
                    raise RuntimeError("input{} cbclk {}can't large than dp{} feclk {} ".format(di.index, cbclks[di.index], dp.index, feclks[dp.index]))

    def _chip_init_sccb_check(self, di, dp):
        if (not di.cben):
            sccblist = [self.oax4k_cfg.sccb0, self.oax4k_cfg.sccb1]

            aec_done_oft = dp.isp.top.aecdoneoft

            isp_buf_line = 16
            aec_estimation_time = 120 * self.oax4k_cfg.sys.clkt.sysclk / 210000000  # 90us @210m sysclk
            idc_buf_line = dp.input.rd_start
            rgbir_buf_line = 4 if (dp.rgbiren) else 0

            snr = di.sensor_buf[dp.input.strmsrc]

            sccb = sccblist[di.sccb_idx]

            for i in [1, 2, 4, 6]:
                vts = snr.strm.vts * i
                vblk = vts - snr.strm.vsize - snr.strm.preblank
                snr_sclk = snr.strm.sclk
                hts = snr.strm.hts
                aec_estimation_line = round(aec_estimation_time * snr.strm.sclk/hts/1000000)
                sccb_write_window = vblk+aec_done_oft-idc_buf_line-isp_buf_line - rgbir_buf_line - aec_estimation_line
                sdsen = sccb.sds_en
                sccb_speed = sccb.speed
                max_send_byte = sum(sccb.sendbuf)
                if (sccb_speed > snr.sccb.maxspeed):
                    raise RuntimeError("sccb{} speed {} is too fast for current sensor maximum only support {}".format(sccb.index, sccb_speed, snr.sccb.maxspeed))
                if (sdsen):
                    sccb_write_linenum = max_send_byte*24/sccb_speed * snr_sclk / hts  # due to sccb clock stretch
                else:
                    sccb_write_linenum = max_send_byte*10/sccb_speed * snr_sclk / hts

                print("sccb################",
                      sccb_write_window, sccb_speed, vblk, aec_estimation_line, idc_buf_line, isp_buf_line, sccb_write_window * hts / snr_sclk, hts * 1000000 / snr_sclk)
                if (sccb_write_linenum > sccb_write_window):
                    if (i == 6):
                        raise RuntimeError("sccb write  time is too large for current dp{}, write window {} ,actual {}".format(dp.index,
                                                                                                                               sccb_write_window,
                                                                                                                               sccb_write_linenum))
                else:
                    snr.strm.vts = snr.strm.vts * i
                    break
            pass

    def _chip_init_ovitm_check(self, do):
        embl = do.embl
        dp = do.dpbuf[0]
        di = dp.dibuf[0]
        outlist = [self.oax4k_cfg.out0, self.oax4k_cfg.out1, self.oax4k_cfg.out2, self.oax4k_cfg.out3]
        if (embl.en):
            dma_word_time_ns = 40*self.oax4k_cfg.sys.clkt.sysclk / 210000000
            dma_init_time_us = 30*self.oax4k_cfg.sys.clkt.sysclk / 210000000
            dma_switch_time_us = 7*self.oax4k_cfg.sys.clkt.sysclk / 210000000

            snr = di.cb_buf[0] if (di.cben) else di.sensor_buf[dp.input.strmsrc]
            vts = snr.strm.vts
            vblk = vts - snr.strm.vsize

            snr_sclk = snr.strm.sclk
            hts = snr.strm.hts
            line_time = snr.strm.hts / snr.strm.sclk

            pre_byte_cnt = 0
            post_byte_cnt = 0
            dma_prepare_time_us = dma_init_time_us
            dma_switch_cnt = 0

            for out in outlist:
                if (out.embl.en and out.en):
                    pre_byte_cnt = pre_byte_cnt + out.embl.ovipre.len  # 125,dma switch time
                    post_byte_cnt = post_byte_cnt + out.embl.ovipost.len
                    dma_switch_cnt = dma_switch_cnt + 1

            pre_word_cnt = pre_byte_cnt // 4
            post_word_cnt = post_byte_cnt // 4
            dma_prepare_time_us = dma_init_time_us + (dma_switch_cnt-1)*dma_switch_time_us

            pre_ready_line = (dma_prepare_time_us * snr.strm.sclk/hts/1000000) + (pre_word_cnt*dma_word_time_ns*snr.strm.sclk/hts/1000000000)
            post_ready_line = (dma_prepare_time_us * snr.strm.sclk/hts/1000000) + (post_word_cnt*dma_word_time_ns*snr.strm.sclk/hts/1000000000)

            yuv_pre_blank = 14
            isp_raw_pre_blank = 10
            idc_raw_pre_blank = snr.strm.preblank if (dp.input.seof_dlymode) else 4  # tbd,need decrease pre sei number

#            if(dp.isp.top.sof_sel not in[0,8] or dp.isp.top.eof_sel!=6):
#                raise RuntimeError("current timing check don't support isp sof, eof select other value{} {}".format(dp.isp.top.sof_sel,dp.isp.top.eof_sel))
            if (do.embl.ovipost.intsel != 5):
                raise RuntimeError("current timing check don't support embl sof, eof select other value {} {}".format(do.embl.ovipre.intsel, do.embl.ovipost.intsel))

            sof_int_vialation = (0 if (do.embl.ovipre.intsel == 4) else (idc_raw_pre_blank if (dp.isp.top.sof_sel == 0) else 0))

            if (embl.chn):
                preemb_write_blank = yuv_pre_blank + sof_int_vialation
            else:
                preemb_write_blank = isp_raw_pre_blank + sof_int_vialation if (do.rawmv.sel == 3) else idc_raw_pre_blank

            chn = do.yuv if(embl.chn) else do.rawmv
            rawformat, hmul = get_dict_key(output_raw_format_dict, chn.format) if (raw_sel_dist[chn.sel] != 'ISPMV') else get_dict_key(output_yuv_format_dict, chn.format)
            format_name, hmul = get_dict_key(output_yuv_format_dict, chn.format) if (embl.chn) else (rawformat, hmul)
            byterate, vldwd = rt_byterate_dict[format_name]
            rt_fifo_sram_size = 1920 * 16
            bufline = int(rt_fifo_sram_size*2/chn.hsize/byterate)
            if (do.sram_merge):
                bufline = bufline*2

            postemb_write_window = vblk - do.embl.sta.outnum - do.embl.seipost.outnum - preemb_write_blank - 2
            preemb_write_window = preemb_write_blank +bufline - 4

            if (preemb_write_window < pre_ready_line or postemb_write_window < post_ready_line):
                raise RuntimeError("ovi timing error,pre_ready_line,post_ready_line,bufline,preemb_write_window,postemb_write_window {} {} {} {} {} ",
                                   pre_ready_line, post_ready_line, bufline, preemb_write_window, postemb_write_window)
        pass

    def _chip_init_idc_timing_check(self):
        '''
        (HSIZEx * BPx * Tmax/Tx)/BRxout <= dpclk * Tmax * HSIZEx/(∑HSIZEx)
        BPx: x path stream pixel bit
        BRxout: x path stream bit rate in dp domain
        T : time of one line
        '''
        ins = [self.oax4k_cfg.in0, self.oax4k_cfg.in1, self.oax4k_cfg.in2, self.oax4k_cfg.in3]
        dps = [self.oax4k_cfg.dp0, self.oax4k_cfg.dp1, self.oax4k_cfg.dp2, self.oax4k_cfg.dp3]
        total_hsize = 0
        for dpobj in dps:
            snrobj = ins[dpobj.input.portsrc].sensor_buf[dpobj.input.strmsrc]
            if dpobj.en and dpobj.input.idcen and snrobj.strm.byptc == 0:
                total_hsize += snrobj.strm.hsize

        for dpobj in dps:
            snrobj = ins[dpobj.input.portsrc].sensor_buf[dpobj.input.strmsrc]
            if dpobj.en and dpobj.input.idcen and snrobj.strm.byptc == 0:
                exdpclk = snrobj.strm.sclk * total_hsize / (2*snrobj.strm.hts)
#                print("[IDCCHK] dp{}, hts {}, sclk {}, total hsize {}, exdpclk {}".format(dpobj.index, snrobj.strm.hts, snrobj.strm.sclk,total_hsize,exdpclk))
                if exdpclk >= self.oax4k_cfg.sys.clkt.dpclk:
                    raise RuntimeError("dp{} except dpclk {} >= actual dpclk {}".format(dpobj.index, exdpclk, self.oax4k_cfg.sys.clkt.dpclk))

    def _chip_init_timing_check(self):
        # print("chip init timing check")

        clkt = self.oax4k_cfg.sys.clkt
        ins = [self.oax4k_cfg.in0, self.oax4k_cfg.in1, self.oax4k_cfg.in2, self.oax4k_cfg.in3]
        dps = [self.oax4k_cfg.dp0, self.oax4k_cfg.dp1, self.oax4k_cfg.dp2, self.oax4k_cfg.dp3]
        dos = [self.oax4k_cfg.out0, self.oax4k_cfg.out1, self.oax4k_cfg.out2, self.oax4k_cfg.out3]
        cbclks = [clkt.cb0clk, clkt.cb1clk, clkt.cb2clk, clkt.cb3clk]
        feclks = [clkt.fe0clk, clkt.fe1clk, clkt.fe2clk, clkt.fe3clk]
        idphblk = self.oax4k_cfg.topctrl.idp_hblk
        # rgbirhblk =self.oax4k_cfg.topctrl.rgbir_hblk
        rgbirhblk = self.oax4k_cfg.rgbir.lnhblk

        if (idphblk < 100):
            raise RuntimeError(" the hblk can't less than 100 for isp")

        idphblk = max(idphblk, rgbirhblk) if (self.oax4k_cfg.rgbir.en) else idphblk  # tbd,need check
        print("idp final hblk {} rgbir en {} rhblk {}".format(idphblk, self.oax4k_cfg.rgbir.en, rgbirhblk))

        in_total_bw = 0
        in_total_hblk = 0
        dphts_s = []
        dphblk_s = []
        hsize_s = []
        ispin_hsize_s = []
        linev2_s = []
        rgbirbw_s = []
        idpvblk_factor_s = []

        fix_bufls = []
        fix_htss = []
        fix_hsizes = []
        fix_rdsts = []
        actual_bws = []
        dphblk_s.append(idphblk)

        dp_hsizes = []

        for dp in dps:
            if (dp.en and dp.input.idcen):
                dpin = dp.isp.inbuf[0]
                if (dpin.hsize % 4):
                    raise RuntimeError(" DP{} in{} strm{} input HSIZE {} is not 4x".format(dp.index, dp.input.portsrc, dp.input.strmsrc, dpin.hsize))
                else:
                    dp_hsizes.append(dpin.hsize)

        for i in range(len(dps)):
            if (dps[i].en):
                di = dps[i].dibuf[0]
                ispin = dps[i].isp.inbuf[0]
                dp_input = dps[i].input
                difeclk = feclks[dps[i].index]
                self._chip_init_timing_check_input(di, dps[i])
                if (not dps[i].bypisp and not self.oax4k_cfg.topctrl.byp_sccbchk):
                    self._chip_init_sccb_check(di, dps[i])
                # self._chip_init_ovitm_check(di,dps[i])
                # if(difeclk > clkt.dpclk):

                dmynum = (dp_input.dmy_num if (dp_input.dmy_mode) else 14) if (dp_input.dmy_en) else 0
                tpnum = (dp_input.sertp_num + dp_input.partp_num) if (dp_input.itpgen) else 0
                if (dp_input.sertp_num < 4 or dp_input.partp_num % 2 or dp_input.sertp_num % 2):
                    raise RuntimeError(" ISP tp number should 2x ,and stest number should not less than 4")
                if (dmynum % 2 or tpnum % 2):
                    raise RuntimeError(" Dummy line number or test pattern number should be even")

                testnum = (dmynum+tpnum)

                rgbir_buf_line = 0

                if (dp_input.seof_dlymode):
                    actual_preblank = ispin.preblank + rgbir_buf_line
                else:
                    actual_preblank = 2 + rgbir_buf_line  # 2 buf line + 2 preblk

                datbuf_line = 0 if (dp_input.fixen) else (dp_input.vsdly_max if (dp_input.vsdly_en) else 0)
                datbuf_line = dp_input.rd_start - 2 if (dp_input.fixen and not dp_input.vsdly_en) else 0

                extra_line_dly = dp_input.extra_bufline

                dihts = ispin.hts
                divts = ispin.vts
                dphts = int(2*dihts*clkt.dpclk/dps[i].input.sclk)

                if (ispin.hsize in dp_hsizes):
                    dp_hsizes.remove(ispin.hsize)

                tp_delta_dly_line = 0

                if (dp_hsizes != []):
                    tp_delta_dly_line = max(dp_hsizes)*testnum//dphts

                di_line_type = ispin.line_v2
                if (divts < ispin.vsize + testnum + actual_preblank + datbuf_line + extra_line_dly + tp_delta_dly_line):
                    raise RuntimeError(" VTS should large than Vsize + dmmy line + actual pre_blank + tp_delta_dly_line +extra_line_dly {} {} {} {} {} {} {}".format(
                        divts,
                        ispin.vsize,
                        testnum,
                        actual_preblank,
                        datbuf_line,
                        extra_line_dly,
                        tp_delta_dly_line))

                if (dp_input.vsdly_en):
                    instrm = di.cb_buf[0].strm if (di.cben) else di.sensor_buf[dp_input.strmsrc].strm
                    if (dp_input.fixen):
                        delta_negvs_max = divts - (ispin.vsize + testnum + actual_preblank + datbuf_line + extra_line_dly + tp_delta_dly_line)
                        # oax4k_negvs_step = dp_input.vsdly_step  if(dp_input.vsdly_step) else delta_negvs_max
                        dp_input.vsdly_step = dp_input.vsdly_step if (dp_input.vsdly_step) else min(delta_negvs_max, instrm.vsdly_step)
                        pass
                    else:
                        delta_negvs_max = divts - (ispin.vsize + testnum + actual_preblank + datbuf_line + extra_line_dly + tp_delta_dly_line)
                        oax4k_negvs_step = dp_input.vsdly_step if (dp_input.vsdly_step) else delta_negvs_max
                        if (oax4k_negvs_step > delta_negvs_max):
                            raise RuntimeError('')
                        if (instrm.vsdly_step):
                            actual_negvs_step = min(oax4k_negvs_step, instrm.vsdly_step)
                        else:
                            actual_negvs_step = oax4k_negvs_step
                        dp_input.vsdly_step = actual_negvs_step
                    print("dp{} input vsdly step {}".format(dps[i].index, dp_input.vsdly_step))

                dihblk = (dihts - ispin.hsize)
                # dphblk = int(2*dihblk*clkt.dpclk/dps[i].input.sclk)
                dphblk = int(dphts - ispin.hsize)
                dps[i].byptc = ispin.byptc | dps[i].byptc
                if (dp_input.fixen and dp_input.idcen and dp_input.vsdly_en and not dps[i].byptc):  # @2021.06.01, only vsdly enable sensor check fix timing bandwidth
                    fix_bufls.append(dp_input.bufline_max)
                    fix_hsizes.append(ispin.hsize)
                    fix_htss.append(dphts)
                    fix_rdsts.append(dp_input.rd_start)

                vblk = divts - ispin.vsize
                # bufline = dps[i].input.vsdly_max +3 if (dps[i].input.vsdly_en) else 2
                bufline = dps[i].input.bufline_max if (dps[i].input.vsdly_en) else 2
                if (dmynum + tpnum + bufline > vblk):
                    add_line = dmynum + tpnum + bufline - vblk
                    # idpvblk_factor = (divts - add_line) /divts # vts -add /vts
                    idpvblk_factor = (ispin.vsize - add_line) / ispin.vsize # vts -add /vts
                else:
                    idpvblk_factor = 1
                div_a, div_b, exponum = idc_mem_hsize_div_dict[get_dict_key(input_format_dict, ispin.format & 0x3f)]

                vld_ratio = (dphts) * (div_a-1)/div_a/ispin.hsize
                actual_bw_cal = (dphts)*div_a/(div_a+exponum+2) * vld_ratio
                actual_bw = min((dphts),actual_bw_cal)

                if ((dp_input.idcen and not dps[i].byptc) or (dps[i].rgbiren and not dps[i].bypisp and not dps[i].byptc)):
                    dphts_s.append(dphts)
                    dphblk_s.append(dphblk)
                    idpvblk_factor_s.append(idpvblk_factor)
#                    hsize_s.append(ispin.hsize)
                    linev2_s.append(di_line_type)
                    actual_bws.append(actual_bw)

                # if ((dp_input.idcen and not dps[i].byptc) or (dps[i].rgbiren)) and not dps[i].bypisp:
                if ((dp_input.idcen and not dps[i].byptc) or (dps[i].rgbiren and not dps[i].bypisp)):  # modify @2021.06/01,for idc bypass case
                    hsize_s.append(ispin.hsize)
                    if (not dps[i].bypisp):
                        ispin_hsize_s.append(ispin.hsize)
                    if (ispin.hsize > actual_bw):
                        raise RuntimeError("bandwidth is not enough! try to adjust SCLK")
                print("IDC{} memory toatl {} avaiable {} ,valid ratio {} insclk {} bufline{} abw{}".format(dps[i].index,
                                                                                                                    dphts,
                                                                                                                    actual_bw,
                                                                                                                    vld_ratio,
                                                                                                                    dps[i].input.sclk,
                                                                                                                    bufline,
                                                                                                                    actual_bw))
                if (dps[i].rgbiren):
                    if (not dps[i].bypisp):
                        instrm = di.cb_buf[0].strm if (di.cben) else di.sensor_buf[dps[i].input.strmsrc].strm

                        mulfactorold = instrm.vcnum  # it should be exp num
                        fmt_type_name = get_dict_key(sensor_input_format_type_top_dict, ispin.format_tid >> 4)
                        mulfactor = sensor_expo_num_dict[fmt_type_name]
                        # workaround
                        if gens_globals.raw_format == 'RAW12' or gens_globals.raw_format == 'RAW10':
                            mulfactor = 1
                        print("rgbir format type {} exponum{} oldexpo{}".format(fmt_type_name, mulfactor, mulfactorold))
                        # dphblk_s.append(dphblk*mulfactor)
                        chip = self.oax4k_cfg
                        rgbir_dps = [chip.rgbir.dp0, chip.rgbir.dp1]
                        rgbirdp = rgbir_dps[int(i/2)]
                        rgbirhblk = rgbirdp.exphblk
                        rgbir_dmynum = rgbirdp.dmynum if (rgbirdp.dmyen) else 0
                        rgbir_tpnum = rgbirdp.tpnum if (rgbirdp.tpen) else 0
                        vblk = divts - ispin.vsize
                        if (rgbir_dmynum + rgbir_tpnum + bufline > vblk):
                            add_line = rgbir_dmynum + rgbir_tpnum + bufline - vblk
                            vblk_factor = (divts - add_line) / divts  # vts -add /vts
                        else:
                            vblk_factor = 1
                        print("rgbir vblk_factor {} idp factor {}".format(idpvblk_factor, vblk_factor))
                        if (rgbir_dmynum % 2 or rgbir_tpnum % 2):
                            raise RuntimeError(" rgbir Dummy line number or test pattern number should be even")
                        rgbir_add_num = rgbir_dmynum + rgbir_tpnum
                        # if(divts <= ispin.vsize + rgbir_add_num + preblank +3):
                        if (divts <= ispin.vsize + rgbir_add_num +3):
                            raise RuntimeError(" VTS should large than Vsize + dmmy line  {} {} {}".format(divts, ispin.vsize, rgbir_add_num))
                        # rgbir_single_path_bw= (ispin.hsize + rgbirhblk)*mulfactor/vblk_factor
                        rgbir_single_path_bw = (instrm.hsize + rgbirhblk)*mulfactor/vblk_factor
                        rgbirbw_s.append((dps[i].index, rgbir_single_path_bw, dphts))
                        # print("!!!!rgbir toatl BW {}".format(rgbirbw_s))
                        if (rgbir_single_path_bw > dphts):
                            raise RuntimeError(" path{} rgbir  BW is too narrow,  dphts {}  path need {}".format(dps[i].index, rgbir_single_path_bw, dphts))
                else:
                    pass
        if (dphts_s != []):
            max_hts = max(item for item in dphts_s)
            min_hblk = min(item for item in dphblk_s)
            pure_dphblks = dphblk_s[1:]
            if (rgbirbw_s != []):   # rgbir timing check
                total_rgbir_bw = 0
                for idx, path_bw, dphts in rgbirbw_s:
                    # print("!!!!!!!!!!!!!!!!!!!!!!", idx, path_bw, dphts)
                    if (not idx % 2):
                        total_rgbir_bw = total_rgbir_bw + path_bw * max_hts / dphts
                        print("rgbir input total {} max {}".format(total_rgbir_bw, max_hts))
                if (total_rgbir_bw > max_hts):
                    raise RuntimeError("rgbir  BW is too narrow,    actual total need {}  maxhts only {}".format(total_rgbir_bw, max_hts))
            worst_dp_ratio = 1
            if (len(fix_htss) > 1):  # fix timing mode check
                maxhts = max(fix_htss)
                common_delay_line = min(fix_rdsts)
                total_bw = 0
                # total_hsize = sum( fix_hsizes)
                total_hsize = 0
                for hsize in fix_hsizes:
                    total_hsize = total_hsize + min_hblk + hsize
                for hsize, hts in zip(fix_hsizes, fix_htss):
                    total_bw = total_bw + hsize*maxhts/hts + min_hblk
                    if (hts < total_hsize):
                        raise RuntimeError("can't support fix timiing mode hts {} total_hsize{} {}".format(hts, total_hsize, fix_htss))
                    print("!!!!fix timing check dp input hts {} total_hsize {}".format(hts, total_hsize))
                dp_factor = 1 if (total_bw < maxhts) else total_bw / maxhts
                dp_bw_real_ratios = [hsize / total_hsize for hsize in fix_hsizes]
                dp_bw_ideal_ratios = [hsize*max_hts/hts/total_bw for hsize, hts in zip(fix_hsizes, fix_htss)]
                if (self.oax4k_cfg.topctrl.tmfix_mode):  # large buf line
                    dp_enlarge_ratios = [ideal_ratio / real_ratio*dp_factor for ideal_ratio, real_ratio in zip(dp_bw_ideal_ratios, dp_bw_real_ratios)]
                    extra_buf_lines = [(dp_enlarge_ratio-1) * common_delay_line for dp_enlarge_ratio in dp_enlarge_ratios]
                    for rdst_line, buf_max, extra_line in zip(fix_rdsts, fix_bufls, extra_buf_lines):
                        delta_line = buf_max - rdst_line if (rdst_line) else 0
                        if (delta_line < extra_line):
                            raise RuntimeError("current buf is not enough for fix timing mode {} {} {} {}".format(buf_max, rdst_line, extra_line, common_delay_line))
                    print("dp input ratio {} max {}".format(dp_enlarge_ratios, extra_buf_lines))
                else:
                    dp_enlarge_ratios = [ideal_ratio / real_ratio for ideal_ratio, real_ratio in zip(dp_bw_ideal_ratios, dp_bw_real_ratios)]
                    worst_dp_ratio = max(dp_enlarge_ratios)
                    print("dp input ratio {} worst_dp_ratio {}".format(dp_enlarge_ratios, worst_dp_ratio))

            def find_cnt(val, buf):
                cnt = 0
                for dat in buf:
                    if val == dat:
                        cnt = cnt + 1
                return cnt

            min_hts = min(item for item in dphts_s)
            round_robin_cycle = 20
            isp_line_buf_depth = 3840 * 2
            in_total_line_size = 0
            extra_dly_buf = []
            actual_min_hblk = (int(min_hblk/round_robin_cycle)+1)*round_robin_cycle
            actual_size = 0
            for size in ispin_hsize_s:  # modify 2021.06.01,only check the size through isp
                in_total_line_size = in_total_line_size + size
            if (in_total_line_size > isp_line_buf_depth):
                raise RuntimeError("ISP line buf is too small {} {}".format(in_total_line_size, isp_line_buf_depth))

            for size, hts, vblk_factor, dphblk, line_type, actual_bw in zip(hsize_s, dphts_s, idpvblk_factor_s, pure_dphblks, linev2_s, actual_bws):
                index = list(zip(hsize_s, dphts_s)).index((size, hts))
                # print(index)
                ahts = hts
                actual_size = size * hts // actual_bw
                print("size {} hts {} abw{} {}".format(size, hts, actual_bw, actual_bws))
                # ahts = hts if(v2) else hts/2
                # in_total_line_size = in_total_line_size + size
                if (size > ahts):
                    raise RuntimeError("current in{} is too fast, size {}  hts {}".format(index, size, ahts))
                # print(" hts min_hts {} {}".format(hts,min_hts))
                if (hts != min_hts):
                    in_total_bw = in_total_bw + (actual_size+min_hblk)*max_hts/hts/vblk_factor
                else:
                    # if (find_cnt(hts, dphts_s) != 1 and extra_dly_buf != [] or (len(set(dphts_s)) == 1)):
                    if (find_cnt(hts, dphts_s) != 1 and extra_dly_buf != []):
                        # actual_size =size*hts/actual_bw
                        in_total_bw = in_total_bw + (actual_size+min_hblk)*max_hts/hts/vblk_factor
                    else:
                        actual_hblk = max(min_hblk, dphblk)
                        # dup_dphtss = copy.deepcopy(dphts_s)
                        dup_dphtss = copy.deepcopy(list(zip(hsize_s, dphts_s)))
                        dup_dphtss.remove((size, hts))
                        # sec_min_hts = min(dup_dphtss)
                        # extra_dly_cnt = (sec_min_hts-hts)//hts
                        total_size = 0
                        cnt = 0
                        for rmsize, rmhts in dup_dphtss:
                            # total_size = total_size + rmsize * max_hts / rmhts + min_hblk
                            total_size = total_size + rmsize + min_hblk
                            # total_size = total_size + rmsize
                            cnt = cnt + 1
                        # total_size = max([ size for size,hts in dup_dphtss ])
                        dp_line_nums = [max_hts/hts for hts in dphts_s]
                        ready_size_cnt = (total_size/hts)
                        extra_line_cnt = ready_size_cnt
                        if (extra_line_cnt > 1):
                            extra_dly = 0
                            extra_dly_avg = 0
                            pass
                        else:
                            actual_hblk = max(hts - size, idphblk) if (line_type) else max(hts/2 - size, idphblk)  # v1 hblk
                            extra_dly0 = hts - hts * extra_line_cnt - actual_hblk if (total_size) else 0
                            extra_dly1 = actual_hblk * extra_line_cnt
                            extra_dly = (extra_dly0+extra_dly1)/2
                            round_robin_cycle = 10
                            extra_dly = (int(extra_dly / round_robin_cycle)+len(dup_dphtss)) * round_robin_cycle
                            extra_dly = 0 if (line_type) else ((hts - hts * extra_line_cnt)/2//round_robin_cycle+1)*round_robin_cycle
                            extra_dly = ((hts - hts * extra_line_cnt)/2//round_robin_cycle+1)*round_robin_cycle
                            extra_dly_max = ((hts - hts * extra_line_cnt)//round_robin_cycle+1)*round_robin_cycle
                            extra_dly_min = ((hts/2+size - hts * extra_line_cnt)//round_robin_cycle+1)*round_robin_cycle
                            extra_dly_avg = (extra_dly_max+extra_dly_min) / 2
                            extra_dly = 0
                            if (extra_dly < 0):
                                print("extra_line cnt is negative  {} {} {} {}".format(hts, actual_hblk, extra_dly, extra_line_cnt))
                                extra_dly = 0
                        extra_dly_buf.append(extra_dly)
                        # in_total_bw =in_total_bw+((actual_size+min_hblk)*max_hts/hts +extra_dly)/vblk_factor
                        in_total_bw = in_total_bw+((actual_size+min_hblk)*max_hts/hts + extra_dly)/vblk_factor
                        print(" extra dly {} {} total_size {} actual_hblk {} line type{} {}".format(extra_dly,
                                                                                                             ready_size_cnt,
                                                                                                             total_size,
                                                                                                             actual_hblk,
                                                                                                             line_type,
                                                                                                             extra_dly_avg))

                print("input toal bw {} total line size {} maxhts {} hts {} size {} hblkmin {} vblk factor {}".format(in_total_bw,
                                                                                                                              in_total_line_size,
                                                                                                                              max_hts,
                                                                                                                              hts,
                                                                                                                              actual_size,
                                                                                                                              min_hblk,
                                                                                                                              vblk_factor))
            # if (in_total_bw > max_hts / worst_dp_ratio):
            #    from tkinter import messagebox
            #    messagebox.showwarning("datapth BW is too low ", "Warning! datapth BW is too low. continue Geneneral datapath ")
            #    raise RuntimeError("datapth BW is too low {} {} {} ".format(in_total_bw, max_hts / worst_dp_ratio, worst_dp_ratio))
        pass

    def _chip_init_isp(self, dp, yuvout, rawmvout):
        ispcfg = dp.isp
        # if (self.oax4k_cfg.rgbir.en):
        if (self.oax4k_cfg.rgbir.en and dp.rgbiren):
            # print("rgbir en {}".format(len(self.oax4k_cfg.rgbir.outs)))
            for (id, obj) in self.oax4k_cfg.rgbir.outs:
                if (id == dp.index):
                    idcin = obj
                    if (dp.dibuf == []):
                        # dp.dibuf.append(self.oax4k_cfg.rgbir.ins[dp.rgbirsrc])
                        dp.dibuf.append(self.oax4k_cfg.rgbir.ins[dp.index//2])
                        dp.input.sclk = dp.dibuf[0].sclk
        else:
            # idcin= dp.input.buf[0]
            dpin = dp.input
            # dpinbuf=dp.input.buf[0]
            # print("dp.dibuf len {}".format(len(dp.dibuf)))
            if (dp.dibuf == []):
                raise RuntimeError("Current DP{} corresponding input {} have not assign {}".format(dp.index, dp.input.portsrc, dp.input.strmsrc))
            dpinbuf = dp.dibuf[0]
            if (dpinbuf.cben):
                idcin = dpinbuf.cb_buf[0].strm
            else:
                idcin = dpinbuf.sensor_buf[dpin.strmsrc].strm
        ispcfg.inbuf.append(idcin)
        dpclk = self.oax4k_cfg.sys.clkt.dpclk
        diclk = dp.input.sclk
        ispcfg.yuvout.format = yuvout.format
        ispcfg.yuvout.sel = ispyuv_sel_dist[yuvout.format]

        isp_ohsize = idcin.hsize
        isp_ovsize = idcin.vsize

        ispcfg.yuvout.hts = round(idcin.hts * dpclk * 2 / diclk)
        ispcfg.yuvout.vts = round(idcin.vts/2)
        print("di_clk {} di_hts {} di_vts {}".format(diclk, idcin.hts, idcin.vts))
        print("dp_clk {} dp_hts {} dp_vts {}".format(dpclk, ispcfg.yuvout.hts, ispcfg.yuvout.vts))

        print("GENS configure RETIME yuvout parameter manually {} {}".format(yuvout.hsize, yuvout.vsize))
        if (ispcfg.yuvout.scale.precropen):
            if (ispcfg.yuvout.scale.precrop_hsize and ispcfg.yuvout.scale.precrop_vsize):
                print("GENS configure ISP scale precrop parameter manually {} {} {} {}".format(ispcfg.yuvout.scale.precrop_hstart,
                                                                                               ispcfg.yuvout.scale.precrop_vstart,
                                                                                               ispcfg.yuvout.scale.precrop_hsize,
                                                                                               ispcfg.yuvout.scale.precrop_vsize))
                if ((ispcfg.yuvout.scale.precrop_hsize > idcin.hsize) or (ispcfg.yuvout.scale.precrop_vsize > idcin.vsize)):
                    raise RuntimeError("YUV scale precrop size {} {} is larger than input IDC size {} {}!".format(ispcfg.yuvout.scale.precrop_hsize,
                                                                                                                  ispcfg.yuvout.scale.precrop_vsize,
                                                                                                                  idcin.hsize,
                                                                                                                  idcin.vsize))
                if ((ispcfg.yuvout.scale.precrop_hsize % 4) != 0):
                    raise RuntimeError("YUV scale precop output hsize must be mulpile of 4!")
                if (((ispcfg.yuvout.scale.precrop_hstart % 2) != 0) or ((ispcfg.yuvout.scale.precrop_vstart % 2) != 0)):
                    raise RuntimeError("YUV scale precop hstart, vstart must be even number!")
                else:
                    isp_ohsize = ispcfg.yuvout.scale.precrop_hsize
                    isp_ovsize = ispcfg.yuvout.scale.precrop_vsize
            else:
                raise RuntimeError("isp scale precrop size can not be 0!")

        ispcfg.yuvout.scale.ihsize = isp_ohsize
        ispcfg.yuvout.scale.ivsize = isp_ovsize

        if (ispcfg.yuvout.scale.en):
            if (ispcfg.yuvout.scale.hsize and ispcfg.yuvout.scale.vsize):
                print("GENS configure ISP YUV scale output parameter manually {} {}".format(ispcfg.yuvout.scale.hsize, ispcfg.yuvout.scale.vsize))
                if (ispcfg.yuvout.scale.hsize > ispcfg.yuvout.scale.ihsize) or (ispcfg.yuvout.scale.vsize > ispcfg.yuvout.scale.ivsize):
                    raise RuntimeError("YUV scale output size {} {} is larger than input size {} {}!".format(ispcfg.yuvout.scale.hsize,
                                                                                                             ispcfg.yuvout.scale.vsize,
                                                                                                             ispcfg.yuvout.scale.ihsize,
                                                                                                             ispcfg.yuvout.scale.ivsize))
                else:
                    isp_ohsize = ispcfg.yuvout.scale.hsize
                    isp_ovsize = ispcfg.yuvout.scale.vsize
            else:
                raise RuntimeError("isp scale size can not be 0!")
            ispcfg.yuvout.vts = round(idcin.vts/2 * ispcfg.yuvout.scale.vsize/idcin.vsize)
            ispcfg.yuvout.hts = round(idcin.hts*idcin.vts*dpclk/diclk/ispcfg.yuvout.vts)
            print("after scale dp_hts {} dp_vts {}".format(ispcfg.yuvout.hts, ispcfg.yuvout.vts))

        if (ispcfg.yuvout.scale.postcropen):
            if (ispcfg.yuvout.scale.postcrop_hsize and ispcfg.yuvout.scale.postcrop_vsize):
                print("GENS configure ISP YUV scale postcrop parameter manually {} {} {} {}".format(ispcfg.yuvout.scale.postcrop_hstart,
                                                                                                    ispcfg.yuvout.scale.postcrop_vstart,
                                                                                                    ispcfg.yuvout.scale.postcrop_hsize,
                                                                                                    ispcfg.yuvout.scale.postcrop_vsize))
                if (ispcfg.yuvout.scale.postcrop_hsize > isp_ohsize) or (yuvout.scale.postcrop_vsize > isp_ovsize):
                    raise RuntimeError("YUV scale postcrop size {} {} is larger than input size {} {}!".format(ispcfg.yuvout.scale.postcrop_hsize,
                                                                                                               ispcfg.yuvout.scale.postcrop_vsize,
                                                                                                               isp_ohsize,
                                                                                                               isp_ovsize))
                if ((ispcfg.yuvout.scale.postcrop_hsize % 4) != 0):
                    raise RuntimeError("YUV scale postcop output hsize must be mulpile of 4!")
                if (((ispcfg.yuvout.scale.postcrop_hstart % 2) != 0) or ((ispcfg.yuvout.scale.postcrop_vstart % 2) != 0)):
                    raise RuntimeError("YUV scale postcop hstart, vstart must be even number!")
                else:
                    isp_ohsize = ispcfg.yuvout.scale.postcrop_hsize
                    isp_ovsize = ispcfg.yuvout.scale.postcrop_vsize
            else:
                raise RuntimeError("isp scale post crop size can not be 0!")
        if (ispcfg.yuvout.cropen):
            if (ispcfg.yuvout.hsize and ispcfg.yuvout.vsize):
                print("GENS configure the ISP yuvout windowing parameter manually {} {} {} {}".format(ispcfg.yuvout.hstart,
                                                                                                      ispcfg.yuvout.vstart,
                                                                                                      ispcfg.yuvout.hsize,
                                                                                                      ispcfg.yuvout.vsize))
                if (ispcfg.yuvout.hsize > isp_ohsize) or (ispcfg.yuvout.vsize > isp_ovsize):
                    raise RuntimeError("YUV windowing output size {} {} is larger than input size {}!".format(ispcfg.yuvout.scale.postcrop_hsize,
                                                                                                              ispcfg.yuvout.scale.postcrop_vsize,
                                                                                                              ispcfg.yuvout.hsize,
                                                                                                              ispcfg.yuvout.vsize))
                if ((ispcfg.yuvout.hsize % 4) != 0):
                    raise RuntimeError("YUV windowing output  hsize must be mulpile of 4!")
                if (((ispcfg.yuvout.hstart % 2) != 0) or ((ispcfg.yuvout.vstart % 2) != 0)):
                    raise RuntimeError("YUV windowing output hstart, vstart must be even number!")
                if (ispcfg.yuvout.hsize > ispcfg.yuvout.hsize) or (ispcfg.yuvout.vsize > ispcfg.yuvout.vsize):
                    raise RuntimeError("YUV windowing output size {} {} is larger than input size {}!".format(ispcfg.yuvout.scale.postcrop_hsize,
                                                                                                              ispcfg.yuvout.scale.postcrop_vsize,
                                                                                                              ispcfg.yuvout.hsize,
                                                                                                              ispcfg.yuvout.vsize))
            else:
                raise RuntimeError("isp yuv windowing size can not be 0!")
        else:  # auto crop
            ispcfg.yuvout.hsize = yuvout.hsize if (yuvout.hsize != 0 and yuvout.hsize <= isp_ohsize) else isp_ohsize
            ispcfg.yuvout.vsize = yuvout.vsize if (yuvout.vsize != 0 and yuvout.hsize <= isp_ohsize) else isp_ovsize
            ispcfg.yuvout.cropen = 1 if ((0 < yuvout.vsize < isp_ohsize) or (0 < yuvout.hsize < isp_ovsize)) else 0

        ispcfg.rawout.format = rawmvout.format
        if (ispcfg.rawout.cropen and ispcfg.rawout.hsize and ispcfg.rawout.vsize):
            print("GENS configure the ISP rawout crop parameter manually")
            pass
        else:
            ispcfg.rawout.hsize = rawmvout.hsize if (rawmvout.hsize != 0 and rawmvout.hsize <= idcin.hsize) else idcin.hsize
            ispcfg.rawout.vsize = rawmvout.vsize if (rawmvout.vsize != 0 and rawmvout.vsize <= idcin.vsize) else idcin.vsize
            # ispcfg.rawout.cropen = 1 if(rawmvout.vsize!=idcin.vsize or rawmvout.hsize!=idcin.hsize ) else 0
            ispcfg.rawout.cropen = 1 if ((0 < rawmvout.vsize < idcin.vsize) or (0 < rawmvout.hsize < idcin.hsize)) else 0
        ispcfg.rawout.hts = round(idcin.hts * dpclk * 2 / diclk)
        ispcfg.rawout.vts = round(idcin.vts/2)

        ispcfg.mvout.format = rawmvout.format
        if (raw_sel_dist[rawmvout.sel] != 'ISPMV'):
            ispcfg.mvout.sel = ispyuv_sel_dist[0]  # tbd ,fix yuv output
        else:
            ispcfg.mvout.sel = ispyuv_sel_dist[rawmvout.format]  # tbd ,fix yuv output
        if (ispcfg.mvout.cropen and ispcfg.mvout.hsize and ispcfg.mvout.vsize):
            print("GENS configure the ISP rawmvout crop parameter manually")
            pass
        else:
            ispcfg.mvout.hsize = rawmvout.hsize if (rawmvout.hsize != 0 and rawmvout.hsize <= idcin.hsize) else idcin.hsize
            ispcfg.mvout.vsize = rawmvout.vsize if (rawmvout.vsize != 0 and rawmvout.vsize <= idcin.vsize) else idcin.vsize
            # ispcfg.mvout.cropen = 1 if(rawmvout.vsize!=idcin.vsize or rawmvout.hsize!=idcin.hsize ) else 0
            ispcfg.mvout.cropen = 1 if ((0 < rawmvout.vsize < idcin.vsize) or (0 < rawmvout.hsize < idcin.hsize)) else 0
        ispcfg.mvout.hts = round(idcin.hts * dpclk * 2 / diclk)
        ispcfg.mvout.vts = round(idcin.vts / 2)
        pass

    def _chip_init_internal_embl(self, do, dp):
        # dpsnrs = dp.input.buf[0]
        dpsnrs = dp.dibuf[0]
        # doobj = dp.dobuf[0]
        doobj = do
        isp = dp.isp
        snr = dpsnrs.cb_buf[0] if (dpsnrs.cben) else dpsnrs.sensor_buf[dp.input.strmsrc]
        embl = do.embl
        embl.crypto = do.crypto_slv
#        print("[CRYPTO] idx{} topembl {} bottomembl {}".format(do.crypto_slv.index, do.crypto_slv.topembl, do.crypto_slv.bottomembl))
        if (embl.en):
            embl.seibuf = dp.input.seibuf
            try:
                snrembl = embl.seibuf[0]
            except Exception:
                raise RuntimeError("current output{} snr embl snr is empty ".format(do.index))
            if dpsnrs.cben == 1 and snr.embl.en == 1:
                snrembl.pre.num = 2
                snrembl.post.num = 2
                snrembl.pre.len = snr.strm.hsize - 4
                snrembl.post.len = snr.strm.hsize - 4
                snrembl.emb_tag_en = 1
                snrembl.pre.emb_id = 0x14
                snrembl.post.emb_id = 0x14
                snrembl.pre.bitpos = 4
                snrembl.post.bitpos = 4
                snrembl.pre.takebyte = 0xa
                snrembl.post.takebyte = 0xa
                print('intn embl->', [dpsnrs.cben, snr.embl.en, snr.embl.pre.takebyte, snr.embl.post.takebyte])
            snrembl.pre.takebyte = 0
            snrembl.pre.len = snr.strm.hsize - 4
            snrembl.post.takebyte = 0
            snrembl.post.len = snr.strm.hsize - 4
            embl.x3a_en = snrembl.x3a_en
            embl.seipre.innum = snrembl.pre.num if(embl.seipre.inen) else 0
            embl.seipre.takebyte = snrembl.pre.takebyte
            embl.seipre.vldbyte =snrembl.pre.len

            embl.seipost.innum = snrembl.post.num if (embl.seipost.inen) else 0
            embl.seipost.takebyte = snrembl.post.takebyte
            embl.seipost.vldbyte = snrembl.post.len
            embl.seipost.outnum = 0 if (embl.seipost.innum == 0) else embl.seipost.outnum
            embl.seipre.outnum = 0 if (embl.seipre.innum == 0) else embl.seipre.outnum
            embl.ovipre.outnum = 0 if (embl.ovipre.en == 0) else embl.ovipre.outnum
            embl.ovipost.outnum = 0 if (embl.ovipost.en == 0) else embl.ovipost.outnum
            embl.ovipre.len = 0
            embl.ovipost.len = 0
            embl.ovipre.src = doobj.emblsrc
            embl.ovipost.src = doobj.emblsrc
            ovipre_chnlen_list = [lent for addr, lent in embl.ovipre.chain_list] if (embl.ovipre.chain_list != []) else embl.ovipre.chnlen_list
            ovipost_chnlen_list = [lent for addr, lent in embl.ovipost.chain_list] if (embl.ovipost.chain_list != []) else embl.ovipost.chnlen_list

            if (embl_chn_dist[embl.chn] == 'YUV'):
                if (doobj.yuv.en):
                    if (embl.ovipre.en):
                        embl.ovipre.len = max(int_inc(sum(ovipre_chnlen_list), 4), 32)  # int((sum(ovipre_chnlen_list)+4)/4)*4
                    if (embl.ovipost.en):
                        embl.ovipost.len = max(int_inc(sum(ovipost_chnlen_list), 4), 32)  # int((sum(ovipre_chnlen_list)+4)/4)*4
                    doobj.yuv.emblbuf.append(embl)
                    if (embl.ovipre.len > doobj.yuv.hsize - 4 or embl.ovipost.len > doobj.yuv.hsize - 4):
                        raise RuntimeError("embeded line total len can't large than hsize {} {} {}".format(embl.ovipre.len, embl.ovipost.len, doobj.yuv.hsize))
                else:
                    print("embeded line can't enable when output channel disable")
                    raise RuntimeError("embeded line{} can't enable when output channel{} disable".format(embl.index, doobj.index))
            else:
                if (doobj.rawmv.en):
                    if (embl.ovipre.en):
                        # embl.ovipre.len = embl.ovipre.len if( embl.ovipre.len) else doobj.rawmv.hsize -4
                        embl.ovipre.len = max(int_inc(sum(ovipre_chnlen_list), 4), 32)  # sum(ovipre_chnlen_list)
                    if (embl.ovipost.en):
                        # embl.ovipost.len =embl.ovipost.len if( embl.ovipost.len) else  doobj.rawmv.hsize -4
                        embl.ovipost.len = max(int_inc(sum(ovipost_chnlen_list), 4), 32)  # sum(ovipost_chnlen_list)
                    doobj.rawmv.emblbuf.append(embl)
                    if (embl.ovipre.len > doobj.rawmv.hsize - 4 or embl.ovipost.len > doobj.rawmv.hsize - 4):
                        raise RuntimeError("embeded line total len can't large than hsize {} {} {}".format(embl.ovipre.len, embl.ovipost.len, doobj.rawmv.hsize))
                else:
                    print("embedede line can't enable when output channel disable")
                    raise RuntimeError("embedede line can't enable when output channel disable {} {}".format(embl.index, doobj.index))

            embl.sta.innum = snrembl.sta.num if (embl.sta.inen) else 0
            embl.sta.outnum = 0 if (embl.sta.innum == 0) else embl.sta.outnum
            embl.sta.valid_byte0 = int_inc(snrembl.sta.valid_byte[0], 12)
            embl.sta.valid_byte1 = int_inc(snrembl.sta.valid_byte[1], 12)  # tbd
            embl.sta.valid_byte2 = int_inc(snrembl.sta.valid_byte[2], 12)
            embl.sta.valid_byte3 = int_inc(snrembl.sta.valid_byte[3], 12)

            total_vldbyte = sum([embl.sta.valid_byte0, embl.sta.valid_byte1, embl.sta.valid_byte2, embl.sta.valid_byte3])*8//12

            embl.sta.total_vldbyte = total_vldbyte if (snrembl.sta.dis2nd_line) else total_vldbyte*2
        else:
            embl.seipost.outnum = 0
            embl.seipre.outnum = 0
            embl.ovipre.outnum = 0
            embl.ovipost.outnum = 0
            embl.sta.outnum = 0
            pass
        pass

    def _chip_init_internal(self, cfg):
        """
        inital paramter which invovle ISP,IDP,RGBIR,EMBL,Security
        """
        # print("chip init internal")
        dplist = [self.oax4k_cfg.dp0, self.oax4k_cfg.dp1, self.oax4k_cfg.dp2, self.oax4k_cfg.dp3]
        # emblist=[ self.oax4k_cfg.embl0,self.oax4k_cfg.embl1,self.oax4k_cfg.embl2,self.oax4k_cfg.embl3]
        outlist = [self.oax4k_cfg.out0, self.oax4k_cfg.out1, self.oax4k_cfg.out2, self.oax4k_cfg.out3]

        dp_actives = []
        do_actives = []
        for dpobj in dplist:
            if (dpobj.en):
                for outobj in outlist:
                    if (outobj.en and (outobj.yuv.en or outobj.rawmv.en)):
                        dpobjact = dplist[outobj.src]
                        # embobj =emblist[outobj.emblsrc]
                        if outobj not in do_actives:
                            do_actives.append(outobj)
                            # outobj.emblbuf.append(embobj)
                            if (dpobjact.en):
                                outobj.dpbuf.append(dpobjact)
                                if (dpobjact.bypisp):
                                    if (outobj.yuv.en or (outobj.rawmv.en and (outobj.rawmv.sel > 2))):
                                        raise RuntimeError("current output datapath don't enable {} {} {} when isp bypass enable".format(outobj.index,
                                                                                                                                         dpobjact.index,
                                                                                                                                         outobj.src))

                            else:
                                raise RuntimeError("current output corrersponding datapath don't enable {} {} {}".format(outobj.index,
                                                                                                                         dpobjact.index,
                                                                                                                         outobj.src))
                        if dpobjact not in dp_actives:
                            dpobjact.dobuf.append(outobj)
                            dp_actives.append(dpobjact)
                            yuvout = outobj.yuv
                            rawout = outobj.rawmv
                            self._chip_init_isp(dpobjact, yuvout, rawout)
                # if(dpobj.en):
                if dpobj not in dp_actives:
                    # raise RuntimeError("current dp{} don't have corresponding output enable".format(dpobj.index))
                    outobj = outlist[dpobj.index]
                    print("current dp{} don't have output ,use default out{}".format(dpobj.index, outobj.index))
                    dpobj.dobuf.append(outobj)
                    yuvout = outobj.yuv
                    rawout = outobj.rawmv
                    self._chip_init_isp(dpobj, yuvout, rawout)
                self._chip_init_vsdlymax(dpobj)

    def _output_para_init_by_dp(self, out, dp, txlist):
        rtyuv = out.yuv
        rtraw = out.rawmv
        orgmtx = out.mtx
        dpclk = self.oax4k_cfg.sys.clkt.dpclk
        outclklist = [self.oax4k_cfg.sys.clkt.do0clk, self.oax4k_cfg.sys.clkt.do1clk]
        # doclk = outclklist[int(out.index/2)]
        doclk = outclklist[0]
        orgmtx.csi.freq = outclklist[int(out.index/2)]
        fps = dp.isp.inbuf[0].fps
        instrm = dp.isp.inbuf[0]
        rtyuv.byptc = int(dp.isp.inbuf[0].byptc or dp.byptc)
        if (yuv_sel_dist[out.yuv.sel] == 'ISPHV'):
            rtyuv.hsize = dp.isp.yuvout.hsize
            rtyuv.vsize = dp.isp.yuvout.vsize
            # doclk = outclklist[rtyuv.outport//2]
            rtyuv.hts = round(dp.isp.yuvout.hts * doclk / dpclk)
            rtyuv.vts = dp.isp.yuvout.vts
            rtyuv.fps = fps
        elif (yuv_sel_dist[out.yuv.sel] == 'ISPMV'):
            rtyuv.hsize = dp.isp.mvout.hsize
            rtyuv.vsize = dp.isp.mvout.vsize
            # doclk = outclklist[rtyuv.outport//2]
            rtyuv.hts = round(dp.isp.mvout.hts * doclk / dpclk)
            rtyuv.vts = dp.isp.mvout.vts
            rtyuv.fps = fps

        if (raw_sel_dist[out.rawmv.sel] != 'PGEN1'):
            ispin = dp.isp.inbuf[0]
            # doclk =  outclklist[rtraw.outport//2]

            rtraw.hts = round(ispin.hts * 2 * doclk / dp.input.sclk)
            rtraw.vts = round(ispin.vts/2)
            rtraw.fps = fps
            rtraw.byptc = int(dp.isp.inbuf[0].byptc or dp.byptc)
            if (raw_sel_dist[out.rawmv.sel] == 'ISPMV'):  # TBD, selece MV
                rtraw.hsize = dp.isp.mvout.hsize
                rtraw.vsize = dp.isp.mvout.vsize
            elif (raw_sel_dist[out.rawmv.sel] == 'ISPRAW'):
                rtraw.hsize = dp.isp.rawout.hsize
                rtraw.vsize = dp.isp.rawout.vsize
            else:
                if ((rtraw.hsize and rtraw.hsize != dp.isp.inbuf[0].hsize) or (rtraw.vsize and rtraw.vsize != dp.isp.inbuf[0].vsize)):
                    raise RuntimeError("IDC output don't support crop")
                rtraw.hsize = dp.isp.inbuf[0].hsize
                rtraw.vsize = dp.isp.inbuf[0].vsize

                if ((out.rawmv.idcsel < 2) and out.rawmv.en):  # select byp
                    if (not dp.bypisp):
                        raise RuntimeError("out{} sel isp{} should bypass when select byp path".format(out.index, dp.index))
                    else:
                        if (not (dp.rgbiren ^ out.rawmv.idcsel)):
                            print(dp.rgbiren, out.rawmv.idcsel)
                            raise RuntimeError("out{} idc sel should match idp dp{} byp mode".format(out.index, dp.index))
                elif (out.rawmv.en and dp.bypisp):
                    if (out.rawmv.idcsel == 2):
                        raise RuntimeError("isp should not bypass when select duplicate path")
                    pass

    def _output_para_init_by_pgnew(self, out, txlist):
        rtyuv = out.yuv
        rtraw = out.rawmv
        orgmtx = out.mtx
        dpclk = self.oax4k_cfg.sys.clkt.dpclk
        outclklist = [self.oax4k_cfg.sys.clkt.do0clk, self.oax4k_cfg.sys.clkt.do1clk]
        pglist = [self.oax4k_cfg.pg0, self.oax4k_cfg.pg1]
        # doclk = outclklist[int(out.index/2)]
        doclk = outclklist[0]
        orgmtx.csi.freq = outclklist[int(out.index/2)]
        # fps = dp.isp.inbuf[0].fps

        if (yuv_sel_dist[rtyuv.sel] == 'PGEN0'):
            self._output_para_init_by_pg(out.index, rtyuv, pglist[0], txlist)
        if (raw_sel_dist[rtraw.sel] == 'PGEN1'):
            self._output_para_init_by_pg(out.index, rtraw, pglist[1], txlist)
        pass

    def _output_para_init_by_pg(self, index, out, pg, txlist):
        if (out.en):
            outclks = [self.oax4k_cfg.sys.clkt.do0clk, self.oax4k_cfg.sys.clkt.do1clk]
            pg.sclk = self.oax4k_cfg.sys.clkt.dpclk
            # doclk =outclks[int(index /2)]
            # doclk =outclks[out.outport//2]
            doclk = outclks[0]
            out.hsize = pg.hsize
            out.vsize = pg.vsize
            out.format = pg.format  # TBD
            out.hts = int(pg.hts * doclk / pg.sclk)
            out.vts = pg.vts
            out.fps = pg.sclk/pg.hts/pg.vts
            out.byptc = 0
        pass

    def _pg_init_byisp(self, pg, dp):
        pg0 = pg[0]
        pg1 = pg[1]
        pg_sclk = self.oax4k_cfg.sys.clkt.dpclk
        pg0.hsize = dp.isp.yuvout.hsize
        pg0.vsize = dp.isp.yuvout.vsize
        pg0.hts = dp.isp.yuvout.hts
        pg0.vts = dp.isp.yuvout.vts
        pg0.format = dp.isp.yuvout.format
        pg0.fps = pg_sclk / dp.isp.yuvout.hts / dp.isp.yuvout.vts
        pg0.en = 1

        pg1.hsize = dp.isp.rawout.hsize
        pg1.vsize = dp.isp.rawout.vsize
        pg1.hts = dp.isp.rawout.hts
        pg1.vts = dp.isp.rawout.vts
        pg1.format = dp.isp.rawout.format
        pg1.fps = pg_sclk / dp.isp.rawout.hts / dp.isp.rawout.vts
        pg1.en = 1

        pass

    def _chip_init_output(self, cfg):
        """
        initial the paramters which invovle Retime ,MIPITX
        """
        # print("chip init output")
        topctrl = self.oax4k_cfg.topctrl
        pginit = 0
        # embllist=[ self.oax4k_cfg.embl0,self.oax4k_cfg.embl1,self.oax4k_cfg.embl2,self.oax4k_cfg.embl3]
        dplist = [self.oax4k_cfg.dp0, self.oax4k_cfg.dp1, self.oax4k_cfg.dp2, self.oax4k_cfg.dp3]
        outlist = [self.oax4k_cfg.out0, self.oax4k_cfg.out1, self.oax4k_cfg.out2, self.oax4k_cfg.out3]
        txlist = [self.oax4k_cfg.out0.mtx, self.oax4k_cfg.out1.mtx, self.oax4k_cfg.out2.mtx, self.oax4k_cfg.out3.mtx]
        pglist = [self.oax4k_cfg.pg0, self.oax4k_cfg.pg1]

        outclklist = [self.oax4k_cfg.sys.clkt.do0clk, self.oax4k_cfg.sys.clkt.do1clk]
        doclk = outclklist[0]
        for doobj in outlist:
            # doclk =  outclklist[int(out.index/2)]
            if (doobj.en):
                doobj.mtx.csi.freq = outclklist[int(doobj.index/2)]
            if (doobj.en and (doobj.yuv.en or doobj.rawmv.en)):
                if (topctrl.pg_copy_isp):
                    if (pginit == 0):
                        pginit = 1
                        self._pg_init_byisp(pglist, dplist[doobj.src])
                if (yuv_sel_dist[doobj.yuv.sel] == 'PGEN0' or raw_sel_dist[doobj.rawmv.sel] == 'PGEN1'):
                    self._output_para_init_by_pgnew(doobj, txlist)

                if (yuv_sel_dist[doobj.yuv.sel] != 'PGEN0' or raw_sel_dist[doobj.rawmv.sel] != 'PGEN1'):
                    for dpobj in dplist:
                        if (doobj.src == dpobj.index and dpobj.en):
                            self._output_para_init_by_dp(doobj, dpobj, txlist)
                if (doobj.embl.en):
                    dpobj = dplist[doobj.emblsrc]
                    self._chip_init_internal_embl(doobj, dpobj)

    def _cfg_snrs(self, inobj, sdsobj, snr_dict, cclklist, automode):
        # vcidx = 0
        snr_vcs = []
        total_vcnum = 0
        if len(snr_dict) == 0:
            return

        serlist = []
        for i in range(len(sdsobj.rxports)):
            if inobj.sds_en:
                sdsobj.rxports[i].en = 1
            if sdsobj.rxports[i].stream_port == inobj.sds_txport and sdsobj.rxports[i].en:
                serlist.append(sdsobj.rxports[i])

        if len(serlist) < inobj.sensor_num and inobj.sds_en:
            raise RuntimeError("sds{} txport{} stream num {} < in{} snr num {}".format(sdsobj.index, inobj.sds_txport, len(serlist), inobj.index, inobj.sensor_num))

        sdstxport = sdsobj.txports[inobj.sds_txport]
        if inobj.cpy_cfg and not inobj.sds_en:
            for idx in range(1, inobj.sensor_num):
                inobj.sensor_buf[idx] = copy.deepcopy(inobj.sensor_buf[0])
                # inobj.sensor_buf[idx].img_src = idx
        autosnrcfgs = []
        cclks = [self.oax4k_cfg.sys.clkt.snrcclk0, self.oax4k_cfg.sys.clkt.snrcclk1, self.oax4k_cfg.sys.clkt.snrcclk2, self.oax4k_cfg.sys.clkt.snrcclk3]
        for snridx in range(inobj.sensor_num):
            # print("cfg_snrs {} from sensor setting".format(snridx))
            snrcfg = inobj.sensor_buf[snridx]
            if (automode):
                try:
                    # if(autosnrcfgs==[]):
                    autosnrcfgs = snr_dict[snrcfg.set_index].gen_cfg(snrcfg, self.setheader, cclks[inobj.index])
                    # print('snr{} get refclk {}'.format(inobj.index, cclks[inobj.index]))
                except Exception:
                    print("snr_dict len {}, set_index {}, ".format(
                        len(snr_dict), snrcfg.set_index))
                    raise
                # print("~~~~~~~~~~~~len(autosnrcfgs) {}, imgsrc {}".format(len(autosnrcfgs), snrcfg.img_src))
                if (len(autosnrcfgs) > 1):
                    # autosnrcfg = autosnrcfgs[snrcfg.img_src]
                    autosnrcfg = autosnrcfgs[snridx]
                else:
                    autosnrcfg = autosnrcfgs[0]
                total_vcnum += len(autosnrcfg.strm.vclist)
#                print("[DEBUG] snr{} setindex{} vclist {}".format(snridx, snrcfg.set_index, autosnrcfg.strm.vclist))
                print("autosnrcfg embl pre vc {} post vc{} sta {}".format(autosnrcfg.embl.pre.emb_vcid,
                                                                                   autosnrcfg.embl.post.emb_vcid,
                                                                                   autosnrcfg.embl.sta.chn_vc))
                autosnrcfg.ctrl = snrcfg.ctrl

                autosnrcfg.set_index = snrcfg.set_index
                # print(autosnrcfg.index,autosnrcfg.strm.sclk,autosnrcfg.strm.phyclk,autosnrcfg.strm.cclk,dpobj.input.snrsrc,"!!!")
                autosnrcfg.index = snridx
                autosnrcfg.sccb.index = inobj.sccb_idx
                # print(autosnrcfg.strm.vclist,autosnrcfg.index)
                autosnrcfg.strm.sclk = int(autosnrcfg.strm.sclk)
                # autosnrcfg.strm.fps = autosnrcfg.strm.sclk/autosnrcfg.strm.hts/autosnrcfg.strm.vts
                autosnrcfg.strm.phyclk = int(autosnrcfg.strm.phyclk)
                autosnrcfg.strm.cclk = cclklist[autosnrcfg.ctrl.cclk_id]
                inobj.sensor_buf[snridx] = copy.deepcopy(autosnrcfg)
        if total_vcnum > sdstxport._max_vcnum:
            raise RuntimeError("sds{} txport{} support max vcnum {}, but total strm vc num {}".format(inobj.sds_index,
                                                                                                      inobj.sds_txport,
                                                                                                      sdstxport._max_vcnum,
                                                                                                      total_vcnum))
#        print("autosnrcfg vcnum {} vclist {}".format(total_vcnum,snr_vcs))

    def _cfg_sds(self, sdsobj, chipsdscfg, auto_mode):
        # sdscfg decode from sds setting
        # chipsdscfg from struct
        # auto_mode from topctrl sds auto mode
        sdscfg = sdsobj.gen_cfg(self.setheader)
        if auto_mode:
            chipsdscfg.sccb_addrlen = sdscfg.sccb_addrlen
            chipsdscfg.sds_setting_len = sdscfg.sds_setting_len
            for i in range(len(chipsdscfg.rxports)):
                chipser = chipsdscfg.rxports[i]
                ser = sdscfg.rxports[i]
                chipser.max_phyclk = ser.max_phyclk
            if sdsobj.marker == 'MAX':
                raise RuntimeError("not support auto mode for MAX SDS !!")
            chipsdscfg.sccb_id = sdscfg.sccb_id
            print("[CHIPSDS] index {}, en {} sccb id 0x{:x} addrlen {}".format(chipsdscfg.index, chipsdscfg.en, chipsdscfg.sccb_id, chipsdscfg.sccb_addrlen))
            for i in range(len(chipsdscfg.txports)):
                chiptxport = chipsdscfg.txports[i]
                txport = sdscfg.txports[i]
                if txport.en:
                    chiptxport.en = txport.en
                    chiptxport.lane_num = txport.lane_num
                    chiptxport.phyclk = txport.phyclk
                    chiptxport._strm_num = txport._strm_num
                    txport.sccb_idx = chiptxport.sccb_idx
                    print("[CHIPTX] index {}, en {}, lane num {}, sccb idx {}, phyclk {}".format(chiptxport.index,
                                                                                                 chiptxport.en,
                                                                                                 chiptxport.lane_num,
                                                                                                 chiptxport.sccb_idx,
                                                                                                 chiptxport.phyclk))
            for i in range(len(chipsdscfg.rxports)):
                chipser = chipsdscfg.rxports[i]
                ser = sdscfg.rxports[i]
                chipser.en = ser.en
                chipser.sccb_id = ser.sccb_id
                chipser.snr_sccb_id = ser.snr_sccb_id
                chipser.sccb_port = ser.sccb_port
                chipser._sccb_idx = chipsdscfg.txports[chipser.sccb_port].sccb_idx
                ser._sccb_idx = chipser._sccb_idx
                chipser.lane_num = ser.lane_num
                chipser.stream_port = ser.stream_port
                chipser.vcmap = ser.vcmap
#                chipser.max_phyclk = ser.max_phyclk
                if chipser.en:
                    print("[CHIPSER] index {}, en {}, sccb id 0x{:x}, snr sccb id 0x{:x}, sccb idx {}, vamap {}".format(ser.index,
                                                                                                                        ser.en,
                                                                                                                        ser.sccb_id,
                                                                                                                        ser.snr_sccb_id,
                                                                                                                        chipser._sccb_idx,
                                                                                                                        ser.vcmap))
        else:
#            chipsdscfg.sccb_addrlen = sdscfg.sccb_addrlen
            print("[CHIPSDS] index {}, en {} sccb id 0x{:x} addrlen {}".format(chipsdscfg.index, chipsdscfg.en, chipsdscfg.sccb_id, chipsdscfg.sccb_addrlen))
            for i in range(len(chipsdscfg.txports)):
                for j in range(len(chipsdscfg.rxports)):
                    if chipsdscfg.rxports[j].en and chipsdscfg.rxports[j].stream_port == i:
                        chipsdscfg.txports[i]._strm_num += 1
            for txport in chipsdscfg.txports:
                if txport.en:
                    txport.phyclk = txport.phyclk if txport.phyclk > 3000 else txport.phyclk * 1000000
                    print("[CHIPTX] index {}, en {}, lane num {}, strm num {}, sccb idx {}, phyclk {}".format(txport.index,
                                                                                                              txport.en,
                                                                                                              txport.lane_num,
                                                                                                              txport._strm_num,
                                                                                                              txport.sccb_idx,
                                                                                                              txport.phyclk))
            for rxport in chipsdscfg.rxports:
                rxport._sccb_idx = chipsdscfg.txports[rxport.sccb_port].sccb_idx
                if rxport.en:
                    print("[CHIPSER] index {}, en {}, sccb id 0x{:x}, snr sccb id 0x{:x}, sccb idx {}, vamap {}".format(rxport.index,
                                                                                                                        rxport.en,
                                                                                                                        rxport.sccb_id,
                                                                                                                        rxport.snr_sccb_id,
                                                                                                                        rxport._sccb_idx,
                                                                                                                        rxport.vcmap))
                    if not chipsdscfg.txports[rxport.stream_port].en:
                        raise RuntimeError("[CHIPSER] index {} stream port {} not enabled !!".format(rxport.index, rxport.stream_port))
                    if not chipsdscfg.txports[rxport.sccb_port].en:
                        raise RuntimeError("[CHIPSER] index {} sccb port {} not enabled !!".format(rxport.index, rxport.sccb_port))

    def _chip_init_vsdlymax(self, dp):
        dps = [self.oax4k_cfg.dp0, self.oax4k_cfg.dp1, self.oax4k_cfg.dp2, self.oax4k_cfg.dp3]
        inobj = dp.dibuf[0]

        strm = inobj.cb_buf[0].strm if (inobj.cben) else inobj.sensor_buf[dp.input.strmsrc].strm

        idphblk = self.oax4k_cfg.topctrl.idp_hblk

        rgbir_dps = [self.oax4k_cfg.rgbir.dp0, self.oax4k_cfg.rgbir.dp1]
        rgbirdp = rgbir_dps[int(dp.index/2)]
        rgbirhblk = rgbirdp.exphblk
        total_hsize = 0
        dpclk = self.oax4k_cfg.sys.clkt.dpclk
        diclk = dp.input.sclk
        current_hsize = strm.hsize
        dphts = strm.hts * 2 * dpclk/diclk
        extra_buf_line_rgbir = 0
        idc_en_paths = [dps[0].input.idcen & dps[0].en,
                        dps[1].input.idcen & dps[1].en,
                        dps[2].input.idcen & dps[2].en,
                        dps[3].input.idcen & dps[3].en]

        for dpx in dps:
            if (dpx.en and dpx.input.idcen):
                inx = dpx.dibuf[0]
                strmx = inx.cb_buf[0].strm if (inx.cben) else inx.sensor_buf[dpx.input.strmsrc].strm
                total_hsize = total_hsize + strmx.hsize + idphblk  # 100 idp hblk
                if (dpx.input.mem_share and not dp.index % 2):
                    if (idc_en_paths[dpx.index+1]):
                        raise RuntimeError("idc{} memory share can't enable when odd path enable".format(dpx.index))

        if (dp.en and dp.input.idcen and dp.rgbiren):
            fmt_type_name = get_dict_key(sensor_input_format_type_top_dict,
                                         strm.format_tid >> 4)
            mulfactor = sensor_expo_num_dict[fmt_type_name]
            rgbir_total_hsize = mulfactor*(current_hsize+rgbirhblk)
            extra_buf_line_rgbir = int_inc((rgbir_total_hsize)*2 / dphts, 1)
            print("idc{} need {} {} {} extra line for rgbir".format(dp.index,
                                                                             rgbir_total_hsize,
                                                                             dphts,
                                                                             extra_buf_line_rgbir))
        extra_buf_line = max(int_inc((total_hsize-current_hsize)*4 / dphts, 1), extra_buf_line_rgbir)
        dp.input.extra_bufline = extra_buf_line

        print("idc{} need  {} extra line for memroy round robin {} {}".format(dp.index,
                                                                                       dp.input.extra_bufline,
                                                                                       total_hsize - current_hsize,
                                                                                       dphts))
        if (dp.index % 2):
            memory_max_depth = 2774*4
        else:
            memory_max_depth = 2774*8 if (dp.input.mem_share) else 2774*4

        # strm = inobj.cb_buf[0].strm if(inobj.cben) else   inobj.sensor_buf[dp.input.strmsrc].strm
        dp.input.vsdly_en = strm.vsdly_en
        div_a, div_b, _ = idc_mem_hsize_div_dict[get_dict_key(input_format_dict, strm.format & 0x3f)]
        chn_num = len(strm.vclist)
        if (strm.vsdly_en):
            if (chn_num < 2):
                raise RuntimeError("the channel number is too small {}".format(chn_num))
            if (dp.input.fixen):
                max_buf_line_v2 = int(memory_max_depth / (strm.hsize/div_b + (chn_num-1)*(strm.hsize/div_a)))
                max_buf_line = max_buf_line_v2 << 1
            else:
                max_buf_line_v2 = int((memory_max_depth - (1+dp.input.extra_bufline/2)*(strm.hsize/div_b)) / (chn_num-1)/(strm.hsize/div_a))
                max_buf_line = max_buf_line_v2 << 1
            # dp.input.bufline_max = max_buf_line -2
            dp.input.bufline_max = min(max_buf_line, 127)

            dp.input.rd_start = (dp.input.rd_start if (dp.input.rd_start) else dp.input.bufline_max - extra_buf_line)//2*2
            # rd_start_max = min(dp.input.bufline_max,dp.input.rd_start)
            rd_start_max = dp.input.rd_start
            # rgbir_buf_line = (1 if(dp.rgbiren) else 0)
            rgbir_buf_line = 0
            if (dp.input.vsdly_max > rd_start_max - 2 - rgbir_buf_line):
                raise RuntimeError("the maxvs delay is too large set{} max{}".format(dp.input.vsdly_max, rd_start_max - 2 - rgbir_buf_line))
            if (dp.input.vsdly_max == 0):
                dp.input.vsdly_max = rd_start_max - 2 - rgbir_buf_line
            # rd_start= dp.input.rd_start if(dp.input.rd_start) else dp.input.vsdly_max
            dp.input.vsdly_max = min(dp.input.vsdly_max, strm.vsdly_max)

            actual_dly_line = max(strm.mdly_line, strm.sdly_line, strm.vdly_line)
            if (dp.input.vsdly_max < actual_dly_line):
                raise RuntimeError("the sensor vsldy line is too large set{} max{} during power up".format(actual_dly_line, dp.input.vsdly_max))
            # dp.input.rd_start_max = dp.input.vsdly_max
        else:
            dp.input.vsdly_max = strm.vsdly_max
            # if( dp.input.fixen):
            max_buf_line_v2 = int(memory_max_depth / (chn_num)/(strm.hsize/div_a))
            max_buf_line = max_buf_line_v2 << 1
            # dp.input.bufline_max = max_buf_line -2
            dp.input.bufline_max = min(max_buf_line, 127)
            dp.input.rd_start = dp.input.rd_start if (dp.input.rd_start) else 2

        if (dp.input.rd_start > dp.input.bufline_max - extra_buf_line):
            raise RuntimeError("the maxvs delay is too large set{} max{}".format(dp.input.rd_start, dp.input.bufline_max - extra_buf_line))

        print("IDC{} mode {} ,user don't set max vs ,use auto cal value {} snr max{} bufl max{}".format(dp.index,
                                                                                                                dp.input.fixen,
                                                                                                                dp.input.vsdly_max,
                                                                                                                strm.vsdly_max,
                                                                                                                dp.input.bufline_max))

    def _serdes_timing_check(self, inid, snrcfgs, sdsobj, txport):
        '''
        (HSIZEx+HBLK)*BPx*Tmax/T <= phyclk * lane_num *0.86 * Tmax
        (HSIZEx+HBLK)*BPx*SCLKx/(HTSx*0.9*lane_num) <= rxphyclk
        ∑(HSIZEx+HBLK)*BPx*SCLKx/(HTSx*0.9*lane_num) <= txphyclk
        '''
        totalall = 0
        for snrobj in snrcfgs:
            sigbw = 0
            vcparam = 1
            format_name = get_dict_key(input_format_dict, snrobj.strm.format)
            if len(snrobj.strm.imgdt) == 1 and ('X' in format_name or '+' in format_name):
                if 'X' in format_name:
                    vcparam = int(format_name.split('X')[0])
                elif '+' in format_name:
                    vcparam = 2
#            print("[SDSTCHK] format {}, vcparam {}".format(format_name, vcparam))
            for dtype in snrobj.strm.imgdt:
                hsize = snrobj.strm.hsize
                # vsize = snrobj.strm.vsize
                # fps = snrobj.strm.fps
                pixbit = fmt_bitwidth_dict[dtype[0]] * vcparam
#                total_bit = hsize * vsize * fps * pixbit * 1.27 * vcparam
                total_bit = (hsize+80)*pixbit*snrobj.strm.sclk/(snrobj.strm.hts*0.88)
                sigbw += total_bit
                totalall += total_bit
            if sigbw//snrobj.strm.lane_num > sdsobj.rxport0.max_phyclk:
                raise RuntimeError("in{} snr{} actual phyclk {} out of limitation {}!!".format(inid,
                                                                                               snrobj.index,
                                                                                               sigbw//snrobj.strm.lane_num,
                                                                                               sdsobj.rxport0.max_phyclk))
            else:
                print("[SDSTCHK] in{} snr{} actual phyclk {}".format(inid, snrobj.index, sigbw//snrobj.strm.lane_num))
        phyclk = totalall//txport.lane_num
        if phyclk >= txport.phyclk:
            raise RuntimeError("actual phyclk {}, but request phyclk {}".format(txport.phyclk, phyclk))
        else:
            print("sds{} tx phyclk {}, actual request phyclk {}".format(sdsobj.index, txport.phyclk, phyclk))

    def _chip_init_input(self, cfg, automode=1):
        # print("chip init input start")
        snr_module_count = 0
        clkt = self.oax4k_cfg.sys.clkt
        cclklist = [clkt.snrcclk0, clkt.snrcclk1, clkt.snrcclk2, clkt.snrcclk3]
        cbckllist = [clkt.cb0clk, clkt.cb1clk, clkt.cb2clk, clkt.cb3clk]
        dplist = [self.oax4k_cfg.dp0, self.oax4k_cfg.dp1, self.oax4k_cfg.dp2, self.oax4k_cfg.dp3]

        inlist = [self.oax4k_cfg.in0, self.oax4k_cfg.in1, self.oax4k_cfg.in2, self.oax4k_cfg.in3]
        sccblist = [self.oax4k_cfg.sccb0, self.oax4k_cfg.sccb1]
        sdslist = [self.oax4k_cfg.sds0, self.oax4k_cfg.sds1, self.oax4k_cfg.sds2, self.oax4k_cfg.sds3]
        # sdslist =[self.oax4k_cfg.sds0,self.oax4k_cfg.sds1,self.oax4k_cfg.sds2,self.oax4k_cfg.sds3]
#        snr_dict,sdssets=self._parse_sensor_setting_real(self)  # snr_dict and sdssets are initialized in SNRTOP
        topctrl = self.oax4k_cfg.topctrl
        snr_dict = self.snrtop.get_snrs()
        # snrbuflist =[self.chip.in0.sensor_buf,self.chip.in1.sensor_buf,self.chip.in2.sensor_buf,self.chip.in3.sensor_buf]
        inobjbuf = []
        for inobj in inlist:
            # if inobj.en and not inobj.cben:
            if inobj.en:
                if (inobj.sccb_idx == 0):
                    sccblist[0].en = 1
                elif (inobj.sccb_idx == 1):
                    sccblist[1].en = 1
                sdsobj = sdslist[inobj.sds_index]
                self._cfg_snrs(inobj, sdsobj, snr_dict, cclklist, automode)
                inobjbuf.append(inobj)
                if sdsobj.en:
                    if sdsobj.txports[inobj.sds_txport].en:
                        inobj.lane_num = sdsobj.txports[inobj.sds_txport].lane_num
                        inobj.phyclk = sdsobj.txports[inobj.sds_txport].phyclk
                        inobj.sclk = inobj.sensor_buf[0].strm.sclk
                        if inobj.sensor_num > sdsobj.txports[inobj.sds_txport]._strm_num:
                            raise RuntimeError("in{} strm num {}, but sds{} txport{} strm num {} !!".format(inobj.index,
                                                                                                            inobj.sensor_num,
                                                                                                            sdsobj.index,
                                                                                                            inobj.sds_txport,
                                                                                                            sdsobj.txports[inobj.sds_txport]._strm_num))
                        else:
                            sdsobj.txports[inobj.sds_txport]._strm_num = inobj.sensor_num
                        if self.oax4k_cfg.topctrl.byp_sdschk == 0:
                            self._serdes_timing_check(inobj.index, inobj.sensor_buf, sdsobj, sdsobj.txports[inobj.sds_txport])
                    else:
                        raise RuntimeError("sds {} txport {} not enable !!".format(inobj.sds_index, inobj.sds_txport))
                else:
                    inobj.lane_num = inobj.sensor_buf[0].strm.lane_num
                    inobj.phyclk = inobj.sensor_buf[0].strm.phyclk
                    inobj.sclk = inobj.sensor_buf[0].strm.sclk
        for dpobj in dplist:
            # if(dpobj.en):
            for inobj in inlist:
                if (inobj.en and dpobj.en):
                    if (dpobj.input.portsrc == inobj.index):
                        vclist_new = []
                        autosnrcfg = inobj.sensor_buf[dpobj.input.strmsrc]
                        inobj.phyclk = autosnrcfg.strm.phyclk
                        if inobj.sds_en and dpobj.input.idcen:
                            sdsobj = sdslist[inobj.sds_index]
                            sdstxport = sdsobj.txports[inobj.sds_txport]
                            serobj = sdsobj.rxports[dpobj.input.sersrc]
                            serobj.vcmap[0] = dpobj.input.sersrc  # jean workaround
                            vclist_new = [serobj.vcmap[vc] for vc in autosnrcfg.strm.vclist]
                            print("[DEBUG] in{} snr{} vclist {} map to {}".format(inobj.index, dpobj.input.strmsrc, autosnrcfg.strm.vclist, vclist_new))
                            autosnrcfg.strm.vclist = vclist_new
                            autosnrcfg.embl.pre.emb_vcid = autosnrcfg.embl.pre.emb_vcid + autosnrcfg.strm.vclist[0]
                            autosnrcfg.embl.post.emb_vcid = autosnrcfg.embl.post.emb_vcid + autosnrcfg.strm.vclist[0]
                            autosnrcfg.embl.sta.chn_vc = [chn + autosnrcfg.strm.vclist[0] for chn in autosnrcfg.embl.sta.chn_vc]
                            inobj.phyclk = sdstxport.phyclk
                            autosnrcfg.sccb.index = serobj._sccb_idx
                            # if autosnrcfg.strm.phyclk <= serobj.max_phyclk:
                            #    # autosnrcfg.strm.phyclk = sdstxport.phyclk
                            #    pass
                            # else:
                            #    raise RuntimeError("snr phyclk {} out of serializer limitation {} !!".format(autosnrcfg.strm.phyclk, serobj.max_phyclk))

                            # if autosnrcfg.strm.lane_num==serobj.lane_num:
                            #    autosnrcfg.strm.lane_num = sdstxport.lane_num
                            # else:
                            #    raise RuntimeError("snr{} lane num {} do not match sds{} ser{} lane num {} !!".format(dpobj.input.snrsrc, autosnrcfg.strm.lane_num, inobj.sds_index, dpobj.input.sersrc, serobj.lane_num))
                        if (inobj.cben):
                            if (topctrl.cb_copy_snr):
                                input_lane_num = autosnrcfg.strm.lane_num
                            else:
                                input_lane_num = inobj.cb_buf[0].strm.lane_num
                            dpobj.input.sclk = cbckllist[inobj.index]
                            inobj.sclk = dpobj.input.sclk
                            inobj.phyclk = inobj.sclk * 16
                        else:
                            # dpobj.input.sclk = int(autosnrcfg.strm.sclk*cclklist[autosnrcfg.ctrl.cclk_id] /24000000)
                            dpobj.input.sclk = autosnrcfg.strm.sclk
                            inobj.sclk = dpobj.input.sclk
                            # inobj.phyclk = autosnrcfg.strm.phyclk
                            input_lane_num = autosnrcfg.strm.lane_num
                            fps = inobj.sclk / (autosnrcfg.strm.hts * autosnrcfg.strm.vts)
                            format_type = get_dict_key(sensor_input_format_type_dict, autosnrcfg.strm.format_tid)
                            format_name = get_dict_key(input_format_dict, autosnrcfg.strm.format)
                            embl_info = [autosnrcfg.embl.pre.num, autosnrcfg.embl.post.num, autosnrcfg.embl.sta.num]
                            embl_vldbyte_info = [autosnrcfg.embl.pre.len, autosnrcfg.embl.post.len, autosnrcfg.embl.sta.valid_byte]
                            print("dp{} input sclk {} ,phyclk {},cclk {}".format(dpobj.index, dpobj.input.sclk, autosnrcfg.strm.phyclk, autosnrcfg.strm.cclk))
                            print("fmttype {} format_name {} ,hsize {},vsize {},hts {},vts {}, pvb {} lane{} fps {} vc {} dt {} embl {} {} mode {}".format(
                                format_type,
                                format_name,
                                autosnrcfg.strm.hsize,
                                autosnrcfg.strm.vsize,
                                autosnrcfg.strm.hts,
                                autosnrcfg.strm.vts,
                                autosnrcfg.strm.preblank,
                                autosnrcfg.strm.lane_num,
                                int(fps),
                                autosnrcfg.strm.vclist,
                                autosnrcfg.strm.imgdt,
                                embl_info,
                                embl_vldbyte_info,
                                autosnrcfg.embl.linemode))
                        # if(inobj.sd)
                        sccb = sccblist[inobj.sccb_idx]
                        # serdes =sdslist[inobj.serdes_idx]
                        sccb.sds_en = 1 if (inobj.sensor_num > 1 or inobj.sds_en) else 0
                        sccb.sds_en = inobj.sds_en  # CHIPNEW,TBD
                        sccb.sds_idx = inobj.sds_index
                        if (not dpobj.bypisp and not (self.oax4k_cfg.topctrl.algo_disable & (1 << dpobj.index))):
                            sccb.sendbuf.append(autosnrcfg.sccb.sendbyte)
                        inobj.sccbbuf.append(sccb)
                        inobj.lane_num = input_lane_num
                        dpobj.dibuf.append(inobj)

                        if (topctrl.cb_copy_snr):
                            # inobj.cb_buf=[]
                            cbcfg = inobj.cb_buf[0]
                            # cbcfg.en =1
                            cbcfg.strm = copy.deepcopy(autosnrcfg.strm)
                            cbcfg.embl = copy.deepcopy(autosnrcfg.embl)
                            snrsclk = cbcfg.strm.sclk
                            snrhts = cbcfg.strm.hts
                            cbcfg.strm.sclk = cbckllist[inobj.index] * input_lane_num
                            cbcfg.strm.hts = cbcfg.strm.hts * cbcfg.strm.sclk / snrsclk
                            cbcfg.strm.imgid = cbcfg.strm.imgdt
                            cbcfg.strm.vcnum, tmpimid, cbcfg.strm.vclist, _, cbcfg.strm.expnum = precb_format_vcdt_dict[get_dict_key(input_format_dict,
                                                                                                                                     cbcfg.strm.format)]
                            cbcfg.strm.embid = [[0x14] for item in tmpimid] if cbcfg.embl.en else [[] for item in tmpimid]
                            cbcfg.embl.linemode = 0
                            # print("new cb cp snr",snrsclk,snrhts,cbcfg.strm.sclk,cbcfg.strm.hts)

                            cbcfg.strm.fps = cbcfg.strm.sclk / cbcfg.strm.hts / cbcfg.strm.vts
                            format_type = get_dict_key(sensor_input_format_type_dict, cbcfg.strm.format_tid)
                            format_name = get_dict_key(input_format_dict, cbcfg.strm.format)
                            # printk(cbcfg.strm.vcnum,cbcfg.strm.vclist,cbcfg.strm.imgid,cbcfg.strm.embid )
                            if (inobj.cben):
                                print("fmttype {} format_name {} ,hsize {},vsize {},hts {},vts {}, pvb {} lane{} fps {} vc {} id{} dt {} sclk{}".format(
                                    format_type,
                                    format_name,
                                    cbcfg.strm.hsize,
                                    cbcfg.strm.vsize,
                                    cbcfg.strm.hts,
                                    cbcfg.strm.vts,
                                    cbcfg.strm.preblank,
                                    cbcfg.strm.lane_num,
                                    int(cbcfg.strm.fps),
                                    cbcfg.strm.vclist,
                                    cbcfg.strm.imgid,
                                    cbcfg.strm.imgdt,
                                    cbcfg.strm.sclk))
                        else:
                            cbcfg = inobj.cb_buf[0]
                            cbcfg.strm.vcnum, tmpimid, cbcfg.strm.vclist, _, cbcfg.strm.expnum = precb_format_vcdt_dict[get_dict_key(input_format_dict, cbcfg.strm.format)]
                            cbcfg.strm.imgid = [[id] for id in tmpimid]
                            cbcfg.strm.imgdt = cbcfg.strm.imgid
                            cbcfg.strm.embid = [[0x14] for item in tmpimid] if cbcfg.embl.en else [[] for item in tmpimid]
                            cbcfg.strm.sclk = cbckllist[inobj.index] * input_lane_num
                            cbcfg.strm.fps = cbcfg.strm.sclk / cbcfg.strm.hts / cbcfg.strm.vts
                            cbcfg.embl.linemode = 0
                        dpobj.input.seibuf.append(inobj.cb_buf[0].embl if (inobj.cben) else autosnrcfg.embl)
        self._setting_add_header(cfg)
        # print(self.oax4k_cfg.in0.sensor_buf[0].strm.phyclk)

    def _setting_add_header(self, cfg):
        dplist = [self.oax4k_cfg.dp0, self.oax4k_cfg.dp1, self.oax4k_cfg.dp2, self.oax4k_cfg.dp3]
        inlist = [self.oax4k_cfg.in0, self.oax4k_cfg.in1, self.oax4k_cfg.in2, self.oax4k_cfg.in3]
        sdslist = [self.oax4k_cfg.sds0, self.oax4k_cfg.sds1, self.oax4k_cfg.sds2, self.oax4k_cfg.sds3]
        sensorlist = self.snrtop.get_snrs()
        for dpobj in dplist:
            if dpobj.en and dpobj.input.idcen:
                inobj = inlist[dpobj.input.portsrc]
                sdsobj = sdslist[inobj.sds_index]
                if (not inobj.cben):
                    sensoridx = inobj.sensor_buf[dpobj.input.strmsrc].set_index
                    sensorobj = sensorlist[sensoridx]
                    if (dpobj.input.loaden):
                        sensorobj.ppl_bitmap |= 0x01 << dpobj.input.snrsrc
                    print("[DEBUG] sensor{} bcen {} sccb idx {} ppl 0x{:x}".format(sensoridx, sensorobj.broadcast_en, sensorobj.snr_sccb_idx, sensorobj.ppl_bitmap))

    def _chip_init_rgbir(self, cfg):
        # print("chip init rgbir")
        if (self.oax4k_cfg.rgbir.en):
            dplist = [self.oax4k_cfg.dp0, self.oax4k_cfg.dp1, self.oax4k_cfg.dp2, self.oax4k_cfg.dp3]
            inlist = [self.oax4k_cfg.in0, self.oax4k_cfg.in1, self.oax4k_cfg.in2, self.oax4k_cfg.in3]
            rgbir = self.oax4k_cfg.rgbir
            rgbin0 = dplist[0]
            rgbin01 = dplist[1]
            rgbin1 = dplist[2]
            rgbin11 = dplist[3]

            chnlist = rgbir.chnlist
            chncnt = 0

            if (rgbin0.en and rgbin0.rgbiren):
                if (rgbin0.index):
                    raise RuntimeError("RGBIR0 enable path mismatch {}".format(rgbin0.index))
                intmp = rgbin0.dibuf[0]
                rgbir.ins.append(intmp)
                rgbir.dp0.chnbase = chncnt
                rgbin0.rgbirsrc = chncnt
                rgbin01.rgbirsrc = chncnt
                in0strm = intmp.cb_buf[0].strm if (intmp.cben) else intmp.sensor_buf[rgbin0.input.strmsrc].strm
                chncnt = in0strm.vcnum
                if (chncnt < 3):
                    chncnt = 2  # tbd
                    rgbir.dp0.v3_sel = 0
                    rgbir.dp0.v4_sel = 0
                elif (chncnt < 4):
                    rgbir.dp0.v4_sel = 0
                    rgbir.dp0.v3_sel = 1
                else:
                    rgbir.dp0.v3_sel = 0
                    rgbir.dp0.v4_sel = 1

                for i in range(in0strm.vcnum):
                    chnlist[i].inbuf.append(in0strm)
                    chnlist[i].en = 1
                    chnlist[i].ctrlbuf.append(rgbir.dp0)

                idpraw0 = copy.deepcopy(in0strm)
                idpir0 = copy.deepcopy(in0strm)
                idpraw0.hsize = in0strm.hsize
                idpraw0.vsize = in0strm.vsize
                idpraw0.vts = (in0strm.vts << 1) if (rgbir.dp0.raw.abmode) else in0strm.vts
                idpir0.vts = (in0strm.vts << 1) if (rgbir.dp0.ir.abmode) else in0strm.vts
                # print("!!!!!!!!!!!!!!!!!!!!!!!!",rgbir.dp0.raw.abmode)
                if (rgbir.dp0.raw.abmode):
                    idpraw0.fps = idpraw0.fps / 2
                if (rgbir.dp0.ir.abmode):
                    idpir0.fps = idpir0.fps / 2
                idpir0.hsize = (in0strm.hsize >> 1) if (rgbir.dp0.irexen) else in0strm.hsize
                idpir0.vsize = (in0strm.vsize >> 1) if (rgbir.dp0.irexen) else in0strm.vsize
                print("rgbir dp0 hsize {} vsize {} vcnum {} chncnt{} v3_sel{} chnbase{}".format(in0strm.hsize,
                                                                                                        in0strm.vsize,
                                                                                                        in0strm.vcnum,
                                                                                                        chncnt,
                                                                                                        rgbir.dp0.v3_sel,
                                                                                                        rgbir.dp0.chnbase))
            chncnt2 = 0
            if (rgbin1.en and rgbin1.rgbiren):
                rgbir.dp1.v3_sel = 0
                rgbir.dp1.v4_sel = 0
                if (chncnt == 0):
                    raise RuntimeError("RGB pipe should start from DP0")
                if (rgbin1.index != 2):
                    raise RuntimeError("RGBIR1 enable path mismatch {}".format(rgbin1.index))
                if (rgbir.dp0.v4_sel):
                    raise RuntimeError("RGBIR1 4 channel enable,not enough chn for input {}".format(rgbin1.index))

                intmp = rgbin1.dibuf[0]
                rgbir.ins.append(intmp)
                in1strm = intmp.cb_buf[0].strm if (intmp.cben) else intmp.sensor_buf[rgbin1.input.strmsrc].strm  # tbd
                rgbir.dp1.chnbase = chncnt
                rgbin1.rgbirsrc = chncnt
                rgbin11.rgbirsrc = chncnt
                # print(in1strm.hsize,in1strm.vsize,in1strm.vcnum,chncnt2,chncnt,rgbir.dp0.v3_sel,"rgbtttt")
                print("rgbir dp1 hsize {} vsize {} vcnum {} chncnt{}  v3_sel{} chnbase{}".format(in1strm.hsize,
                                                                                                         in1strm.vsize,
                                                                                                         in1strm.vcnum,
                                                                                                         chncnt,
                                                                                                         rgbir.dp0.v3_sel,
                                                                                                         rgbir.dp1.chnbase))
                if (chncnt + in1strm.vcnum > 4):
                    raise RuntimeError("RGB pipe can't large than 4,please check")
                for i in range(in1strm.vcnum):
                    chnlist[chncnt+i].inbuf.append(in1strm)
                    # chnlist[chncnt+i].rawout.hsize=(in1strm.hsize>>1) if( chnlist[chncnt+i].rawout.binning) else in1strm.hsize
                    # chnlist[chncnt+i].rawout.vsize=(in1strm.vsize>>1) if( chnlist[chncnt+i].rawout.binning) else in1strm.vsize
                    # chnlist[chncnt+i].rawout.hsize= in1strm.hsize
                    # chnlist[chncnt+i].rawout.vsize= in1strm.vsize
                    # chnlist[chncnt+i].irout.hsize=(in1strm.hsize>>1) if(rgbir.dp1.irexen) else in1strm.hsize
                    # chnlist[chncnt+i].irout.vsize=(in1strm.vsize>>1) if(rgbir.dp1.irexen) else in1strm.vsize
                    chnlist[chncnt+i].en = 1
                    chnlist[chncnt+i].ctrlbuf.append(rgbir.dp1)
                    chncnt2 = chncnt2 + 1
                idpraw1 = copy.deepcopy(in1strm)
                idpir1 = copy.deepcopy(in1strm)
                # if(rgbir.dp1.v3_sel):
                #     idpraw1.hsize =chnlist[3].rawout.hsize
                #     idpraw1.vsize =chnlist[3].rawout.vsize
                #     idpir1.hsize  =chnlist[3].irout.hsize
                #     idpir1.vsize  =chnlist[3].irout.vsize

                # else:
                #     idpraw1.hsize =chnlist[2].rawout.hsize
                #     idpraw1.vsize =chnlist[2].rawout.vsize
                #     idpir1.hsize  =chnlist[2].irout.hsize
                #     idpir1.vsize  =chnlist[2].irout.vsize
            # print( idp.raw1.hsize, idp.ir1.hsize)
                idpraw1.hsize = in1strm.hsize
                idpraw1.vsize = in1strm.vsize
                idpraw1.vts = (in1strm.vts << 1) if (rgbir.dp1.raw.abmode) else in1strm.vts
                idpir1.vts = (in1strm.vts << 1) if (rgbir.dp1.ir.abmode) else in1strm.vts
                if (rgbir.dp1.raw.abmode):
                    idpraw1.fps = idpraw1.fps / 2
                if (rgbir.dp1.ir.abmode):
                    idpir1.fps = idpir1.fps / 2
                idpir1.hsize = (in1strm.hsize >> 1) if (rgbir.dp1.irexen) else in1strm.hsize
                idpir1.vsize = (in1strm.vsize >> 1) if (rgbir.dp1.irexen) else in1strm.vsize
            if (chncnt + chncnt2 > 4):
                raise RuntimeError("RGB pipe can't large than 4,please check")

            if (chncnt or chncnt2):
                if (chncnt):
                    rgbir.outs.append((0, idpraw0))
                    rgbir.outs.append((1, idpir0))
                if (chncnt2):
                    rgbir.outs.append((2, idpraw1))
                    rgbir.outs.append((3, idpir1))
        # print(rgbir.outs)

    def varlist_diff_check(self, obj, pre, post):
        for (var, val) in post:
            if (var, val) in pre:
                ignore_list = ["snrgrphd_idx",
                               "snrstrobe_en",
                               "manual_mode",
                               "strobe_max",
                               "strobe_min",
                               "strobe_width",
                               "tnegative",
                               "sequence_group_idx",
                               "sequence_setting_en",
                               "cb_copy_snr_vld"]  # tbd, need check!!!
                if (var not in ignore_list and "rsvd" not in var):
                    print("{} parameter {} <--> {} don't init ,please check".format(obj.__class__, var, val))

    def varlist_intl_check(self, obj, pre, post):
        usrparas = [var for (var, val) in pre]
        for (var, val) in post:
            if (var not in usrparas):
                print("{} parameter {} <--> {} internal use ,please check".format(obj.__class__, var, val))

    def _fw_dp_init_rgbir(self, fw, hw, rgbircfg):
        fw.ctrl = 0  # CHIPNEW, TBD
        fw.en = hw.rgbiren
        fw.module_id = hw.rgbirsrc
        pass

    def _fw_dp_init_embl_new(self, fwembl, out):
        hwembl = out.embl
        fwembl.ctrl = hwembl.en  # for test tbd
        fwembl.module_id = out.index  # tbd
        fwembl.chn = hwembl.chn
        fwembl.txport = out.yuv.outport if (hwembl.chn) else out.rawmv.outport
        fwembl.txchn = out.yuv.outchn if (hwembl.chn) else out.rawmv.outchn
        fwembl.sei_pre_num = hwembl.seipre.outnum  # tbd ,check in or out
        fwembl.sei_pre_validbyte = hwembl.seipre.vldbyte  # tbd ,check in or out
        fwembl.sei_post_num = hwembl.seipost.outnum  # tbd
        fwembl.sei_post_validbyte = hwembl.seipost.vldbyte  # tbd ,check in or out
        fwembl.sta_num = hwembl.sta.outnum
        fwembl.sta_validbyte0 = hwembl.sta.valid_byte0
        fwembl.sta_validbyte1 = hwembl.sta.valid_byte1
        fwembl.sta_validbyte2 = hwembl.sta.valid_byte2
        fwembl.sta_validbyte3 = hwembl.sta.valid_byte3

        fwembl.ovipre.chain = [(hwembl.ovipre.chnaddr_list[i], hwembl.ovipre.chnlen_list[i]) for i in range(len(hwembl.ovipre.chnaddr_list))]
        if (len(hwembl.ovipre.chain_list)):
            fwembl.ovipre.chain = hwembl.ovipre.chain_list
        # print( fwembl.ovipre.chain,"kkkkkkkkkkkkkkkkkkkkkkk")
        fwembl.ovipost.chain = [(hwembl.ovipost.chnaddr_list[i], hwembl.ovipost.chnlen_list[i]) for i in range(len(hwembl.ovipost.chnaddr_list))]
        if (len(hwembl.ovipost.chain_list)):
            fwembl.ovipost.chain = hwembl.ovipost.chain_list
        fwembl.ovipre.chain_cnt = len(fwembl.ovipre.chain)
        ovipre_chnlen_list = [lent for addr, lent in fwembl.ovipre.chain]
        fwembl.ovipre.validlen = max(int_inc(sum(ovipre_chnlen_list), 4), 32)
        fwembl.ovipre.output_num = hwembl.ovipre.outnum
        ovipost_chnlen_list = [lent for addr,lent in fwembl.ovipost.chain]
        fwembl.ovipost.validlen = max(int_inc(sum(ovipost_chnlen_list), 4), 32)
        fwembl.ovipost.output_num = hwembl.ovipost.outnum
        fwembl.ovipost.chain_cnt = len(fwembl.ovipost.chain)

    def _fw_dp_init_ppln(self, fw, hw):
        ppln = fw.ppln
        hwisp = hw.isp
        dpin = hw.input
        hwin = hw.dibuf[0]
        hwout = hw.dobuf[0]

        ppln_pre_vvs = get_class_var(ppln)

        ppln.strm_src = 1 if (hwin.cben) else (4 if (dpin.shadow) else 0)
        ppln.sclk = dpin.sclk
        ppln.strm_mdl_id = dpin.snrsrc
        ppln.strm_upload_en = dpin.loaden
        ppln.fullfrm_en = dpin.fullfrm_en
        ppln.fullfrm_cnt = dpin.frmnum_gate
        ppln.lanenum = hwin.lane_num
        if hwin.cben == 0:
            imgin = hwin.sensor_buf[0]
            if imgin.embl.en or imgin.embl.linemode:
                ppln.cb_copy_snr_vld = 0
            else:
                ppln.cb_copy_snr_vld = 1
#            print("[CBDEBUG] cben {}, embl en {}, line mode {} !".format(hwin.cben, imgin.embl.en, imgin.embl.linemode))
        else:
            ppln.cb_copy_snr_vld = 0

        # added by CurrenXiao for rgbir 2020/9/15
        # print("[RGBIR_MODE]:rgbir src:{}, rgbir_en:{}, update_en:{}".format(hw.rgbirsrc, hw.rgbiren,hw.rgbir_updateen))
        if (not hw.rgbiren):
            hw.rgbirsrc = 0
        ppln.rgbir_mode = ((hw.rgbirsrc & 0x3) << 4) | (hw.rgbiren << 3) | (hw.rgbir_updateen & 0x01)  # [7:4]: rgbir channel index[0/1/2/3]
        #                                                                                                  [3]: rgbir enable;
        #                                                                                                  [0]: update enable
        # endadd CurrenXiao 2020/9/15
        # ppln.embl_src =hwout.index # tbd
        ppln.vsdly_max = dpin.vsdly_max - 1 if (dpin.vsdly_max) else 0  # tbd
        ppln.vsdly_step = dpin.vsdly_step # tbd

        ppln.mrxport = dpin.portsrc
        ppln.idcport = hw.index//2*2 if (hw.rgbiren) else hw.index
        ppln.ispport = hw.index
        ppln.rtport = hwout.index

        ppln.ispyuv.outhsize = hwisp.yuvout.hsize
        ppln.ispyuv.outvsize = hwisp.yuvout.vsize
        ppln.ispyuv.hts = hwisp.yuvout.hts
        ppln.ispyuv.vts = hwisp.yuvout.vts
        ppln.ispyuv.en = 1
        ppln.ispraw.outhsize = hwisp.rawout.hsize
        ppln.ispraw.outvsize = hwisp.rawout.vsize
        ppln.ispraw.hts = hwisp.rawout.hts
        ppln.ispraw.vts = hwisp.rawout.vts
        ppln.ispraw.en = 1

        ppln.ispmv.outhsize = hwisp.mvout.hsize
        ppln.ispmv.outvsize = hwisp.mvout.vsize
        ppln.ispmv.hts = hwisp.mvout.hts
        ppln.ispmv.vts = hwisp.mvout.vts
        ppln.ispmv.en = 1

        ppln.outyuv.en = hwout.yuv.en  # CHIPNEW,2020/10/30
        ppln.outyuv.src = hwout.yuv.sel
        ppln.outyuv.outfmt = hwout.yuv.format
        ppln.outyuv.outport = hwout.yuv.outport
        ppln.outyuv.outvc = hwout.yuv.outvc
        ppln.outyuv.outchn = hwout.yuv.outchn

        ppln.outraw.en = hwout.rawmv.en
        ppln.outraw.src = hwout.rawmv.sel
        ppln.outraw.outfmt = hwout.rawmv.format
        ppln.outraw.outport = hwout.rawmv.outport
        ppln.outraw.outvc = hwout.rawmv.outvc
        ppln.outraw.outchn = hwout.rawmv.outchn
        ppln.scalecrop.scalen = hwisp.yuvout.scale.en
        ppln.scalecrop.sohsize = hwisp.yuvout.scale.hsize
        ppln.scalecrop.sovsize = hwisp.yuvout.scale.vsize

        ppln.scalecrop.scaleprecropen = hwisp.yuvout.scale.precropen
        ppln.scalecrop.scaleprecrop_hsize = hwisp.yuvout.scale.precrop_hsize
        ppln.scalecrop.scaleprecrop_vsize = hwisp.yuvout.scale.precrop_vsize
        ppln.scalecrop.scalepostcropen = hwisp.yuvout.scale.postcropen
        ppln.scalecrop.scalepostcrop_hsize = hwisp.yuvout.scale.postcrop_hsize
        ppln.scalecrop.scalepostcrop_vsize = hwisp.yuvout.scale.postcrop_vsize

        print('isp scale en {}, ohsize {}, ovsize {}'.format(ppln.scalecrop.scalen, ppln.scalecrop.sohsize, ppln.scalecrop.sovsize))
        print('isp scale pre crop en {}, pre crop hsize {}, pre crop vsize {}'.format(ppln.scalecrop.scaleprecropen,
                                                                                      ppln.scalecrop.scaleprecrop_hsize,
                                                                                      ppln.scalecrop.scaleprecrop_vsize))
        print('isp scale post crop en {}, post crop hsize {}, post crop vsize {}'.format(ppln.scalecrop.scalepostcropen,
                                                                                         ppln.scalecrop.scalepostcrop_hsize,
                                                                                         ppln.scalecrop.scalepostcrop_vsize))

        ppln.scalecrop.cropen = hwisp.yuvout.cropen
        ppln.scalecrop.cohsize = hwisp.yuvout.hsize
        ppln.scalecrop.covsize = hwisp.yuvout.vsize
        print('isp windowing en {}, ohsize {}, ovsize {}'.format(ppln.scalecrop.cropen, ppln.scalecrop.cohsize, ppln.scalecrop.covsize))

        ppln_post_vvs = get_class_var(ppln)
        self.varlist_diff_check(ppln, ppln_pre_vvs, ppln_post_vvs)

    def _fw_dp_init(self, fw, hw, do):
        self._fw_dp_init_ppln(fw, hw)
        # ppln_post_vvs = get_class_var(fw.ppln)
        # self.varlist_diff_check(fw.ppln, ppln_pre_vvs, ppln_post_vvs)
        pass

    def _fw_sccb_init(self, fw, hw):
        fw.speed = hw.speed
        fw.ctrl = hw.en  # tbd,for debug only
        fw.timeout = hw.timeout  # tbd
        fw.sds_en = hw.sds_en
        fw.sds_idx = hw.sds_idx
        fw.num = hw.index

    def _chip_init_sys(self, cfg):
        sys = self.oax4k_cfg.sys
        clkt = sys.clkt
        pll = sys.pll
        clkclasslist = [clkt, pll]

        for i in range(len(clkclasslist)):
            varlist = get_class_var(clkclasslist[i])
            for item, val in varlist:
                newval = CHIPCFG.clkfreq_autoconvt(val)
                setattr(clkclasslist[i], item, newval)

        ctrl = sys.ctrl

        # if (ctrl.cpu2xbus):
        #     sys.clkt.busclk = int(sys.clkt.sysclk/2)

        pad = sys.pad
        #pad.gpio_num = 26
        varlist = get_class_var(pad,level=1)
        padlist = []
        # for io in varlist:
        #     if (isinstance(io, str)):
        #         print("kkkkkkk")
        #         if (not isinstance(getattr(pad,io), list)):
        #             padio = getattr(pad, io)
        #             padio.output_oen = 0
        #         else:
        #             padlist.append(io)
        padlist = get_class_list(pad)
        objlist_varcfg= get_class_listvar_new(pad, padlist, chip_obj_dict)
        for i in range(16):
            pad.peri_buf[i].output_oen = 0
        pad.peri_buf[16].output_oen = 0  # TXD
        pad.peri_buf[17].input_en = 1  # TXD

        pad.peri_buf[24].input_en = 1  # SCCB ID
        pad.peri_buf[25].input_en = 1  # SCCB ID 1
        pad.peri_buf[31].input_en = 1  # SCCB ID 1

        for i in range(pad.gpio_num):
            pad.gpio_buf[i].input_en = 0
        pad.gpio_buf[17].input_en = 1
        pad.gpio_buf[18].input_en = 1
        pad.gpio_buf[17].output_oen = 0
        pad.gpio_buf[18].output_oen = 0
        pad.gpio_buf[0].output_oen = 0  # SCCB ID 1

        if (self.chiptype >= 2):
            pll = sys.pll

            if (pll.tx0_clk0 == 0 or pll.tx0_clk1 == 0):
                pll.tx0_clk0 = sys.clkt.do0clk * 4
                # pll.tx0_clk1= sys.clkt.do0clk*16
                if (pll.tx0_clk0 > 500000000):
                    pll.tx0_clk0 = pll.tx0_clk0 >> 1
                if (pll.tx0_clk1 == 0):
                    pll.tx0_clk1 = pll.tx0_clk0

            if (pll.tx1_clk0 == 0 or pll.tx1_clk1 == 0):
                pll.tx1_clk0 = sys.clkt.do1clk * 4
                if (pll.tx1_clk0 > 500000000):
                    pll.tx1_clk0 = pll.tx1_clk0 >> 1
                if ( pll.tx1_clk1 == 0):
                    pll.tx1_clk1 = pll.tx1_clk0

    def _parse_chipcfg_xml(self):
        self.listbuf = []
        self._parse_object_var(self.oax4k_cfg, self.oax4k_dup, printen=0)
        # print(self.listbuf)
        self._parse_object_list(printen=0)

    def _parse_object_list(self, spilter='-', printen=0):
        for prefix, obj, item in self.listbuf:
            if (item.endswith("_list")):
                # print(prefix+item+'!!!')
                itemname = item.split("_list")[0]
                # print(itemname,item)
                item_num = itemname + "_num"
                if (len(prefix.split(spilter)) >= 3):
                    tag3spilter = "_"
                    newprefix = prefix + tag3spilter + itemname.upper()
                else:
                    newprefix = prefix + spilter + itemname.upper()
                # print(newprefix)
                buftmp = []
                for i in range(getattr(obj, item_num)):
                    found, val = self.update(newprefix + str(i))
                    self.oax4k_chipvar_dict[newprefix + str(i)] = (val, 0)
                    if found:
                        buftmp.append(val)
                if (buftmp != []):
                    # if (printen):
                    #     print(newprefix, buftmp)
                    setattr(obj, item, buftmp)
            elif (item.endswith("_buf")):
                itemname = item.split("_buf")[0]
                item_num = itemname + "_num"
                item_cfg = itemname.upper() + "_CFG"
                if (len(prefix.split(spilter)) >= 3):
                    tmpspilter = "_"
                else:
                    tmpspilter = "-"
                newprefix = prefix + tmpspilter + itemname.upper()

                #self._get_char_attr(obj, item_num)
                buftmp = []
                buforg=getattr(obj, item)
                if (hasattr(obj, "index")):
                    superidx = getattr(obj, "index")
                else:
                    superidx = 0
                # print("[VAL_CFG]", itemname, superidx)
                if (hasattr(obj,item_num)):
                    objnum = getattr(obj, item_num)
                else:
                    objnum = 1
                for i in range(objnum):
                    tmpobj = chip_obj_dict[item_cfg](i, superidx)
                    # tmpobj.index=i
                    if (i < len(buforg)):
                        #print("@@@@{} {} {} @@@".format(i,newprefix+str(i),item_cfg))
                        self._parse_object_var(buforg[i], tmpobj, newprefix + str(i), spilter, printen)
                        buftmp.append(buforg[i])
                    else:
                        self._parse_object_var(tmpobj, tmpobj, newprefix + str(i), spilter, printen)
                        buftmp.append(tmpobj)
                if (buftmp != []):
                    # print(newprefix, buftmp)
                    setattr(obj, item, buftmp)

    def _parse_object_var(self, obj, dupobj, prefix="", spilter='-', printen=0):
        objlist = dir(obj)
        objlistdup = dir(dupobj)
        for item in objlist:
            obj_attr = getattr(obj, item)
            if not callable(obj_attr) and not item.startswith("__") :
                if(isinstance(obj_attr, list)):
                    self.listbuf.append((prefix, obj, item))
                elif isinstance(obj_attr, dict):
                    if(len(prefix.split(spilter)) >= 3):
                        spilter = "_"
                    newchar = prefix + spilter + item.upper()
                    deftval = getattr(obj, item)
                    dupdeftval = getattr(dupobj, item)
                    found, val = self.update(newchar, type(obj_attr))
                    if found:
                        setattr(obj, item, val)
                    newval = getattr(obj, item)
                    self.oax4k_chipvar_dict[newchar] = (newval, deftval)
                    if (printen):
                        if(deftval != newval):
                            print("{} {}->{}".format(newchar, dupdeftval, newval))
                elif (isinstance(obj_attr, int)):
                    if (len(prefix.split(spilter)) >= 3):
                        spilter = "_"
                    newchar = prefix + spilter + item.upper()
                    deftval = getattr(obj, item)
                    dupdeftval = getattr(dupobj, item)
                    found, val = self.update(newchar)
                    if found:
                        setattr(obj, item, val)
                    newval = getattr(obj, item)
                    self.oax4k_chipvar_dict[newchar] = (newval, deftval)
                    if(printen):
                        if(deftval != newval):
                            print("{} {}->{}".format(newchar, dupdeftval, newval))
                else:
                    if(prefix == ""):
                        newprefix = item.upper()
                    else:
                        newprefix = prefix + spilter + item.upper()
                    #print("item {} is class {}".format(item, obj_attr))
                    self._parse_object_var(obj_attr, getattr(dupobj, item), newprefix, spilter, printen)


class OAX4K(object):
    def __init__(self, cfg):
        self.setbuf = []
        self.fsetbuf0 = []
        self.fsetbuf1 = []
        self.mdobj = []
        self.chipcfg = CHIPCFG(cfg)
#        self.outfile = cfg.outfile
        self.houtfile = cfg.houtfile
        self.foutfile0 = cfg.foutfile0
        self.fsds_files = cfg.fsds_files
#        self.strmon_files = cfg.strmon_files
        dirname = os.path.dirname(self.houtfile)
        outfilename = os.path.basename(self.houtfile)
        self.casecfg = cfg
        #print(dirname,outfilename)
        cfgname = outfilename.split('.')[0] + 'CFGINFO' + '.txt'
        self.cfginfo = Path(dirname).joinpath(cfgname)
        # print("OAX4K gen fwtop")
        #self.GENOBJ(FWTOP)
        # print("OAX4K gen snrtop")
        self.mdobj.append(self.chipcfg.snrtop)
        # self.GENOBJ(SNRTOP)
        # print("OAX4K gen systop")
        self.GENOBJ(SYSTOP)
        # print("OAX4K gen dptop")
        self.GENOBJ(DPTOP)
        # print("OAX4K gen strmtop")
        self.GENOBJ(STRMTOP)
        pass


    # @classmethod
    def GENOBJ(self, obj, setid=0):
        # print(obj)
        mdl = obj(self.chipcfg)
        self.mdobj.append(mdl)
        pass


    def start(self):
        # print("oax4k start")
        for i in range(len(self.mdobj)):
            self.mdobj[i].start()
            # print("[{:s}] start !".format(self.mdobj[i].__class__.__name__))


    #def save(self):
    #    for i in range(len(self.mdobj)):
    #        self.setbuf.append(self.mdobj[i].save())
    #    self.save_setting(self.outfile,self.setbuf)
    def reg_save(self, mode):
        robjbuf = [reg for addr, reg in self.chipcfg.regtable.items()]
        setbuf = []
        for i in range(len(robjbuf)):
            if (mode < 2):
                if (robjbuf[i].type == 'REG8'):
                    if (robjbuf[i].flag):
                        if (robjbuf[i].mask):
                            setbuf.append((robjbuf[i].addr, int(robjbuf[i].val) & 0xff, 1))
                elif (robjbuf[i].type == 'REG16'):
                    if (robjbuf[i].flag):
                        if (bus_endian_dict[robjbuf[i].endian] == 'Little_Endian'):
                            if (robjbuf[i].mask & BIT0):
                                setbuf.append((robjbuf[i].addr, int(robjbuf[i].val) & 0xff, 1))
                            if (robjbuf[i].mask & BIT1):
                                setbuf.append((robjbuf[i].addr + 1, int(robjbuf[i].val) >> 8, 1))
                        else:
                            if (robjbuf[i].mask & BIT1):
                                setbuf.append((robjbuf[i].addr, int(robjbuf[i].val) >> 8, 1))
                            if (robjbuf[i].mask & BIT0):
                                setbuf.append((robjbuf[i].addr + 1, int(robjbuf[i].val) & 0xff, 1))
                elif (robjbuf[i].type == 'REG32'):
                    if (robjbuf[i].flag):
                        if (bus_endian_dict[robjbuf[i].endian] == 'Little_Endian'):
                            #print("mask val {}".format(self.reg.objr[i].mask))
                            if (robjbuf[i].mask & BIT0):
                                setbuf.append((robjbuf[i].addr, int(robjbuf[i].val) & 0xff, 1))
                            if (robjbuf[i].mask & BIT1):
                                setbuf.append((robjbuf[i].addr + 1, (int(robjbuf[i].val) >> 8) & 0xff, 1))
                            if (robjbuf[i].mask & BIT2):
                                setbuf.append((robjbuf[i].addr + 2, (int(robjbuf[i].val) >> 16) & 0xff, 1))
                            if (robjbuf[i].mask & BIT3):
                                setbuf.append((robjbuf[i].addr + 3, int(robjbuf[i].val) >> 24, 1))
                        else:
                            if (robjbuf[i].mask & BIT3):
                                setbuf.append((robjbuf[i].addr + 0, int(robjbuf[i].val) >> 24, 1))
                            if (robjbuf[i].mask & BIT2):
                                setbuf.append((robjbuf[i].addr + 1, (int(robjbuf[i].val) >> 16) & 0xff, 1))
                            if (robjbuf[i].mask & BIT1):
                                setbuf.append((robjbuf[i].addr + 2, (int(robjbuf[i].val) >> 8) & 0xff, 1))
                            if (robjbuf[i].mask & BIT0):
                                setbuf.append((robjbuf[i].addr + 3, int(robjbuf[i].val) & 0xff, 1))
            else:
                if (robjbuf[i].flag):
                    if (bus_endian_dict[robjbuf[i].endian] == 'Little_Endian'):
                        b3, b2, b1, b0 = (robjbuf[i].val >> 24), (robjbuf[i].val >> 16) & 0xff, (robjbuf[i].val >> 8) & 0xff, (robjbuf[i].val >> 0) & 0xff
                        newvbal = (b0 << 24) | (b1 << 16) | (b2 << 8) | (b3 << 0)
                        setbuf.append((robjbuf[i].addr, newvbal, 4))
                    else:
                        setbuf.append((robjbuf[i].addr, robjbuf[i].val, 4))
        return  setbuf

    def save(self, mode=2, bootmode=1):
        # self.setbuf.extend(self.reg_save(mode))
        for i in range(len(self.mdobj)):
            self.setbuf.extend(self.mdobj[i].save())
            if self.chipcfg.oax4k_cfg.sds0.en and self.chipcfg.sdsspliten:
                if self.mdobj[i].__class__.__name__ == 'DPTOP':
                    self.fsetbuf1.extend(self.mdobj[i].save())
                elif self.mdobj[i].__class__.__name__ == 'SNRTOP':
                    pass
                else:
                    self.fsetbuf0.extend(self.mdobj[i].save())
            else:
                if self.mdobj[i].__class__.__name__ == 'SNRTOP':
                    pass
                else:
                    self.fsetbuf0.extend(self.mdobj[i].save())
        if self.chipcfg.oax4k_cfg.sds0.en and self.chipcfg.sdsspliten:
            self.fsetbuf0.append((0x80208054, 0xf, 1, 0xff))
            self.fsetbuf1.insert(0, (0x80208054, 0x0, 1, 0xff))

        #sorted_set_buf = sorted(self.setbuf)
        sorted_set_buf = self.setbuf

        self.save_output(gens_globals.FilenameOut, self.fsetbuf0, 1, 0, tag=0)

        if mode == 2 and bootmode == 0:
            raise RuntimeError("flash mode don't support setting mode 2")
        oax4k_cfg = self.chipcfg.oax4k_cfg
        for snrid,snrfile in self.chipcfg.fsnr_files.items():
            self.gen_sensor_flash_tag(snrid,snrfile)

        if (mode > 2):
            self.save_cfginfo(self.cfginfo, self.chipcfg)

    def gen_sensor_flash_tag(self, index, snrfile):
        oax4k_cfg = self.chipcfg.oax4k_cfg
        ins = [oax4k_cfg.in0, oax4k_cfg.in1, oax4k_cfg.in2, oax4k_cfg.in3]
        dps = [oax4k_cfg.dp0, oax4k_cfg.dp1, oax4k_cfg.dp2, oax4k_cfg.dp3]

        set_index_tag = 0x00
        snr_sccbid = 0

        for dp in dps:
            if(dp.en and dp.input.loaden):
                if(ins[dp.input.portsrc].sensor_buf[dp.input.strmsrc].set_index == index):
                    set_index_tag = set_index_tag | (1 << dp.input.snrsrc)
                    snr_sccbid = ins[dp.input.portsrc].sensor_buf[dp.input.strmsrc].sccb.id

        with open(snrfile, 'r', encoding='UTF-8') as frh:
            snr_org_lines = frh.readlines()
            with open(snrfile, 'w') as fh:
                fh.write('TAG:0x{:x}\n'.format(set_index_tag))
                for line in snr_org_lines:
                    line = re.sub(r"(@@|TAG).*", "", line)
                    rematch = re.match(r"^\s*([0-9A-F][0-9A-F])", line.upper())
                    if(rematch):
                        if(int(rematch.group(1), 16) == snr_sccbid):  # only the id equal sensor sccb id will write to file
                            fh.write('{}'.format(line))
                    else:
                        fh.write('{}'.format(line))

    def setting_file_comment(self, fh):
        fw_ver = 0
        chiptype = self.casecfg.testcfg.chiptype

        fh.write(';FW version: {:x} \n'.format(fw_ver))  # else:
        fh.write(';Chip Type: {} \n'.format(chip_type_dict[chiptype]))  # else:
        for snrid,snr in self.casecfg.snr_files.items():
            fh.write(';input info{}: {} \n'.format(snrid, os.path.basename(snr).split("#")[0]))
        for sdsid,sds in self.casecfg.sds_files.items():
            fh.write(';serdes info{}: {} \n'.format(sdsid, os.path.basename(sds)))  #else:
        oax4k_cfg = self.chipcfg.oax4k_cfg
        outs = [oax4k_cfg.out0, oax4k_cfg.out1, oax4k_cfg.out2, oax4k_cfg.out3]
        chns = []
        rtmode0 = oax4k_cfg.out0.rtmode
        rtmode2 = oax4k_cfg.out2.rtmode
        mntcfg = oax4k_cfg.mnt
        allchns = [oax4k_cfg.out0.chnlist, oax4k_cfg.out1.chnlist, oax4k_cfg.out2.chnlist, oax4k_cfg.out3.chnlist]
        allouts = [oax4k_cfg.out0, oax4k_cfg.out1, oax4k_cfg.out2, oax4k_cfg.out3]
        # print(allchns)
        # if(chn.outport ==mntcfg.outsel):

        for chn in allchns[mntcfg.outsel]:
            if chn.txfmt != 0xff:
                rawformat, hmul = get_dict_key(output_raw_format_dict, chn.txfmt) if (raw_sel_dist[chn.sel] != 'ISPMV') else  get_dict_key(output_yuv_format_dict,
                                                                                                                                           chn.format)
            else:
                rawformat, hmul = get_dict_key(output_raw_format_dict, chn.format) if (raw_sel_dist[chn.sel] != 'ISPMV') else  get_dict_key(output_yuv_format_dict,
                                                                                                                                            chn.format)
            rawformat = "YUV422-8" if rawformat == "YUV422-12" else rawformat
            format_name,hmul = get_dict_key(output_yuv_format_dict, chn.format) if (chn.index) else (rawformat, hmul)
            if(chn.en):
                embl = allouts[chn.rtidx].embl
                fh.write(';output{} VC{} info: format:{} size:{}x{}  \n'.format(chn.outport,
                                                                                chn.outvc,
                                                                                iptvc_format_dict[format_name],
                                                                                chn.hsize,
                                                                                chn.vsize))  #else:
        pass


    def monitor_setting_save(self, fh):
        slval = 10
        mnttype = self.casecfg.testcfg.mnttype
        oax4k_cfg = self.chipcfg.oax4k_cfg
        mntcfg = oax4k_cfg.mnt
        phyclk = oax4k_cfg.out0.mtx.csi.freq * 16
        dphyv12 = oax4k_cfg.out0.mtx.csi.deskew
        outs = [oax4k_cfg.out0, oax4k_cfg.out1, oax4k_cfg.out2, oax4k_cfg.out3]
        vcmap = 0
        rtmode0 = oax4k_cfg.out0.rtmode
        rtmode2 = oax4k_cfg.out2.rtmode

        for out in outs:
            if (out.en):
                if (out.yuv.outport == mntcfg.outsel or out.rawmv.outport == mntcfg.outsel):
                    if (out.yuv.outport == mntcfg.outsel and out.yuv.en):
                        if ((rtmode0 == 1 and out.index % 2 != 0)):
                            pass
                        else:
                            vcmap = vcmap | (1 << out.yuv.outvc)
                    if (out.rawmv.outport == mntcfg.outsel and out.rawmv.en):
                        vcmap = vcmap | (1 << out.rawmv.outvc)

        if (mnttype):  # venus
            # fh.write('{:02X} {:02X} {:02X}\n'.format(0x5a, 0x01, 0xb3))  # set dovdd to 1.8v
            fh.write('{:02X} {:02X} {:02X}\n'.format(0x5a, 0x21, 0xb3))  # set dovdd to 1.8v
            fh.write('SL {}\n'.format(100))
            # fh.write('{:02X} {:02X} {:02X}\n'.format(0x5a, 0x03, 0xb3))  # set dovdd to 1.8v
            fh.write('{:02X} {:02X} {:02X}\n'.format(0x5a, 0x23, 0xb3))  # set dovdd to 1.8v
            if(phyclk > 1500000000 or dphyv12 ):
                fh.write('{:02X} {:08x} {:08x}\n'.format(0x64, 0x70200100, 0x0002118d))
            else:
                fh.write('{:02X} {:08x} {:08x}\n'.format(0x64, 0x70200100, 0x0000118d))
            fh.write('{:02X} {:08x} {:08x}\n'.format(0x64, 0x70200104, 0x0f))
            fh.write('{:02X} {:08x} {:08x}\n'.format(0x64, 0x7020010c, 0x08000f00))
            fh.write('{:02X} {:08x} {:08x}\n'.format(0x64, 0x600a0020, vcmap))
            pass
        else:
            lanenum = oax4k_cfg.out0.mtx.csi.lane
            lane_code_dict = {4:0x0f, 2:0x03, 1:0x01}

            # fh.write('{:02X} {:02X} {:02X}\n'.format(0x5c, 0x01, 0x71))  # set dovdd to 1.8v ,0.8v x256/reg val
            fh.write('{:02X} {:02X} {:02X}\n'.format(0x5c, 0x21, 0x71))  # set dovdd to 1.8v
            fh.write('SL {}\n'.format(100))
            # fh.write('{:02X} {:02X} {:02X}\n'.format(0x5c, 0x03, 0x71))  # set dovdd to 1.8v
            fh.write('{:02X} {:02X} {:02X}\n'.format(0x5c, 0x23, 0x71))  # set dovdd to 1.8v
            fh.write('{:02X} {:04X} {:02X}\n'.format(0x64, 0x101, 0x01))
            fh.write('{:02X} {:04X} {:02X}\n'.format(0x64, 0x1000, lane_code_dict[lanenum]))
            fh.write('{:02X} {:04X} {:02X}\n'.format(0x64, 0x1002, 0x10))
            fh.write('{:02X} {:04X} {:02X}\n'.format(0x64, 0x1007, 0x0f))
            pass
        fh.write('SL {}\n'.format(slval))  # else:
        fh.write('\n;OAX4000 setting Content \n')  # else:

    def save_single_reg(self, fh, mode, sccb_id, addr, val, width, mask, bootmode, addr_pre=0):
        if (mode == 0):
            if ((addr >> 16) != (addr_pre >> 16)):
                fh.write('{:02X} {:04X} {:02X}\n'.format(sccb_id, 0xfffd, (addr >> 24) & 0xff))
                fh.write('{:02X} {:04X} {:02X}\n'.format(sccb_id, 0xfffe, (addr >> 16) & 0xff))
                # print("{:x} {:x} {:x}".format(addr_pre, addr, val))
                addr_pre = addr
            for idx in range(width):
                # if((addr>>16) !=(SYSBASE>>16)):
                #     fh.write('{:02X} {:04X} {:02X}\n'.format(sccb_id,(addr+idx)&0xffff,(val>>idx*8)&0xff))
                # else:
                if((mask >> idx) & BIT0 or not mask):
                    fh.write('{:02X} {:04X} {:02X}\n'.format(sccb_id, (addr + idx) & 0xffff, (val >> (width - 1 - idx) * 8) & 0xff))
            # fh.write('{:02X} {:04X} {:02X}\n'.format(sccb_id, addr & 0xffff, val))
        elif (mode == 1):
            for idx in range(width):
                if (bootmode):
                    if ((mask >> idx) & BIT0 or not mask):
                        fh.write('{:08x} {:02X}\n'.format(addr + idx, (val >> (width - 1- idx) * 8) & 0xff))
                else:
                    if ((mask >> idx) & BIT0 or not mask):
                        fh.write('{:02X} {:08x} {:02X}\n'.format(sccb_id, addr + idx, (val >> (width - 1 - idx) * 8) & 0xff))
        else:
            if (width == 4):
                if (bootmode):  # ram boot
                    fh.write('{:08x} {:08x}\n'.format(addr, val))
                else:  # flash boot
                    fh.write('{:02X} {:08x} {:08x}\n'.format(sccb_id, addr, val))
            elif (width == 2):
                if (bootmode):  # ram boot
                    fh.write('{:08x} {:04X}\n'.format(addr, val))
                else:   # flash boot
                    fh.write('{:02X} {:08x} {:04X}\n'.format(sccb_id, addr, val))
            else:
                if (bootmode):  # ram boot
                    fh.write('{:08x} {:02X}\n'.format(addr, val))
                else:  # flash boot
                    fh.write('{:02X} {:08x} {:02X}\n'.format(sccb_id, addr, val))
        return addr_pre

    def single_reg_16b(self, fh, mode, sccb_id, addr, val, width, mask, bootmode, addr_pre=0):
        if (addr == 0x8020805E):
            pass
        elif (mode == 0):
            if ((addr >> 16) != (addr_pre >> 16)):
                fh.write('{:02X} {:04X} {:02X}\n'.format(sccb_id, 0xfffd, (addr >> 24) & 0xff))
                fh.write('{:02X} {:04X} {:02X}\n'.format(sccb_id, 0xfffe, (addr >> 16) & 0xff))
                # print("{:x} {:x} {:x}".format(addr_pre, addr, val))
                addr_pre = addr

            for idx in range(width):
                # if ((addr >> 16) != (SYSBASE >> 16)):
                #     fh.write('{:02X} {:04X} {:02X}\n'.format(sccb_id, (addr+idx)&0xffff, (val>>idx*8)&0xff))
                # else:
                if ((mask >> idx) & BIT0 or not mask):
                    fh.write('{:02X} {:04X} {:02X}\n'.format(sccb_id, (addr + idx) & 0xffff, (val >> (width - 1 - idx) * 8) & 0xff))
            # fh.write('{:02X} {:04X} {:02X}\n'.format(sccb_id, addr & 0xffff, val))
        elif (mode ==1):
            if ((addr >> 16) == 0x8022) and ((addr >> 13) != (addr_pre >> 13)):
                fh.write('\n')
                fh.write('{:02X} {:04X} {:02X} ; remap addr \n'.format(sccb_id, 0x9644, 0))
                fh.write('{:02X} {:04X} {:02X}\n'.format(sccb_id, 0x9645, (addr >> 8) & 0xE0))
                fh.write('{:02X} {:04X} {:02X}\n'.format(sccb_id, 0x9646, (addr >> 16) & 0xff))
                fh.write('{:02X} {:04X} {:02X}\n'.format(sccb_id, 0x9647, (addr >> 24) & 0xff))
                # print("{:x} {:x} {:x}".format(addr_pre, addr, val))
                addr_pre = addr
            for idx in range(width):
                if (bootmode):
                    if ((mask >> idx) & BIT0 or not mask):
                        fh.write('{:08x} {:02X}\n'.format(addr + idx, (val >> (width - 1 - idx) * 8) & 0xff))
                else:
                    if ((mask >> idx) & BIT0 or not mask):
                        if addr >= 0x80220000:
                            addroff = addr & 0xFFFFE000
                            fh.write('{:02X} {:04X} {:02X}\n'.format(sccb_id, (addr - addroff + idx) & 0xffff, (val >> (width - 1 - idx) * 8) & 0xff))
                        else:
                            fh.write('{:02X} {:04X} {:02X}\n'.format(sccb_id, (addr + idx) & 0xffff, (val >> (width - 1 - idx) * 8) & 0xff))
        else:
            if (width == 4):
                if (bootmode):  # ram boot
                    fh.write('{:08x} {:08x}\n'.format(addr, val))
                else:  # flash boot
                    fh.write('{:02X} {:04X} {:08x}\n'.format(sccb_id, addr & 0xffff, val))
            elif (width == 2):
                if(bootmode):  # ram boot
                    fh.write('{:08x} {:04X}\n'.format(addr, val))
                else:  # flash boot
                    fh.write('{:02X} {:04X} {:04X}\n'.format(sccb_id, addr & 0xffff, val))
            else:
                if (bootmode):  # ram boot
                    fh.write('{:08x} {:02X}\n'.format(addr,val))
                else:   # flash boot
                    fh.write('{:02X} {:04X} {:02X}\n'.format(sccb_id, addr & 0xffff, val))
        return addr_pre

    def save_output(self, file, buf, mode=1, bootmode=1, save_mode=1, tag=0):
        """
        save_mode: 
                1: only save the change byte when setting mode is 1 
                0: save all bytes 
        """
        oax4k_cfg = self.chipcfg.oax4k_cfg
        sccb_id = oax4k_cfg.topctrl.slvid
        SYSBASE = 0x80200000
        addr_pre = 0
        with open(file,'w') as fh:
            if (bootmode == 2):
                self.monitor_setting_save(fh)
            if (mode == 0):
                fh.write('{:02X} {:04X} {:02X}\n'.format(sccb_id, 0x9601, 0x0b))

            for i in range(len(buf)):
                # print(buf[i])
                addr, val, width, *masks = buf[i]
                mask = masks[0] if (masks and save_mode) else 0
                addr_pre_ret = self.single_reg_16b(fh=fh,
                                                   mode=mode,
                                                   sccb_id=sccb_id,
                                                   addr=addr,
                                                   val=val,
                                                   width=width,
                                                   mask=mask,
                                                   bootmode=bootmode,
                                                   addr_pre=addr_pre)
                addr_pre = addr_pre_ret

            fh.write(';OAX4000 debug setting start here \n')  # else:

    def save_cfginfo(self, file, cfg):
        with open(file,'w') as fh:
            chipobj = get_class_object(cfg.oax4k_cfg, level=1)
            #print(chipobj)

            for item in chipobj:
                if (item != 'fw' ):
                # if (item == 'sys'):
                    obj= getattr(cfg.oax4k_cfg, item)

                    #if (obj.en):
                    normal_varcfg = get_class_var(obj)
                    object_list = get_class_list(obj)
                    #print(object_list)
                    objlist_varcfg = get_class_listvar_new(obj, object_list, chip_obj_dict)
                    for nameval in normal_varcfg:
                        name,val = nameval
                        fh.write('{} {} {}\n'.format(item.upper(), name.upper(), val))
                    for obj, clist in objlist_varcfg:
                        objs = obj.split(".")
                        if(len(objs) > 1):
                            objs = objs[0:-1]
                            objstr = ' '.join(objs)
                        else:
                            objstr = ''
                        pass
                        for name, val in clist:
                            fh.write('{} {} {} {}\n'.format(item.upper(), objstr.upper(), name.upper(), val))
        #print(file)
        pass
