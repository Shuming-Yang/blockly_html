
# WARNING
# pylint: disable=C0103, C0114, C0115, C0200, C0412, W0231, W0401, W0612, W0613, W0614, W0622
from Utility.Reg import REGOBJ
from Utility.Entity import Entity
from Utility.Para import *
from Define.Para import *
from Utility.Others import *
from RegTable.Regdefdist import define_dist


class IDP_ITPG_CFG():
    def __init__(self):
        self.lum_en =0
        self.load_seed =1
        self.rand_en =0
        self.ch1_shift =0
        self.ch2_shift =0
        self.ch3_shift =0
        #self.start_mode =0


class IDP_COMMON_CFG():
    def __init__(self):
        self.img_en =0
        self.rgbir_en =0
        self.byp_mode =0
        self.swset_err =0
        self.sof_err_mode =1   # 0: not err ,1: tie to 0 2: tie to high 3: inv
        self.eof_err_mode =1
        self.href_err_mode =1
        self.vld_err_mode =1
        self.hblank_cont =100
        self.rgbir_hblk =150
        self.rgbir_h2tblk =640
        self.pre_rd_cnt =0
        self.err_ctrl =0x1e20
        self.itpg =IDP_ITPG_CFG()


class IDP_PATH_CFG():
    def __init__(self,id):
        self.index =id
        self.en =0
        self.safe_en =0
        self.rgbir_en =0
        self.byp_en =0
        self.rgbir_dmy_en =0
        self.rgbir_tp_en =0
        self.dmy_en =0
        self.tp_en =0
        self.err_inj =0
        self.sen_fmt =0
        self.sen_id =id
        self.sen_hsize =0
        self.sen_vsize =0
        self.rgbir_dmy_num =0
        self.rgbir_tp_num =0
        self.dmy_num =0
        self.tp0_num =0
        self.tp1_num =0
        self.sof_dly_cnt =0
        self.eof_dly_cnt =0
        self.frm_time =0
        self.pix_num =0
        self.rgbir_abmode =0
        self.rgbir_amsk =0
        self.rgbir_bmsk =0
        self.rgbir_afrmnum =1
        self.rgbir_bfrmnum =1
        self.rgbir_vsync_sel =id
        self.ispdmyln_mode =0
        self.isp_datbit_fix =0
        self.ispdup_datbit_fix =0
        self.lfm_datbit_fix =0
        self.eof_chk_sel =1
        self.dmytest_ready_cycle =100
        self.err_chk_en =0x3ff
        self.rgbir_dmytest_ready_cycle =100
        self.ispdata_chn0_pos =0 #the position1 for channel data 0:{L:X,X,X} 1:{X:L:X:X} 2:{X:X:L:X} 3:{X:X:X:L}
        self.ispdata_chn1_pos =1
        self.ispdata_chn2_pos =2
        self.ispdata_chn3_pos =3


class IDP_CFG(object):
    def __init__(self,chipcfg):
        self.cmmn =IDP_COMMON_CFG()
        self.path0 =IDP_PATH_CFG(0)
        self.path1 =IDP_PATH_CFG(1)
        self.path2 =IDP_PATH_CFG(2)
        self.path3 =IDP_PATH_CFG(3)


class IDP_REG(REGOBJ):
    def __init__(self,cfg,uid=0):
        self.base =self.get_baseaddr('IDP',define_dist,uid)
        self.regtable=cfg.regtable
        self.objr=[]


