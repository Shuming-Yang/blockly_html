"""
This GENS mode code which be ported from GENS source code.
@@OAX4K dist define

Author: OVT AE
Date: 2024-11-04
"""
# WARNING
# pylint: disable=C0103, C0200, C0116, C0325, C0411, C0412, W0201, W0401, W0611, W0612, W0614, W0622
from Utility.Para import *
from Define.Struct import SENSOR_CFG
from Define.Para import *
from SNR.SNRBASE import SNRBASE
from Utility.Others import *
import gens_globals
import copy


pwl_dx_exp_defaults = (
    0x08, 0x09, 0x0a, 0x0b,  # 1-4
    0x0c, 0x0c, 0x0c, 0x0c,  # 5-8
    0x0c, 0x0d, 0x0d, 0x0d,  # 9-c
    0x0d, 0x0d, 0x0e, 0x0e,  # d-10
    0x0e, 0x0e, 0x0f, 0x0f,  # 11-14
    0x10, 0x11, 0x11, 0x12,  # 15-18
    0x12, 0x13, 0x13, 0x14,  # 19-1c
    0x14, 0x16, 0x16, 0x16,  # 1d-20
    0x08  # 21
)

pwl_dy_exp_defaults = (
    0x00, 0x01, 0x00, 0x00, 0x02, 0x00, 0x00, 0x02, 0x00,  # 22 -2a
    0x00, 0x02, 0x00, 0x00, 0x02, 0x00, 0x00, 0x02, 0x00,  # 2b -33
    0x00, 0x02, 0x00, 0x00, 0x02, 0x00, 0x00, 0x02, 0x00,  # 34 -3c
    0x00, 0x02, 0x00, 0x00, 0x02, 0x00, 0x00, 0x02, 0x00,  # 3d -45
    0x00, 0x04, 0x00, 0x00, 0x04, 0x00, 0x00, 0x04, 0x00,  # 46 -4e
    0x00, 0x04, 0x00, 0x00, 0x04, 0x00, 0x00, 0x04, 0x00,  # 4f -57
    0x00, 0x04, 0x00, 0x00, 0x04, 0x00, 0x00, 0x08, 0x00,  # 58 -60
    0x00, 0x08, 0x00, 0x00, 0x08, 0x00, 0x00, 0x08, 0x00,  # 61 -69
    0x00, 0x08, 0x00, 0x00, 0x10, 0x00, 0x00, 0x10, 0x00,  # 6a -72
    0x00, 0x10, 0x00, 0x00, 0x10, 0x00, 0x00, 0x20, 0x00,  # 73 -7b
    0x00, 0x20, 0x00, 0x00, 0x20, 0x00, 0x00, 0x00, 0xff,  # 7c -84
)

snr_reg_dist = {
    "B_HSIZE_H": (0x6a04, 0x00),
    "B_HSIZE_L": (0x6a05, 0x00),
    "B_VSIZE_H": (0x6a06, 0x00),
    "B_VSIZE_L": (0x6a07, 0x00),
    "ROI_HSIZE_H": (0x6a24, 0x00),
    "ROI_HSIZE_L": (0x6a25, 0x00),
    "ROI_VSIZE_H": (0x6a26, 0x00),
    "ROI_VSIZE_L": (0x6a27, 0x00),
    "PRE_EMBLDT": (0x430d, 0x13),
    "POST_EMBLDT": (0x430e, 0x94),
    "STAT_CTRL": (0x430f, 0x57),
    "CRYPTO_CONF0": (0x4700, 0xE0),
}

snr_embl_bitpos = {
    'COM12': 0,
    'COM14': 4,
    'COM16': 4,
    'COM20': 2,
    'COM24': 0,
    '12+SPD10': 0,
    '16+SPD10': 4,
    '24+LFM': 0,
    '4X10RAW': 2,
    'YUV422': 4
}

snr_embl_takebyte = {
    'COM12': 2,
    'COM14': 6,
    'COM16': 0xa,
    'COM20': 0xa,
    'COM24': 0xa,
    '12+SPD10': 2,
    '16+SPD10': 0xa,
    '24+LFM': 0xa,
    '4X10RAW': 2,
    '3X10RAW': 2
}

