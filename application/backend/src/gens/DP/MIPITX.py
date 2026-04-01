# WARNING
# pylint: disable=C0103, C0114, C0115, C0116, C0200, C0412, W0231, W0401, W0612, W0613, W0614, W0622
from Utility.Reg import REGOBJ
from Utility.Entity import Entity
from Utility.Para import *
from Define.Para import *
from Utility.Others import *
from RegTable.Regdefdist import define_dist


MHZ = 1000000


mipitx_lane_dict={
    0:0,
    1:3,
    2:7,
    3:0x0f,
    4:0x1f,
}


class MIPITX_CHANNEL_CFG(object):
    def __init__(self,id):
        self.en =0
        self.img_dt =0
        self.embl_dt =0
        self.img_id =0
        self.crc_len =0
        self.crc_vsize =0
        self.feint_en =1
        self.chn =0
        self.sbs_en =0


class MIPITX_BASIC_CFG(object):
    def __init__(self):
        self.lane_ctrl =0
        self.scramble_en =0
        self.ext_timing =0
        self.sbs_en =0
        self.clk_gate =0
        self.clkdat_exchg =0
        self.sof_send_fs =0
        self.ds_en =0
        self.ds_pu_en =0
        self.ds_fb_en =0
        self.ds_alte_en =0
        self.lrte_timeout_en =0
        self.misc_epd_en =0
        self.clk_period =0
        self.ds_pt = 0
        self.ds_fbcycle =0
        self.ds_pucycle =0
        self.ds_altecycle =0
        self.lfsr_lane1 =0
        self.lfsr_lane2 =0
        self.lfsr_lane3 =0
        self.lfsr_lane4 =0
        self.epd_ssp =0
        self.epd_lsp =0
        self.epd_en =0


#class MIPITX_CFG(object):
#    def __init__(self,chipcfg):
#        self.lane=4
#        self.gateclk=0
#        self.lsync=1
#        self.fstype=1
#        self.yuv=CHANNEL_CFG()
#        self.raw=CHANNEL_CFG()
#        self.embl=CHANNEL_CFG()
#        self.freq=150
#        self.en =0
#        self.laneswap =0


class MIPITX_CFG(object):
    def __init__(self,chipcfg,uid):
        self.index =uid
        self.intvl_time =4
        self.vc0=MIPITX_CHANNEL_CFG(0)
        self.vc1=MIPITX_CHANNEL_CFG(1)
        self.vc2=MIPITX_CHANNEL_CFG(2)
        self.vc3=MIPITX_CHANNEL_CFG(3)
        if uid ==0:
            self.vc4=MIPITX_CHANNEL_CFG(4)
            self.vc5=MIPITX_CHANNEL_CFG(5)
            self.vc6=MIPITX_CHANNEL_CFG(6)
            self.vc7=MIPITX_CHANNEL_CFG(7)
        self.ctrl =MIPITX_BASIC_CFG()


class MIPITX_REG(REGOBJ):
    def __init__(self,cfg,uid):
        self.base =self.get_baseaddr('MIPI_TX_CHN',define_dist,uid)
        self.regtable=cfg.regtable
        self.objr=[]


