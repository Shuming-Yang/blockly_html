# WARNING
# pylint: disable=C0103, C0114, C0115, C0116, C0200, C0412, W0231, W0401, W0612, W0613, W0614, W0622
from Utility.Reg import REGOBJ
from Utility.Entity import Entity
from Utility.Para import *
from RegTable.Regdefdist import *
from Define.Para import *
from Utility.Others import *


class IMGMT_VC_CFG(object):
    def __init__(self,id):
        self.id =id
        self.href_len =0
        self.ln_num =0
        self.tchken =0
        self.flt_en =0
        self.frmtime =0
        self.href_len =0
        self.erren =0xff
        self.intrsof_en =0
        self.intreof_en =0


class IMGMT_ERR_CFG(object):
    def __init__(self):
        self.sof_mode =0
        self.eof_mode =0
        self.href_mode =0
        self.valid_mode =0
        self.en =0
        self.data_flt =0
        self.glb_en0 =0
        self.glb_en1 =0


class IMGMT_CFG(object):
    def __init__(self,id=0):
        self.index = id
        self.en =0
        self.vc0 =IMGMT_VC_CFG(0)
        self.vc1 =IMGMT_VC_CFG(1)
        self.vc2 =IMGMT_VC_CFG(2)
        self.vc3 =IMGMT_VC_CFG(3)
        self.err = IMGMT_ERR_CFG()
        self.ln_num =0
        self.swap_48b =0
        self.lalign_12b =0
        self.frmtime =0
        self.dt10= 0x2b
        self.dt12 =0x2c
        self.dt14 =0x2d
        self.int_sel =1


class IMGMT_WRAP_CFG(object):
    def __init__(self,chipcfg):
        self.im0 =IMGMT_CFG(0)
        self.im1 =IMGMT_CFG(1)
        self.im2 =IMGMT_CFG(2)
        self.im3 =IMGMT_CFG(3)


class IMGMT_REG(REGOBJ):
    def __init__(self,cfg,uid=0):
        self.base =self.get_baseaddr('IMAGE_MONITOR',define_dist,uid)
        self.regtable=cfg.regtable
        self.objr=[]


