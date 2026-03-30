# WARNING
# pylint: disable=C0103, C0114, C0115, C0116, C0200, C0412, W0201, W0231, W0401, W0612, W0613, W0614, W0622
from Utility.Reg import REGOBJ
from Utility.Entity import Entity
from Utility.Para import *
from Define.Para import *
from Utility.Others import *
from RegTable.Regdefdist import define_dist


vc_mode_dist={
    0:(1,0),
    1:(0,0,0,0),
    2:(0,1,0,0),
    3:(0,1,0,1),
    4:(0,1,1,0),
    5:(0,1,1,1),
}


mipirx_lane_enable_dict={
    0:(0,0,0,0),
    1:(1,0,0,0),
    2:(1,1,0,0),
    3:(1,1,1,0),
    4:(1,1,1,1),
}


class MRX_IDDT_CFG(object):
    def __init__(self):
        self.snrid =0
        self.intdt =0


class EMBL_LINECNT_CFG(object):
    def __init__(self):
        self.pre_num =0
        self.post_num =0
        self.vsize =0


class MRX_VC_CFG_NEW(object):
    def __init__(self,id):
        self.index =id
        self.mode =0
        self.line = EMBL_LINECNT_CFG()
        self.imgs=[]
        self.embs=[]


class MRX_LANE_CFG(object):
    def __init__(self,id):
        self.index =id
        self.en =0
        self.lpfunc_en =0
        self.calib_en =0
        self.sel =id # lane select


class MRX_CSI_CFG(object):
    def __init__(self):
        self.vc_num =1
        self.dflt_mode =0
        self.csi_ver =1
        self.descramble_en =0
        self.lrte_en = 0
        self.ln0=MRX_LANE_CFG(0)
        self.ln1=MRX_LANE_CFG(1)
        self.ln2=MRX_LANE_CFG(2)
        self.ln3=MRX_LANE_CFG(3)
        self.clk=MRX_LANE_CFG(4)
        self.crc_err_inj =0
        self.ecc1_err_inj =0
        self.ecc2_err_inj =0
        self.errst_inten =1  # tbd
        self.vc_mon_sel =0
        self.int_en0=0xffffffff
        self.int_en1 =0x1ffff
        self.pix_width_en0 = 0  # for raw8,raw10
        self.pix_width_en1 = 0  # for raw12
        self.lineint_num  =100
        self.descramble_seedL0 = 0x10
        self.descramble_seedH0 = 0x08
        self.descramble_seedL1 = 0x90
        self.descramble_seedH1 = 0x09
        self.descramble_seedL2 = 0x51
        self.descramble_seedH2 = 0x0a
        self.descramble_seedL3 = 0xd0
        self.descramble_seedH3 = 0x0b


class MRX_CFG(object):
    def __init__(self,chipcfg):
        self.vcbuf =[]
        self.csi = MRX_CSI_CFG()
        self.abm_en =0 #tbd
        self.a_frm_vc_id = 0
        self.b_frm_vc_id = 1
        self.a_frm_num = 1
        self.b_frm_num = 1
        # self.descramble_seed = 0

    def config(self):
        pass


class MRX_REG(REGOBJ):
    def __init__(self,cfg,uid=0):
        self.base =self.get_baseaddr('MIPI_RX_',define_dist,uid)
        self.regtable=cfg.regtable
        self.objr=[]


