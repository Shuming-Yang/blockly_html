# WARNING
# pylint: disable=C0103, C0114, C0115, C0116, C0412, W0231, W0401, W0612, W0614, W0622
from Utility.Reg import REGOBJ
from Utility.Entity import Entity
from Utility.Para import *
from Define.Para import *
from Utility.Others import *
from RegTable.Regdefdist import define_dist


rt_validbit_dict ={
    "RAW12L":0,
    "RAW12S":0,
    "RAW12V":0,
    "RAW12M":0,
    "RAW10":1,
    "RAW14":3,
    "RAW16":2,
    "RAW20":1,
    "RAW24":0,
    "RAW2X11":0,
    "RAW2X12":0,
    "RAW3X10":1,
    "RAW3X12":0,
    "RAW12+12":0,
    "YUV422-8":2,
    "YUV422-10":1,
    "YUV422-12":0,
    "RGB565":2,
    "RGB888":0,
    "YUV420-8":2,  # tbd
    "YUV420-10":1,
    "YUV420-12":0,
}


class RETIME_PATH_CFG():
    def __init__(self,id):
        self.size_sel =0
        self.en =0
        self.vts =0
        self.hsize =0
        self.vsize =0
        self.ready_hsize =0
        self.swap =0
        self.crc_len =0
        self.valid_bit =0
        self.index =id
        self.rgbseq =2
        self.balance_en =0
        self.hblk_num_odd =300
        self.hblk_num_even =300
        self.yuvin =0
        self.lint_num =4
        self.format = "RAW12"
        # self.fmt = "RAW12"


class RETIME_FSYNC_CFG():
    def __init__(self):
        self.en =0
        self.trig_mode =0
        self.out_mode =0
        self.byp_fsin =0
        self.polarity =0
        self.act_len  =100
        self.act_frm  =1
        self.act_dly  = 0xffff
        self.dly_en   =0
        self.extra_vts = 0


class RETIME_EMBL_CFG():
    def __init__(self):
        self.preseino =0
        self.postseino =0
        self.preovino =0
        self.postovino =0
        self.poststano =0
        self.path_sel =0


class RETIME_CFG(object):
    def __init__(self,chipcfg):
        self.mode =0
        self.merge_en =0
        self.rtsof_sel =1
        self.yuv = RETIME_PATH_CFG(0)
        self.raw = RETIME_PATH_CFG(1)
        self.embl = RETIME_EMBL_CFG()
        self.fsync = RETIME_FSYNC_CFG()
        self.err_det_en =0x3f
        self.safe_en =0xff
        self.yuv_in_rawpath = 0
        self.strmoff_mode =1
        self.hmac_out = 0
        self.mtx_lane = 0
        self.chipcfg =chipcfg
        #self.emb_path_sel =0
        #self.emb_cfg =0


    def config(self):
        pass

class RETIME_REG(REGOBJ):
    def __init__(self,cfg,uid=0):
        self.base =self.get_baseaddr('RETIME',define_dist,uid)
        self.regtable=cfg.regtable
        self.objr=[]