snr_sta_fmt_dict = {
    'COM12': 0,
    'COM14': 1,
    'COM16': 2,
    'COM20': 3,
    'COM24': 4,
    '24+LFM': 0,  # need check
    '4X10RAW': 0,
    '12+SPD10': 0,
    '16+SPD10': 2,
    '3X10RAW': 2
}


def get_group_set(datlist, addr, val0, val1):
    retlist, tmplist, sflag = [], [], 0
    for i in range(len(datlist)):
        if datlist[i][0] == addr:
            if datlist[i][1] == val0:
                tmplist, sflag = [], 1
                continue
            elif datlist[i][1] == val1:
                sflag = 0
                retlist.append(tmplist)
        else:
            if sflag == 1:
                tmplist.append(datlist[i])
    return retlist


class SNRPARSE(SNRBASE):
    """description of class"""
    def __init__(self, setfile, _chipcfg):
        super().__init__()
        self.sccb_id = 0x6c
        self.cfg = SENSOR_CFG()
        self.setfile = setfile
        self.baseaddr = 0
        self.setbuf = []
        self.regdist = snr_reg_dist
        self.addrlen = 0
        self.a_cfg = SENSOR_CFG()
        self.b_cfg = SENSOR_CFG()
        self.roi_cfg = SENSOR_CFG()
        self.spd_cfg = SENSOR_CFG()
        self.spd_en = 0
        self.cclk = 24000000
        self.chipver = 0

    def sensor_setting_parse(self):
        # print("!!!!!!!neee set id{:x}".format(self.cfg.sccb.setid))
        self.sccb_id = self.cfg.sccb.setid if (self.cfg.sccb.setid) else self.sccb_id
        self.setdist, self.setlist, mtlen, self.sccb_id = self._setting_parse(self.setfile, self.sccb_id, group_en=1, group_start=0x3208, group_tirg=0xe0)
        self.chipver = 0 if self.cfg.ver else 1
        # self.

    def gen_ab_dual_roi_setting(self):
        self.a_cfg = copy.deepcopy(self.cfg)
        self.b_cfg = copy.deepcopy(self.cfg)
        self.roi_cfg = copy.deepcopy(self.cfg)
        if self.cfg.ab_mode:
            # self.a_cfg.strm.hts = int(((self.cfg.a_frm_num + self.cfg.b_frm_num)
            #                         * self.cfg.strm.hts) / self.cfg.a_frm_num)
            # self.a_cfg.strm.vclist = [self.cfg.a_vc_id]
            # self.b_cfg.strm.hts = int(((self.cfg.a_frm_num + self.cfg.b_frm_num)
            #                         * self.cfg.strm.hts) / self.cfg.b_frm_num)
            self.a_cfg.strm.vts = int(((self.cfg.a_frm_num + self.cfg.b_frm_num) * self.cfg.strm.vts) / self.cfg.a_frm_num)
            self.a_cfg.strm.vclist = [self.cfg.a_vc_id]
            self.b_cfg.strm.vts = int(((self.cfg.a_frm_num + self.cfg.b_frm_num) * self.cfg.strm.vts) / self.cfg.b_frm_num)
            b_hsize_h = self.get_sensor_reg_val("B_HSIZE_H")
            b_hsize_l = self.get_sensor_reg_val("B_HSIZE_L")
            b_vsize_h = self.get_sensor_reg_val("B_VSIZE_H")
            b_vsize_l = self.get_sensor_reg_val("B_VSIZE_L")
            self.b_cfg.strm.hsize = (b_hsize_h << 8) + b_hsize_l
            self.b_cfg.strm.vsize = (b_vsize_h << 8) + b_vsize_l
            self.b_cfg.strm.vclist = [self.cfg.b_vc_id]
            self.b_cfg.strm.byptc = 1
            self.b_cfg.embl.pre.emb_vcid = self.cfg.b_vc_id
            self.b_cfg.embl.post.emb_vcid = self.cfg.b_vc_id
            # self.b_cfg.embl.sta.chn_vc = [1,0,2,3]
            self.b_cfg.embl.sta.chn_vc = [self.cfg.b_vc_id, 0, 2, 3]
            # self.b_cfg.embl.en = 0
            # self.b_cfg.embl.post.num =0
            # self.b_cfg.embl.pre.num =0
            # self.b_cfg.embl.sta.num =0
            # self.a_cfg.embl.crc_order = 1
            # self.a_cfg.embl.crc_inv = 1
            # self.b_cfg.embl.crc_order = 1
            # self.b_cfg.embl.crc_inv = 1
        if self.cfg.dual_roi:
            roi_hsize_h = self.get_sensor_reg_val("ROI_HSIZE_H")
            roi_hsize_l = self.get_sensor_reg_val("ROI_HSIZE_L")
            roi_vsize_h = self.get_sensor_reg_val("ROI_VSIZE_H")
            roi_vsize_l = self.get_sensor_reg_val("ROI_VSIZE_L")
            self.roi_cfg.strm.hsize = (roi_hsize_h << 8) + roi_hsize_l
            self.roi_cfg.strm.vsize = (roi_vsize_h << 8) + roi_vsize_l
            self.roi_cfg.strm.vclist = [self.cfg.roi_vc_id]
            self.roi_cfg.strm.byptc = 0
            # self.roi_cfg.embl.en = 0
            # self.roi_cfg.embl.en = 0
            # self.roi_cfg.embl.post.num =0
            # self.roi_cfg.embl.pre.num =0
            # self.roi_cfg.embl.sta.num =0
            # self.roi_cfg.embl.sta.en = 0
            # self.roi_cfg.embl.sta.chn_num = 0
            roi1_embl_self_timing = 1
            if roi1_embl_self_timing:  # if roi use self timing ,the embl content will be all 0 ,if disable , it will use roi0 embl data
                self.roi_cfg.embl.pre.emb_vcid = self.cfg.roi_vc_id
                self.roi_cfg.embl.post.emb_vcid = self.cfg.roi_vc_id
                self.roi_cfg.embl.sta.chn_vc = [self.cfg.roi_vc_id, 2, 0, 3]

    def gen_spd_cfg(self):
        if self.spd_en:
            self.spd_cfg = copy.deepcopy(self.cfg)
            self.spd_cfg.strm.format = input_format_dict['SPD_RAW10']
            self.spd_cfg.strm.format_tid = sensor_input_format_type_dict['HDR1_LINEARRAW']
            # self.spd_cfg.strm.format_nid = sensor_input_format_name_dict['RAW12']
            self.spd_cfg.strm.vcnum = 1
            self.spd_cfg.strm.imgid = [[0x2b]]
            self.spd_cfg.strm.imgdt = [[0x2b]]
            self.spd_cfg.strm.vclist = [1]
            self.spd_cfg.strm.byptc = 0 if (self.spd_cfg.spd_byp) else 1
            # self.spd_cfg.not_check_timing = 1
            self.cfgs.append(self.spd_cfg)

    def gen_lfm_cfg(self):
        if self.lfm_bit_out_en:
            self.lfm_cfg = copy.deepcopy(self.cfg)
            self.lfm_cfg.strm.format = input_format_dict['LFM_RAW8']
            self.lfm_cfg.strm.format_tid = sensor_input_format_type_dict['HDR1_LINEARRAW']
            # self.spd_cfg.strm.format_nid = sensor_input_format_name_dict['RAW12']
            self.lfm_cfg.strm.vcnum = 1
            if self.chipver:
                self.lfm_cfg.strm.imgid = [[0x27]]
            else:
                self.lfm_cfg.strm.imgid = [[0x2a]]
            self.lfm_cfg.strm.imgdt = [[0x2a]]
            self.lfm_cfg.strm.vclist = [1]
            self.lfm_cfg.strm.byptc = 0 if (self.lfm_cfg.spd_byp) else 1
            # self.lfm_cfg.not_check_timing = 1
            # LFM hsize is 1/8 image hsize, as 8 pixels lfm bits are grouped into one byte
            self.lfm_cfg.strm.hsize = self.lfm_cfg.strm.hsize >> 3
            self.cfgs.append(self.lfm_cfg)

    def cfg_cb(self):
        self.cfgs = []
        # self.get_sensor_timing()
        if ((not self.cfg.ab_mode) and (not self.cfg.dual_roi)):
            self.cfgs.append(self.cfg)
            self.gen_spd_cfg()
            self.gen_lfm_cfg()
        else:
            self.gen_ab_dual_roi_setting()
            # self.b_cfg.not_check_timing = 1
            # self.roi_cfg.not_check_timing = 1
            self.cfgs.append(self.a_cfg)
            if self.cfg.ab_mode and (not self.cfg.dual_roi):
                self.cfgs.append(self.b_cfg)
            elif (not self.cfg.ab_mode) and (self.cfg.dual_roi):
                self.cfgs.append(self.roi_cfg)
            else:
                self.cfgs.append(self.roi_cfg)
                self.cfgs.append(self.b_cfg)
        print(f"cfg len {len(self.cfgs)}")

    def cal_snr_clk(self):
        self.cfg.strm.phyclk = gens_globals.do0clk * 16
        # print('''pre_divp {} r303 {} pre_div {} r304 {} r305 {} div_loop {}
        #         divm {}'''.format(pre_divp, r303, pre_div, r304, r305, div_loop, divm))
        # self.old_cal_snr_clk()
        self.cfg.strm.sclk= int(gens_globals.sclk , 10)
        # print('''pre_div0 {} r323 {} pre_div {} r324 {} r325 {} div_loop {}
        #         divm {} r32a {} r32b {}'''.format(pre_div0, r323, pre_div, r324,
        #         r325, div_loop, divm, r32a, r32b))
        # print(" vco1 {} vco2 {}".format(vco1, vco2))
        # print(" phyclk {}, sclk {} cclk {} ".format(self.cfg.strm.phyclk ,self.cfg.strm.sclk, self.cclk))


    def get_format_cfg(self, cfg):
        self.lfm_en = True #TTT
        self.spd_en = False #TTT
        self.lfm_bit_out_en = False #TTT
        self.hdr_mode = True #TTT
        fmt_type = "HDR4_DCGSVSCOMB" if (self.hdr_mode) else "HDR3_DCGVSCOMB"
        cfg.strm.preblank = 1
        self.fmt0_name = gens_globals.raw_format
        # check fmt type ============= TBD
        if self.fmt0_name == "RAW12": # 10640,X1A,X2A   RAW20,RAW16,RAW12
            self.fmt0_name = "COM12"
        if self.fmt0_name == "YUV422": #X1E
            fmt_type = "BYP_YUV"
        # check fmt type ============= TBD
        # print("snr fmt name {} fmt type {}".format(fmt_name, fmt_type))
        cfg.strm.format = input_format_dict[self.fmt0_name]
        cfg.strm.format_tid = sensor_input_format_type_dict[fmt_type]
        # cfg.strm.format_nid = sensor_input_format_name_dict[fmt_name]

    def get_embl_cfg(self, cfg):
        cfg.embl.en = 0
        pre_emb_dt = 0x93 #self.get_sensor_reg_val("PRE_EMBLDT")
        cfg.embl.linemode = 1 #TTT
        if int(gens_globals.TopNum, 0) != 0:
            cfg.embl.pre.num = int(gens_globals.TopNum, 0)
            cfg.embl.pre.emb_id = pre_emb_dt & 0x3f
            if self.fmt0_name in snr_embl_bitpos:
                cfg.embl.pre.bitpos = snr_embl_bitpos[self.fmt0_name]
            else:
                cfg.embl.pre.bitpos = 2
            if self.fmt0_name in snr_embl_takebyte:
                cfg.embl.pre.takebyte = snr_embl_takebyte[self.fmt0_name]
            else:
                cfg.embl.pre.takebyte = 2
