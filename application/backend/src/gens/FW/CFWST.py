# WARNING
# pylint: disable=C0103, C0114, C0115, W0102
from Utility.OrderClass import Structure


class SNR_PAD_CFG(Structure):
    pullen_regaddr='DW8'
    pullen_regbit='DW8'
    pullsel_regaddr='DW8'
    pullsel_regbit='DW8'
    inputen_regaddr='DW8'
    inputen_regbit='DW8'
    outputen_regaddr='DW8'
    outputen_regbit='DW8'
    drivingsel_regaddr='DW8'
    drivingsel_regbit='DW8'
    pin_pol='DW8'
    rsvd=['DW8',5]

    def __init__(self):
        self.pullen_regaddr='x'
        self.pullen_regbit='x'
        self.pullsel_regaddr='x'
        self.pullsel_regbit='x'
        self.inputen_regaddr='x'
        self.inputen_regbit='x'
        self.outputen_regaddr='x'
        self.outputen_regbit='x'
        self.drivingsel_regaddr='x'
        self.drivingsel_regbit='x'
        self.pin_pol='x'
        self.rsvd=[]


class SNR_REGADDR_CFG(Structure):
    temp='DW16'
    hsizeh='DW16'
    hsizel ='DW16'
    vsizeh ='DW16'
    vsizel ='DW16'
    htsh ='DW16'
    htsl ='DW16'
    vtsh ='DW16'
    vtsl ='DW16'
    strmctrl='DW16'
    crch ='DW16'
    crcl ='DW16'
    crop_hsth='DW16'
    crop_hstl ='DW16'
    crop_vsth ='DW16'
    crop_vstl ='DW16'
    crop_hendh='DW16'
    crop_hendl ='DW16'
    crop_vendh ='DW16'
    crop_vendl ='DW16'
    rsvd=['DW8',88] #snr_regaddr

    def __init__(self):
        self.temp='x'
        self.hsizeh='x'
        self.hsizel ='x'
        self.vsizeh ='x'
        self.vsizel ='x'
        self.htsh ='x'
        self.htsl ='x'
        self.vtsh ='x'
        self.vtsl ='x'
        self.strmctrl='x'
        self.crch ='x'
        self.crcl ='x'
        self.crop_hsth='x'
        self.crop_hstl ='x'
        self.crop_vsth ='x'
        self.crop_vstl ='x'
        self.crop_hendh='x'
        self.crop_hendl ='x'
        self.crop_vendh ='x'
        self.crop_vendl ='x'
        self.rsvd =[]


class SNR_REG_CFG(Structure):
    ctrl='DW8'
    module_id='DW8'
    rsvd0='DW16'
    cclk ='DW32'
    sclk ='DW32'
    pclk ='DW32'
    hsize ='DW16'
    vsize ='DW16'
    hts ='DW16'
    vts ='DW16'
    vsdly ='DW16'
    format_type ='DW8'
    format_name ='DW8'
    snr_id ='DW32'
    sccb_num ='DW8'
    sccb_id ='DW8'
    sccb_addrlen ='DW8'
    crc_mode ='DW8'
    setting_len ='DW16'
    setting_id ='DW8'
    fsync_en ='DW8'
    blc =['DW16', 4]
    dvalue =['DW16', 4]
    # exp =['DW16', 4]
    tnegative='DW16'
    strobe_min='DW16'
    strobe_max='DW16'
    strobe_width='DW16'
    manual_mode='DW8'
    embl_en='DW8'
    rsvd1=['DW8',62] #snr_regaddr

    def __init__(self,_addr=0):
        self.ctrl= 0
        self.module_id='x'
        self.rsvd0 ='x'
        self.cclk ='x'
        self.sclk ='x'
        self.pclk ='x'
        self.hsize ='x'
        self.vsize ='x'
        self.hts ='x'
        self.vts ='x'
        self.vsdly ='x'
        self.format_type ='x'
        self.format_name ='x'
        self.snr_id ='x'
        self.sccb_num ='x'
        self.sccb_id ='x'
        self.sccb_addrlen='x'
        self.crc_mode ='x'
        self.setting_len ='x'
        self.setting_id = 'x'
        self.fsync_en = 'x'
        self.blc =[]
        self.dvalue =[]
        self.tnegative='x'
        self.strobe_min='x'
        self.strobe_max='x'
        self.strobe_width='x'
        self.manual_mode=0
        self.embl_en='x'
        # self.exp =[]
        self.rsvd1 =[]


