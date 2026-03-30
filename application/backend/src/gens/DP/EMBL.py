# WARNING
# pylint: disable=C0103, C0114, C0115, C0303, C0412, W0109, W0231, W0401, W0612, W0614, W0622
from Utility.Reg import REGOBJ
from Utility.Entity import Entity
from Utility.Para import *
from Define.Para import *
from Utility.Others import *
from RegTable.Regdefdist import *
import gens_globals


prert_yuvfmt_code = {
    0 : 'YUV422-8',
    1 : 'YUV422-10',
    2 : 'YUV422-12',
    3 : 'RGB565',
    4 : 'RGB888',
    5 : 'YUV420-8',
    6 : 'YUV420-10',
    7 : 'YUV420-12'
}


prert_rawfmt_code = {
    0 : 'RAW12L',
    1 : 'RAW12S',
    2 : 'RAW12V',
    3 : 'RAW14',
    4 : 'RAW16',
    5 : 'RAW20',
    6 : 'RAW24',
    7 : 'RAW2X11',
    8 : 'RAW2X12',
    9 : 'RAW3X10',
    10 : 'RAW3X12',
    11 : 'RAW12+12',
    12 : 'RAW12_LM',
    13 : 'YUV422-8',
    14 : 'RAW10'
}


embl_byterate_dec={
    'YUV422-8':2,
    'YUV422-10':2,
    'YUV422-12':2,
    'RGB565':2,
    'RGB888':2,
    'RAW12':1,
    'RAW12L':1,
    'RAW12S':1,
    'RAW12VS':1,
    'RAW12V':1,
    'RAW12_LM':1,
    'RAW10':1,
    'RAW8':1,
    'RAW14':1,
    'RAW16':2,
    'RAW20':2,
    'RAW24':2,
    'RAW2X11':2,
    'RAW2X12':2,
    'RAW12+12':2,
    'RAW2X12':2,
    'RAW3X10':3,
    'RAW3X12':3,
    'YUV420-8':2,
    'YUV420-10':2,
    'YUV420-12':2,
}


embl_ofmt_dict = {
    'RAW8':0,
    'RAW10':0,
    'RAW12L':0,
    'RAW12_LM':0,
    'RAW12S':0,
    'RAW12VS':0,
    'RAW12V':0,
    'RAW14':1,
    'RAW16':2,
    'RAW20':2,
    'RAW24':2,
    'RAW3X10':0,
    'RAW2X11':0,
    'RAW2X12':0,
    'RAW12+12':0,
    'RAW3X12':0,
    'RGB565':0,
    'RGB888':3,
    'YUV422-8':0,
    'YUV422-10':0,
    'YUV422-12':0,
    'RAW2X12':0,
    'YUV420-8':0,
    'YUV420-10':0,
    'YUV420-12':0,
}


sta_ofmt_dict = {
    'RAW8':2,
    'RAW10':3,
    'RAW12L':0,
    'RAW12_LM':0,
    'RAW12S':0,
    'RAW12VS':0,
    'RAW12V':0,
    'RAW14':1,
    'RAW16':2,
    'RAW20':3,
    'RAW24':4,
    'RAW3X10':3,
    'RAW2X11':2,
    'RAW2X12':2,
    'RAW12+12':2,
    'RAW3X12':3,
    'RGB565':2,
    'RGB888':0,
    'YUV422-8':2,
    'YUV422-10':3,
    'YUV422-12':0,
    'YUV420-8':2,
    'YUV420-10':3,
    'RAW2X12':0,  # tbd
    'YUV420-12':0
    
}


class EMBL_INFO(object):
    def __init__(self):
        self.inen =0
        self.innum =0
        self.vldbyte=0
        self.vldbyteout=0
        self.dmyln=0
        self.takebyte = 0
        self.frmcrcen = 0
        self.out_swap = 0x0f
        self.in_swap16 = 0x0


class STA_INFO(object):
    def __init__(self):
#        self.swap =0
        self.innum =0
        self.iswap=0
        self.ifmt0=0
        self.ifmt1=0
        self.ifmt2=0
        self.ifmt3=0
        self.valid_byte0=0
        self.valid_byte1=0
        self.valid_byte2=0
        self.valid_byte3=0
        self.ibyte_sel =0
        self.vbno=0             #the number of lines which contain valid bytes
        self.isel_high =0
        self.out_high =0
        self.out12_swap =0
        self.dis2nd_line = 0 #only in X3A RAW3X10 case.


