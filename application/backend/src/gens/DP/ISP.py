# WARNING
# pylint: disable=C0103, C0114, C0115, C0116, C0200, C0412, W0231, W0401, W0612, W0613, W0614, W0622
from Utility.Reg import REGOBJ
from Utility.Entity import Entity
from Utility.Para import *
from Define.Para import *
from Utility.Others import *
from RegTable.Regdefdist import define_dist


isp_expmode_map ={
    "3X12RAW":(3,3,3),
    "3X10RAW":(3,3,3),
    "2X12RAW":(2,2,2),
    "2X11RAW":(2,2,2),
    "2X10RAW":(2,2,2),
    "2X10RAWCB":(2,2,2),
    "YUV422":(1,1,1),
    "RAW12":(1,1,1),
    "12+12RAW":(3,3,3),
    "16+12RAW":(3,3,3),
    "12+SPD10":(4,4,4),
    "16+SPD10":(4,4,4),
    "24+LFM":(3,3,3),
    "COM24":(3,3,3),
    "COM20":(3,3,3),
    "COM16":(2,2,2),
    "COM14":(2,2,2),  
    "COM12":(2,2,2),
    "4X12RAW":(4,4,4),
    "4X10RAW":(4,4,4),
    "RAW10":(1,1,1),
    }


ispmode_mapping_dict ={
    "HDR4_DCGSVSRAW":(4,4,4),
    "HDR4_DCGSVSCOMB":(4,4,4),
    "HDR4_DCGSVSCOMB_SPD":(4,4,4),
    "HDR3_DCGVSRAW":(3,3,3),
    "HDR3_DCGVSCOMB":(3,3,3),
    "HDR3_DCGVSCOMB_SPD":(3,3,3),
    "HDR3_DCGCOMB_VSRAW":(3,3,3),
    "HDR3_DCGVSPWLRAW":(3,3,3),
    "HDR3_LSVSRAW":(3,3,3),
    "HDR3_LMSRAW":(3,3,3),
    "HDR3_SLORVSRAW":(3,3,3),
    "HDR3_LSVSCOMB":(3,3,3),
    "HDR3_DCGSPDRAW":(3,3,3),
    "HDR3_DCGSPDCOMB":(3,3,3),
    "HDR2_DCGRAW":(2,2,2),
    "HDR2_DCGCOMB":(2,2,2),
    "HDR2_LMRAW":(2,2,2),
    # "HDR2_LSRAW":(2,2,2),
    "HDR1_LINEARRAW":(1,1,1),
    "HDR1_PWLRAW":(1,1,1),
    "BYP_YUV":(1,1,1),
}


INV_CMB_EXPONUM1 =0
INV_CMB_EXPONUM2 =1
INV_CMB_EXPONUM3 =2
INV_CMB_EXPONUM4 =3
INV_CMB_2X11_EN  =1
INV_CMB_2X11_OFF =0
INV_CMB_MODE_HDR =0
INV_CMB_MODE_DCG =1
INV_CMB_EN =1
INV_CMB_OFF =0
INV_PWL_EN =1
INV_PWL_OFF =0
INV_PWL_12TO24 =0
INV_PWL_14TO24 =1
INV_PWL_16TO24 =2
INV_PWL_20TO24 =3
INV_PWL_SIMP_EN =4
INV_PWL_SIMP_12TO14 =4
INV_PWL_SIMP_10TO12 =5
INV_PWL_SIMP_12TO16 =6
INV_PWL_SIMP_16TO20 =7
INV_PWL_SIMP_12TO20 =7
CFA_BTCMP_MAN_ON =1
CFA_BTCMP_MAN_OFF =0
CFA_BTCMP_EN =1
CFA_BTCMP_OFF =0
CMB_BTCMP_MAN_ON =1
CMB_BTCMP_MAN_OFF =0
CMB_BTCMP_EN =1
CMB_BTCMP_OFF =0