class ALGO_REG_CFG(Structure):
    ctrl='DW8'
    module_id='DW8'
    rsvd0=['DW8',14]
    level1_intr0='DW32'
    level1_intr1='DW32'
    level1_intr2='DW32'
    level1_intr3='DW32'
    rsvd1=['DW8',224]

    def __init__(self):
        self.ctrl='x'
        self.module_id='x'
        self.rsvd0=[]
        self.level1_intr0=0x4000 #ISP_SOF BIT14
        self.level1_intr1=0x8000 #ISP_EOF BIT15
        self.level1_intr2=0x20 #ISP_AECDone BIT5
        self.level1_intr3=0x10000 #ISP_Stat_Done BIT16
        self.rsvd1=[]


class CRYPTO_REG_CFG(Structure):
    master_en='DW8'
    m_crpt_module_id='DW8'
    m_crpt_abmode_en='DW8'
    m_bmode_channel= 'DW8'
    m_embl_sei_post_length='DW32'
    m_geoma_b2h ='DW16'
    m_geomb_b2h ='DW16'
    m_inhsize ='DW16'
    m_invsize ='DW16'
    m_inhsize_b ='DW16'
    m_invsize_b ='DW16'
    m_a_vc_id= 'DW8'
    m_b_vc_id= 'DW8'
    slave_en= 'DW8'
    s_crpt_module_id= 'DW8'
    s_crpt_abmode_en= 'DW8'
    s_bmode_channel= 'DW8'
    s_geoma_b2h ='DW16'
    s_geomb_b2h ='DW16'
    s_inhsize ='DW16'
    s_invsize ='DW16'
    s_inhsize_b ='DW16'
    s_invsize_b ='DW16'
    s_a_vc_id= 'DW8'
    s_b_vc_id= 'DW8'
    s_ab_mode_map= 'DW8'
    m_snr_idx = 'DW8'
    crpt_rsvd=['DW8',86]

    def __init__(self,_sys=0):
        self.master_en='x'
        self.m_crpt_module_id='x'
        self.m_crpt_abmode_en='x'
        self.m_bmode_channel= 'x'
        self.m_embl_sei_post_length='x'
        self.m_geoma_b2h ='x'
        self.m_geomb_b2h ='x'
        self.m_inhsize ='x'
        self.m_invsize ='x'
        self.m_inhsize_b ='x'
        self.m_invsize_b ='x'
        self.m_a_vc_id= 'x'
        self.m_b_vc_id= 'x'
        self.slave_en= 'x'
        self.s_crpt_module_id= 'x'
        self.s_crpt_abmode_en= 'x'
        self.s_bmode_channel= 'x'
        self.s_geoma_b2h ='x'
        self.s_geomb_b2h ='x'
        self.s_inhsize ='x'
        self.s_invsize ='x'
        self.s_inhsize_b ='x'
        self.s_invsize_b ='x'
        self.s_a_vc_id= 'x'
        self.s_b_vc_id= 'x'
        self.s_ab_mode_map= 'x'
        self.m_snr_idx = 'x'
        self.crpt_rsvd=[]


class RGBIR_REG_CFG(Structure):
    ctrl='DW8'
    module_id='DW8'
    en ='DW8'
    rsvd=['DW8',61]

    def __init__(self,_sys=0):
        self.ctrl='x'
        self.module_id='x'
        self.en ='x'
        self.rsvd =[]


