# WARNING
# pylint: disable=C0103, C0114, C0115, C0200, C0412, W0231, W0401, W0612, W0613, W0614, W0622
from Utility.Reg import REGOBJ
from Utility.Entity import Entity
from Utility.Para import *
from Define.Para import *
from Utility.Others import *
from RegTable.Regdefdist import *
# import gens_globals


IDC_MAXIMUM_MEM_DEPTH =2772*4


idc_format_chnno_dict ={
    "3X12RAW":3,
    "3X10RAW":3,
    "2X12RAW":2,
    "2X10RAW":2,
    "2X11RAW":2,
    # "YUV422":1,
    "YUV422":2,
    "RAW12":1,
    "12+12RAW":2,
    "16+12RAW":2,
    "COM24":1,
    "24+LFM":1,
    "COM20":1,
    "COM16":1,
    "COM14":1,  
    "COM12":1,
    "4X12RAW":4,
    "4X10RAW":4,
    "RAW10":1,
    "12+SPD10" : 2,
    "16+SPD10" : 2,
    }


rgbir_bitpos_format_dict ={
    "3X12RAW":0,
    "3X10RAW":2,
    "2X12RAW":0,
    "2X10RAW":2,
    "RAW12":0,
    "RAW10":2,
    "4X12RAW":0,
    "4X10RAW":2,
}


class IDC_ITPG_CFG():
    def __init__(self):
        self.lum_en =0
        self.load_seed =0
        self.rand_en =0
        self.ch1_shift =0
        self.ch2_shift =0
        self.ch3_shift =0
        self.start_mode =0
        self.ln_hblank =0


class IDC_COMMON_CFG():
    def __init__(self):
        self.swset_err =0
        self.vsync_overlap_adjust =1
        self.booton_test_en =0
        self.itpg = IDC_ITPG_CFG()


class IDC_MEMORY_CFG():
    def __init__(self,id):
        self.index =id
        self.addr =0
        self.len =0


class IDC_PATH_CFG():
    def __init__(self,id):
        self.sel =id
        self.en =0
        self.intr_en =1
        self.emb_en =0
        self.sta_en =0
        self.safe_en =0
        self.vs_delay_en =0
        self.mem_share =0
        self.rd_auto =0
        self.rgbir_en =0
        self.err_all_clr =0
        self.intr_all_clr =0
        self.sen_src =0
        self.sen_mode =0
        self.sen_fmt =0
        self.sen_vcid0 =0
        self.sen_vcid1 =1
        self.sen_vcid2 =2
        self.sen_vcid3 =3
        self.sof_sel =0
        self.eof_sel =0
        self.sen_intlv0 =0
        self.sen_intlv1 =1
        self.sen_intlv2 =2
        self.sen_intlv3 =3
        self.delay_sel =0
        self.sen_id =id
        self.emb_pre_vcid =0
        self.emb_post_vcid=0
        self.emb_pre_chn =0
        self.emb_pos_chn =0
        self.emb_pre_bitpos =0
        self.emb_pos_bitpos =0
        self.emb_pix_endian =0
        self.emb_sof_sel =0
        self.emb_eof_sel =0
        self.emb_pre_num =0
        self.emb_post_num =0
        self.sta_chn_vc = [0,1,2,3]
        self.sta_bit_pos =0
        self.sta_in_mode =0
        self.sta_sof_sel =0
        self.sta_eof_sel =0
        self.rd_start_ln =0
        self.dlymax_ln =0
        self.rd_start_ref =0
        self.sel_err_enj =0
        self.mem_err_enj =0
        self.id_err_enj =0
        self.sof_dly_cnt =0
        self.eof_dly_cnt =0
        self.sen_hsize =0
        self.sen_vsize =0
        self.mem_buf=[]
        self.rgbir_bitpos =2
        self.rgbir_hblk  =100
        self.pix_width =0
        self.pix_width12p12 =0
        self.full_frm_en = 1
        # self.mem0_addr =0
        # self.mem0_len =0
        # self.mem1_addr =0
        # self.mem1_len =0
        # self.mem2_addr =0
        # self.mem2_len =0
        # self.mem3_addr =0
        # self.mem3_len =0


class IDC_CFG(object):
    def __init__(self,chipcfg):
        self.cmmn= IDC_COMMON_CFG()
        self.path0=IDC_PATH_CFG(0)
        self.path1=IDC_PATH_CFG(1)
        self.path2=IDC_PATH_CFG(2)
        self.path3=IDC_PATH_CFG(3)


class IDC_REG(REGOBJ):
    def __init__(self,cfg,uid=0):
        self.base =self.get_baseaddr('IDC',define_dist,uid)
        self.regtable=cfg.regtable
        self.objr=[]