class EMBL_CRC_INFO(object):
    def __init__(self):
        self.byteorder_bfdtg =0
        self.byteorder_afdtg =0
        self.order =0
        self.rx_sum_inv=0
        self.tx_sum_inv=1
        self.tx_msb =0


class EMBL_HMAC_INFO(object):
    def __init__(self):
        self.inen =0
        self.outen =0
        self.validbyte =0
        self.in_32swap =0


class EMBL_CFG(object):
    def __init__(self):
        self.en =0
        self.inten =0
        self.fcperren =0xffffbfff
        self.ofmt = 'YUV422-12'
        self.presei=EMBL_INFO()
        self.postsei=EMBL_INFO()
        self.preovi=EMBL_INFO()
        self.postovi=EMBL_INFO()
        self.sta =STA_INFO()
        self.hmac = EMBL_HMAC_INFO()
        #hmac = EMBL_HMAC_INFO()
        self.crc =EMBL_CRC_INFO()
        #self.__hash__
        self.row1_rm =0
        self.row2_rm =0
        self.x3a_en =0
        self.fcp_en =1
        self.yuv420_en=0
        self.ohsize_sel=0   #0 from reg, 1 from input signal
        self.ohsize = 1920
#        self.sta_ibsel=0    #0:12bit, 1:h8bit, 2:m8it, 3:l8bit
#        self.sta_vbno=0     #the no for line which contents valid bytes
        self.byte_rate=0
        self.byte_order=0
        self.r2byte_order =0
        self.sta_sel_high =0
        self.tag_en=0
        self.tag_data=0
#        self.rgb888_en=0
        self.rgb888_swap =0
#        self.rgb888_order=0
        self.hsize_remainder = 0
        self.sta_dis2nd_line = 0 #only in X3A RAW3X10 case.


class EMBL_REG(REGOBJ):
    def __init__(self,cfg,uid):
        self.base =self.get_baseaddr('EMB',define_dist,uid)
        self.regtable=cfg.regtable
        self.objr=[]


class EMBL(Entity):
    """description of class"""
    def __init__(self,chipcfg,uid=0):
        self.cfg =EMBL_CFG()
        self.reg =EMBL_REG(chipcfg,uid)
        self.setbuf=[]
        self._embl_cfg_init(chipcfg,uid)

    def _embl_cfg_init_rgb(self,format):
        pass