class OVIEMBL_PREDEF_CFG(Structure):
    manufacture_id='DW32'
    version_id='DW8'
    sub_id='DW8'
    setting_version='DW16'
    fw_version='DW16'
    rsvd=['DW8',22]

    def __init__(self,_sys=0):  #TODO need update in the future
        self.manufacture_id=0x4f565449 #"OVTI"
        self.version_id=0x55
        self.sub_id=0xaa
        self.setting_version=0x1234
        self.fw_version=0x8899
        self.rsvd =[]


class OVIEMBL_CTRL_CFG(Structure):
    rsvd=['DW8',12]
    validlen ='DW16'
    output_num='DW8'
    chain_cnt='DW8'
    chain=[('DW32','DW16'),32]

    def __init__(self,_sys=0):
        self.validlen='x'
        self.output_num='x'
        self.chain_cnt='x'
        self.rsvd =[]
        self.chain=[]


class EMBL_REG_CFG(Structure):
    ctrl='DW8'
    module_id='DW8'
    chn ='DW8'
    txport ='DW8'
    txchn ='DW8'
    # hmacen = 'DW8'
    rsvd0=['DW8',2]
    # ovipre_def=OVIEMBL_PREDEF_CFG()
    ovipre_def= ['DW8',32]
    ovipost_def=['DW8', 8]
    ovipre = OVIEMBL_CTRL_CFG()
    ovipost =OVIEMBL_CTRL_CFG()
    sei_pre_num ='DW8'
    sei_post_num ='DW8'
    sei_pre_validbyte ='DW16'
    sei_post_validbyte ='DW16'
    sei_rsvd=['DW8',10]
    sta_validbyte0 ='DW16'
    sta_validbyte1 ='DW16'
    sta_validbyte2 ='DW16'
    sta_validbyte3 ='DW16'
    sta_num ='DW8'
    sta_rsvd=['DW8',23]

    def __init__(self,_objlist=[0,0]):
        self.ctrl=0
        self.module_id='x'
        self.chn='x'
        self.txport='x'
        self.txchn='x'
        # self.hmacen='x'
        self.rsvd0 =[]
        # self.ovipre_def =OVIEMBL_PREDEF_CFG()
        self.ovipre_def =[]
        self.ovipost_def =[]
        self.ovipre =OVIEMBL_CTRL_CFG()
        self.ovipost =OVIEMBL_CTRL_CFG()
        self.sei_pre_num ='x'
        self.sei_post_num ='x'
        self.sei_pre_validbyte ='x'
        self.sei_post_validbyte ='x'
        self.sei_rsvd=[]
        self.sta_validbyte0 ='x'
        self.sta_validbyte1 ='x'
        self.sta_validbyte2 ='x'
        self.sta_validbyte3 ='x'
        self.sta_num ='x'
        self.sta_rsvd=[]


class PPLN_ISP_CFG(Structure): # 0x40 byte
    outhsize='DW16'
    outvsize='DW16'
    hts='DW16'
    vts='DW16'
    en='DW8'
    rsvd=['DW8',23]

    def __init__(self,_sys=0):
        self.outhsize='x'
        self.outvsize='x'
        self.hts='x'
        self.vts='x'
        self.en='x'
        self.rsvd=[]

class PPLN_OUTPUT_CFG(Structure): # 0x40 byte
    en='DW8'
    src='DW8'
    outfmt='DW8'
    outport='DW8'
    outvc='DW8'
    outchn='DW8'
    rsvd=['DW8',26]

    def __init__(self,_sys=0):
        self.en='x'
        self.src='x'
        self.outfmt='x'
        self.outport='x'
        self.outvc='x'
        self.outchn='x'
        self.rsvd=[]


class PPLN_SCALECROP_CFG(Structure):
    cropen = 'DW8'
    scalen = 'DW8'
    cohsize = 'DW16'
    covsize = 'DW16'
    sohsize = 'DW16'
    sovsize = 'DW16'
    scaleprecropen = 'DW16'
    scalepostcropen = 'DW16'
    scaleprecrop_hsize = 'DW16'
    scaleprecrop_vsize = 'DW16'
    scalepostcrop_hsize = 'DW16'
    scalepostcrop_vsize = 'DW16'

    def __init__(self):
        self.cropen = 'x'
        self.scalen = 'x'
        self.cohsize = 'x'
        self.covsize = 'x'
        self.sohsize = 'x'
        self.sovsize = 'x'
        self.scaleprecropen = 'x'
        self.scalepostcropen = 'x'
        self.scaleprecrop_hsize = 'x'
        self.scaleprecrop_vsize = 'x'
        self.scalepostcrop_hsize = 'x'
        self.scalepostcrop_vsize = 'x'