isp_decmprpwl_map ={
    "3X12RAW":((INV_CMB_OFF,INV_CMB_MODE_HDR,INV_CMB_2X11_OFF),    (INV_PWL_OFF,INV_PWL_12TO24),(CFA_BTCMP_MAN_ON,CFA_BTCMP_EN)), 
    "2X12RAW":((INV_CMB_OFF,INV_CMB_MODE_HDR,INV_CMB_2X11_OFF),    (INV_PWL_OFF,INV_PWL_12TO24)),
    "2X10RAW":((INV_CMB_OFF,INV_CMB_MODE_HDR,INV_CMB_2X11_OFF),    (INV_PWL_OFF,INV_PWL_12TO24)),  # tbd
    "2X10RAWCB":((INV_CMB_OFF,INV_CMB_MODE_HDR,INV_CMB_2X11_OFF),  (INV_PWL_OFF,INV_PWL_12TO24)),  # tbd
    "3X10RAW":((INV_CMB_OFF,INV_CMB_MODE_HDR,INV_CMB_2X11_OFF),    (INV_PWL_EN,INV_PWL_SIMP_10TO12)),
    "2X11RAW":((INV_CMB_OFF,INV_CMB_MODE_HDR,INV_CMB_2X11_EN),     (INV_PWL_OFF,INV_PWL_12TO24)),
    "YUV422": ((INV_CMB_OFF,INV_CMB_MODE_DCG,INV_CMB_2X11_OFF),    (INV_PWL_OFF,INV_PWL_12TO24)),
    "RAW12":  ((INV_CMB_OFF,INV_CMB_MODE_DCG,INV_CMB_2X11_OFF),    (INV_PWL_OFF,INV_PWL_12TO24)),
    "12+12RAW":((INV_CMB_EN,INV_CMB_MODE_DCG,INV_CMB_2X11_OFF),    (INV_PWL_EN,INV_PWL_SIMP_12TO16)),  # ok
    "16+12RAW":((INV_CMB_EN,INV_CMB_MODE_DCG,INV_CMB_2X11_OFF),    (INV_PWL_OFF,INV_PWL_12TO24)),  # ok
    "COM24":((INV_CMB_EN,INV_CMB_MODE_HDR,INV_CMB_2X11_OFF),       (INV_PWL_OFF,INV_PWL_12TO24)),
    "24+LFM":((INV_CMB_EN,INV_CMB_MODE_HDR,INV_CMB_2X11_OFF),      (INV_PWL_OFF,INV_PWL_12TO24)),
    "COM20":((INV_CMB_EN,INV_CMB_MODE_HDR,INV_CMB_2X11_OFF),       (INV_PWL_EN,INV_PWL_20TO24)),
    "COM16":((INV_CMB_EN,INV_CMB_MODE_HDR,INV_CMB_2X11_OFF),       (INV_PWL_EN,INV_PWL_16TO24)),
    "COM14":((INV_CMB_EN,INV_CMB_MODE_HDR,INV_CMB_2X11_OFF),       (INV_PWL_EN,INV_PWL_14TO24)),
    "COM12":((INV_CMB_EN,INV_CMB_MODE_HDR,INV_CMB_2X11_OFF),       (INV_PWL_EN,INV_PWL_12TO24)),
    "12+SPD10":((INV_CMB_EN,INV_CMB_MODE_HDR,INV_CMB_2X11_OFF),    (INV_PWL_EN,INV_PWL_12TO24)),
    "16+SPD10":((INV_CMB_EN,INV_CMB_MODE_HDR,INV_CMB_2X11_OFF),    (INV_PWL_EN,INV_PWL_16TO24)),
    "4X12RAW":((INV_CMB_OFF,INV_CMB_MODE_HDR,INV_CMB_2X11_OFF),    (INV_PWL_OFF,INV_PWL_12TO24),(CFA_BTCMP_MAN_ON,CFA_BTCMP_EN)),
    "4X10RAW":((INV_CMB_OFF,INV_CMB_MODE_HDR,INV_CMB_2X11_OFF),    (INV_PWL_OFF,INV_PWL_12TO24),(CFA_BTCMP_MAN_OFF,CFA_BTCMP_OFF)),
    "RAW10":((INV_CMB_OFF,INV_CMB_MODE_DCG,INV_CMB_2X11_OFF),      (INV_PWL_OFF,INV_PWL_12TO24)),
    # "RAW10":(1,1,1),
}


class ISP_SCALE_CFG(object):
    def __init__(self):
        self.en=0    # scale down enable
        self.hratio=0   # scale h ratio
        self.vratio=0    # cale h ratio
        self.ihsize=0   # scale input hsize
        self.ivsize=0    # scale input vsize
        self.hsize=0   # scale output hsize
        self.vsize=0    # scale output vsize
        self.hstart=0   ## scale input hstart
        self.vstart=0   ## scale input vstart
        self.precropen =0 ## scale pre crop enable
        self.precrop_hstart=0   ## scale pre crop hstart, before isp scale
        self.precrop_vstart=0   ## scale pre crop vstart, before isp scale
        self.precrop_hsize=0   # scale pre crop hsize
        self.precrop_vsize=0   # scale pre crop vsize
        self.postcropen =0     ## scale post crop enable
        self.postcrop_hstart=0   ## scale post crop hstart, after isp scale
        self.postcrop_vstart=0   ## scale post crop vstart, after isp scale
        self.postcrop_hsize=0   # scale post crop hsize
        self.postcrop_vsize=0   # scale post crop vsize


class ISP_PTAH_CHN_CFG(object):
    def __init__(self,id=0):
        self.osel =0
        self.exp_osel =0
        self.win_left =0
        self.win_right =0
        self.win_top =0
        self.win_bottom =0
        self.win_sel =0
        self.stest_out =0
        self.outen =1
        if id<2:
            self.scale = ISP_SCALE_CFG()


class ISP_DECOMPRESS_CFG(object):
    def __init__(self):
        self.inv_cmb_en =0
        self.cmb_recover_mode =0
        self.inv_2x11_en =0
        self.inv_cmb_mode =0  # 0 : HDR, 1:DCG
        self.inv_pwl_dither_en =1
        self.inv_pwl_mode =0  # 0
        self.inv_pwl_en =0
        self.inv_pwl_outbit =0x0e
        self.man_cmb_blc_en =1
        self.inv_hdr_outbit_sel =0
        self.dx_exp_reg =[]
        self.dy_val_reg =[]
        self.cfa_cmp_man =0
        self.cfa_cmp_en =0
        self.cmb_cmp_man =0
        self.cmb_cmp_en =0