class RETIME(Entity):
    """description of class"""
    def __init__(self,chipcfg,uid=0):
        #self.cfg=mrx_cfg()
        self.cfg =RETIME_CFG(chipcfg)
        self.reg =RETIME_REG(chipcfg,uid)
        self._rt_cfg_init(chipcfg,uid)
        self.setbuf=[]

    def _rt_cfg_init_fsync(self,rtfsync,chipout):
        yuvout =chipout.yuv
        rawmvout =chipout.rawmv
        extra_line = chipout.fsync.extra_line
        rtfsync.en =chipout.fsync.en
        rtfsync.trig_mode =chipout.fsync.trig_mode
        rtfsync.out_mode =chipout.fsync.out_mode
        rtfsync.byp_fsin =chipout.fsync.byp_fsin
        rtfsync.polarity =chipout.fsync.polarity
        rtfsync.act_len =chipout.fsync.act_len
        rtfsync.act_frm =chipout.fsync.act_frm
        rtfsync.act_dly =chipout.fsync.act_oft * yuvout.hts  if(yuvout.en) else chipout.fsync.act_oft *rawmvout.hts
        rtfsync.dly_en =chipout.fsync.oft_en
        rtfsync.extra_vts =extra_line *yuvout.hts  if(yuvout.en) else extra_line *rawmvout.hts

    def _rt_cfg_init(self,cfg,uid):
        dp0,out0 =cfg.oax4k_cfg.dp0,cfg.oax4k_cfg.out0
        dp1,out1 =cfg.oax4k_cfg.dp1,cfg.oax4k_cfg.out1
        dp2,out2 =cfg.oax4k_cfg.dp2,cfg.oax4k_cfg.out2
        dp3,out3 =cfg.oax4k_cfg.dp3,cfg.oax4k_cfg.out3
        outlist = [out0,out1,out2,out3]
        dplist = [dp0,dp1,dp2,dp3]
        outobj =outlist[uid]
        self.cfg.mode = 0 if (outobj.index%2) else outobj.rtmode
        # outembl =outobj.dpbuf[0].embl
        self.cfg.hmac_out = outobj.hmacout
        self.cfg.mtx_lane = outobj.mtx.csi.lane
        outembl =outobj.embl
        if outembl.en:
            self.cfg.embl.path_sel =outembl.chn
            self.cfg.embl.preseino =outembl.seipre.outnum
            self.cfg.embl.postseino =outembl.seipost.outnum
            self.cfg.embl.preovino =outembl.ovipre.outnum
            self.cfg.embl.postovino =outembl.ovipost.outnum
            self.cfg.embl.poststano =outembl.sta.outnum
        # print("retime embl num {} {} {} {} {}".format(
        #         self.cfg.embl.preseino, self.cfg.embl.postseino,
        #         self.cfg.embl.preovino, self.cfg.embl.postovino,
        #         self.cfg.embl.poststano
        #     ))
        outobj.yuv.en =  outobj.yuv.en  if outobj.en else 0
        outobj.rawmv.en =  outobj.rawmv.en  if outobj.en else 0
        dpobj= dplist[outobj.idcsrc]
        if outobj.yuv.en:
            self._rtcfg_path_init(self.cfg.yuv,outobj.yuv,dpobj)
        if outobj.rawmv.en:
            self._rtcfg_path_init(self.cfg.raw,outobj.rawmv,dpobj)
        if outobj.fsync.en:
            self._rt_cfg_init_fsync(self.cfg.fsync,outobj)
        self.cfg.err_det_en = self.cfg.yuv.en |  (self.cfg.raw.en<<1) | (self.cfg.yuv.en<<2) |  (self.cfg.raw.en<<3) |\
                (self.cfg.yuv.en<<4) |  (self.cfg.raw.en<<5)

    def _rtcfg_path_init(self,rtpath,chippath,dpobj):
        rtpath.en = chippath.en and chippath.outen
        rawformat,hmul =get_dict_key(output_raw_format_dict,chippath.format) if (raw_sel_dist[chippath.sel]!='ISPMV') else  get_dict_key(output_yuv_format_dict,chippath.format)
        format_name,hmul = get_dict_key(output_yuv_format_dict,chippath.format) if (chippath.index) else (rawformat,hmul)
        rtpath.format = format_name
        rtpath.vsize = chippath.vsize
        rtpath.hsize = chippath.hsize*hmul
        byterate,*_ = rt_byterate_dict[format_name]
        #print("rt format name {} byte rate {}".format(format_name,byterate))
        rtpath.ready_hsize = chippath.hsize *byterate
        if 'RAW14' in format_name:
            rtpath.ready_hsize = int(chippath.hsize * 4 /3)
            if chippath.hsize * 4 %3 != 0:
                rtpath.ready_hsize += 1
        if chippath.hsize %16:
            crc_act_len =  (int(chippath.hsize/8)+1)*8*chippath.vsize* byterate/2
        else:
            crc_act_len =  chippath.hsize*chippath.vsize* byterate /2
        rtpath.crc_len =int(crc_act_len)
        rtpath.size_sel = 1 # tbd ,select internal register
        rtpath.swap =chippath.swap
        rtpath.rgbseq =chippath.seq
        rtpath.valid_bit=rt_validbit_dict[format_name]
        rtpath.vts = int(chippath.hts *chippath.vts)
        frmtime = self.cfg.chipcfg.oax4k_cfg.sys.clkt.do0clk/chippath.fps
        rtpath.balance_en = chippath.hblk_balance
        rtpath.hblk_num_odd = chippath.hblk_odd
        rtpath.hblk_num_even = chippath.hblk_even
        rtpath.lint_num = (rtpath.vsize -chippath.lnint_oft)>>1
        # rtpath.fmt = chippath.format
        if ((chippath.index ==0) and raw_sel_dist[chippath.sel]!='ISPMV'):
            if 'YUV' in format_name:
                rtpath.yuvin =1
                # if(dpobj.yuvin_mode)
                rtpath.swap = dpobj.yuvin_mode

    def start(self):
        yuv =self.cfg.yuv
        raw =self.cfg.raw
        fsync = self.cfg.fsync
        self.cfg.merge_en = ~(self.cfg.raw.en & self.cfg.yuv.en) &BIT0
        yuv.swap = 1
        # if raw.en and ('YUV' in raw.fmt):
        #     self.cfg.yuv_in_rawpath = 1
        #     raw.swap = 1
        #     print("[RT] {:s}".format(raw.fmt))
        if self.cfg.hmac_out:
            if self.cfg.mtx_lane == 4:
                if((raw.format == "RAW10") or (raw.format == "RAW12L")or(raw.format == "RAW12S")
                    or(raw.format == "RAW12V")or(raw.format == "RAW14")):
                    self.cfg.raw.balance_en = 1
                elif((yuv.format == "YUV420-8") or (yuv.format == "YUV420-10")or(yuv.format == "YUV420-12")): #yuv420-12
                    self.cfg.yuv.balance_en = 1
        r0 =   self.cfg.merge_en|(self.cfg.yuv.en<<1)|(self.cfg.yuv.size_sel<<3) | (self.cfg.raw.en<<2)|(self.cfg.raw.size_sel<<4) |(self.cfg.mode<<5)| \
            (fsync.en<<9) |(fsync.out_mode<<11) |(fsync.trig_mode<<12) |(fsync.byp_fsin<<13) |(fsync.dly_en<<14)|(fsync.polarity<<15) |\
            (yuv.swap<<20)| (raw.swap<<22) | (self.cfg.embl.path_sel<<26) |\
                (self.cfg.yuv.balance_en<<28) | (self.cfg.raw.balance_en<<29) | (raw.yuvin<<30) | (self.cfg.rtsof_sel<<31)
        self.reg.writereg32(0,r0)
        emb_cfg =self.cfg.embl.preseino | (self.cfg.embl.postseino<<4) |(self.cfg.embl.preovino<<8) |\
            (self.cfg.embl.postovino<<12) |(self.cfg.embl.poststano<<16)
        r4= (emb_cfg) |(yuv.rgbseq<<24)|(raw.rgbseq<<28) | (self.cfg.mode<<20)
        self.reg.writereg32(4,r4)
        # print("retime r4 {:x}".format(r4))
        #r8= raw.swap
        #self.reg.writereg8(8,r8)
        r48= yuv.hsize | (yuv.vsize<<16)
        self.reg.writereg32(0x48,r48)
        r4c= raw.hsize | (raw.vsize<<16)
        self.reg.writereg32(0x4c,r4c)
        self.reg.writereg32(0x58,yuv.ready_hsize | (raw.ready_hsize<<16))
        r0f =yuv.valid_bit | (raw.valid_bit<<2)
        self.reg.writereg8(0x0f,r0f)
        self.reg.writereg32(0x10,yuv.crc_len)
        self.reg.writereg32(0x14,raw.crc_len)
        self.reg.writereg32(0x18,int(yuv.vts*2))
        self.reg.writereg32(0x1c,int(raw.vts*2))
        self.reg.writereg8(0x0c,self.cfg.safe_en)
        self.reg.writereg8(0x0d,self.cfg.err_det_en)
        self.reg.writereg32(0x50,yuv.hblk_num_even | (yuv.hblk_num_odd<<16))
        self.reg.writereg32(0x54,raw.hblk_num_even | (raw.hblk_num_odd<<16))
        self.reg.writereg8(0x7b, 0x3)  # glb_fcp_en
        self.reg.writereg8(0x74, raw.en<<1|yuv.en)  #
        self.reg.writereg32(0x64,yuv.lint_num | (raw.lint_num<<16) | (self.cfg.strmoff_mode<<31) )  # glb_fcp_en
        blk = 0
        if self.cfg.hmac_out:
            if self.cfg.mtx_lane == 4:
                if((raw.format == "RAW10") or (raw.format == "RAW12L")or(raw.format == "RAW12S")
                    or(raw.format == "RAW12V")or(raw.format == "RAW14")):
#                    self.reg.writereg8(0x03, self.reg.readreg8(0x03) & 0x0f | BIT5);
                    blk = raw.hsize//4
                    self.reg.writereg8(0x56, blk & 0xff)
                    self.reg.writereg8(0x57, (blk &0xff00) >> 8)
                elif((yuv.format == "YUV420-8") or (yuv.format == "YUV420-10")or(yuv.format == "YUV420-12")): #yuv420-12
#                    self.reg.writereg8(0x03, self.reg.readreg8(0x03) & 0x0f | BIT4);
                    blk = yuv.hsize//4
                    self.reg.writereg8(0x52, blk & 0xff)
                    self.reg.writereg8(0x53, (blk &0xff00) >> 8)