class PPLN_REG_CFG(Structure):
    strm_src='DW8'
    strm_mdl_id ='DW8'
    strm_upload_en ='DW8'
    fullfrm_en ='DW8'
    fullfrm_cnt ='DW8'
    lanenum='DW8'
    rgbir_mode = 'DW8'
    snrgrphd_idx = 'DW8'
    snrstrobe_en = 'DW8'
    rsvd0=['DW8',7]
    sclk='DW32'
    vsdly_max='DW16'
    vsdly_step='DW8'
    mrxport='DW8'
    idcport='DW8'
    ispport='DW8'
    rtport='DW8'
    cb_copy_snr_vld='DW8'
    # txport='DW8'
    rsvd1=['DW8',4]
    ispyuv =PPLN_ISP_CFG()
    ispraw =PPLN_ISP_CFG()
    ispmv  =PPLN_ISP_CFG()
    isprsvd=['DW8',32]
    outyuv= PPLN_OUTPUT_CFG()
    outraw= PPLN_OUTPUT_CFG()
    scalecrop = PPLN_SCALECROP_CFG()
    outrsvd1=['DW8',22]

    def __init__(self,_sys=0):
        self.strm_src='x'
        self.strm_mdl_id ='x'
        self.strm_upload_en ='x'
        self.fullfrm_en ='x'
        self.fullfrm_cnt ='x'
        self.lanenum='x'
        self.rgbir_mode = 'x'
        self.snrgrphd_idx = 0
        self.snrstrobe_en = 0
        self.rsvd0=[]
        self.sclk='x'
        self.vsdly_max='x'
        self.vsdly_step='x'
        self.mrxport='x'
        self.idcport='x'
        self.ispport='x'
        self.rtport='x'
        self.cb_copy_snr_vld='x'
        # self.txport='x'
        self.rsvd1=[]
        self.ispyuv =PPLN_ISP_CFG()
        self.ispraw =PPLN_ISP_CFG()
        self.ispmv  =PPLN_ISP_CFG()
        self.isprsvd=[]
        self.outyuv= PPLN_OUTPUT_CFG()
        self.outraw= PPLN_OUTPUT_CFG()
        self.scalecrop = PPLN_SCALECROP_CFG()
        self.outrsvd1=[]


class DP_REG_CFG(Structure):
    crypto=CRYPTO_REG_CFG()
    ppln=PPLN_REG_CFG()
    rsvd=['DW8',0x80]

    def __init__(self,_objlist=[0,0,0,0,0]):
        self.crypto=CRYPTO_REG_CFG()
        self.ppln=PPLN_REG_CFG()
        self.rsvd=[]


class SERSTREAM_CTRL(Structure):
    snr_index='DW8'
    ser_sccb_num='DW8'
    ser_sccb_id='DW8'
    ser_sccb_addrlen='DW8'

    def __init__(self):
        self.snr_index='x'
        self.ser_sccb_num='x'
        self.ser_sccb_id='x'
        self.ser_sccb_addrlen='x'