#        self.cfg.rgb888_en =1 if format =='RGB888' else 0
#        self.cfg.rgb888_order =0 # tbd,tmp
#        self.cfg.rgb888_msb =0
#        if(format =='RGB888'):
#            self.cfg.rgb888_en =1
##            self.cfg.out_msb4 =0
#        else:
#            self.cfg.rgb888_en =0
##            self.cfg.out_msb4 =0
    def _embl_cfg_init_hmac(self,cfg,uid):
        dp0 =cfg.oax4k_cfg.dp0
        dp1 =cfg.oax4k_cfg.dp1
        dp2 =cfg.oax4k_cfg.dp2
        dp3 =cfg.oax4k_cfg.dp3
        crypto= cfg.oax4k_cfg.crypto
        dplist = [dp0,dp1,dp2,dp3]
        out0 =cfg.oax4k_cfg.out0
        out1 =cfg.oax4k_cfg.out1
        out2 =cfg.oax4k_cfg.out2
        out3 =cfg.oax4k_cfg.out3
        outlist = [out0,out1,out2,out3]
        doobj=outlist[uid]
        dpobj =dplist[doobj.emblsrc]
        dpemb =doobj.embl
        self.cfg.hmac.inen = dpemb.hmac.inen
        self.cfg.hmac.outen = dpemb.hmac.outen
        self.cfg.hmac.validbyte = dpemb.hmac.vbyte

    def _embl_cfg_init_sta(self,snr,dpemb):
        # self.cfg.sta.innum = snr.embl.sta.num
        self.cfg.sta.innum = dpemb.sta.innum
        self.cfg.sta.ifmt0 = snr.embl.sta.ifmt[0]
        self.cfg.sta.ifmt1 = snr.embl.sta.ifmt[1]
        self.cfg.sta.ifmt2 = snr.embl.sta.ifmt[2]
        self.cfg.sta.ifmt3 = snr.embl.sta.ifmt[3]
        if( self.cfg.sta.ifmt0 <2  or self.cfg.sta.ifmt0 >4  ):
            self.cfg.sta.isel_high =1
        # for i in range(0, 4):
        #     snr.embl.sta.valid_byte[i] = int(snr.embl.sta.valid_byte[i]/12
        #                                      + (snr.embl.sta.valid_byte[i] %12 != 0)) * 12
        # self.cfg.sta.valid_byte0 = snr.embl.sta.valid_byte[0]
        # self.cfg.sta.valid_byte1 = snr.embl.sta.valid_byte[1]
        # self.cfg.sta.valid_byte2 = snr.embl.sta.valid_byte[2]
        # self.cfg.sta.valid_byte3 = snr.embl.sta.valid_byte[3]
        if self.cfg.sta.innum:
            self.cfg.sta.valid_byte0 = dpemb.sta.valid_byte0
            self.cfg.sta.valid_byte1 = dpemb.sta.valid_byte1
            self.cfg.sta.valid_byte2 = dpemb.sta.valid_byte2
            self.cfg.sta.valid_byte3 = dpemb.sta.valid_byte3
            self.cfg.sta.ibyte_sel = snr.embl.sta.ibyte_sel
            self.cfg.sta.vbno = snr.embl.sta.vbno
            self.cfg.sta.dis2nd_line = snr.embl.sta.dis2nd_line
        # print("!!!!!!!!!!sta_dis2nd_line {}".format(self.cfg.sta_dis2nd_line))

    def _embl_cfg_init_crc(self,snr):
        self.cfg.crc.order = snr.embl.crc_order
        self.cfg.crc.rx_sum_inv = snr.embl.crc_inv

    def _embl_cfg_init(self,cfg,uid):
        dp0 =cfg.oax4k_cfg.dp0
        dp1 =cfg.oax4k_cfg.dp1
        dp2 =cfg.oax4k_cfg.dp2
        dp3 =cfg.oax4k_cfg.dp3
        crypto= cfg.oax4k_cfg.crypto