class IDC(Entity):
    """description of class"""
    def __init__(self,chipcfg,uid=0):
        self.cfg =IDC_CFG(chipcfg)
        self.reg =IDC_REG(chipcfg,uid)
        self.setbuf=[]
        self._idc_cfg_init(chipcfg)

    def _idc_common_cfg_init(self,chipcfg):
        self.cfg.cmmn.swset_err =0
        # self.cfg.cmmn.itpg.lum_en =chipcfg.oax4k_cfg.topctrl.rgbirtp_mode
        self.cfg.cmmn.itpg.lum_en =chipcfg.oax4k_cfg.rgbir.tpmode
        self.cfg.cmmn.itpg.load_seed =0
        # self.cfg.cmmn.itpg.rand_en =0 if(chipcfg.oax4k_cfg.topctrl.rgbirtp_mode) else 1
        self.cfg.cmmn.itpg.rand_en =0 if(chipcfg.oax4k_cfg.rgbir.tpmode) else 1
        self.cfg.cmmn.itpg.ch1_shift =1
        self.cfg.cmmn.itpg.ch2_shift =2
        self.cfg.cmmn.itpg.ch3_shift =3
        # ln_hblank =chipcfg.oax4k_cfg.topctrl.rgbir_hblk if(chipcfg.oax4k_cfg.rgbir.en) else chipcfg.oax4k_cfg.topctrl.idp_hblk
        ln_hblank =chipcfg.oax4k_cfg.rgbir.lnhblk if(chipcfg.oax4k_cfg.rgbir.en) else chipcfg.oax4k_cfg.topctrl.idp_hblk
        self.cfg.cmmn.itpg.ln_hblank =ln_hblank

    def _idc_path_init(self,idcp,dp,chipcfg):
        # print("init idp {}".format(idcp))
        dpin =dp.dibuf[0]
        snr = dpin.cb_buf[0] if(dpin.cben) else dpin.sensor_buf[dp.input.strmsrc]
        idcp.en =dp.en & dp.input.idcen
        idcp.pix_width = dpin.pix_width
        idcp.pix_width12p12 = dpin.pix_width
        idcp.rd_auto= not dp.input.fixen
        idcp.mem_share= 0 if(idcp.sel %2) else dp.input.mem_share
        idcp.emb_en =1 if (snr.embl.pre.num |snr.embl.post.num) else 0
        idcp.emb_pre_bitpos = snr.embl.pre.bitpos
        idcp.emb_pos_bitpos = snr.embl.post.bitpos
        idcp.full_frm_en = dp.input.fullfrm_en
        # print("!!!!!!!!!!!!idc emb_pre_bitpos {} post bitpos {}".format(idcp.emb_pre_bitpos,
        #     idcp.emb_pos_bitpos))
        idcp.sta_en =snr.embl.sta.en
        idcp.safe_en = dp.input.safe_en  #tbd
        idcp.vs_delay_en = snr.strm.vsdly_en
        idcp.sen_src = dp.input.portsrc
        idcp.sen_mode = snr.strm.imgmode
        # idcp.sen_fmt = 5 if (snr.strm.format ==50 ) else snr.strm.format
        # # idcp.sen_fmt = 14 if (idcp.sen_fmt==15 ) else idcp.sen_fmt
        # idcp.sen_fmt = 12 if (idcp.sen_fmt==120 ) else idcp.sen_fmt
        # idcp.sen_fmt = 6 if (idcp.sen_fmt == 16) else idcp.sen_fmt
        # idcp.sen_fmt = 7 if (idcp.sen_fmt == 17) else idcp.sen_fmt
        # idcp.sen_fmt = 8 if (idcp.sen_fmt == 18) else idcp.sen_fmt
        idcp.sen_fmt = snr.strm.format &0x3f
        idcp.sen_hsize =snr.strm.hsize
        idcp.sen_vsize =snr.strm.vsize
        if idcp.sen_fmt == 4: # yuv in
            if dp.yuvin_mode:
                idcp.sen_fmt =8
            else:
                if idcp.sen_hsize%8:
                    raise RuntimeError(f"yuv in hsize must be 8x ,actual {idcp.sen_hsize}")
        # print("!!!!idc hsize {} vsize {}".format(idcp.sen_hsize, idcp.sen_vsize))
        if idcp.vs_delay_en:
            if idcp.rd_auto:
                idcp.rd_start_ln=2
            else:
                if(dp.input.rd_start >dp.input.bufline_max  or (dp.input.rd_start==1 ) ):
                    raise RuntimeError(f"idc rd start line is not fitable {dp.input.rd_start} {dp.input.bufline_max}")
                else:
                    idcp.rd_start_ln =dp.input.rd_start if(dp.input.rd_start) else dp.input.bufline_max  # tbd equal max_vs_dly ?
            idcp.dlymax_ln = dp.input.bufline_max  &0x7f
        else:
            if idcp.rd_auto:
                idcp.rd_start_ln=2
            else:
                if(dp.input.rd_start >dp.input.bufline_max  or (dp.input.rd_start==1 ) ):
                    raise RuntimeError(f"idc rd start line is not fitable {dp.input.rd_start} {dp.input.bufline_max}")
                idcp.rd_start_ln = dp.input.rd_start if(dp.input.rd_start) else 2
            # idcp.dlymax_ln  =
        # idcp.rgbir_en = dp.input.rgbiren
        idcp.rgbir_en = dp.rgbiren
        if idcp.rgbir_en:
            rgbir_dps=[chipcfg.oax4k_cfg.rgbir.dp0,chipcfg.oax4k_cfg.rgbir.dp1]
            rgbir_cfg =rgbir_dps[int(idcp.sel/2)]
            idcp.rgbir_hblk = rgbir_cfg.exphblk
        # if snr.strm.preblank:
        #     idcp.sof_dly_cnt = int(snr.strm.hts*chipcfg.oax4k_cfg.sys.clkt.dpclk/ dp.input.sclk *snr.strm.preblank) #TBD
        # else:
        #     idcp.sof_dly_cnt = 0x100
        sof_dly_line = 2 if(dp.input.seof_dlymode) else (max(snr.strm.preblank,2) -2) # for x8b, x3c, need -2,other can -1
        eof_dly_line =  2 if(dp.input.seof_dlymode) else max(snr.strm.preblank,2)
        if(dp.input.fixen and idcp.vs_delay_en ):
            idcp.sof_dly_cnt = int(snr.strm.hts*chipcfg.oax4k_cfg.sys.clkt.dpclk/ dp.input.sclk * (idcp.rd_start_ln +sof_dly_line)) #TBD
            idcp.eof_dly_cnt = int(snr.strm.hts*chipcfg.oax4k_cfg.sys.clkt.dpclk/ dp.input.sclk * (idcp.rd_start_ln +eof_dly_line+dp.input.extra_bufline))
        else:
            idcp.sof_dly_cnt = int(snr.strm.hts*chipcfg.oax4k_cfg.sys.clkt.dpclk/ dp.input.sclk * sof_dly_line)
            idcp.eof_dly_cnt = int(snr.strm.hts*chipcfg.oax4k_cfg.sys.clkt.dpclk/ dp.input.sclk * (eof_dly_line +dp.input.extra_bufline))
        # print("idcp sof_dly_cnt {}".format(idcp.sof_dly_cnt))
        idcvcid_ls =[idcp.sen_vcid0,idcp.sen_vcid1,idcp.sen_vcid2,idcp.sen_vcid3]
        for i in range(len(snr.strm.vclist)):
            idcvcid_ls[i] =snr.strm.vclist[i]
        [idcp.sen_vcid0,idcp.sen_vcid1,idcp.sen_vcid2,idcp.sen_vcid3] = idcvcid_ls
        idcp.emb_pre_vcid =snr.embl.pre.emb_vcid
        idcp.emb_post_vcid =snr.embl.post.emb_vcid
        idcp.emb_pre_chn = snr.strm.emblchn
        idcp.emb_pos_chn = snr.strm.emblchn
        idcp.emb_pre_num =snr.embl.pre.num
        idcp.emb_post_num =snr.embl.post.num
        idcp.sta_num =snr.embl.sta.chn_num
        idcp.sta_chn_vc = snr.embl.sta.chn_vc
        idcp.sta_in_mode = snr.embl.sta.mode
        # print("!!!!!!!!!!!sta num {}".format(idcp.sta_num))
        snrfmtname =get_dict_key(input_format_dict,idcp.sen_fmt)
        # print("[IDC] {:s}".format(snrfmtname))
        if idcp.rgbir_en:
            idcp.rgbir_bitpos =rgbir_bitpos_format_dict[snrfmtname]  # pyright: ignore[reportArgumentType]
        # self._idc_mem_cfg_init(idcp)
        self._idc_mem_cfg_init_new(idcp)

    def _idc_mem_cfg_init_new(self,path):
        chnno = idc_format_chnno_dict[get_dict_key(input_format_dict,path.sen_fmt)]  # pyright: ignore[reportArgumentType]
        div_a,div_b,_ = idc_mem_hsize_div_dict[get_dict_key(input_format_dict,path.sen_fmt)]  # pyright: ignore[reportArgumentType]
        path.delay_sel = chnno-1  # b
        tmpaddr =0
        nondly_chnno =chnno-1
        if(path.vs_delay_en and (chnno >1) ):
            if path.rd_auto:
                path.sof_sel = path.delay_sel
                path.eof_sel = path.delay_sel
            else:
                path.sof_sel = 0
                path.eof_sel = 0
            for i in range(chnno):
                mem=IDC_MEMORY_CFG(i)
                if i<nondly_chnno:
                    mem.len = (((path.dlymax_ln)>>1))* int(path.sen_hsize/div_a)
                else:
                    mem.len = (IDC_MAXIMUM_MEM_DEPTH*2 -tmpaddr) if(path.mem_share) else (IDC_MAXIMUM_MEM_DEPTH-tmpaddr)
                mem.addr = tmpaddr
                tmpaddr = tmpaddr +mem.len
                path.mem_buf.append(mem)
        else:
            tmpaddr =0
            path.delay_sel=0
            #print(chnno,"idc memory no vs")
            for i in range(chnno):
                mem=IDC_MEMORY_CFG(i)
                if path.mem_share:
                    mem.len =int(IDC_MAXIMUM_MEM_DEPTH*2/chnno)
                else:
                    mem.len =int(IDC_MAXIMUM_MEM_DEPTH/chnno)
                mem.addr =tmpaddr
                path.mem_buf.append(mem)
                tmpaddr = tmpaddr + mem.len

    def _idc_mem_cfg_init(self,path):
        chnno = idc_format_chnno_dict[get_dict_key(input_format_dict,path.sen_fmt)]  # pyright: ignore[reportArgumentType]
        path.delay_sel = chnno-1 # b
        # mems= [[path.mem0_addr,path.mem0_len],[path.mem1_addr,path.mem1_len],[path.mem2_addr,path.mem2_len],[path.mem3_addr,path.mem3_len]]
        if(path.vs_delay_en and (chnno >1) and path.rd_auto ):
            resv_mem = int(2*path.sen_hsize/8)
            tmpaddr =0
            nondly_chnno =chnno-1
            for i in range(nondly_chnno):# assume only one vs delay
                mem=IDC_MEMORY_CFG(i)
                # memaddr,memlen=mems[i]
                if path.mem_share:
                    mem.len = int((IDC_MAXIMUM_MEM_DEPTH*2-resv_mem) /nondly_chnno)
                else:
                    mem.len = int((IDC_MAXIMUM_MEM_DEPTH-resv_mem) /nondly_chnno)
                mem.addr = tmpaddr
                tmpaddr = tmpaddr +mem.len
                path.mem_buf.append(mem)
                #print(memaddr,memlen)
            mem=IDC_MEMORY_CFG(i+1)
            #memaddr,memlen=mems[i]
            mem.addr=tmpaddr
            mem.len= resv_mem
            path.mem_buf.append(mem)
            #print(__file__,"IDC total number",i,chnno,mem.addr,mem.len)
            #print(memaddr,memlen)
        else:
            tmpaddr =0
            #print(chnno,"idc memory no vs")
            for i in range(chnno):
                mem=IDC_MEMORY_CFG(i)
                if path.mem_share:
                    mem.len =int(IDC_MAXIMUM_MEM_DEPTH*2/chnno)
                else:
                    mem.len =int(IDC_MAXIMUM_MEM_DEPTH/chnno)
                mem.addr =tmpaddr
                path.mem_buf.append(mem)
                tmpaddr = tmpaddr + mem.len

    def _idc_cfg_init(self,chipcfg):
        dplist =[chipcfg.oax4k_cfg.dp0,chipcfg.oax4k_cfg.dp1,chipcfg.oax4k_cfg.dp2,chipcfg.oax4k_cfg.dp3]
        idclist =[self.cfg.path0,self.cfg.path1,self.cfg.path2,self.cfg.path3]
        for i in range(len(dplist)):
            if dplist[i].en:
                self._idc_path_init(idclist[i],dplist[i],chipcfg)
                # print("idc path {} init done ".format(i))
        self._idc_common_cfg_init(chipcfg)

    def _idc_common_start(self):
        cmmn =self.cfg.cmmn
        r70 = (cmmn.swset_err<<0) |\
            (cmmn.itpg.rand_en<<4)| (cmmn.itpg.lum_en<<1)| (cmmn.itpg.load_seed<<2)| \
            (cmmn.itpg.ch1_shift<<8)| (cmmn.itpg.ch2_shift<<12)|(cmmn.itpg.ch3_shift<<16) |\
            (cmmn.itpg.start_mode<<20)|(cmmn.itpg.ln_hblank<<24) | BIT23
        r78 =(cmmn.vsync_overlap_adjust<<1) | cmmn.booton_test_en
        self.reg.writereg32(0x70,r70)
        self.reg.writereg8(0x78,r78)

    def _idc_path_start(self,path):
        if path.en:
            bit_pathen =0 if(path.full_frm_en) else path.en
            r0 = bit_pathen |(path.intr_en<<1) | (path.emb_en<<2) | (path.sta_en<<3) |(path.safe_en<<4) |(path.vs_delay_en<<5) |\
                (path.rd_auto<<6) |(path.rgbir_en<<7) |(path.pix_width<<8) |(path.pix_width12p12<<9) |(path.sen_mode<<10) |(path.sen_fmt<<12) |\
                (path.sen_vcid0<<16) | (path.sen_vcid1<<20) | (path.sen_vcid2<<24)| (path.sen_vcid3<<28)
            # path.sof_sel = path.
            # path.eof_sel = path.delay_sel
            r4 =(path.sof_sel<<0) |(path.eof_sel<<2) |  (path.sen_intlv0<<4) | (path.sen_intlv1<<6)|\
                (path.sen_intlv2<<8)|(path.sen_intlv3<<10) |(path.delay_sel<<12) |(path.sen_id<<14) |\
                (path.emb_pre_vcid<<16)  |(path.emb_pre_chn<<20) |(path.emb_pos_chn<<22) |\
                (path.emb_pre_bitpos<<24) |(path.emb_pix_endian<<27) |(path.emb_sof_sel<<28) |(path.emb_eof_sel<<30)
            r8=(path.sta_chn_vc[0]<<0) |(path.sta_chn_vc[1]<<4) |(path.sta_bit_pos<<8) |(path.sta_in_mode<<11) |(path.emb_pos_bitpos<<13) |\
                (path.rd_start_ln<<16) |(path.sel_err_enj<<23)  |(path.mem_err_enj<<24) | (path.id_err_enj<<25) |(path.emb_post_vcid<<27)
            rc = path.sof_dly_cnt
            r50 = path.eof_dly_cnt
            r10 =  (path.sen_hsize<<0) | (path.sen_vsize<<16) | (path.rgbir_bitpos<<28)
            # if 'YUV422' in get_dict_key(input_format_dict,path.sen_fmt):
            #     print("YUV4222 !!!!!!!!!!!!!!!!!!!!!!")
            #     pass
            # else:
            for i in range(len(path.mem_buf)):
                rmem =  (path.mem_buf[i].addr<<0) | (path.mem_buf[i].len<<16)
                self.reg.writereg32(0x14+path.sel*0x80+i*4,rmem,mask=BIT15|BIT31)
            r48 =path.emb_pre_num |(path.emb_post_num<<8) |(path.sta_num<<16) | (path.rgbir_hblk<<24)
            # print("!!!!!!!!!!!!!!r48 {:x}, path.sta_num {}".format(r48, path.sta_num))
            r4c = 0xff #err_en
            r4d = 0xff #err_en
            r4e = path.mem_share | (path.rd_start_ref<<1) | (path.full_frm_en<<3)
            r4f = path.sta_chn_vc[2] | (path.sta_chn_vc[3] << 4)
            self.reg.writereg32(0+path.sel*0x80,r0)
            self.reg.writereg32(4+path.sel*0x80,r4)
            self.reg.writereg32(8+path.sel*0x80,r8)
            self.reg.writereg32(0x0c+path.sel*0x80,rc)
            self.reg.writereg32(0x10+path.sel*0x80,r10,mask=BIT12|BIT13|BIT14|BIT15|BIT30|BIT31)
            # self.reg.writereg32(0x10+path.sel*0x80,r10)
            self.reg.writereg32(0x48+path.sel*0x80,r48)
            self.reg.writereg8(0x4c+path.sel*0x80,r4c)
            self.reg.writereg8(0x4d+path.sel*0x80,r4d)
            self.reg.writereg8(0x4e+path.sel*0x80,r4e)
            self.reg.writereg8(0x4f+path.sel*0x80,r4f)
            self.reg.writereg32(0x50+path.sel*0x80,r50)
            # print("rc is 0x{:x}".format(rc))

    def start(self):
        self._idc_common_start()
        self._idc_path_start(self.cfg.path0)
        self._idc_path_start(self.cfg.path1)
        self._idc_path_start(self.cfg.path2)
        self._idc_path_start(self.cfg.path3)
