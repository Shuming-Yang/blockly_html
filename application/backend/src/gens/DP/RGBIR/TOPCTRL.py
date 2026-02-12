# WARNING
# pylint: disable=C0103, C0114, C0115, C0412, W0231, W0401, W0612, W0613, W0614
from Utility.Reg import REGOBJ
from Utility.Entity import Entity
from Utility.Para import *
from Define.Para import *
from Utility.Others import *
from RegTable.Regdefdist import define_dist

IR_REMOVE_NEW =0
IR_REMOVE_SIMPLE =1
IR_REMOVE_OFF =0
IR_EXTRAT_FROM_RAW_ON =1
IR_EXTRAT_FROM_RAW_OFF =0
IR_EXTRAT_ON =1
IR_EXTRAT_OFF =0

rgbir_rawout_sel_dict={
    0:(IR_EXTRAT_FROM_RAW_OFF,IR_REMOVE_NEW),
    1:(IR_EXTRAT_FROM_RAW_OFF,IR_REMOVE_SIMPLE),
    2:(IR_EXTRAT_FROM_RAW_ON,IR_REMOVE_NEW),
}

rgbir_irout_sel_dict={
    0:(IR_EXTRAT_FROM_RAW_OFF,IR_EXTRAT_OFF,IR_REMOVE_OFF),
    1:(IR_EXTRAT_FROM_RAW_OFF,IR_EXTRAT_OFF,IR_REMOVE_SIMPLE),
    2:(IR_EXTRAT_FROM_RAW_OFF,IR_EXTRAT_ON,IR_REMOVE_SIMPLE),
    3:(IR_EXTRAT_FROM_RAW_ON,IR_EXTRAT_OFF,IR_REMOVE_NEW),
}


goldcrc_lut_dict ={
    (1600,16):(0x3e86,0x51e3eea9,0x0007dc7c),
    (1928,16):(0x3e86,0x51e3eea9,0x0007dc7c), # tbd
    (1920,16):(0x3e86,0x51e3eea9,0x0007dc7c), # tbd
}

class TOPCTRL_CFG(object):
    def __init__(self,chipcfg):
        self.chn_en =0
        self.extractir_fromraw_en =0
        self.irremove =0
        self.dns_en =0
        self.dpc_en =0
        self.ctrl_latch =1
        self.irextract_crc_en =1
        self.cipbin_crc_en =1
        self.v3_sel =0
        self.simple_irrm_en =0
        self.cfa_pattern =0
        self.ch01_en =3
        self.cip_binmode =0
        self.test_pat_en =0
        self.blc =0x40
        self.amode_frmnum =0
        self.bmode_frmnum =0
        self.hsize =0
        self.vsize =0
        self.dummy_line =0
        self.test_vsize=0
        self.test_hsize =0
        self.abmode_en =0
        self.rawout_sel =0
        self.irout_sel =0
        self.camera_gain =0
        self.digi_gain =0
        self.snr_4chn =0
        self.irext_glod_crc =0
        self.brir_glod_crc =0
        self.sta_glod_crc =0
        self.win_cut =1
        self.cfa_array = 0x77ce77ec
        self.sta_thres = 0x3fc


class TOPCTRL_REG(REGOBJ):
    def __init__(self,cfg,uid=0):
        self.base =self.get_baseaddr('RGBIR_TOP',define_dist,uid)
        self.regtable=cfg.regtable
        self.objr=[]