class CBAR_CFG(object):
    def __init__(self,id):
        self.index =id
        self.en =0
        self.ihsw=12
        self.ivsw=12
        self.rolling =0
        self.trans =0
        self.style =0
        self.rnd_seed =1
        self.test_sel =0
        self.const_en =0
        self.const_b =0
        self.const_bg=0
        self.const_gr =0
        self.const_r =0
        self.linecnt=0
        self.pixcnt =0
        self.line_inten =0
        self.line_num =2


class ISP_INTERRUPT_CFG(object):
    def __init__(self):
        self.en0= 0x00010000
        self.en1= 0x00020000
        self.en2= 0x00000020
        self.en3= 0x00044000


class ISP_PTAH_CFG(object):
    def __init__(self,id):
        self.index =id
        self.en =0
        self.ctrl_00 =0x07303fff # enable
        self.ctrl_04 =0xff0ff0f0
        self.ctrl_08 =0x004f67ff
        self.ctrl_0c =0x000f67bd
        self.asic_err_en =0xffffffff
        # self.ctrl_10 =0x00ffffff # clock disable
        # self.ctrl_14 =0xffffffff
        self.ctrl_10 =0x0 # clock disable
        self.ctrl_14 =0x00000008
        #self.ctrl_18 =0
        self.ahb2reg_endian =0
        self.latch_dis =0
        self.rst_prot_en =1
        self.intr_vsync_clr =0
        self.cfa_pat =0
        self.exp_num =0
        self.exp_mode =0
        self.work_mode =0
        self.sof_sel =0
        self.eof_sel =0
        self.aecdone_bot=0x20
        self.ltm_sel =0
        self.ltm_en =0
        self.hsize =0
        self.vsize =0
        self.man_dmyln_en =0
        self.dmy_lnum=0
        self.man_blc =0
        self.expol_order =0
        self.expom_order =1
        self.expos_order =2
        self.expov_order =3
        self.single_expo_sel =0
        self.decmpr= ISP_DECOMPRESS_CFG()
        self.yuv =ISP_PTAH_CHN_CFG(0)
        self.rmv =ISP_PTAH_CHN_CFG(1)
        self.raw =ISP_PTAH_CHN_CFG(2)
        self.intr=ISP_INTERRUPT_CFG()
        self.cben =0
        self.cbl = CBAR_CFG(0)
        self.cbs = CBAR_CFG(1)
        self.cbm = CBAR_CFG(2)
        self.cbv = CBAR_CFG(3)


class ISP_CFG(object):
    def __init__(self,chipcfg):
        self.core_safe_en  =1
        self.decmp_safe_en  =1
        self.ltm_mode =0
        self.path0=ISP_PTAH_CFG(0)
        self.path1=ISP_PTAH_CFG(1)
        self.path2=ISP_PTAH_CFG(2)
        self.path3=ISP_PTAH_CFG(3)


class ISP_REG(REGOBJ):
    def __init__(self,cfg,uid=0):
        self.base =self.get_baseaddr('ISP',define_dist,uid)
        self.regtable=cfg.regtable
        self.objr=[]