class IDP(Entity):
    """description of class"""
    def __init__(self,chipcfg,uid=0):
        #self.cfg=mrx_cfg()
        self.cfg =IDP_CFG(chipcfg)
        self.reg =IDP_REG(chipcfg,uid)
        self.setbuf=[]
        self._idp_cfg_init(chipcfg)

    def _idp_path_init(self,idpp,dp,chipcfg):
        dpin =dp.dibuf[0]
        ispin =dp.isp.inbuf[0]
        idpp.en =dp.en
        # idpp.sen_fmt = 5 if(ispin.format==50) else ispin.format
        # # idpp.sen_fmt = 14 if(idpp.sen_fmt==15) else idpp.sen_fmt
        # idpp.sen_fmt = 12 if(idpp.sen_fmt==120) else idpp.sen_fmt
        # idpp.sen_fmt = 6 if (idpp.sen_fmt == 16) else idpp.sen_fmt
        # idpp.sen_fmt = 7 if (idpp.sen_fmt == 17) else idpp.sen_fmt
        # idpp.sen_fmt = 8 if (idpp.sen_fmt == 18) else idpp.sen_fmt
        idpp.sen_fmt = ispin.format &0x3f
        # for RAW2X10, RAW3X10 RAW4X10 case, left shift image data 2 bits, to treat it like RAW12
        if idpp.sen_fmt in [1, 0xc, 0xf]:
            if idpp.rgbir_en:
                idpp.isp_datbit_fix = 0x0
                idpp.ispdup_datbit_fix = 0x2
            # else:
            #     path.isp_datbit_fix = 0x2
            #     path.ispdup_datbit_fix = 0x2
        elif idpp.sen_fmt == 4:     # yuv in
            idpp.isp_datbit_fix = 0x0
            idpp.ispdup_datbit_fix = 0x4
            idpp.lfm_datbit_fix = 0x4
        elif idpp.sen_fmt == 13 and chipcfg.oax4k_cfg.out0.rawmv.idcsel == 2:     # RAW10 can not saturate
            idpp.isp_datbit_fix = 0x0
            idpp.ispdup_datbit_fix = 0x2
            idpp.lfm_datbit_fix = 0x0
        else:
            idpp.isp_datbit_fix = 0x0
            idpp.ispdup_datbit_fix = 0x0
            idpp.lfm_datbit_fix = 0x0
        if idpp.sen_fmt ==4: # yuv in
            if dp.yuvin_mode:
                idpp.sen_fmt =8
        if idpp.sen_fmt ==3: # 2x11 in,swap l/v,s to s,l/v for isp
            idpp.ispdata_chn0_pos =1
            idpp.ispdata_chn1_pos =0
        idpp.sen_hsize =ispin.hsize
        idpp.sen_vsize =ispin.vsize
        idpp.pix_num = idpp.sen_hsize *idpp.sen_vsize
        #snrsclk = snr.strm.sclk
        chip = chipcfg.oax4k_cfg
        dpclk =chip.sys.clkt.dpclk
        #snrsclk =snr.strm.sclk *cclks[inobj.cclk_idx]/24000000
        idpp.frm_time =int(ispin.hts *ispin.vts * dpclk/ispin.sclk)# tbd, clock domain switch
        frm_time1 = dpclk/ispin.fps
        # print(idpp.frm_time,frm_time1,"fpstest")
        idpp.safe_en =  dp.input.safe_en
        rgbirouten = 1 if(dp.index < len(chip.rgbir.outs)) else 0
        # idpp.rgbir_en =chip.rgbir.en & rgbirouten# tbd
        idpp.rgbir_en =dp.rgbiren
        idpp.pix_num = ispin.hsize *ispin.vsize
        round_robin_cycle =24
        dphts = int(2*ispin.hts*dpclk/ispin.sclk)
        idpp.dmytest_ready_cycle = max((dphts- ispin.hsize - chipcfg.oax4k_cfg.topctrl.idp_hblk-round_robin_cycle),chipcfg.oax4k_cfg.topctrl.idp_hblk)
        # print("!!!!idp inhts {} dpths{} tphblk{}".format(dphts,ispin.hts,idpp.dmytest_ready_cycle ))
        idpp.dmy_en = dp.input.dmy_en
        idpp.ispdmyln_mode = dp.input.dmy_mode
        idpp.tp_en = dp.input.itpgen # tbd
        idpp.byp_en = dp.bypisp
        if idpp.byp_en:
            idpp.tp_en =0
            idpp.dmy_en =0
        if idpp.rgbir_en:
            rgbir_dps=[chip.rgbir.dp0,chip.rgbir.dp1]
            rgbir_cfg =rgbir_dps[int(idpp.index/2)]
            idpp.dmy_num =4
            idpp.rgbir_dmy_num =rgbir_cfg.dmynum
            idpp.rgbir_dmy_en =rgbir_cfg.dmyen
            idpp.rgbir_tp_en =rgbir_cfg.tpen
            idpp.rgbir_tp_num =rgbir_cfg.tpnum
            idpp.tp0_num = dp.input.partp_num# par
            idpp.tp1_num = dp.input.sertp_num # ser_num
            idpp.sof_dly_cnt =16
            # idpp.eof_dly_cnt = ispin.hts
            idpp.eof_dly_cnt = 16
            fmt_type_name=get_dict_key(sensor_input_format_type_top_dict,ispin.format_tid >>4)
            exponum = sensor_expo_num_dict[fmt_type_name]  # pyright: ignore[reportArgumentType]
            idpp.rgbir_dmytest_ready_cycle = max(dphts - (ispin.hsize +rgbir_cfg.exphblk)*exponum,chipcfg.oax4k_cfg.topctrl.idp_hblk)
            # print("rgbir dmy test line cycle {} exponum{} hts {}".format(idpp.rgbir_dmytest_ready_cycle,exponum,ispin.hts))
            rgbir_cfg_path = rgbir_cfg.ir  if(idpp.index %2) else  rgbir_cfg.raw
            idpp.rgbir_abmode =rgbir_cfg_path.abmode
            idpp.rgbir_afrmnum =rgbir_cfg_path.afrmnum
            idpp.rgbir_bfrmnum =rgbir_cfg_path.bfrmnum
            idpp.rgbir_amsk =rgbir_cfg_path.amask
            idpp.rgbir_bmsk  =rgbir_cfg_path.bmask
            idpp.rgbir_vsync_sel = rgbir_cfg.chnbase
            # print("rgbir idp new config ab mode {} {} {} ".format(idpp.rgbir_abmode,idpp.rgbir_amsk,idpp.rgbir_bmsk))
        else:
            idpp.dmy_num = dp.input.dmy_num
            idpp.rgbir_dmy_num =16
            idpp.rgbir_tp_num =16
            idpp.tp0_num = dp.input.partp_num  # par
            idpp.tp1_num = dp.input.sertp_num  # ser_num
            idpp.sof_dly_cnt =16
            idpp.eof_dly_cnt =16

    def _idp_cmmn_init(self,chipcfg):
        cmmn =self.cfg.cmmn
        dplist = [ chipcfg.oax4k_cfg.dp0,chipcfg.oax4k_cfg.dp1,chipcfg.oax4k_cfg.dp2,chipcfg.oax4k_cfg.dp3]
        dp_rgbiren=0
        for dp in dplist:
            dp_rgbiren=dp_rgbiren |dp.rgbiren
        cmmn.rgbir_en,cmmn.img_en =(1,0) if (chipcfg.oax4k_cfg.rgbir.en and dp_rgbiren) else (0,1)
        cmmn.itpg.lum_en,cmmn.itpg.rand_en =(1,0) if (chipcfg.oax4k_cfg.topctrl.isptp_mode) else (0,1)
        # cmmn.itpg.ch1_shift =1
        # cmmn.itpg.ch2_shift =2
        # cmmn.itpg.ch3_shift =3
        #cmmn.hblank_cont= 100
        cmmn.pre_rd_cnt =8
        # cmmn.byp_mode =chipcfg.oax4k_cfg.topctrl.bypmode

    def _idp_cfg_init(self,chipcfg):
        dplist =[chipcfg.oax4k_cfg.dp0,chipcfg.oax4k_cfg.dp1,chipcfg.oax4k_cfg.dp2,chipcfg.oax4k_cfg.dp3]
        idplist =[self.cfg.path0,self.cfg.path1,self.cfg.path2,self.cfg.path3]
        clkt =chipcfg.oax4k_cfg.sys.clkt
        idpblk = chipcfg.oax4k_cfg.topctrl.idp_hblk
        htsmin =0xffff
        path_rgbiren_cnt =0
        rgbirhts_buf=[]
        hblkorg = idpblk
        for i in range(len(dplist)):
            if dplist[i].en:
                path_rgbiren_cnt = path_rgbiren_cnt + dplist[i].rgbiren
                self._idp_path_init(idplist[i],dplist[i],chipcfg)
                dihts = dplist[i].isp.inbuf[0].hts
                dihsize = dplist[i].isp.inbuf[0].hsize
                infmt = dplist[i].isp.inbuf[0].format
                dphts = int(2*dihts*clkt.dpclk/dplist[i].input.sclk)
                htsmin = min(htsmin,dphts)
                fmt_name = get_dict_key(input_format_dict,infmt)
                if dplist[i].rgbiren:
                    if fmt_name in ['12+SPD10', '16+SPD10','SPD_RAW10']:
                        mulfactor = 2  # need ,double check
                    else:
                        vldbit,mulfactor =colorbar_wordcnt_dict[fmt_name]  # pyright: ignore[reportArgumentType]
                else:
                    mulfactor = 1
                hblkmin = int(htsmin/mulfactor) -dihsize
                if hblkmin <100:
                    raise RuntimeError(f"the hblk{hblkmin} is too small for idc htsmin {htsmin} mul{mulfactor} hsize{dihsize}")
                hblkorg = int(htsmin/mulfactor) -dihsize
                # hblkorg = int(2*(dihts-dihsize)*clkt.dpclk/dplist[i].input.sclk/mulfactor)
                rgbirhts_buf.append(dihts)
        self.cfg.cmmn.hblank_cont =min(hblkorg,idpblk)
        # print("!!!!!!!!!!!!!!!",hblkorg,idpblk,htsmin,mulfactor,fmt_name)
        # self.cfg.cmmn.rgbir_hblk  = chipcfg.oax4k_cfg.topctrl.rgbir_hblk
        self.cfg.cmmn.rgbir_hblk  = chipcfg.oax4k_cfg.rgbir.lnhblk
        self.cfg.cmmn.rgbir_h2tblk  = min(tuple(rgbirhts_buf))
        self.cfg.cmmn.rgbir_h2tblk  = chipcfg.oax4k_cfg.rgbir.ln2tphblk
        # if( chipcfg.oax4k_cfg.rgbir.en and path_rgbiren_cnt):
        #     self.cfg.cmmn.hblank_cont = self.cfg.cmmn.rgbir_hblk
        # print(self.cfg.cmmn.rgbir_h2tblk,self.cfg.cmmn.hblank_cont ,"~~~~~~")
        self._idp_cmmn_init(chipcfg)

    def _idp_common_start(self):
        cmmn =self.cfg.cmmn
        r30 = (cmmn.img_en<<0) |(cmmn.rgbir_en<<1) |(cmmn.swset_err<<2) |(cmmn.sof_err_mode<<8) |\
            (cmmn.eof_err_mode<<10)|(cmmn.href_err_mode<<12) |(cmmn.vld_err_mode<<14) |\
            (cmmn.itpg.rand_en<<16)| (cmmn.itpg.lum_en<<17)| (cmmn.itpg.load_seed<<18)| \
            (cmmn.itpg.ch1_shift<<20)| (cmmn.itpg.ch2_shift<<24)|(cmmn.itpg.ch3_shift<<28)
        rgbir_rdln_hblk_l = cmmn.rgbir_hblk&0xff
        rgbir_rdln_hblk_h = (cmmn.rgbir_hblk>>8) &0x07
        r38 = (cmmn.hblank_cont<<0) |(cmmn.pre_rd_cnt<<16) |(rgbir_rdln_hblk_l<<24)
        self.reg.writereg32(0x30,r30)
        self.reg.writereg32(0x38,r38)
        self.reg.writereg32(0x3c, cmmn.err_ctrl | (rgbir_rdln_hblk_h<<13) |(cmmn.rgbir_h2tblk<<16) ) # fcp en

    def _idp_path_start(self,path):
        if path.en:
            r0 = path.en |(path.safe_en<<1)|(path.byp_en<<2)|(path.rgbir_en<<3)|\
                (path.rgbir_dmy_en<<4)|(path.rgbir_tp_en<<5)|(path.dmy_en<<6)|(path.tp_en<<7)|\
                (path.err_inj<<8)|(path.ispdmyln_mode<<10) | (path.rgbir_abmode<<11) | (path.rgbir_amsk<<12)|(path.rgbir_bmsk<<13)|\
                (path.sen_fmt<<16)|(path.sen_id<<20) |(path.sen_id<<22) | (path.eof_chk_sel<<24) |(path.lfm_datbit_fix<<25)
            r4 = path.sen_hsize | (path.sen_vsize<<16)
            r8 = path.rgbir_dmy_num |(path.rgbir_tp_num<<8) | (path.rgbir_afrmnum<<16) |(path.rgbir_bfrmnum<<24)
            rc = (path.dmy_num<<24)|( path.tp0_num<<8)|( path.tp1_num<<16)
            r10 =path.sof_dly_cnt | (path.eof_dly_cnt<<16)
            r14 =int(path.frm_time * 2)
            r18= path.pix_num >> 1
            isp_datchn_pos = (path.ispdata_chn0_pos <<0) |(path.ispdata_chn1_pos <<2) |(path.ispdata_chn2_pos <<4) |(path.ispdata_chn3_pos <<6)
            r20 =path.isp_datbit_fix |(path.ispdup_datbit_fix <<4) | (isp_datchn_pos<<8) | (path.rgbir_vsync_sel<<16) | (path.dmytest_ready_cycle<<18)
            r1c = (path.err_chk_en<<8) | (path.rgbir_dmytest_ready_cycle<<18)
            self.reg.writereg32(4+path.index*0x40,r4)
            # self.reg.writereg16(4+path.index*0x40,r4&0xffff,mask=BIT12|BIT13|BIT14|BIT15)
            # self.reg.writereg16(6+path.index*0x40,r4>>16,mask=BIT12|BIT13|BIT14|BIT15)
            self.reg.writereg32(8+path.index*0x40,r8)
            self.reg.writereg32(0x0c+path.index*0x40,rc)
            self.reg.writereg32(0x10+path.index*0x40,r10)
            self.reg.writereg32(0x14+path.index*0x40,r14)
            self.reg.writereg32(0x18+path.index*0x40,r18)
            self.reg.writereg32(0x1c+path.index*0x40,r1c)
            self.reg.writereg32(0x20+path.index*0x40,r20)
            self.reg.writereg32(0+path.index*0x40,r0)

    def start(self):
        self._idp_common_start()
        self._idp_path_start(self.cfg.path0)
        self._idp_path_start(self.cfg.path1)
        self._idp_path_start(self.cfg.path2)
        self._idp_path_start(self.cfg.path3)