class MIPIRX(Entity):
    """description of class"""
    def __init__(self,chipcfg,uid=0):
        #self.cfg=mrx_cfg()
        self.cfg =MRX_CFG(chipcfg)
        self.reg =MRX_REG(chipcfg,uid)
        self.setbuf=[]
        self._mipirx_cfg_init(chipcfg,uid)
        self.index = uid

    def _mipirx_cfg_init(self,chipcfg,uid):
        # print("mipirx_cfg_init {}".format(uid))
        csi =self.cfg.csi
        inlist = [chipcfg.oax4k_cfg.in0,chipcfg.oax4k_cfg.in1,chipcfg.oax4k_cfg.in2,chipcfg.oax4k_cfg.in3]
        inobj = inlist[uid]
        #sensor_cfg = inobj.sensor_buf[uid]
        imgbuf = inobj.cb_buf if(inobj.cben) else inobj.sensor_buf
        phyclk = inobj.phyclk
        lpfen = inobj.lpfen
        #>1.5G
        phy_calib_en =1 if(phyclk>=1500*1000000) else 0
        phy_calib_en =inobj.deskew_en
        csi.ln0.en,csi.ln1.en,csi.ln2.en,csi.ln3.en = mipirx_lane_enable_dict[inobj.lane_num]
        if inobj.cben==0:
            # csi.ln0.lpfunc_en,csi.ln1.lpfunc_en,csi.ln2.lpfunc_en,csi.ln3.lpfunc_en = mipirx_lane_enable_dict[img.strm.lane_num]
            lanelist = [csi.ln0,csi.ln1,csi.ln2,csi.ln3,csi.clk]
            # alllist =[item for item in mipirx_lane_enable_dict[img.strm.lane_num]]
            alllist =[item for item in mipirx_lane_enable_dict[inobj.lane_num]]
            alllist.append(1)
            for i in range(len(lanelist)):
                lanelist[i].lpfunc_en =alllist[i] &lpfen  #tbd
                lanelist[i].calib_en = alllist[i] &phy_calib_en
            # todo
        #csi.lrte_en = imgbuf[0].strm.lrte_en
        #print("lrte_en = ", csi.lrte_en)
        if imgbuf[0].strm.descramble_en:
            csi.descramble_en = imgbuf[0].strm.descramble_en
            csi.descramble_seedL0 = imgbuf[0].strm.descramble_seedL0
            csi.descramble_seedH0 = imgbuf[0].strm.descramble_seedH0
            csi.descramble_seedL1 = imgbuf[0].strm.descramble_seedL1
            csi.descramble_seedH1 = imgbuf[0].strm.descramble_seedH1
            csi.descramble_seedL2 = imgbuf[0].strm.descramble_seedL2
            csi.descramble_seedH2 = imgbuf[0].strm.descramble_seedH2
            csi.descramble_seedL3 = imgbuf[0].strm.descramble_seedL3
            csi.descramble_seedH3 = imgbuf[0].strm.descramble_seedH3
        if not inobj.cben:
            self._cfg_ab_mode(imgbuf)
        # else:
        #     print("mrx input is colorbar")
        self._cfg_vc(imgbuf)
        self.cfg.pix_width_en0 = inobj.pix_width # pyright: ignore[reportAttributeAccessIssue]
        self.cfg.pix_width_en1 = inobj.pix_width # pyright: ignore[reportAttributeAccessIssue]

    def _cfg_ab_mode(self, imgbuf):
        self.cfg.abm_en = imgbuf[0].ab_mode
        if not self.cfg.abm_en:
            # print("abmode not enable, do not need to config mrx ab mode")
            return
        self.cfg.a_frm_vc_id = imgbuf[0].a_vc_id
        self.cfg.b_frm_vc_id = imgbuf[0].b_vc_id
        self.cfg.a_frm_num = imgbuf[0].a_frm_num
        self.cfg.b_frm_num = imgbuf[0].b_frm_num
        print(f"mrx ab_mode {self.cfg.abm_en}, a_frm_vc_id {self.cfg.a_frm_vc_id}, b_frm_vc_id {self.cfg.b_frm_vc_id}, a_frm_num {self.cfg.a_frm_num}, b_frm_num {self.cfg.b_frm_num}")
    def _cfg_vc(self, imgbuf):
        csi = self.cfg.csi
        csi.vc_num = 0
        for img in imgbuf:
            #csi.vc_num = max(csi.vc_num, img.strm.vclist)
            csi.vc_num = max(csi.vc_num, max(img.strm.vclist))
            for i in range(len(img.strm.vclist)):
                vctmp =MRX_VC_CFG_NEW(img.strm.vclist[i])
                embchn =MRX_IDDT_CFG()
                for idx in range(len(img.strm.imgid[i])):
                    imgchn=MRX_IDDT_CFG()
                    imgchn.snrid=img.strm.imgid[i][idx]
                    imgchn.intdt=img.strm.imgdt[i][idx]
                    vctmp.imgs.append(imgchn)
                if(img.embl.linemode and img.embl.en):
                    vctmp.mode =0
                    vctmp.line.pre_num = img.embl.pre.num
                    vctmp.line.post_num = img.embl.post.num
                    if img.embl.sta.en:
                        vctmp.line.post_num += img.embl.sta.chn_num
                    vctmp.line.vsize =img.strm.vsize
                else:
                    embids=[]
                    for idx in range(len(img.strm.embid[i])):
                        embchn=MRX_IDDT_CFG()
                        embchn.snrid=img.strm.embid[i][idx]
                        # if(embchn.snrid not in embids):
                        #     embids.append( embchn.snrid)
                        # else:
                        #     raise RuntimeError("embedded line dt mode ,dt {} and ids {} should be different".format(embchn.snrid,embids ))
                        embchn.intdt=img.strm.imgdt[i][0]
                        # print("!!!",embchn.snrid,embchn.intdt)
                        if embchn.snrid ==embchn.intdt:
                            raise RuntimeError(f"embedded line dt mode ,dt {embchn.snrid} and idt {embchn.intdt} should be different")
                        vctmp.embs.append(embchn)
                    vctmp.mode =len(vctmp.embs)+1
                self.cfg.vcbuf.append(vctmp)

    def _mipirx_vc_set(self,vc):
        r64 =0
        for i in range(len(vc.imgs)):
            r64  = r64 | ((vc.imgs[i].snrid |(vc.imgs[i].intdt<<6) )<<12*i )
        if vc.mode ==0:
            r64 =r64 | (vc.line.vsize<<24) |(vc.line.pre_num<<56) |(vc.line.post_num<<59) | (1<<63)
        else:
            embllen =len(vc.embs)
            # print("!!!{}".format(embllen))
            for i in range(embllen,0,-1):
                r64  = r64 | ((vc.embs[embllen-i].snrid |(vc.embs[embllen-i].intdt<<6) )<<(60-12*i) )
            b63,b62,b61,b60 =vc_mode_dist[vc.mode]
            r64  =r64 | (b63<<63) |(b62<<62)|(b61<<61)|(b60<<60)
        r0 = r64 &0xffffffff
        r4 = (r64 >>32)&0xffffffff
        self.reg.writereg32(vc.index*8,r0,save_force=1)
        self.reg.writereg32(vc.index*8+4,r4,save_force=1)

    def _mipirx_vc_start(self):
        #csi =self.cfg.csi
        for vc in self.cfg.vcbuf:
            self._mipirx_vc_set(vc)
        self.reg.writereg8(0x20c,1)
        self.reg.writereg8(0x20c,0)

    def _mipirx_csi_start(self):
        csi =self.cfg.csi
        print("csi.descramble_en =", csi.descramble_en)
        lane0 =self.cfg.csi.ln0
        lane1 =self.cfg.csi.ln1
        lane2 =self.cfg.csi.ln2
        lane3 =self.cfg.csi.ln3
        lanec =self.cfg.csi.clk
        r204 = lane0.sel | (lane1.sel<<2) |(lane2.sel<<4)|(lane3.sel<<6) |\
                (csi.vc_mon_sel<<8) |  (lane0.lpfunc_en<<16) | (lane1.lpfunc_en<<17)|(lane2.lpfunc_en<<18)|(lane3.lpfunc_en<<19) |\
                (lane0.calib_en<<20) | (lane1.calib_en<<21)|(lane2.calib_en<<22)|(lane3.calib_en<<23) |(lanec.lpfunc_en<<24)
        r220 = csi.int_en0
        r224 = csi.int_en1
        r200 = csi.dflt_mode | (csi.csi_ver<<2) | (2<<5) |(csi.vc_num<<8) |(csi.descramble_en<<13) |(self.cfg.abm_en<<15) |\
            (lane0.en<<16) |(lane1.en<<17) |(lane2.en<<18) |(lane3.en<<19) |\
            (csi.crc_err_inj<<20) |(csi.ecc1_err_inj<<21)|(csi.ecc2_err_inj<<22) |(csi.errst_inten<<23) |\
                (self.cfg.pix_width_en0<<29) |   (self.cfg.pix_width_en1<<30) # pyright: ignore[reportAttributeAccessIssue]
        if csi.int_en0 or csi.int_en1:
            r200 = r200 | BIT27 # global intr en
        r20c = (((self.cfg.a_frm_vc_id & 0xf) << 8)
                + ((self.cfg.b_frm_vc_id & 0xf) << 12)
                + ((self.cfg.a_frm_num & 0xff) << 16)
                + ((self.cfg.b_frm_num & 0xff) << 24))
        # print("r20c 0x{:x} a_frm_num {} b_frm_num {}".format(r20c, self.cfg.a_frm_num, self.cfg.b_frm_num))
        # descramble seed value
        r214 = csi.descramble_seedL0
        r215 = csi.descramble_seedH0
        r216 = csi.descramble_seedL1
        r217 = csi.descramble_seedH1
        r218 = csi.descramble_seedL2
        r219 = csi.descramble_seedH2
        r21a = csi.descramble_seedL3
        r21b = csi.descramble_seedH3
        # end
        r20a = csi.lineint_num
        self.reg.writereg32(0x200,r200)
        self.reg.writereg32(0x204,r204)
        self.reg.writereg16(0x20a,r20a)
        self.reg.writereg32(0x20c,r20c)
        self.reg.writereg32(0x220,r220)
        self.reg.writereg32(0x224,r224)
        if csi.descramble_en:
            self.reg.writereg8(0x214,r214)
            self.reg.writereg8(0x215,r215)
            if self.index in (0, 2):
                self.reg.writereg8(0x216,r216)
                self.reg.writereg8(0x217,r217)
                self.reg.writereg8(0x218,r218)
                self.reg.writereg8(0x219,r219)
                self.reg.writereg8(0x21a,r21a)
                self.reg.writereg8(0x21b,r21b)

    def start(self):
        self._mipirx_csi_start()
        self._mipirx_vc_start()