#         crypto_list=[crypto.hst0,crypto.hst1,crypto.hst2,crypto.hst3]
        dplist = [dp0,dp1,dp2,dp3]
        out0 =cfg.oax4k_cfg.out0
        out1 =cfg.oax4k_cfg.out1
        out2 =cfg.oax4k_cfg.out2
        out3 =cfg.oax4k_cfg.out3
        out0.embl.seipre.outnum = int(gens_globals.TopNum, 0)
        out0.embl.seipost.outnum = int(gens_globals.BtmNum, 0)
        outlist = [out0,out1,out2,out3]
        doobj=outlist[uid]
        dpobj =dplist[doobj.emblsrc]
        dpemb =doobj.embl
        yuvchn = doobj.yuv
        rawmvchn = doobj.rawmv
        dpin = dpobj.input
        self.cfg.en =dpemb.en & doobj.en
        if not self.cfg.en:
            return
        if dpobj.dibuf:
            inobj =dpobj.dibuf[0]
        else:
            raise RuntimeError ("current embedded line don't have input source")
        snr  =  inobj.cb_buf[0] if(inobj.cben) else inobj.sensor_buf[dpin.strmsrc]
        # print("embl enable {:d}".format(self.cfg.en))
        rawchn_fmt =  'RAW' if (rawmvchn.sel !=4) else 'YUV'
        embl_chn = 'YUV' if doobj.embl.chn else rawchn_fmt
        if embl_chn == 'YUV':
            if doobj.embl.chn:
                self.cfg.ofmt = prert_yuvfmt_code[doobj.yuv.format]
            else:
                self.cfg.ofmt = prert_yuvfmt_code[doobj.rawmv.format]
        if embl_chn == 'RAW':
            self.cfg.ofmt = prert_rawfmt_code[doobj.rawmv.format]
        self.cfg.tag_en =dpemb.tagen
        self.cfg.tag_data =dpemb.tagdata
        self.cfg.x3a_en = snr.embl.x3a_en
        if self.cfg.x3a_en:
            self.cfg.row1_rm=6
            self.cfg.row2_rm =1
        self.cfg.byte_rate = embl_byterate_dec[self.cfg.ofmt]
        # print('embl format {:s}'.format(self.cfg.ofmt))
        self.cfg.byte_order = 2
        self.cfg.yuv420_en = int('YUV420' in self.cfg.ofmt)
        #self.cfg.presei.inen = dpemb.seipre.inen
        # self.cfg.presei.innum    = snr.embl.pre.num
        self.cfg.presei.innum    = dpemb.seipre.innum
        if self.cfg.presei.innum:
            self.cfg.presei.takebyte = snr.embl.pre.takebyte
            self.cfg.presei.vldbyte  =  snr.embl.pre.len
            if self.cfg.presei.vldbyte % 4 != 0 or (self.cfg.presei.vldbyte<32 and self.cfg.presei.vldbyte!=0):
                raise RuntimeError(f"EMBL sei pre len {self.cfg.presei.vldbyte} must be multiple of 4 and great than 32")
        #self.cfg.postsei.inen = dpemb.postsei.inen
        # self.cfg.postsei.innum    = snr.embl.post.num
        self.cfg.postsei.innum    =  dpemb.seipost.innum
        if self.cfg.postsei.innum:
            self.cfg.postsei.takebyte = snr.embl.post.takebyte
            self.cfg.postsei.vldbyte  = snr.embl.post.len 
        if self.cfg.postsei.vldbyte % 4 != 0 or (self.cfg.postsei.vldbyte<32 and self.cfg.postsei.vldbyte!=0):
            raise RuntimeError(f"EMBL sei post len {self.cfg.postsei.vldbyte} must be multiple of 4 and great than 32")
        self.cfg.preovi.inen = dpemb.ovipre.en
        #self.cfg.preovi.innum = dpemb.ovipre.innum
        #self.cfg.preovi.vldbyte = dpemb.ovipre.vldbyte
        self.cfg.preovi.vldbyteout = dpemb.ovipre.len
        if self.cfg.preovi.vldbyteout % 4 != 0 or (self.cfg.preovi.vldbyteout<32 and self.cfg.preovi.vldbyteout!=0):
            raise RuntimeError(f"EMBL ovi pre len {self.cfg.preovi.vldbyteout} must be multiple of 4 and great than 32")
        self.cfg.postovi.inen = dpemb.ovipost.en
        #self.cfg.postovi.innum = dpemb.ovipost.innum
        #self.cfg.postovi.vldbyte = dpemb.ovipost.vldbyte
        self.cfg.postovi.vldbyteout = dpemb.ovipost.len
        self.cfg.postovi.frmcrcen = dpemb.ovipost.frmcrcen
        if self.cfg.postovi.vldbyteout % 4 != 0 or (self.cfg.postovi.vldbyteout<32 and self.cfg.postovi.vldbyteout!=0):
            raise RuntimeError(f"EMBL ovi post len {self.cfg.postovi.vldbyteout} must be multiple of 4 and great than 32")
        self.cfg.ohsize = doobj.yuv.hsize if dpemb.chn==1 else doobj.rawmv.hsize
        # print("EMBL ovi vldbyteout {} {}" .format(self.cfg.preovi.vldbyteout,self.cfg.postovi.vldbyteout))
        if self.cfg.ofmt == 'RAW14':
            self.cfg.hsize_remainder = self.cfg.ohsize % 6
        else:
            self.cfg.hsize_remainder = self.cfg.ohsize * self.cfg.byte_rate %8
        # self.cfg.postsei =dpemb.seipost