class TOPCTRL(Entity):
    """description of class"""
    def __init__(self,chipcfg,uid=0):
        self.cfg =TOPCTRL_CFG(chipcfg)
        self.reg =TOPCTRL_REG(chipcfg,uid)
        self.setbuf=[]
        self._topctrl_cfg_init(chipcfg,uid)

    def _topctrl_cfg_init(self,chipcfg,uid):
        chip_rgbir= chipcfg.oax4k_cfg.rgbir
        cfg =self.cfg
        # chnlist =[chip_rgbir.chn0,chip_rgbir.chn1,chip_rgbir.chn2,chip_rgbir.chn3]
        chnlist =chip_rgbir.chnlist
        chn =chnlist[uid]
        self.cfg.v3_sel = chn.ctrlbuf[0].v3_sel
        self.cfg.dns_en = chn.ctrlbuf[0].dnsen
        self.cfg.dpc_en = chn.ctrlbuf[0].dpcen
        self.cfg.irremove = chn.ctrlbuf[0].irrmen
        self.cfg.snr_4chn = chn.ctrlbuf[0].v4_sel
        if chn.en:
            self.cfg.chn_en =chn.en
            rgbir_in = chn.inbuf[0]
            self.cfg.vsize =rgbir_in.vsize
            self.cfg.hsize =rgbir_in.hsize
            self.cfg.test_hsize =rgbir_in.hsize
            self.cfg.dummy_line  = chn.ctrlbuf[0].dmynum
            self.cfg.test_vsize =chn.ctrlbuf[0].tpnum -self.cfg.dummy_line
            if self.cfg.test_vsize%4:
                raise RuntimeError("RGBIR TPNUM -dummy number should be 4x")
            self.cfg.test_pat_en =chn.ctrlbuf[0].tpen
            #chn.irout.sel  =3 # tbd
            self.cfg.rawout_sel =chn.ctrlbuf[0].raw.osel
            self.cfg.irout_sel= chn.ctrlbuf[0].ir.osel
            # self.cfg.extractir_fromraw_en = chn.irout.irext_en
            self.cfg.extractir_fromraw_en = chn.ctrlbuf[0].irexen
            self.cfg.simple_irrm_en = chn.ctrlbuf[0].irrm_opt
            # self.cfg.irremove =1 # tbd
            self.cfg.abmode_en = 1 #tbd
            # self.cfg.amode_frmnum = chn.ctrlbuf[0].frmnum_a
            # self.cfg.bmode_frmnum = chn.ctrlbuf[0].frmnum_b
            self.cfg.cfa_array = chn.ctrlbuf[0].cfa_array
            self.cfg.cfa_pattern = chn.ctrlbuf[0].cfa_pattern
            # self.cfg.irext_glod_crc,self.cfg.brir_glod_crc,self.cfg.sta_glod_crc = goldcrc_lut_dict[(self.cfg.test_hsize,chn.ctrlbuf[0].tpnum)]
#            self.cfg.cip_binmode =
            print(f"rgbir enable,{self.cfg.vsize} {self.cfg.hsize}")

    def start(self):
        r0 = self.cfg.blc | (self.cfg.test_pat_en<<10) |  (self.cfg.cip_binmode<<11) |  (self.cfg.ch01_en<<14) |\
             (self.cfg.rawout_sel<<12) |  (self.cfg.irout_sel<<13) |\
             (self.cfg.cfa_pattern<<16) | (self.cfg.simple_irrm_en<<18) | (self.cfg.v3_sel<<19) | (self.cfg.abmode_en<<20) | (self.cfg.cipbin_crc_en<<21) |\
                  (self.cfg.irextract_crc_en<<22)  |  (self.cfg.snr_4chn<<23) | (self.cfg.dpc_en<<24) | (self.cfg.dns_en<<25) | (self.cfg.irremove<<26) |\
                       (self.cfg.extractir_fromraw_en<<27) | (self.cfg.chn_en<<29) | (self.cfg.ctrl_latch<<30) | (self.cfg.win_cut<<28)
        self.reg.writereg32(0,r0)
        if self.cfg.chn_en:
            fcp_err_glb =1
            # rc = 0 | (0x07 <<16)  |  (fcp_err_glb<<24)
            # rc = 0 | (0x07 <<16) | (self.cfg.amode_frmnum<<8) | (self.cfg.bmode_frmnum<<12)
            self.reg.writereg8(0x0c,0xff)
            self.reg.writereg8(0x0e,7)
            self.reg.writereg8(0x0f,fcp_err_glb)
            r10 = self.cfg.vsize | (self.cfg.hsize<<16)
            lineint_num =10
            r14 = (self.cfg.dummy_line <<1) | (lineint_num<<16)
            r18 = self.cfg.test_vsize |(self.cfg.test_hsize<<16)
            r280 = (self.cfg.camera_gain<<16 )|self.cfg.digi_gain
            self.reg.writereg32(0x10,r10)
            self.reg.writereg32(0x14,r14,mask=BIT0|BIT7|BIT28|BIT29|BIT30|BIT31)
            self.reg.writereg32(0x18,r18)
            self.reg.writereg32(0x04,self.cfg.cfa_array)
            self.reg.writereg16(0x166,self.cfg.sta_thres)
# tmp for 2312 1600x1300
            # self.reg.writereg32(0x38,self.cfg.irext_glod_crc)
            # self.reg.writereg32(0x3c,self.cfg.brir_glod_crc)
            # self.reg.writereg32(0x40,self.cfg.sta_glod_crc)
            # self.reg.writereg32(0x280,r280)