class SDS_REG_CFG(Structure):
    ctrl='DW8'
    module_id='DW8'
    mode_set='DW8'
    dser_sccb_num='DW8'
    dser_sccb_id='DW8'
    dser_sccb_addrlen='DW8'
    setting_len='DW16'
    rsvd0=['DW8',8]
    stream_num = 'DW8'
    serstrm_ctrl0 = SERSTREAM_CTRL()
    serstrm_ctrl1 = SERSTREAM_CTRL()
    serstrm_ctrl2 = SERSTREAM_CTRL()
    serstrm_ctrl3 = SERSTREAM_CTRL()
    rsvd1=['DW8',31]

    def __init__(self,_objlist=[0,0,0,0]):
        self.ctrl='x'
        self.module_id='x'
        self.mode_set='x'
        self.dser_sccb_num='x'
        self.dser_sccb_id ='x'
        self.dser_sccb_addrlen ='x'
        self.setting_len='x'
        self.stream_num ='x'
        #self.snr_moduleid=[]
        self.serstrm_ctrl0 = SERSTREAM_CTRL()
        self.serstrm_ctrl1 = SERSTREAM_CTRL()
        self.serstrm_ctrl2 = SERSTREAM_CTRL()
        self.serstrm_ctrl3 = SERSTREAM_CTRL()
        self.rsvd0=[]
        self.rsvd1=[]


class SCCB_REG_CFG(Structure):
    ctrl='DW8'
    num='DW8'
    rsvd0=['DW8',2]
    speed='DW32'
    timeout='DW32'
    sds_en ='DW8'
    sds_idx ='DW8'
    rsvd=['DW8',18]

    def __init__(self,_sys=0):
        self.ctrl='x'
        self.num='x'
        self.rsvd0=[]
        self.speed='x'
        self.timeout='x'
        self.sds_en ='x'
        self.sds_idx ='x'
        self.rsvd=[]


class SYSTEM_REGLOAD_CFG(Structure):
    baseaddrh='DW16'
    setcnt='DW8'
    rsvd=['DW8',5]
    table =[('DW16','DW32'),10]

    def __init__(self,_sys=0):
        self.baseaddrh='x'
        self.setcnt='x'
        self.rsvd=[]
        self.table =[]


class SYSTEM_REG_CFG(Structure):
    sysclk='DW32'
    periclk='DW32'
    rsvd=['DW8',8]
    vendor_id='DW32'
    version_id='DW8'
    sub_id='DW8'
    set_version='DW16'
    fw_version='DW16'
    patch_version='DW16'
    setload =SYSTEM_REGLOAD_CFG()
    rsvd1=['DW8',16]


    def __init__(self,_sys=0):
        self.sysclk='x'
        self.periclk='x'
        self.rsvd=[]
        self.vendor_id='x'
        self.version_id='x'
        self.sub_id='x'
        self.set_version='x'
        self.fw_version='x'
        self.patch_version='x'
        self.setload =SYSTEM_REGLOAD_CFG()
        self.rsvd1=[]


class CONTROL_REG_CFG(Structure):
    dp_active_num ='DW8'
    sds_active_num ='DW8'
    sccb_active_num ='DW8'
    bootmode ='DW8'
    algo_disable ='DW8'
    algo_disable_2 ='DW8'
    sequence_setting_en='DW8'
    sequence_group_idx='DW8'
    rsvd=['DW8',24]

    def __init__(self,_sys=0):
        self.dp_active_num ='x'
        self.sds_active_num ='x'
        self.sccb_active_num ='x'
        self.bootmode ='x'
        self.algo_disable ='x'
        self.algo_disable_2 ='x'
        self.sequence_setting_en=0
        self.sequence_group_idx=0
        self.rsvd=[]


class HOSTCMD_REG_CFG(Structure):
    timeout ='DW32'
    lock_key ='DW32'
    lock_thres ='DW32'
    unlock_thres ='DW32'
    lock_en ='DW8'
    crc_mode ='DW8'
    seq_en ='DW8'
    thread_prio='DW8'
    rsvd0=['DW8',11]  #tbd
    strm_ctrl_mode='DW8'
    cmd_irq_opts_en='DW8'
    int_type=['DW8',256]  #tbd
    rsvd1=['DW8',15]  #tbd

    def __init__(self,_sys=0):
        self.timeout ='x'
        self.lock_key ='x'
        self.lock_thres ='x'
        self.unlock_thres ='x'
        self.lock_en ='x'
        self.crc_mode ='x'
        self.seq_en ='x'
        self.thread_prio='x'
        self.strm_ctrl_mode='x'
        self.cmd_irq_opts_en='x'
        self.rsvd0=[]  #tbd
        self.rsvd1=[]  #tbd
        self.int_type=[]  #tbd