#        self.cfg.out_msb8 =1
        self.cfg.inten =0x3fffbfff if dpemb.inten==1 else 0
        if not (self.cfg.postsei.innum or self.cfg.presei.innum ): # ov2312 or input disable crc check
            self.cfg.fcperren =0xffffbffb # disable input crc check and ahb conflit
        # hmac and sta init tbd
        if crypto.en:
            self._embl_cfg_init_hmac(cfg,uid)
        self._embl_cfg_init_sta(snr,dpemb)
        self._embl_cfg_init_rgb(self.cfg.ofmt)
        self._embl_cfg_init_crc(snr)

    def start(self):
        if self.cfg.en:
            # print("[CRYPO_EMBL]: presei.innum:{},sta.innum:{},hmac.inen:{},hmac.validbyte:{}".format(self.cfg.presei.innum,
            #     self.cfg.sta.innum,self.cfg.hmac.inen,self.cfg.hmac.validbyte))
            sei_swap16 = self.cfg.presei.in_swap16 |  self.cfg.postsei.in_swap16
            b0 =self.cfg.en | (self.cfg.tag_en<<1)| (self.cfg.fcp_en<<2)| (self.cfg.rgb888_swap<<4)| \
                (sei_swap16<<6)| (self.cfg.x3a_en<<7)
            b1 =self.cfg.presei.takebyte |  (self.cfg.presei.innum<<4)
            b2 = (self.cfg.postsei.innum)| (self.cfg.preovi.inen<<4)| (self.cfg.postovi.inen<<5) | (self.cfg.crc.byteorder_bfdtg<<6)| (self.cfg.crc.byteorder_afdtg<<7)
            fault_inj_en=0
            b3 = (self.cfg.sta.innum) | (self.cfg.hmac.inen<<4) | (self.cfg.hmac.outen<<5) |(fault_inj_en<<6) | (self.cfg.hmac.in_32swap<<7)
            r0 = b0 | (b1<<8) | (b2<<16) | (b3<<24)
            self.reg.writereg32(0,r0)
            b0 =self.cfg.hmac.validbyte
            b1 =(self.cfg.yuv420_en) |(self.cfg.crc.tx_msb<<1) |(self.cfg.crc.tx_sum_inv<<2)|(self.cfg.ohsize_sel<<3) |\
                (self.cfg.byte_rate<<4)|(self.cfg.byte_order<<6)
            b2= self.cfg.tag_data
            debug_sel =0
            b3 = (self.cfg.crc.order<<4) | (self.cfg.crc.rx_sum_inv<<5)| (self.cfg.sta.isel_high<<6) |debug_sel
            r4 = b0 | (b1<<8) | (b2<<16) | (b3<<24)
            self.reg.writereg32(4,r4)
            r8 =self.cfg.presei.vldbyte | (self.cfg.sta.iswap<<12)|(self.cfg.postsei.vldbyte<<16)
            self.reg.writereg32(8,r8,mask=BIT28|BIT29|BIT30|BIT31)
            rc = (self.cfg.sta.dis2nd_line << 11)|(self.cfg.row1_rm<<12) |(self.cfg.row2_rm<<28)  #tbd ,abmode
            self.reg.writereg32(0x0c,rc)
            r10 =self.cfg.preovi.vldbyteout | (self.cfg.sta.ifmt0<<12)|(self.cfg.postovi.vldbyteout<<16)|\
                (self.cfg.sta.ifmt1<<28)
            self.reg.writereg32(0x10,r10)
            # print("EMBL ifmt0 {}".format(self.cfg.sta.ifmt0))
            r14 =self.cfg.sta.valid_byte0 | \
                (self.cfg.hsize_remainder<<12) | \
                (self.cfg.sta.valid_byte1<<16)|\
                (self.cfg.sta.vbno<<28)
            # print("EMBL vbno {:x} r14 0x{:x} {:x}".format(self.cfg.sta.valid_byte0, self.cfg.hsize_remainder,self.cfg.sta.valid_byte1))
            r18 =self.cfg.sta.valid_byte2 |(self.cfg.sta.ifmt2<<12)| (self.cfg.sta.valid_byte3<<16)|\
                (self.cfg.sta.ifmt3<<28)
            self.reg.writereg32(0x14,r14)
            self.reg.writereg32(0x18,r18)
            self.reg.writereg32(0x20,self.cfg.inten)
            self.reg.writereg32(0x28,self.cfg.fcperren) #fcp all en
            sei_oswap = self.cfg.presei.out_swap | self.cfg.postsei.out_swap
            ovi_oswap = self.cfg.preovi.out_swap | self.cfg.postovi.out_swap
            sta_o12swap= self.cfg.sta.out12_swap
            sta_outhigh =self.cfg.sta.out_high
            b0 = self.cfg.preovi.dmyln|(self.cfg.postovi.dmyln<<4)
            b1 = embl_ofmt_dict[self.cfg.ofmt] |(sei_oswap<<4)
            b2 = ovi_oswap |  (sta_ofmt_dict[self.cfg.ofmt]<<4)
            b3 = sta_o12swap |(sta_outhigh<<3)| (self.cfg.postsei.takebyte<<4)
            r38 = b0 | (b1<<8) | (b2<<16) | (b3<<24)
            self.reg.writereg32(0x38,r38)
            self.reg.writereg32(0x3c,self.cfg.ohsize | (self.cfg.postovi.frmcrcen<<12))
        #self.reg.writereg16(0x20,0x1234)
        #self.reg.writereg16(0x22,0x0006)
        else:
            self.reg.writereg8(0,0)