class MIPITX(Entity):
    """description of class"""
    def __init__(self,chipcfg,uid):
        self.cfg =MIPITX_CFG(chipcfg,uid)
        self.reg =MIPITX_REG(chipcfg,uid)
        self.uid = uid
        self.chip= chipcfg
        self._cfg_init(chipcfg,uid)
        self.setbuf=[]

    def _cfg_init(self,chipcfg,uid):
        out0 =chipcfg.oax4k_cfg.out0
        out1 =chipcfg.oax4k_cfg.out1
        out2 =chipcfg.oax4k_cfg.out2
        out3 =chipcfg.oax4k_cfg.out3
        clkt = chipcfg.oax4k_cfg.sys.clkt
        do_clks = [clkt.do0clk, clkt.do0clk,
                    clkt.do1clk, clkt.do1clk]
        self.do_clk = do_clks[uid]
        outlist = [out0,out1,out2,out3]
        if uid ==0:
            vclist = [self.cfg.vc0,self.cfg.vc1,self.cfg.vc2,self.cfg.vc3,self.cfg.vc4,self.cfg.vc5,self.cfg.vc6,self.cfg.vc7]
        else:
            vclist = [self.cfg.vc0,self.cfg.vc1,self.cfg.vc2,self.cfg.vc3]
        chnlist = outlist[uid].chnlist
        if self.cfg.index//2:
            self.cfg.intvl_time = round(clkt.do0clk/ clkt.do1clk*4)
        for i in range(len(chnlist)):
            if  chnlist[i].txfmt != 0xff:
                rawformat,hmul =get_dict_key(output_raw_format_dict,chnlist[i].txfmt) if (raw_sel_dist[chnlist[i].sel]!='ISPMV') else  get_dict_key(output_yuv_format_dict,chnlist[i].format)
            else:
                rawformat,hmul =get_dict_key(output_raw_format_dict,chnlist[i].format) if (raw_sel_dist[chnlist[i].sel]!='ISPMV') else  get_dict_key(output_yuv_format_dict,chnlist[i].format)
            format_name,hmul = get_dict_key(output_yuv_format_dict,chnlist[i].format) if (chnlist[i].index) else  (rawformat,hmul)
            vclist[i].img_dt=mipitx_datatype_dict[format_name]
            vclist[i].embl_dt=mipitx_datatype_dict[format_name] # embedded line output the same dt with image
            vclist[i].img_id = chnlist[i].outvc
            vclist[i].sbs_en = chnlist[i].sbsen
            # if( vclist[i].sbs_en):
            #     print("out {} chn {} sbs en".format(uid,i))
            # print("chnlist[{}].outvc {}".format(i, chnlist[i].outvc))
            # print("!!!!vclist[{}] format_name {}, img_dt 0x{:x}".format(i, format_name, vclist[i].img_dt))
            byterate,*_ = rt_byterate_dict[format_name]
            if chnlist[i].hsize %16:
                crc_act_len =  (int(chnlist[i].hsize/8)+1)*8*chnlist[i].vsize* byterate/2
            else:
                crc_act_len =  chnlist[i].hsize*chnlist[i].vsize* byterate /2
            vclist[i].crc_len = int(crc_act_len)  # tbd
            vclist[i].en =chnlist[i].en
            if chnlist[i].emblbuf!=[]:
                outemb =chnlist[i].emblbuf[0]
                pre_embl_num = outemb.seipre.outnum + outemb.ovipre.outnum
                vclist[i].feint_en =1
                vclist[i].chn = chnlist[i].outchn
            else:
                pre_embl_num =0
            vclist[i].crc_vsize = chnlist[i].vsize + pre_embl_num
            # print("mipit tx vc{} crc vsize{} preembl{}".format(i,vclist[i].crc_vsize,pre_embl_num))
        self.cfg_ctrl_init(outlist[uid].mtx.csi)

    def cfg_ctrl_init(self,outmipi):
        ctrl =self.cfg.ctrl
        ctrl.clk_gate= outmipi.clkmode
        ctrl.lane_ctrl =mipitx_lane_dict[outmipi.lane]
        clkt = self.chip.oax4k_cfg.sys.clkt
        do_clks = [clkt.do0clk, clkt.do0clk,
                    clkt.do1clk, clkt.do1clk]
        if do_clks[self.uid] > 94*MHZ or outmipi.deskew:
            ctrl.ds_en = 1
        else:
            ctrl.ds_en = 0
        # ctrl.ds_en =outmipi.deskew
        ctrl.sof_send_fs = outmipi.fstype