class SAFETY_REG_CFG(Structure):
    fcp_clrctrl='DW32'
    fcp_enactrl='DW32'
    fcp_fnum = 'DW8'
    rsvd=['DW8',631]

    def __init__(self):
#        self.fcp_clrctrl=0x88fe0fff # datapath clear by external host, 0 : extenal host clear 1: firmware clear
        self.fcp_clrctrl=0xffffffff
        self.fcp_enactrl=0xffffffff # datapath clear by external host    0: disable ,1: enable
        self.fcp_fnum = 0x80
        self.rsvd=[]


class ALGO_PIPEREG(Structure): #total 0x80
    param_addr=['DW32',16]
    read_snrsei_en='DW8'
    rsvd=['DW8',63]

    def __init__(self):
        self.param_addr=[]
        self.read_snrsei_en=0
        self.rsvd=[]


class ALGO_REG_CFG(Structure):
    common=['DW8',512]
    pipereg0=ALGO_PIPEREG()
    pipereg1=ALGO_PIPEREG()
    pipereg2=ALGO_PIPEREG()
    pipereg3=ALGO_PIPEREG()

    def __init__(self):
        self.common=[]
        self.pipereg0=ALGO_PIPEREG()
        self.pipereg1=ALGO_PIPEREG()
        self.pipereg2=ALGO_PIPEREG()
        self.pipereg3=ALGO_PIPEREG()


class CFW_REG_CFG(Structure):
    # rsvd=['DW8',3072]
    rsvd=['DW8',2048]
    algo=ALGO_REG_CFG()
    safe=SAFETY_REG_CFG()
    rgbir0=RGBIR_REG_CFG()
    rgbir1=RGBIR_REG_CFG()
    sds0=SDS_REG_CFG()
    sds1=SDS_REG_CFG()
    sds2=SDS_REG_CFG()
    sds3=SDS_REG_CFG()
    snr0 =SNR_REG_CFG()
    snr1 =SNR_REG_CFG()
    snr2 =SNR_REG_CFG()
    snr3 =SNR_REG_CFG()
    sccb0=SCCB_REG_CFG()
    sccb1=SCCB_REG_CFG()
    hcmd=HOSTCMD_REG_CFG()
    sys=SYSTEM_REG_CFG()
    ctrl=CONTROL_REG_CFG()
    embl0=EMBL_REG_CFG()
    embl1=EMBL_REG_CFG()
    embl2=EMBL_REG_CFG()
    embl3=EMBL_REG_CFG()
    dp0=DP_REG_CFG()
    dp1=DP_REG_CFG()
    dp2=DP_REG_CFG()
    dp3=DP_REG_CFG()

    def __init__(self,_objlist=[range(13)]):
        self.rsvd=[]
        self.safe=SAFETY_REG_CFG()
        self.rgbir0=RGBIR_REG_CFG()
        self.rgbir1=RGBIR_REG_CFG()
        self.sds0=SDS_REG_CFG()
        self.sds1=SDS_REG_CFG()
        self.sds2=SDS_REG_CFG()
        self.sds3=SDS_REG_CFG()
        self.dp0=DP_REG_CFG()
        self.dp1=DP_REG_CFG()
        self.dp2=DP_REG_CFG()
        self.dp3=DP_REG_CFG()
        self.embl0=EMBL_REG_CFG()
        self.embl1=EMBL_REG_CFG()
        self.embl2=EMBL_REG_CFG()
        self.embl3=EMBL_REG_CFG()
        self.snr0 =SNR_REG_CFG()
        self.snr1 =SNR_REG_CFG()
        self.snr2 =SNR_REG_CFG()
        self.snr3 =SNR_REG_CFG()
        self.sccb0=SCCB_REG_CFG()
        self.sccb1=SCCB_REG_CFG()
        self.hcmd=HOSTCMD_REG_CFG()
        self.sys=SYSTEM_REG_CFG()
        self.ctrl=CONTROL_REG_CFG()