class IMGMT(Entity):
    """description of class"""
    def __init__(self,chipcfg,uid=0):
        #self.cfg=mrx_cfg()
        self.cfg =IMGMT_WRAP_CFG(chipcfg)
        self.reg =IMGMT_REG(chipcfg,uid)
        # self._imgmon_cfg_init(chipcfg,uid)
        self._imgmon_cfg_init_new(chipcfg)
        self.setbuf=[]

    def _imgmon_cfg_init_new(self,chipcfg):
        inlist = [chipcfg.oax4k_cfg.in0,chipcfg.oax4k_cfg.in1,chipcfg.oax4k_cfg.in2,chipcfg.oax4k_cfg.in3]
        dpslist = [chipcfg.oax4k_cfg.dp0,chipcfg.oax4k_cfg.dp1,chipcfg.oax4k_cfg.dp2,chipcfg.oax4k_cfg.dp3]
        im0=self.cfg.im0
        im1=self.cfg.im1
        im2=self.cfg.im2
        im3=self.cfg.im3
        ims=[im0,im1,im2,im3]
        for dp in dpslist:
            if(dp.en and dp.input.idcen and dp.input.imgmten):
                inport =inlist[dp.input.portsrc]
                strm =inport.cb_buf[0] if(inport.cben) else inport.sensor_buf[dp.input.strmsrc]
                self._imgmon_strm_init(chipcfg,strm,ims[dp.index],dp.input.portsrc)

    def _imgmon_strm_init(self,chipcfg,img,imt,uid):
        imvc = [imt.vc0,imt.vc1,imt.vc2,imt.vc3]
        ins =  [chipcfg.oax4k_cfg.in0,chipcfg.oax4k_cfg.in1,chipcfg.oax4k_cfg.in2,chipcfg.oax4k_cfg.in3]
        feclks = [chipcfg.oax4k_cfg.sys.clkt.fe0clk,chipcfg.oax4k_cfg.sys.clkt.fe1clk,chipcfg.oax4k_cfg.sys.clkt.fe2clk,chipcfg.oax4k_cfg.sys.clkt.fe3clk]
        totalbase =0
        feclk = feclks[uid]
        inobj = ins[uid]
        imt.en =1
        imt.err.glb_en0 = 1
        imgmt_vldbw_idt_dict ={
            0x2a:8,
            0x2b:10,
            0x2c:12,
            0x2d:14,
            0x2e:16,
            0x2f:20,
            0x1e:8,
            0x1f:10,
            0x1b:12,
            0x27:24,
            }
        imgmt_vldbyte_idt_dict ={
            0x2a:8,
            0x2b:8,
            0x2c:8,
            0x2d:4,
            0x2e:4,
            0x2f:4,
            0x1e:4,
            0x1f:4,
            0x1b:4,
            0x27:4,
            }
        for i in range(len(img.strm.vclist)):
            imvc[totalbase+i].flt_en =0
            imvc[totalbase+i].tchken =1
            imvc[totalbase+i].id =img.strm.vclist[i]
            idt =img.strm.imgdt[i][0]
            # print(idt,"!!!!!!!!!!!!!")
            fmtname =get_dict_key(input_format_dict,img.strm.format&0x3f)
            vld_pix = input_format_vldbit_dict_new96[fmtname] if(inobj.pix_width) else input_format_vldbit_dict_new[fmtname] # pyright: ignore[reportArgumentType]
            vld_bw = imgmt_vldbw_idt_dict[idt]
            vld_byte =  imgmt_vldbyte_idt_dict[idt]
            vld_byte =  vld_byte if(inobj.pix_width) else 4
            # print(fmtname,"!!!!",vld_bw,vld_byte)
            # if(vld_pix%vld_bw or (img.strm.hsize% (vld_pix//vld_bw))):
            if img.strm.hsize% vld_byte:
                print(f"!!!!immt{uid} href len cal can't div vald byte {img.strm.hsize} {vld_byte}")
                imvc[totalbase+i].href_len =img.strm.hsize // vld_byte +1 # tbd ,
            else:
                imvc[totalbase+i].href_len =img.strm.hsize // vld_byte  # tbd ,
                # print("imgmt vc{} {} {} {}".format(i,vld_pix,vld_bw,imvc[totalbase+i].href_len))
            if img.strm.imgmode ==2:  # line intl mode
                _,_,exponum =idc_mem_hsize_div_dict[fmtname] # pyright: ignore[reportArgumentType]
                imvc[totalbase+i].ln_num =(img.strm.vsize + img.embl.pre.num +img.embl.post.num +img.embl.sta.chn_num)*exponum
            elif img.strm.imgmode ==1:
                _,_,exponum =idc_mem_hsize_div_dict[fmtname] # pyright: ignore[reportArgumentType]
                imvc[totalbase+i].href_len =imvc[totalbase+i].href_len* exponum
                imvc[totalbase+i].ln_num =img.strm.vsize + img.embl.pre.num +img.embl.post.num +img.embl.sta.chn_num
            else:
                imvc[totalbase+i].ln_num =img.strm.vsize + img.embl.pre.num +img.embl.post.num +img.embl.sta.chn_num
            imvc[totalbase+i].frmtime =int(img.strm.hts *img.strm.vts* feclk/img.strm.sclk*2)
            # print("[IMGMNT] hts {} vts {} feclk {} snr sclk {} fmttime {}".format(img.strm.hts, img.strm.vts, feclk, img.strm.sclk, imvc[totalbase+i].frmtime))
            if imt.int_sel:
                if i ==len(img.strm.vclist) -1:  # select last channel as sof source
                    imvc[totalbase+i].intrsof_en =1
            else:                                  # select first channel as sof
                if i ==0:
                    imvc[totalbase+i].intrsof_en =1
        # print("image mt{} in{} vc{} total {}".format(imt.index,uid,img.strm.vclist,i))
        #snrsclk =inobj.sclk
        # self.cfg.frmtime =int(img.strm.hts *img.strm.vts*img.strm.sclk /feclk*2)
        # self.cfg.ln_num =img.strm.vsize + img.embl.pre.num +img.embl.post.num +img.embl.sta.num
        #print(self.cfg.ln_num,img.ctrl)
        #print(inobj.index,img.ctrl.pwdn_id)
        # totalbase = totalbase + len(img.strm.vclist)

    def path_start(self,imt):
        if imt.en:
            (vc0,vc1,vc2,vc3,err)=(imt.vc0,imt.vc1,imt.vc2,imt.vc3,imt.err)
            r0 =vc0.id | (vc1.id<<8) |(vc2.id<<16) |(vc3.id<<24) | (err.glb_en0<<30) |(err.glb_en1<<31)
            r4= (err.sof_mode<<0) |(err.eof_mode<<2) |(err.href_mode<<4) |(err.valid_mode<<6) |\
                (err.data_flt<<9) |(imt.swap_48b<<10) |(imt.lalign_12b<<11) |\
                (vc0.flt_en<<12)|(vc1.flt_en<<13)|(vc2.flt_en<<14)|(vc3.flt_en<<15)|\
                (vc0.tchken<<28)|(vc1.tchken<<29)|(vc2.tchken<<30)|(vc3.tchken<<31)
            r8  =vc0.frmtime
            rc  =vc1.frmtime
            r10 =vc2.frmtime
            r14 =vc3.frmtime
            r1c =imt.dt10 | (imt.dt12<<8) |(imt.dt14<<16)
            r20 =vc0.href_len | (vc1.href_len<<16)
            r24 =vc2.href_len | (vc3.href_len<<16)
            r28 =vc0.ln_num | (vc1.ln_num<<16)
            r2c =vc2.ln_num | (vc3.ln_num<<16)
            r30 = vc0.erren | (vc1.erren<<8) |(vc2.erren<<16) | (vc3.erren<<24)
            r34 =   (vc0.intrsof_en<<0) |  (vc0.intreof_en<<1) |\
                    (vc1.intrsof_en<<2) |  (vc1.intreof_en<<3) |\
                    (vc2.intrsof_en<<4) |  (vc2.intreof_en<<5) |\
                    (vc3.intrsof_en<<6) |  (vc3.intreof_en<<7)
            self.reg.writereg32(0+imt.index*0x80,r0)
            self.reg.writereg32(4+imt.index*0x80,r4)
            self.reg.writereg32(8+imt.index*0x80,r8)
            self.reg.writereg32(0x0c+imt.index*0x80,rc)
            self.reg.writereg32(0x10+imt.index*0x80,r10)
            self.reg.writereg32(0x14+imt.index*0x80,r14)
            # self.reg.writereg32(0x18+imt.index*0x80,r18)
            self.reg.writereg32(0x1c+imt.index*0x80,r1c)
            self.reg.writereg32(0x20+imt.index*0x80,r20)
            self.reg.writereg32(0x24+imt.index*0x80,r24)
            self.reg.writereg32(0x28+imt.index*0x80,r28)
            self.reg.writereg32(0x2c+imt.index*0x80,r2c)
            self.reg.writereg32(0x30+imt.index*0x80,r30)
            self.reg.writereg8(0x34+imt.index*0x80,r34)

    def start(self):
        self.path_start(self.cfg.im0)
        self.path_start(self.cfg.im1)
        self.path_start(self.cfg.im2)
        self.path_start(self.cfg.im3)