#            print(get_group_set(self.setlist, 0x3208, 0x4, 0x14))
            self.cfg.embl.pre.len = int(gens_globals.snr_hsize, 0)
        if int(gens_globals.BtmNum, 0) != 0:
            cfg.embl.post.num = int(gens_globals.BtmNum, 0)
            # cfg.embl.post.len = 0x104
            post_emb_dt = self.get_sensor_reg_val("POST_EMBLDT")
            cfg.embl.post.emb_id = post_emb_dt & 0x3f
            if self.fmt0_name in snr_embl_takebyte:
                cfg.embl.post.takebyte = snr_embl_takebyte[self.fmt0_name]
            else:
                cfg.embl.post.takebyte = 2
            if self.fmt0_name in snr_embl_bitpos:
                cfg.embl.post.bitpos = snr_embl_bitpos[self.fmt0_name]
            else:
                cfg.embl.post.bitpos = 2
#            print(get_group_set(self.setlist, 0x3208, 0x5, 0x15))
            self.cfg.embl.post.len = int(gens_globals.snr_hsize, 0)
        if cfg.embl.pre.num | cfg.embl.post.num:
            cfg.embl.en = 1
        else:
            cfg.embl.en = 0

    def get_sta_cfg(self):
        sta_ctrl = self.get_sensor_reg_val("STAT_CTRL")
        self.cfg.embl.sta.num = int(gens_globals.StatNum, 0)
        if int(gens_globals.StatNum, 0) != 0:
            self.cfg.embl.sta.en = 1
            self.cfg.embl.sta.num = int(gens_globals.StatNum, 0)
            self.cfg.embl.sta.chn_num = 2
            self.cfg.embl.sta.id = sta_ctrl & 0x3f
            if (self.cfg.embl.pre.num == 0) and (self.cfg.embl.post.num == 0):
                self.cfg.embl.sta.mode = 3
            elif self.cfg.embl.post.num == 0:
                self.cfg.embl.sta.mode = 2
            else:
                self.cfg.embl.sta.mode = 1
            if self.fmt0_name in snr_sta_fmt_dict:
                sta_ifmt = snr_sta_fmt_dict[self.fmt0_name]
            else:
                sta_ifmt = 2
            vld_byte = int(258 * 5 * 24 / 8 / 2)
            self.cfg.embl.sta.valid_byte = [vld_byte, 0, 0, 0]
            self.cfg.embl.sta.ifmt = [sta_ifmt, 0, 0, 0]
            self.cfg.embl.sta.vbno = 2
            self.cfg.embl.sta.ibyte_sel = 0
            if '4X10' in self.fmt0_name:
                vld_byte = int(258 * 24 / 8 / 2)
                self.cfg.embl.sta.valid_byte = [vld_byte, vld_byte, vld_byte, vld_byte]
                self.cfg.embl.sta.ifmt = [0x5, 0x5, 0x5, 0x5]
                self.cfg.embl.sta.num = 8
                self.cfg.embl.sta.ibyte_sel = 0
        else:
            self.cfg.embl.sta.en = 0
            self.cfg.embl.sta.num = 0

    def mipi_vc_cfg(self, cfg):
        imgdtlist = []
        embidlist = []
        if cfg.embl.pre.num:
            embidlist.append(cfg.embl.pre.emb_id)
        if cfg.embl.post.num:
            embidlist.append(cfg.embl.post.emb_id)
        if cfg.embl.sta.en:
            embidlist.append(cfg.embl.sta.id)
        cfg.strm.crypto_cfg = 0 #TTT
        cfg.strm.lane_num = int(gens_globals.snr_mipi_lane, 0)
        self.fmt0_name = gens_globals.raw_format
        try:
            imgdt = x8b_snr_input_itdtvc_dict[cfg.strm.imgmode, self.fmt0_name]
        except KeyError:
            imgdt = x8b_snr_input_itdtvc_dict[0, self.fmt0_name]
        cfg.strm.vcnum = len(list(imgdt[0]))
        if self.spd_en and not self.cfg.spd_byp:
            cfg.strm.imgid = imgdt[0]
        else:
            # cfg.strm.imgid = imgdt[0]
            tmplist = list(imgdt[0])
            for id in range(len(imgdt[0])):
                tmplist[id] = [gens_globals.snr_vc0type[id]]
            cfg.strm.imgid = tuple(tmplist)
        cfg.strm.imgdt = imgdt[1]
        cfg.strm.embid = []
        for embid in embidlist:
            for imgid in self.cfg.strm.imgid:
                if embid in imgid:
                    self.cfg.embl.linemode = 1
                    break
        for _ in range(cfg.strm.vcnum):
            cfg.strm.embid.append(embidlist)
        cfg.strm.vclist = []
        if not isinstance(imgdt[2], int):
            cfg.strm.vclist.extend(list(imgdt[2]))
            # print("!!!!",type(imgdt[2]))
        else:
            cfg.strm.vclist.append(imgdt[2])
        print(f"snr cfg.strm.vclist {cfg.strm.vclist} img id  {cfg.strm.imgid} img dt {cfg.strm.imgdt} embid{cfg.strm.embid} snrver {cfg.ver}")

    def get_ab_roi_cfg(self):
        self.cfg.dual_roi = False #TTT
        self.cfg.roi_vc_id = 2 #TTT
        r5008 = 0 #TTT
        self.cfg.ab_mode = (r5008 & 0x3 != 0)
        if not self.cfg.ab_mode:
            return
        self.cfg.a_frm_num = 1 #TTT
        self.cfg.b_frm_num = 1 #TTT

        def _find_4813(grp_idx):
            grp_start = self.setlist.index((0x3208, grp_idx)) + 1
            grp_end = self.setlist.index((0x3208, grp_idx + 0x10))
            r4813, r4813_val = [(addr, val) for (addr, val) in self.setlist[grp_start: grp_end] if (addr == 0x4813)][0]
            return r4813_val
        a_4813, b_4813 = [_find_4813(idx) for idx in [a_grp_idx, b_grp_idx]]
        self.cfg.a_vc_id = a_4813 & 0x3
        self.cfg.b_vc_id = b_4813 & 0x3
        print(f"snr dual roi {self.cfg.dual_roi} ab_mode {self.cfg.ab_mode} a_frm_num {self.cfg.a_frm_num} b_frm_num {self.cfg.b_frm_num}")
        print(f"a_vc_id {self.cfg.a_vc_id} b_vc_id {self.cfg.b_vc_id} roi_vc_id {self.cfg.roi_vc_id} eco version {eco_version}")

    def get_sensor_info_for_algo(self):
        pass

    def get_sensor_timing(self, refclk=24000000):
        self.cclk = refclk
        # print("get sensor timing")
        self.cfg.regaddrdict = snr_reg_dist
        # self.cfg.strm.line_v2 =1
        self.cfg.strm.hsize= int(gens_globals.snr_hsize , 10)
        self.cfg.strm.vsize= int(gens_globals.snr_vsize , 10)
        self.cfg.strm.vts = int(gens_globals.snr_vts , 10)
        self.cfg.strm.orgvts = self.cfg.strm.vts
        self.cfg.strm.hts = int(gens_globals.snr_hts , 10)
        self.get_format_cfg(self.cfg)
        self.get_embl_cfg(self.cfg)
        self.get_sta_cfg()
        self.get_ab_roi_cfg()
        self.cfg.strm.imgmode = int(gens_globals.pixelmode , 10) # "VCID mode"
        self.cfg.strm.expnum = 4
        self.mipi_vc_cfg(self.cfg)
        self.cfg.settingbuf = self.setlist
        self.cfg.sccb.id = self.cfg.sccb.id if (self.cfg.sccb.id) else self.sccb_id
        self.cfg.sccb.sendbyte = 0
        # print("!!!!!!!!!!!!sensor actual id {:x} {:x} {:x}".format( self.cfg.sccb.id,self.sccb_id,self.cfg.sccb.setid))
        self.cfg.sccb.addrlen = self.addrlen
        self.cfg.sccb.maxspeed = 1000000
        # if not self.cfg.strm.preblank:
        #     self.cfg.strm.preblank = 29  # tbd
        self.cfg.strm.vsdly_en = (len(self.cfg.strm.vclist) > 1)
        self.cfg.strm.vsdly_en = 1 if ('4X10' in self.fmt0_name) else 0
        self.cfg.strm.vsdly_max = 0x23  # tbd
        self.cfg.strm.line_v2 = 1  # tbd
        self.cfg.strm.vx = 2  # tbd
        self.cal_snr_clk()
        self.get_sensor_info_for_algo()
        self.cfg.strm.fps = self.cfg.strm.sclk / self.cfg.strm.hts / self.cfg.strm.vts
        if self.cfg.strm.vsdly_en:
            self.cfg.strm.vdly_line = 2 #TTT