#       ctrl.ds_alte_en = outmipi.deskew_alte
        ctrl.ds_pt = outmipi.deskew_pt
        ctrl.ds_fbcycle = outmipi.deskew_fbcycle
        ctrl.ds_pucycle = outmipi.deskew_pucycle
        ctrl.ds_altecycle = outmipi.deskew_altecycle
        ctrl.ds_fb_en = outmipi.deskew_fb
        ctrl.ds_pu_en = outmipi.deskew_pu
        ctrl.lfsr_lane1 = outmipi.lfsr1
        ctrl.lfsr_lane2 = outmipi.lfsr2
        ctrl.lfsr_lane3 = outmipi.lfsr3
        ctrl.lfsr_lane4 = outmipi.lfsr4
        ctrl.scramble_en =outmipi.scramble
        ctrl.lrte_timeout_en = outmipi.lrte_timeout
        ctrl.ext_timing = outmipi.ext_timing
        ctrl.epd_ssp = outmipi.epd_ssp
        ctrl.epd_lsp = outmipi.epd_lsp
        ctrl.epd_en = outmipi.epd_en
        ctrl.misc_epd_en = outmipi.epd_misc
        ctrl.clk_period  = int(4*1000/(outmipi.freq/1000000))
        if ctrl.clk_period >255:
            ctrl.clk_period = 255
        if( ctrl.epd_en and (ctrl.ds_fb_en&ctrl.ds_en) ):
            raise RuntimeError("LRTE-1 can't work when FB deskew enable")

    def start(self):
        chipcfg =self.chip
        cfg =self.cfg
        #vc0 =self.cfg.vc0
        ctrl =self.cfg.ctrl
        if self.uid ==0:
            vclist = [self.cfg.vc0,self.cfg.vc1,self.cfg.vc2,self.cfg.vc3,self.cfg.vc4,self.cfg.vc5,self.cfg.vc6,self.cfg.vc7]
        else:
            vclist = [self.cfg.vc0,self.cfg.vc1,self.cfg.vc2,self.cfg.vc3]
        for i in range (len(vclist)):
            if i<4:
                # print("!!!!!vclist[{}].en {} img_dt 0x{:x}".format(i, vclist[i].en, vclist[i].img_dt))
                if vclist[i].en:
                    if i==0:
                        self.reg.writereg32(0+i*4,(vclist[i].img_dt<<16)|(vclist[i].embl_dt<<24) |(vclist[i].sbs_en<<30) |0xffff)
                    else:
                        self.reg.writereg32(0+i*4,(vclist[i].img_dt<<16)|(vclist[i].embl_dt<<24) |0xffff )
            else:
                if vclist[i].en:
                    self.reg.writereg32(0x8+i*4,(vclist[i].img_dt<<16)|(vclist[i].embl_dt<<24) |0xffff )
            if vclist[i].en:
                self.reg.writereg32(0x28+i*4,vclist[i].crc_len | (0x1f << 24))
                self.reg.writereg16(0x74+i*2,vclist[i].crc_vsize )
            else:
                self.reg.writereg32(0x28+i*4, 0)
        r10 =0
        r190 =0
        for i in range(len(vclist)):
            r10 = r10 | (vclist[i].img_id<<(i*4))
            r190 = r190 | (vclist[i].feint_en<< vclist[i].chn)
        self.reg.writereg32(0x10,r10)
        # print("MTX {} do_clk {}".format(self.uid, self.do_clk))
        ############################################################################################
        # Assumming current clock period is T (ns)
        # clock lane timing check register is MIPI TX 0x68, this register can be set as :
        # BIT[7:0] <= (40/T),   BIT[15:8] <= (38/T),    BIT[23:16]>= (95/T)
        # data lane timing check register is MIPI TX 0x6c, this register can be set as :
        # BIT[7:0] <= (40/T),   BIT[15:8] <= (40/T),    BIT[23:16]>= (85/T)
        #############################################################################################
        r68 = int_inc(40 * self.do_clk / 1000000000)
        r69 = int_inc(38 * self.do_clk / 1000000000) - 1
        r6a = int_inc(95 * self.do_clk / 1000000000) + 1
        r6c = int_inc(40 * self.do_clk / 1000000000)
        r6d = int_inc(40 * self.do_clk / 1000000000) - 1
        r6e = int_inc(85 * self.do_clk / 1000000000) + 1
        # r68 = 0
        # r69 = 1
        # r6a = 3
        # r6c = 0
        # r6d = 1
        # r6e = 3
        self.reg.writereg8(0x68, r68)
        self.reg.writereg8(0x69, r69)
        self.reg.writereg8(0x6a, r6a)
        self.reg.writereg8(0x6c, r6c)
        self.reg.writereg8(0x6d, r6d)
        self.reg.writereg8(0x6e, r6e)
        # BIT17: detect channel error enable
        # BIT18: force channel to generate FE when error is detected
        r100 = ctrl.lane_ctrl | (ctrl.scramble_en<<5) |(ctrl.ext_timing<<6) |\
            (ctrl.clkdat_exchg<<11)|(ctrl.clk_gate<<12)|(ctrl.sof_send_fs<<16)|(ctrl.lrte_timeout_en<<22)|(ctrl.misc_epd_en<<23)  | BIT17 | BIT18
        self.reg.writereg32(0x100,r100)
        self.reg.writereg8(0x105, 0x1)  #TOIMPLEMENT vld time should be based on do_clk
        self.reg.writereg32(0x158,ctrl.ds_en | (ctrl.ds_pu_en<<2)|(ctrl.ds_fb_en<<3)|(ctrl.ds_pt<<8)|(ctrl.ds_pucycle<<16))
        self.reg.writereg32(0x15c,ctrl.ds_fbcycle | (ctrl.ds_altecycle<<16))
        self.reg.writereg32(0x108,ctrl.epd_ssp | (ctrl.epd_en<<15) | (ctrl.epd_lsp<<16))
        self.reg.writereg32(0x180,ctrl.lfsr_lane1 | (ctrl.lfsr_lane2<<16))
        self.reg.writereg32(0x184,ctrl.lfsr_lane3 | (ctrl.lfsr_lane4<<16))
        self.reg.writereg8(0x147,ctrl.clk_period) # mipoi period
        self.reg.writereg8(0x199, 0x1)
        self.reg.writereg8(0x190, r190)
        self.reg.writereg8(0x18c, r190)
        if self.cfg.index//2:
            self.reg.writereg8(0x131, self.cfg.intvl_time)
        self.reg.writereg8(0x142,60)  #set lpx to 60ns
        self.reg.writereg8(0x139,self.reg.readreg8(0x139)+16)  # add 16 ui for hs_prepare for analog async
        r13b = self.reg.readreg8(0x13b)
        self.reg.writereg8(0x13b,(((r13b>>2)+16) <<2 )+(r13b&0x03))  # add 16 ui for hs_prepare for analog async
        self.reg.writereg8(0x13d,self.reg.readreg8(0x13d)+16)  # add 16 ui for hs_prepare for analog async
        self.reg.writereg8(0x13f,self.reg.readreg8(0x13f)+16)  # add 16 ui for hs_prepare for analog async
        self.reg.writereg8(0x141,self.reg.readreg8(0x141)+16)  #add 16ui for hs_zero
        self.reg.writereg8(0x145,self.reg.readreg8(0x145)+16)  #add 16ui for hs_trail