class ISP(Entity):
    """description of class"""
    def __init__(self,chipcfg,uid=0):
        #self.cfg=mrx_cfg()
        self.cfg =ISP_CFG(chipcfg)
        self.reg =ISP_REG(chipcfg,uid)
        self.setbuf=[]
        self.isp_cfg_init(chipcfg)

    def isp_cfg_init(self,chipcfg):
        dplist =[chipcfg.oax4k_cfg.dp0,chipcfg.oax4k_cfg.dp1,chipcfg.oax4k_cfg.dp2,chipcfg.oax4k_cfg.dp3]
        isplist =[self.cfg.path0,self.cfg.path1,self.cfg.path2,self.cfg.path3]
        test_en =0
        for dp in dplist:
            if(dp.en and not dp.bypisp):
                test_en=test_en | dp.input.itpgen
            # test_en=test_en | dp.isp.safeen
        self.cfg.decmp_safe_en = test_en
        self.cfg.core_safe_en  = test_en
        self.cfg.ltm_mode = chipcfg.oax4k_cfg.topctrl.ispltm_mode
        for i in range(len(dplist)):
            if dplist[i].en:
                self._isp_path_init(isplist[i],dplist[i])
                # self.isp_decomp_init(isplist[i],dplist[i])
                self.isp_decomp_init_new(isplist[i],dplist[i])
    # def isp_decomp_init(self,isp,dp):
    #     ispin =dp.isp.inbuf[0]
    #     snrfmt=get_dict_key(input_format_dict,ispin.format)
    #     allcmpr,allpwl,*cmp =isp_decmprpwl_map[snrfmt]
    #     if(cmp !=[]):
    #         isp.decmpr.cfa_cmp_man, isp.decmpr.cfa_cmp_en =cmp[0]
    #     isp.decmpr.inv_cmb_en, isp.decmpr.inv_cmb_mode,isp.decmpr.inv_2x11_en =allcmpr
    #     isp.decmpr.inv_pwl_en,isp.decmpr.inv_pwl_mode =allpwl
    #     if(ispin.pwlmode and snrfmt=="COM12"):
    #         isp.decmpr.inv_pwl_mode = INV_PWL_SIMP_10TO12
    #         isp.decmpr.inv_cmb_en =0
    #         print(snrfmt,"simple pwl","ispppp")
    #     if(isp.decmpr.inv_pwl_mode==INV_PWL_SIMP_10TO12 and isp.decmpr.inv_pwl_en ):
    #         isp.decmpr.inv_pwl_outbit=0x0c
    #     isp.decmpr.cmb_recover_mode = ispin.expnum -1

    def isp_decomp_init_new(self,isp,dp):
        ispin =dp.isp.inbuf[0]
        snrfmt=get_dict_key(input_format_dict,ispin.format)
        snrtype=get_dict_key(sensor_input_format_type_dict,ispin.format_tid)
        snrpwl_mode=get_dict_key(input_format_dict,ispin.pwlmode)
        dual_roi_en=ispin.dual_roi_en

        def hdrfmt_decmpr_parse(decmpr,snrfmt,snrtype):
            decmpr.inv_cmb_en =  INV_CMB_EN
            decmpr.inv_cmb_mode = INV_CMB_MODE_HDR
            decmpr.inv_2x11_en = INV_CMB_2X11_OFF
            hdrfmt_pwlmode_decode={
                # "RAW12":5,
                "COM12":INV_PWL_12TO24,
                # "12+12RAW":6,
                # "16+12RAW":7,
                "COM20":INV_PWL_20TO24,
                "COM16":INV_PWL_16TO24,
                "COM14":INV_PWL_14TO24,  
                "12+SPD10" : INV_PWL_12TO24,
                "16+SPD10" : INV_PWL_16TO24,
            }
            if(snrfmt in ["COM12","COM14","COM16","COM20","12+SPD10","16+SPD10" ]):
                decmpr.inv_pwl_en = INV_PWL_EN
                decmpr.inv_pwl_mode =hdrfmt_pwlmode_decode[snrfmt]
                decmpr.dx_exp_reg =ispin.dx_exp_reg
                decmpr.dy_val_reg =ispin.dy_val_reg

        def dcgfmt_decmpr_parse(decmpr,snrfmt,snrtype):
            decmpr.inv_cmb_en =  INV_CMB_EN
            if(snrtype in ["HDR3_LSVSCOMB","HDR3_DCGSPDCOMB"]):
                decmpr.inv_cmb_mode = INV_CMB_MODE_HDR  # need check X1D is DCG or HDR,X1A is HDR
            else:
                decmpr.inv_cmb_mode = INV_CMB_MODE_DCG
            decmpr.inv_2x11_en = INV_CMB_2X11_OFF
            dcgfmt_pwlmode_decode={
                # "RAW12":5,
                ("HDR2_DCGCOMB","COM12"):INV_PWL_SIMP_12TO16,
                ("HDR3_DCGSPDCOMB","COM12"):INV_PWL_SIMP_12TO20,
                ("HDR3_LSVSCOMB","COM12"):INV_PWL_SIMP_12TO20,
                ("HDR3_LSVSCOMB","COM16"):INV_PWL_SIMP_16TO20,
                ("HDR2_DCGCOMB","RAW12"):INV_PWL_SIMP_12TO14,
                ("HDR3_DCGCOMB_VSRAW","12+12RAW"):INV_PWL_SIMP_12TO16,
            }
            if(snrfmt in ["COM12","RAW12","12+12RAW","COM16"]):
                if(snrtype=="HDR2_DCGCOMB" and snrfmt=="COM16"):
                    pass
                else:
                    decmpr.inv_pwl_en = INV_PWL_EN
                    decmpr.inv_pwl_mode =dcgfmt_pwlmode_decode[(snrtype,snrfmt)]
                    decmpr.inv_hdr_outbit_sel = 1 if(snrtype not in ["HDR3_DCGCOMB_VSRAW","HDR3_DCGSPDCOMB"]) else 0
                    decmpr.cmb_cmp_man = decmpr.inv_hdr_outbit_sel
                    # decmpr.cmb_cmp_en = decmpr.cmb_cmp_man
                    decmpr.curve_g =ispin.curve_g   # pwl curve gain0,1,2,3
                    decmpr.curve_kp =ispin.curve_kp   # pwl curve kneepoint0,1,2
                    decmpr.curve_of =ispin.curve_of   # pwl curve offset0,1,2,3

        def cmpfmt_decmpr_parse(decmpr,snrfmt,snrtype):
            decmpr.inv_2x11_en = INV_CMB_2X11_OFF
            dcgfmt_pwlmode_decode={
                # "RAW12":5,
                ("HDR3_DCGVSPWLRAW","3X10RAW"):INV_PWL_SIMP_10TO12,
                ("HDR2_HORLVSRAW","10+10RAW"):INV_PWL_SIMP_10TO12,
                ("HDR1_PWLRAW","RAW10"):INV_PWL_SIMP_10TO12,
            }
            # if(snrfmt in ["RAW10","3X10RAW","10+10RAW"]):
            #     pass
            #     # decmpr.inv_pwl_en = INV_PWL_EN
            #     # decmpr.inv_pwl_mode =dcgfmt_pwlmode_decode[(snrtype,snrfmt)]
            #     # decmpr.curve_g =ispin.curve_g   # pwl curve gain0,1,2,3
            #     # decmpr.curve_kp =ispin.curve_kp   # pwl curve kneepoint0,1,2
            #     # decmpr.curve_of =ispin.curve_of   # pwl curve offset0,1,2,3
            # else:
            #     pass
        if(snrtype in ["HDR4_DCGSVSCOMB","HDR4_DCGSVSCOMB_SPD","HDR3_DCGVSCOMB","HDR3_DCGVSCOMB_SPD"]):
            hdrfmt_decmpr_parse(isp.decmpr,snrfmt,snrtype)
        elif(snrtype in ["HDR3_DCGCOMB_VSRAW","HDR3_DCGSPDCOMB","HDR2_DCGCOMB","HDR3_LSVSCOMB"]):
            dcgfmt_decmpr_parse(isp.decmpr,snrfmt,snrtype)
        elif(snrtype in ["HDR3_DCGVSPWLRAW","HDR2_HORLVSRAW","HDR1_PWLRAW"]):
            cmpfmt_decmpr_parse(isp.decmpr,snrfmt,snrtype)
        elif snrtype in ["HDR3_SLORVSRAW"]:
            isp.decmpr.inv_2x11_en = INV_CMB_2X11_EN
        else:
            if(snrfmt in ["2X12RAW","3X12RAW","4X12RAW","RAW12"]):
                #  isp.decmpr.cfa_cmp_man, isp.decmpr.cfa_cmp_en =(CFA_BTCMP_MAN_ON,CFA_BTCMP_EN)
                if dp.rgbiren:
                    isp.decmpr.inv_hdr_outbit_sel =0
                else:
                    isp.decmpr.inv_hdr_outbit_sel =1 # tbd
        if(isp.decmpr.inv_pwl_mode==INV_PWL_SIMP_12TO14 and isp.decmpr.inv_pwl_en ):
            isp.decmpr.inv_pwl_outbit=0x0e
        isp.decmpr.cmb_recover_mode = isp.exp_num -1
        #print("ispcmpr",allcmpr,allpwl)

    def _isp_path_init(self,isp,dp):
        # dpin =dp.input.buf[0]
        # snr = dpin.sensor_buf[dp.input.vcsrc]
        ispin =dp.isp.inbuf[0]
        ispout =dp.dobuf[0]
        isp.en =dp.en
        snrfmt=get_dict_key(input_format_dict,ispin.format)
        fmttype=get_dict_key(sensor_input_format_type_dict,ispin.format_tid)
        # print("snr fmt is {}".format(snrfmt))
        # isp.exp_num,isp.work_mode,isp.exp_mode =isp_expmode_map[snrfmt]
        # if ispin.expnum != 0 :
        #     isp.exp_mode = ispin.expnum
        isp.exp_num,isp.work_mode,isp.exp_mode =ispmode_mapping_dict[fmttype]  # pyright: ignore[reportArgumentType]
        isp.cben = dp.isp.cben
        isp.cbl.en = dp.isp.cben &BIT0
        isp.cbs.en = dp.isp.cben &BIT1
        isp.cbm.en = dp.isp.cben &BIT2
        isp.cbv.en = dp.isp.cben &BIT3
        isp.hsize =ispin.hsize
        isp.vsize =ispin.vsize
        sclhsize = dp.isp.yuvout.scale.hsize
        isp.yuv.scale.precropen = dp.isp.yuvout.scale.precropen
        isp.yuv.scale.en = dp.isp.yuvout.scale.en
        isp.yuv.scale.postcropen = dp.isp.yuvout.scale.postcropen
        isp.yuv.cropen = dp.isp.yuvout.cropen
        isp.raw.cropen = dp.isp.rawout.cropen
        isp.rmv.cropen = dp.isp.mvout.cropen
        isp.yuv.scale.precrop_win_left =dp.isp.yuvout.scale.precrop_hstart if(dp.isp.yuvout.scale.precropen) else 0
        isp.yuv.scale.precrop_win_right =(dp.isp.yuvout.scale.precrop_hsize+isp.yuv.scale.precrop_win_left) if(dp.isp.yuvout.scale.precropen) else 0
        isp.yuv.scale.precrop_win_top =dp.isp.yuvout.scale.precrop_vstart if(dp.isp.yuvout.scale.precropen) else 0
        isp.yuv.scale.precrop_win_bottom =(dp.isp.yuvout.scale.precrop_vsize+isp.yuv.scale.precrop_win_top)if(dp.isp.yuvout.scale.precropen) else 0
        if isp.yuv.scale.precropen:
            print(f"HV ISP scale pre crop left {isp.yuv.scale.precrop_win_left}, right {isp.yuv.scale.precrop_win_right}, top {isp.yuv.scale.precrop_win_top}, bottom {isp.yuv.scale.precrop_win_bottom}")
        dp.isp.yuvout.scale.ihsize = dp.isp.yuvout.scale.precrop_hsize if(dp.isp.yuvout.scale.precropen) else isp.hsize
        dp.isp.yuvout.scale.ivsize = dp.isp.yuvout.scale.precrop_vsize if(dp.isp.yuvout.scale.precropen) else isp.vsize
        isp.yuv.scale.hratio  = int(dp.isp.yuvout.scale.hsize *2048/dp.isp.yuvout.scale.ihsize) +1
        isp.yuv.scale.vratio  = int(dp.isp.yuvout.scale.vsize *2048/dp.isp.yuvout.scale.ivsize) +1
        isp.yuv.scale.hstart  = dp.isp.yuvout.scale.hstart
        isp.yuv.scale.vstart  = dp.isp.yuvout.scale.vstart
        if isp.yuv.scale.en:
            tmp0 = dp.isp.yuvout.scale.ihsize
            tmp1 = dp.isp.yuvout.scale.ivsize
            tmp2 = isp.yuv.scale.hratio
            tmp3 = isp.yuv.scale.vratio
            tmp4 = isp.yuv.scale.hstart
            tmp5 = isp.yuv.scale.vstart
            print(f"HV ISP scale ihsize {tmp0} ivsize {tmp1} hratio {tmp2}, vratio {tmp3} hstart {tmp4} vstart {tmp5}")
        isp.yuv.scale.postcrop_win_left =dp.isp.yuvout.scale.postcrop_hstart if(dp.isp.yuvout.scale.postcropen) else 0
        isp.yuv.scale.postcrop_win_right =(dp.isp.yuvout.scale.hsize+isp.yuv.scale.postcrop_win_left) if(dp.isp.yuvout.scale.postcropen) else 0
        isp.yuv.scale.postcrop_win_top =dp.isp.yuvout.scale.postcrop_vstart if(dp.isp.yuvout.scale.postcropen) else 0
        isp.yuv.scale.postcrop_win_bottom =(dp.isp.yuvout.scale.vsize+isp.yuv.scale.postcrop_win_top)if(dp.isp.yuvout.scale.postcropen) else 0
        if isp.yuv.scale.postcropen:
            print(f"HV ISP scale post crop left {isp.yuv.scale.postcrop_win_left}, right {isp.yuv.scale.postcrop_win_right}, top {isp.yuv.scale.postcrop_win_top}, bottom {isp.yuv.scale.postcrop_win_bottom}")
        isp.yuv.win_left =dp.isp.yuvout.hstart if(dp.isp.yuvout.cropen) else 0
        isp.yuv.win_right =(dp.isp.yuvout.scale.hsize -dp.isp.yuvout.hsize -  isp.yuv.win_left) if(dp.isp.yuvout.cropen ) else 0
        isp.yuv.win_top =dp.isp.yuvout.vstart if(dp.isp.yuvout.cropen) else 0
        isp.yuv.win_bottom =(dp.isp.yuvout.scale.vsize -dp.isp.yuvout.vsize -isp.yuv.win_top )if(dp.isp.yuvout.cropen ) else 0
        if isp.yuv.cropen:
            print(f"HV ISP windowing left {isp.yuv.win_left}, right {isp.yuv.win_right}, top {isp.yuv.win_top}, bottom {isp.yuv.win_bottom}")
        isp.raw.win_left =dp.isp.rawout.hstart if(dp.isp.rawout.cropen) else 0
        isp.raw.win_right =(isp.hsize -dp.isp.rawout.hsize - isp.raw.win_left) if(dp.isp.rawout.cropen ) else 0
        isp.raw.win_top =dp.isp.rawout.vstart if(dp.isp.rawout.cropen) else 0
        isp.raw.win_bottom =(isp.vsize -dp.isp.rawout.vsize - isp.raw.win_top) if(dp.isp.rawout.cropen ) else 0
        if isp.raw.cropen:
            print(f"RAW windowing left {isp.raw.win_left}, right {isp.raw.win_right}, top {isp.raw.win_top}, bottom {isp.raw.win_bottom}")
        isp.rmv.win_left =dp.isp.mvout.hstart if(dp.isp.mvout.cropen) else 0
        isp.rmv.win_right =(isp.hsize-dp.isp.mvout.hsize - isp.rmv.win_left)  if(dp.isp.mvout.cropen ) else 0
        isp.rmv.win_top =dp.isp.mvout.vstart if(dp.isp.mvout.cropen) else 0
        isp.rmv.win_bottom =(isp.vsize -dp.isp.mvout.vsize-isp.rmv.win_top) if(dp.isp.mvout.cropen ) else 0
        if isp.rmv.cropen:
            print(f"MV windowing left {isp.rmv.win_left}, right {isp.rmv.win_right}, top {isp.rmv.win_top}, bottom {isp.rmv.win_bottom}")
        isp.yuv.osel  = dp.isp.yuvout.sel
        isp.raw.osel  = dp.isp.rawout.sel
        isp.raw.exp_osel  = dp.isp.rawout.exposel
        isp.rmv.osel  = dp.isp.mvout.sel
        isp.sof_sel  =dp.isp.top.sof_sel
        isp.eof_sel  =dp.isp.top.eof_sel
        isp.aecdone_bot  =dp.isp.top.aecdoneoft
        isp.ltm_sel  =self.cfg.ltm_mode
        isp.ltm_en =isp.ltm_sel
        isp.rmv.win_sel = dp.isp.mvout.winsel
        isp.yuv.win_sel = dp.isp.yuvout.winsel

    def _isp_path_start(self,path):
        if path.en:
            offset = path.index *0x2000
            self.reg.writereg32(0x00+offset,path.ctrl_00)
            self.reg.writereg32(0x04+offset,path.ctrl_04 | path.cbl.en | path.cbs.en |path.cbm.en |path.cbv.en )
            path.ctrl_08 = path.ctrl_08 | (path.yuv.scale.en <<15) | (path.ltm_en <<25) |  (path.ltm_sel <<27)
            self.reg.writereg32(0x08+offset,path.ctrl_08)
            path.ctrl_0c = path.ctrl_0c | (path.rmv.scale.en <<15)
            self.reg.writereg32(0x0c+offset,path.ctrl_0c)
            self.reg.writereg32(0x10+offset,path.ctrl_10)  #disable clock gate
            self.reg.writereg32(0x14+offset,path.ctrl_14)
            r1c = (path.exp_mode<<0) | (path.work_mode<<4) |(path.exp_num<<8) |(path.cfa_pat<<16) |\
                (path.ahb2reg_endian<<24) |(path.rst_prot_en<<25) |(path.latch_dis<<0) |(path.intr_vsync_clr<<27)
            self.reg.writereg32(0x1c+offset,r1c)
            r20 = (path.rmv.osel <<0) | (path.rmv.outen <<7)|(path.yuv.osel<<8) | (path.yuv.outen <<15) | (path.raw.exp_osel <<16)  | (path.raw.osel <<24) |(path.raw.outen <<20)
            # print("isp r20 0x{:x}".format(r20))
            # print("hv osel {} oen {}".format(path.yuv.osel, path.yuv.outen))
            self.reg.writereg32(0x20+offset,r20)
            self.reg.writereg32(0x24+offset,(path.hsize<<16) |path.vsize)
            self.reg.writereg32(0x28+offset,(path.yuv.win_left<<16) |path.yuv.win_right)
            self.reg.writereg32(0x2c+offset,(path.yuv.win_top<<16) |path.yuv.win_bottom)
            self.reg.writereg32(0x30+offset,(path.rmv.win_left<<16) |path.rmv.win_right)
            self.reg.writereg32(0x34+offset,(path.rmv.win_top<<16) |path.rmv.win_bottom)
            self.reg.writereg32(0x38+offset,(path.raw.win_left<<16) |path.raw.win_right)
            self.reg.writereg32(0x3c+offset,(path.raw.win_top<<16) |path.raw.win_bottom)
            r40 = ((path.expol_order<<28) | (path.expom_order<<24)) |(path.expos_order<<20) |(path.expov_order<<16) | \
                (path.sof_sel<<8) |(path.eof_sel<<12) |(path.single_expo_sel)
            self.reg.writereg32(0x40+offset,r40)
            self.reg.writereg16(0x400+0x56+offset,path.aecdone_bot,save_force=1,newreg=1,endian=1)
            self.reg.writereg16(0x680+0x56+offset,path.aecdone_bot,save_force=1,newreg=1,endian=1)
            self.reg.writereg16(0x900+0x56+offset,path.aecdone_bot,save_force=1,newreg=1,endian=1)
            self.reg.writereg16(0xb80+0x56+offset,path.aecdone_bot,save_force=1,newreg=1,endian=1)
            #self.reg.writereg32(0x40+offset,0x01236000)
            r44B = (path.yuv.win_sel<<1 ) | (path.rmv.win_sel<<0 )
            self.reg.writereg32(0x44+offset,0x00001001 | (r44B<<24) ,mask=0xfc000000 )
            # self.reg.writereg32(0x44+offset,0xf0001001 | (r44B<<24) ,mask=0 )
            self.reg.writereg32(0x48+offset,0x04080400)
            #self.reg.writereg32(0x4c+offset,0x001f2800)
            # self.reg.writereg32(0x50+offset,0x002e0059)
            # self.reg.writereg32(0x54+offset,0x10000000)
            # self.reg.writereg32(0x58+offset,0x001f2800)
            # self.reg.writereg32(0x5c+offset,0x00590100)
            r60 =(path.man_blc <<0) |(path.man_dmyln_en <<24) |(path.dmy_lnum <<16)
            self.reg.writereg32(0x60+offset,r60) # disable man blc tbd
            #self.reg.writereg32(0x60+offset,0x00000000) # disable man blc
            self.reg.writereg32(0x64+offset,0x00100010) # disable man blc
            self.reg.writereg32(0x68+offset,0x00100010) # disable man blc
            self.reg.writereg32(0x6c+offset,0x00100000) # disable man blc
            #self.reg.writereg32(0x70+offset,path.asic_err_en) tbd
            self.reg.writereg32(0x74+offset,0x00000940)
            self.reg.writereg32(0x78+offset,0x00000940)
            self.reg.writereg32(0xa0+offset,path.intr.en0 )
            self.reg.writereg32(0xa4+offset,path.intr.en1 | (self.cfg.core_safe_en<<19))
            self.reg.writereg32(0xa8+offset,path.intr.en2)
            self.reg.writereg32(0xac+offset,path.intr.en3)
            # self.reg.writereg32(0xb4+offset,0x003d0001)
            cmp =path.decmpr
            # cmpr_r100 =((cmp.inv_cmb_en | (cmp.inv_cmb_mode<<1) | (cmp.inv_2x11_en<<2) | (cmp.cmb_recover_mode<<4) |\
            #    (cmp.inv_hdr_outbit_sel<<6)|(cmp.man_cmb_blc_en<<7))<<24)|\
            #      (cmp.inv_pwl_en<<16) | (cmp.inv_pwl_mode<<17) |(cmp.inv_pwl_dither_en<<20)| \
            #       (cmp.cfa_cmp_man<<15 )|(cmp.cfa_cmp_en<<14 ) |(cmp.inv_pwl_outbit)
            r100 = cmp.inv_cmb_en | (cmp.inv_cmb_mode << 1) | (cmp.inv_2x11_en<<2) | (cmp.cmb_recover_mode<<4)| \
                (cmp.inv_hdr_outbit_sel<<6)|(cmp.man_cmb_blc_en<<7)
            r101 = (cmp.inv_pwl_en) | (cmp.inv_pwl_mode<<1) |(cmp.inv_pwl_dither_en<<4)
            r102 = (cmp.cfa_cmp_man<<7 )|(cmp.cfa_cmp_en<<6 ) |(cmp.cmb_cmp_man<<5 )|(cmp.cmb_cmp_en<<4 )
            r103 = cmp.inv_pwl_outbit
            cmpr_r100 = (r100 << 24) | (r101 << 16) | (r102 << 8) | r103 #isp big endian
            self.reg.writereg32(0x100+offset,cmpr_r100,save_force=1,newreg=1,endian=1)
            #self.reg.writereg32(0x100+offset,0xb010c00e,newreg=1,endian=1)
            #self.reg.writereg32(0x104+offset,0x01330400,newreg=1,endian=1)
            self.reg.writereg32(0x108+offset,0x05800880,save_force=1,newreg=1,endian=1)
            if (cmp.inv_pwl_en)&(cmp.inv_pwl_mode > 3):
                r104 = (cmp.curve_g[0]<<4) | cmp.curve_g[1]
                r105 = (cmp.curve_g[2]<<4) | cmp.curve_g[3]
                r106 = (cmp.curve_kp[0]>>8)&0xff
                r107 = cmp.curve_kp[0]&0xff
                cmpr_r104 = (r104 << 24) | (r105 << 16) | (r106 << 8) | r107 #isp big endian
                self.reg.writereg32(0x104+offset,cmpr_r104,save_force=1,newreg=1,endian=1)
                r108 = (cmp.curve_kp[1]>>8)&0xff
                r109 = cmp.curve_kp[1]&0xff
                r10a = (cmp.curve_kp[2]>>8)&0xff
                r10b = cmp.curve_kp[2]&0xff
                cmpr_r108 = (r108 << 24) | (r109 << 16) | (r10a << 8) | r10b #isp big endian
                self.reg.writereg32(0x108+offset,cmpr_r108,save_force=1,newreg=1,endian=1)
                r10d = (cmp.curve_of[0]>>16)&0xff
                r10e = (cmp.curve_of[0]>>8)&0xff
                r10f = cmp.curve_of[0]&0xff
                cmpr_r10c = (r10d << 16) | (r10e << 8) | r10f #isp big endian
                self.reg.writereg32(0x10c+offset,cmpr_r10c,save_force=1,newreg=1,endian=1)
                r111 = (cmp.curve_of[1]>>16)&0xff
                r112 = (cmp.curve_of[1]>>8)&0xff
                r113 = cmp.curve_of[1]&0xff
                cmpr_r110 = (r111 << 16) | (r112 << 8) | r113 #isp big endian
                self.reg.writereg32(0x110+offset,cmpr_r110,save_force=1,newreg=1,endian=1)
                r115 = (cmp.curve_of[2]>>16)&0xff
                r116 = (cmp.curve_of[2]>>8)&0xff
                r117 = cmp.curve_of[2]&0xff
                cmpr_r114 = (r115 << 16) | (r116 << 8) | r117 #isp big endian
                self.reg.writereg32(0x114+offset,cmpr_r114,save_force=1,newreg=1,endian=1)
                r119 = (cmp.curve_of[3]>>16)&0xff
                r11a = (cmp.curve_of[3]>>8)&0xff
                r11b = cmp.curve_of[3]&0xff
                cmpr_r118 = (r119 << 16) | (r11a << 8) | r11b #isp big endian
                self.reg.writereg32(0x118+offset,cmpr_r118,save_force=1,newreg=1,endian=1)
            self.isp_scale_cfg(path)
        else:
            offset = path.index *0x2000
            self.reg.writereg32(0x24+offset,0)

    def isp_scale_cfg(self,path):
        pass

    def _isp_safe_cfg(self):
        if self.cfg.ltm_mode:  # ltm mode
            self.reg.writereg8(0x1b5c,0x0f,save_force=1,newreg=1,endian=1)
        else:
            self.reg.writereg8(0x1b5c,0x60,save_force=1,newreg=1,endian=1)

    def start(self):
        self._isp_safe_cfg()
        self._isp_path_start(self.cfg.path0)
        self._isp_path_start(self.cfg.path1)
        self._isp_path_start(self.cfg.path2)
        self._isp_path_start(self.cfg.path3)
