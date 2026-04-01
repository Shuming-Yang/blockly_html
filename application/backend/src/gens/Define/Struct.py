"""
This GENS mode code which be ported from GENS source code.
sensor related configuration start here
Author: OVT AE
Date: 2024-11-01
"""
# WARNING
# pylint: disable=C0103, C0115, C0116, W0613, W0622, E1133
# from inspect import currentframe


class SDS_RXPORT_CFG(object):
    def __init__(self, id=0):
        self.index = id            # snr or ser index
        self.sccb_addrlen = 0
        self._sccb_idx = 0
        self.lane_num = 4
        self._refclk = 24000000
        self.max_phyclk = 832000000
        # below param should config when manual mode
        self.en = 0
        self.sccb_id = 0           # serializer sccb id
        self.snr_sccb_id = 0       # sensor sccb id
        self.sccb_port = 0          # which txport can access this ser[0/1]
        self.stream_port = 0        # stream will trans to which txport [0/1]
        self.vcmap = {0:0, 1:1, 2:2, 3:3}


class SDS_TXPORT_CFG(object):
    # SDS_CFG is the serdes configuration class of sequencer
    def __init__(self,id=0,spid=0):
        self.index = id                 # port index
        self.sccb_idx = 0               # depend on input

# below param should config when manual mode
        self.en = 0                     # enable
        self.lane_num = 0
        self.phyclk = 0
#
#        self.serdevs = [self.serdev0, self.serdev1, self.serdev2, self.serdev3]
        self._max_vcnum = 4             # TI 4 and
        self._strm_num = 0

class SDS_CFG(object):
    def __init__(self):
        self.sccb_addrlen = 0           # parse from setting name

        # below param should config in xls
        self.en = 0
        self.set_index = 0             # default eq 0
        self.sccb_id = 0               # sccb id
        self.load_index = 0
        self.txport0 = SDS_TXPORT_CFG(0)
        self.txport1 = SDS_TXPORT_CFG(1)
        self.rxport0 = SDS_RXPORT_CFG(0)
        self.rxport1 = SDS_RXPORT_CFG(1)
        self.rxport2 = SDS_RXPORT_CFG(2)
        self.rxport3 = SDS_RXPORT_CFG(3)

        self.txports = [self.txport0, self.txport1]
        self.rxports = [self.rxport0, self.rxport1, self.rxport2, self.rxport3]
        self.sds_setting_len = 0        # baseaddr+0x06 [2B] --
        self.settingbuf = []


class SCCB_CFG(object):
    def __init__(self,id=0):
        self.en =0   # sccb enable  1 : enable
        self.index =id  # sccb number ,mapping to hardware sccb
        self.speed=400000   # unit Hz
        self.sds_idx =0     # corresponding sds id
        self.sds_en =0      # serdes enable
        self.timeout =0  # time out val
        self.sendbuf =[]  # the byte buf for send in eof


class SENSOR_CTRL(object):
    def __init__(self,id):
        self.pwdn_id =id        #GPIOX
        self.rst_id  =id      #HIGH ,low
        self.fsync_id =id
        self.cclk_id =id
        self.pwdn_pol =0   #  Pin active level 0 : low active 1: high active
        self.rst_pol =0
        self.cclk_pol =0
        self.fsync_pol =0


class SENSOR_EMBL_CFG(object):
    def __init__(self,mode =0):
        self.num =0
        self.startaddr =0
        self.len =0
        self.emb_vcid =0
        self.emb_chn =0
        self.bitpos =0
        self.takebyte =0
        self.emb_id =0
        # self.chns =[]

class SENSOR_STA_CFG(object):
    def __init__(self,mode =0):
        self.id =0
        self.en =0
        self.num =0
        self.chn_num =0
        self.len =0
        self.mode =0
        self.chn_vc=[0,1,2,3]
        self.ifmt=[0,0,0,0]
        self.valid_byte=[0,0,0,0]
        self.ibyte_sel=0
        self.vbno=0
        self.dis2nd_line =0

class SENSOR_EMBL_NEW(object):
    def __init__(self,mode =0):
        self.pre =SENSOR_EMBL_CFG()
        self.post =SENSOR_EMBL_CFG()
        self.sta =SENSOR_STA_CFG()
        self.emb_tag_en =0
        self.emb_tag_val =0
        self.en =0
        self.linemode =0
        self.x3a_en =0

        self.crc_order = 0
        self.crc_inv = 0
        self.preemb_chns=[]
        self.posemb_chns=[]


# class SENSOR_EMBL(object):
#     def __init__(self,mode =0):
#         self.pre_num =0  # embedded line pre number
#         self.post_num =0
#         self.pre_startaddr=0
#         self.post_startaddr =0
#         self.pre_len =0
#         self.post_len =0
#         self.emb_tag_en = 0
#         self.emb_tag_val = 0xda
#         #self.datatype =0x12
#         #self.format =0
#         self.en =0
#         self.sta_en = 0
#         self.sta_num =0  # total sta num, for example in x3a RAW12_12, total sta num is 4
#         self.sta_chn_num = 0 # sta num in each channel, typically 2
#         self.sta_len =0
#         self.pre_emb_vcid = 0
#         self.post_emb_vcid = 0
#         self.sta_mode = 0 # 0: after post embl, 1: bf post embl, 2: no post embl 3: no embl
#         self.sta_chn_vc = [0,1,2,3]
#         #sta_ifmt: RAW12-0, RAW14-1, RAW16-2, RAW20-3, RAW24-4
#         self.sta_ifmt = [0,0,0,0]
#         # sta_valid_byte = sta_len
#         self.sta_valid_byte = [0,0,0,0]
#         #sta_ibyte_sel: 0 for 12bits, 1 for high 8 bits, 2 for mid, 3 for low
#         self.sta_ibyte_sel = 0
#         #sta_vbno: the number of lines which contain valid bytes
#         self.sta_vbno = 0
#         #pre_emb and post_emb may be in different image channel
#         #for example, pre_emb in channel DCG, post_emb in channel VS
#         self.pre_emb_chn = 0
#         self.post_emb_chn = 0

#         self.linemode =0  # embeddedl line identify by line mode
#         #bitpos: raw10/20: 2, RAW12/24: 0,  RAW16/14: 3
#         self.pre_bitpos = 0
#         self.post_bitpos = 0
#         #takebyte: raw8/10/12: 2, raw16/20/24: 0xa, raw14: 6
#         self.pre_takebyte = 0
#         self.post_takebyte = 0
#         self.x3a_en = 0
#         self.crc_order = 0
#         self.crc_inv = 0
#         self.sta_dis2nd_line = 0

#         self.preemb_chns=[]
#         self.posemb_chns=[]


class SENSOR_STREAM(object):
    def __init__(self,mode =0):
        #self.name =0
        self.lane_num =2  # lane number which sensor setting output  1,2,4
        self.vcnum =0     # the total vc num which sensor output ,if output with pixel intl ,it is equal 1
        self.imgmode=0    # image output mode , 0 VCID mode ,1: pixel intl 2: line intl
        self.imgid =[]   # img output data type via CSI
        self.embid =[]   # embedded line output data type via CSI
        self.imgdt =[]   # img actual data type
        self.vclist =[]   # vitural channel list when VCID mode
        self.format_tid = 0  # type id  ,corrsponding sensor input
        # self.format_nid = 0  # name id , corresponding idc input
        self.format =0      # image output format ,define refer IDC input format ,it corperate with imgmode
        self.expnum =0      # image exposure number :
        self.cmben =0       # snr combined enable
        self.dual_roi_en =0 # snr dual rol enable
        # self.pwlen =0       # snr pwl enable
        self.pwlmode =0     # image pwlmode when pwl enable ,0 : new pwl 1 : simple pwl
        self.dx_exp_reg =[]   # 33 curves
        self.dy_val_reg =[]   # 33 curves
        self.curve_g =[]   # pwl curve gain0,1,2,3
        self.curve_kp =[]   # pwl curve kneepoint0,1,2
        self.curve_of =[]   # pwl curve offset0,1,2,3
        self.hsize =1920    # image out hszie
        self.vsize =1080   # image out vsize
        self.hts =2200      # image out hts
        self.vts =1125      # image out vts
        self.orgvts =1125      # image out vts
        self.fps = 0         # image out fps
        self.cclk   =24000000   # sensor input xclk freq
        self.sclk   =148500000   # sensor system clock for timing generation
        self.phyclk =1200000000  # sensor phyclk for MIPI CSI
        self.vsdly_max =32            # vsldy number
        self.vsdly_step =0            # vsldy step
        self.mdly_line =0            # vsldy number
        self.sdly_line =0            # vsldy number
        self.vdly_line =0            # vsldy number
        self.preblank =0         #  the line number between sof to first HREF
        self.vsdly_en =0     # vsldy enable
        self.emblchn =0 # indicate the channel whilc embedded valid data locate
        self.blc =[0, 0, 0, 0] # sensor blc array info define
        self.dvalue =[0, 0, 0, 0] # sensor dvalue array define
#        self.low_temperature_threshold =168 # sensor low temperature threshold value [BIT7='1' is negative value, so 168 = -40]
#        self.high_temperature_threshold =125 # sensor high temperature threshold value [always is positive value]
        self.crypto_cfg = 0 #0x4700 at x8b

        self.line_v2 = 0
        self.byptc =0
        self.vx = 1
        self.fsin_en =0
        self.descramble_en = 0
        ##AB and dual ROI mode related kkk
    def remap_vc(self, vc_offset):
        for idx in len(self.vclist): # pyright: ignore[reportGeneralTypeIssues]
            self.vclist[idx] += vc_offset

class SENSOR_CSI_CFG(object):
    def __init__(self):
        self.descramble=0  # de scramble enable
        self.lpfuncen =0   # lower power function enable
        self.caliben =0    # calibrat enable

class CB_CFG(object):
    def __init__(self,id=0,spid=0):
        self.en = 1
        self.index =spid  # Colorbar index
        self.type = 0xaa # colorbar type
        self.strm =SENSOR_STREAM(1)  # colorbar stream config
        self.embl =SENSOR_EMBL_NEW(1)    # colorbar embedded line config

class SENSOR_SCCB(object):
    def __init__(self,id):
        self.id =0       # the sensor sccb id .
        self.setid =0       # the sensor setting  id ,default is the same as sccb id.
        self.addrlen =0       #  the sensor addrress len mode 0 : 16 addr,8 data 1: 8 addr,8 data
        self.index   = id     #  the sccb index ,it is used to select the sccb master for configure sensor
        self.crcmode =0       # the sensor crc mode , 0 : bypass 1: legacy crc 2: PEC
        self.maxspeed = 1000000   # the sensor sccb bus speed (default: 1000khz)
        self.sendbyte = 0   # the total byte send in aec done ,


class SENSOR_SIM(object):
    def __init__(self, id):
        self.v2_mode = 0
        self.fin_mode = 0     # 0:Arbitrary frame sync,1: Continous frame sync,2: don’t care fsin_i
        self.clk_gate = 0     # 2'b00: not gate clock,2'b01: gate all clock in blanking,2'b10: gate clock in vertical blanking
        self.lsyn_en = 0      # line sync number sending enable
        self.max_fnum = 10     # max frame number
        self.pre_div = 0
        self.div_st = 1        # post div 1
        self.div_nd = 8        # post div 2
        self.div_rd = 8        # post div 3
        self.mult = 0x64
        self.ideskew_en = 0   # initial deskew pattern enable
        self.pdeskew_en = 0   # period deskew pattern enable
        self.ideskew_num = 0  # initial deskew pattern bytes num
        self.pdeskew_num = 0  # period deskew pattern bytes num





class SENSOR_CFG(object):
    def __init__(self,id=0,spid=0):
        self.index =id   # sensor index, the range can be from 0 to 3 when serdes enable
        self.set_index= spid    # sensor setting index , it is used to select the sensor setting
        self.ab_mode = 0
        self.dual_roi = 0
        self.a_frm_num = 1
        self.b_frm_num = 1
        self.a_vc_id = 0
        self.b_vc_id = 2
        self.roi_vc_id = 1
        # self.img_src = 0 # 0: a mode cfg, 1: dual_roi_cfg, 2: B_mode_cfg
        self.spd_byp =0
        self.pwlparse_byp = 0
        self.type =0          # map to sensor_id,
        self.ver =0  # sensor version
        self.csi  =SENSOR_CSI_CFG()  # sensor csi configuration
        self.sccb =SENSOR_SCCB(int(spid /2))  # sensor sccb config
        self.ctrl =SENSOR_CTRL(spid)   # sensor reset, fsin, power down ctrl
        self.strm =SENSOR_STREAM()   # sensor stream
        self.embl =SENSOR_EMBL_NEW()   # sensor embedded line
        self.sim = SENSOR_SIM(spid) # used for Veloce simulation
        self.settingbuf =[]   # store the settting which set_index config
        self.regaddrdict ={}  # store the common register and val for firmware use
        # self.not_check_timing = 0 # internal use only, used only in X8B AB mode or SPD case for not checking sensor_buf[1] timing.
        # self.name = '' #internal use only, snr name


class INPUT_CFG(object):
    def __init__(self,id):
        self.index=id    # input port index 0: in0 1: in1
        self.en =0       # input enable contrl  0: disable
        self.cben =0     # colorbar enable  0: disable
        self.sensor_num=1  # sensor number in one input port ,when serdes enable ,this number can up to 4
#        self.serdes_idx =0  # serdes index which current input use
        # self.lane_num = 0   # input lane number
        self.pix_width = 1  # input pixel width 0: 48  1:96
        # self.sclk     =0    # input actual sclk
        self.lpfen =0   # low power function en
        self.deskew_en =1  # deskew enable
        self.sccb_idx = id//2 #  sccb obj index which current input port use
        self.sds_en =0    # serdes enable
        self.sccbbuf =[]     # sccb buf ,search by sccb buf
#        self.sds_rxport = SDS_CFG()
#        self.sds_buf =[]      # corresponding serdes buf ,search by serdes inx
        self.cb_buf=[]       # color bar buf ...
        self.sensor_buf =[]  # sensor buf which  is used to  save all input sensor configure ,auto parse
        self.cpy_cfg = 1 #if 1, all the sensor_buf will copy the first one

        self.sds_index = 0      # sds index [0/1/2/3]
        self.sds_txport = 0       # sds txport index [0/1]

        self._broadcast_en = 0
        self._snr_bc_id = 0
    #     self._phyclk = 0

    # @property
    # def phyclk(self):
    #     return self._phyclk
    # @phyclk.setter
    # def phyclk(self, val):
    #     self._phyclk = val
    #     f_current_line = str(currentframe().f_back.f_lineno)
    #     print("[INPHYCLK] {:d} line no {}".format(val, f_current_line))

# data path configuration start here

class DP_INPUT(object):
    def __init__(self,id):
        self.portsrc= id  # input port source : 0 IN0 ,1: IN1 (include MIPI RX, IDC,IM,CB)
        self.strmsrc =0   # input sensor source in one port when serdes enable  0 : sensor 0 1: sensor 1.
        self.snrsrc = id   # input sensor module id 0/1/2/3
        self.sersrc = id   # input sensor-dser  id src  0/1/2/3 when sds enable
        self.idcen  =1   # dapath idc enable
        self.safe_en = 1   # idcp safe check enable
        self.itpgen = 1    # it pg enable
        self.tp_mode =1   # it pg enable
        self.sertp_num = 8   # tp1 test number enable,this number should not less than 4
        self.partp_num = 4   # tp0 test number,
        self.dmy_en = 1   # tp1 test number
        self.dmy_mode = 0   # isp dmy line mode : 0 isp auto 1: manual mode
        self.dmy_num =16   # tp1 test number
        self.imgmten = 0  # img mon
        # self.rgbiren =0  # rgbir enable
        self.loaden =1   # sensor setting download  0: don't need load 1: need load sensor
        self.shadow =0   # sensor setting download  0: don't need load 1: need load sensor
        #self.buf=[]      # corresponding input buf
        self.vsdly_max =0  # input delay max line number
        self.vsdly_step =0  # vs delay step ,0 means no need step. otherwise vs delay should follow this value
        # self.bufline_max =0  # input delay max line number
        self.rd_start =0  # input read start line
        # self.extra_bufline =0   # extra buf line due to ram shedule ,interanl use only
        # self.rd_start_max =0  # input read start line
        # self.vsdly_en =0  # input delay vs enable
        self.fixen  =1  # idc/p output fix timging
        self.seof_dlymode =0  # 0 ,delay preblank 1: delay 2 line
        self.mem_share  = 0  # idc 0/1 ,2/3 memory share
        self.fullfrm_en = 0  # full frame enable
        self.frmnum_gate =1 # frame number gate when full frame enable
        # self.sclk =0    # input sclk
        # self.fsyncen =0    # input sensor fsync en
        self.seibuf =[]


class OVI_EMBL_CFG(object):
    def __init__(self,id=0,index=0):
        #self.innum =0
        # self.len =0    #  OVI output valid length ,should 4x
        self.intsel =5 if(index==1) else 1    # embedded line interrupt source 0 DP0
        # self.dma_no = 4 + index + id*2
        self.src =id    # embedded line interrupt source
        self.chnaddr_list =[]  # chandder base addr
        # self.chnaddr_list =[]  # chandder base addr
        self.chnlen_list =[]   # chain length
        self.chain_list =[]   # chain length
        self.chnaddr_num=0
        self.chnlen_num=0   # chain number
        self.chain_num=0   # chain number
        self.dflt_en =1   # default context enable
        self.frmcrcen = 1
        self.outnum =0   # embedede line output line number
        self.en =0        # embedde line enable,default enable,if en ==0,outnum =0
class EMBL_SEIO_INFO(object):
    def __init__(self):
        self.inen =1
        # self.innum =0    # input sei line number
        # self.takebyte = 0
        # self.vldbyte=0   # input valid byte
        self.vldbyteout=0 # output valid byte, not used yet
        self.outnum =2   # output sei line number

class EMBL_STA_INFO(object):
    def __init__(self):
        self.swap =0    # sta swap
        self.inen =1
        self.innum =0   # sta input line number
        self.outnum =2  # sta output line number
        #self.out_msb8=0
        #self.out_msb4=0
        # self.valid_byte0=0  # sta valie len
        # self.valid_byte1=0
        # self.valid_byte2=0
        # self.valid_byte3=0
        # self.ibyte_sel =0
        # self.total_vldbyte =0


class EMBL_HMAC_INFO(object):
    def __init__(self):
        self.inen =0    # hmac in enable
        self.outen =0   # hmac out enable
        self.vbyte =0   # hmac valid bytes


class DP_EMBL(object):
    def __init__(self,id=0):
        self.en =0   # embedded line module enable  0 :disable 1: enable
        self.inten=1
        self.chn =1  # embedde line output channel  0: raw 1: yuv
        self.index =id
        #self.dmaen=1
        self.tagdata=0xda  # embedded line tag data
        self.tagen=0      # embedded line tag enable
        # self.x3a_en = 0

        self.ovipre=OVI_EMBL_CFG(id,0)  # OVI PRE configruation
        self.ovipost=OVI_EMBL_CFG(id,1)
        self.seipre = EMBL_SEIO_INFO()  # SEI PRE configruation
        self.seipost = EMBL_SEIO_INFO()
        self.sta  =EMBL_STA_INFO()
        self.hmac = EMBL_HMAC_INFO()
        self.crypto = CRYPTO_SLAVE_CFG()

        self.seibuf =[]   # corresponding SEI input buf

class CRYPTO_GEMO_CFG(object):
    def __init__(self,id=0):
        self.en =0
        self.index =id
        self.b2h =100
        self.nr_rows =0
        self.row_len =0
        self.sei_post_len = 0 #sei post valid length

class CRYPTO_HOST_HMAC_CFG(object):
    def __init__(self,id=0):
        self.index =id
#         self.pix_endian =1 # HMAC engine pixel endian change for every 4 pixels
#         self.intra_pix_order =1 # inter-pixel order reverse  1:{input pixel[7:0], input pixel[15:8]}
        self.data_sel =0  # hash option to choose 16 bit from combine 24 bit in host point
        self.vldbyteout =0x21
        self.outen =0
#         self.verifyen =1

class CRYPTO_SLAVE_HMAC_CFG(object):
    def __init__(self,id=0):
        self.index =id
#         self.pix_endian =1
#         self.intra_pix_order =1 # inter-pixel order reverse  1:{input pixel[7:0], input pixel[15:8]}
        self.format =0
        self.src  =0
        self.data_sel =0  # hash option to choose 16 bit from combine 24 bit in host point
        self.hmac_path = 0# 0 raw 1 yuv, configure according embl path

class CRYPTO_TOP_CFG(object):
    def __init__(self):
        self.en =0
        self.random_sel =0
        self.random_mode =2
#         self.abmode = 0
#         self.bchannel = 2
#         self.bmap = 0 #map bchannel geom to achannel geom[1] for crypto slave
        self.hst0 =CRYPTO_HOST_CFG(0)
        self.hst1 =CRYPTO_HOST_CFG(1)
        self.hst2 =CRYPTO_HOST_CFG(2)
        self.hst3 =CRYPTO_HOST_CFG(3)

        self.slv0 =CRYPTO_SLAVE_CFG(0)
        self.slv1 =CRYPTO_SLAVE_CFG(1)
        self.slv2 =CRYPTO_SLAVE_CFG(2)
        self.slv3 =CRYPTO_SLAVE_CFG(3)


class CRYPTO_HOST_CFG(object):
    def __init__(self,id=0):
        self.en =0
#        self.sds_en = 0
        self.index =id
#         self.portsrc =id
#         self.imgasrc =0
#         self.imgbsrc =1
        self.abmode =0 #if enable ab mode

        self.bchannel = 2 #channel number which b frame send out
        self.bmap = 0
        self.a_vc_id = 0 #get from sensor
        self.b_vc_id = 2 #get from sensor
        self.snrsrc = 0

        self.gemo0 =CRYPTO_GEMO_CFG(0)
        self.gemo1 =CRYPTO_GEMO_CFG(1)
        self.hmac = CRYPTO_HOST_HMAC_CFG()
        self.inbuf = []
        self.dpbuf = []
        self.dobuf = [] #refer sei embl only

class CRYPTO_SLAVE_CFG(object):
    def __init__(self,id=0):
        self.en =0
        self.index =id

        self.abmode =0
        self.bchannel = 2
        self.bmap = 0
        self.a_vc_id = 0 #no use
        self.b_vc_id = 2 #no use
        self.format = 4 #image format,refer to crypto reg0xebee:Slave 0 image pixel data type

        self.topembl = 1 #HMAC top embedded involvement enable
        self.bottomembl = 1 #HMAC bottom statistic involvement enable

        self.gemo0 =CRYPTO_GEMO_CFG(0)
        self.gemo1 =CRYPTO_GEMO_CFG(1)
        self.hmac = CRYPTO_SLAVE_HMAC_CFG()


class ISP_SCALE_CFG(object):
    def __init__(self):
        self.en=0    # scale down enable
        self.ihsize=0   # scale input hsize
        self.ivsize=0    # scale input vsize
        self.hsize=0   # scale output hsize
        self.vsize=0    # scale output vsize
        self.hstart=0   ## scale input hstart (hoffset)
        self.vstart=0   ## scale input vstart (voffset)
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

class ISP_OUT_CFG(object):
    def __init__(self,id=0):
        self.index =id    # internal use for identify yuv,mv,raw
        self.hsize =0     # output image horizontal size
        self.vsize =0     # output image vertical size
        # self.format =0    # output image format
        self.cropen=0      # output image crop enable
        self.hstart=0    # crop h start
        self.vstart=0     # crop v start
        # self.hts =0      # output image total pixel in a line
        # self.vts =0      # output image total pixel in a line
        self.winsel =0  #  0 : from self 1: from the other
        if id == 2:  # RAW
            self.sel =8     # output image source select , 8 : PWL,  10 NML
            self.exposel =0   # raw exposure output select
        else:
            self.sel =0     # output image source select , 0 : YUV 1: RGB565 2:RGB888 3 :YUV420
        # if(id==2):
        if id == 0:
            self.scale=ISP_SCALE_CFG() # ISP scale configruation


class ISP_TOP_CFG(object):
    def __init__(self):
        # self.cbaren =0 # 1 for CLGA TB without pixel array only,0 for other case
        self.aecdoneoft =0x40  # aec done offset
        self.sof_sel =0    # isp sof sel 0: refer isp register table 20
        self.eof_sel =3    # isp eof sel 0:


class DP_ISP(object):
    def __init__(self):
        self.inbuf=[]   # ISP corresponding input buf ,from IDP
        self.cben =0    # isp colorbar enable
        self.safeen =1    # isp safe check en enable
        self.yuvout=ISP_OUT_CFG(0)  # ISP YUVOUT configuration
        self.mvout =ISP_OUT_CFG(1)   # ISP MVOUT configuration
        self.rawout =ISP_OUT_CFG(2)  # ISP RAWOUT configuration
        self.top =ISP_TOP_CFG()   # ISP PROC configuration2

class MIPITX_VC_CFG(object):
    def __init__(self,id):
        self.num =0       # virtual channel active number
        if id == 0:
            self.max_num =8  # maximum virtual channel
        elif id == 2:
            self.max_num =4
        else:
            self.max_num =2
        self.imgs=[]     # virutal channel image buffer


class MIPITX_CSI_CFG(object):
    def __init__(self,id):
        self.lane =2 if (id%2) else 4        # lane number   0: 0 1: 1 lane 2: 2 lane 4: 4 lane
        self.laneswap =0    # lane swap  , refer hardware define
        self.lsync=0        # lsync output enable when
        self.fstype =0      # frame start type  0: input sof  1: vfifo ready
        self.clkmode =0     # output clock mode 0 free 1: gate
        self.deskew_pt =0xaa   # deskew patten  0xaa: default
        self.deskew_fbcycle =0x0400   # data clock cycle number for image blank deskew
        self.deskew_pucycle =0x1000   # data clock cycle number for power up deskew
        self.deskew_altecycle =0x0200   # data clock cycle number for alternate cal seq
        self.deskew_pu =1   # power on deskew
        self.deskew_fb =1   # period deskew
        self.deskew =0      # deskew enable  0: disable
        self.lrte_timeout =1   # detect space time out when it is enable
        self.epd_misc =1    # enable spacer without PDQ prior to DPHY EOT
        self.epd_en =0      # LRTE enable  0: disable
        self.epd_ssp =0    # space number for short packet
        self.epd_lsp =0    # space number for long packet
        self.lfsr1 =0     # lane1 LFSR initial seed
        self.lfsr2 =0     # lane2 LFSR initial seed
        self.lfsr3 =0     # lane3 LFSR initial seed
        self.lfsr4 =0     # lane4 LFSR initial seed
        self.scramble =0     # scramble enable 0: disable
        self.ext_timing =0  # tbd
        self.freq  =0       # mipi pclk freq

class MIPITX_CFG(object):
    def __init__(self,id):
        self.index =id        # MIPI TX  index : 0 MIPI TX0  1: MIPI TX1 ...
        if id % 2:
            self.dup_en = 0   # MIPI TX duplicate output
        self.csi =MIPITX_CSI_CFG(id)   # MIPI TX CSI configuration
        # self.vc =MIPITX_VC_CFG(id)     # MIPI TX virtucal channel config

# class RGBIR_CHNIN_CFG(object):
#     def __init__(self):
#         self.hsize =0
#         self.vsize =0
#         self.fmt =0

# class RGBIR_CHNOUT_CFG(object):
#     def __init__(self,id=0):
#         self.sel  =0
#         self.hsize =0
#         self.vsize =0
#         self.binning =0
#         #self.irrm_opt =0
#         self.irext_en =id

# class RGBIR_CHNPROC_CFG(object):
#     def __init__(self):
#         self.irrm_opt =0
#         self.abmode =0
#         self.frmnum_a =0
#         self.frmnum_b =0
#         self.irexen =0

#         self.dpcen =1
#         self.dnsen =1
#         self.irrmen =1
#         #self.ir_remove_mode =0
#         self.cfa_array =0
#         self.cfa_pattern =0
class RGBIR_PATH_RAWIR_CFG(object):
    def __init__(self,id):
        self.osel =0   # raw path : raw -ir  1: raw+ir   / ir path :ir  1:raw+ir
        self.abmode =0
        if id % 2:
            self.amask =1
            self.bmask =0
        else:
            self.amask =0
            self.bmask =1
        self.afrmnum =1
        self.bfrmnum =1


class RGBIR_PATH_CFG(object):
    def __init__(self,id):
        self.index= id
        # self.chnbase =0
        self.irrm_opt =1   #0 ir rmeove new, 1: simple ir rm
        self.raw = RGBIR_PATH_RAWIR_CFG(0)
        self.ir = RGBIR_PATH_RAWIR_CFG(1)
        # self.abmode =0
        # self.rawmask =0
        # self.irmask =0
        # self.frmnum_a =1
        # self.frmnum_b =1
        self.irexen =0
        # self.v3_sel =0
        # self.v4_sel =0
        self.dpcen =1
        self.dnsen =1
        self.irrmen =1
        #self.ir_remove_mode =0
        self.cfa_array = 0x77ce77ec
        self.cfa_pattern =0
        # self.rawosel  =0
        # self.irosel  =0

        self.tpen =1
        self.dmyen =1
        self.tpnum =16
        self.dmynum =4

        self.exphblk =128


class RGBIR_CHANNEL_CFG(object):
    def __init__(self,id):
        self.en =0
        self.index= id
        self.inbuf =[]
        self.ctrlbuf =[]
        # self.rawout =RGBIR_CHNOUT_CFG(0)
        # self.irout =RGBIR_CHNOUT_CFG(1)


class RGBIR_CFG(object):
    def __init__(self):
        self.en =0
        self.tpmode =1
        self.lnhblk =128
        self.ln2tphblk =888
        self.dp0 = RGBIR_PATH_CFG(0)
        self.dp1 = RGBIR_PATH_CFG(1)
        # self.chn0= RGBIR_CHANNEL_CFG(0)
        # self.chn1= RGBIR_CHANNEL_CFG(1)
        # self.chn2= RGBIR_CHANNEL_CFG(2)
        # self.chn3= RGBIR_CHANNEL_CFG(3)

        self.chnlist =[RGBIR_CHANNEL_CFG(0),RGBIR_CHANNEL_CFG(1),RGBIR_CHANNEL_CFG(2),RGBIR_CHANNEL_CFG(3)]

        self.ins =[]
        self.outs=[]


class DP_SAFETY(object):
    def __init__(self):
        pass

class DP_OUTPUT(object):
    def __init__(self,id,chn,vc,chiptype):
        self.sel = ( 3 if(chiptype) else 0) if(vc) else 0       # output source select 0: IDC 1: PGEN 2: TX 3: ISPRAW 4:ISPMV
        self.idcsel =2       # idc raw souce select  0: ir raw 1: snr raw 2: dup isp raw
        # self.index =chn      # output source id 1: yuv 0 : raw/mv
        # self.rtidx =id      # output source id 1: yuv 0 : raw/mv
        # self.outport=id    # MIPI TX output port  0 : output to MIPI TX 0 1 : Output to MTX1 ...
        self.outvc =vc     # OUTPUT MIPI TX vitrual channel  0: VC0 1 :VC1 ...
        #self.imgsrc =0     # input source index : 0 : select DP0  1: select DP1 ...
        # self.outchn =vc    # channel index ,  0, 1
        # self.sbsen  =0
        self.hsize=0       # image out width
        self.vsize=0       # image out height
        # self.hts =0        # total pixel in one line
        # self.vts =0        # total line in one frame
        # self.fps =0
        self.format =0    # imge output format , refer to output dict:output_raw_format_dict
        self.txfmt = 0xff
        self.seq=2        # image output sequence ,
        self.swap =0      # yuv  swap enable
        self.en =0        # output enanble  0: disable 1: enable
        self.outen = 1
        self.hblk_balance =0
        self.hblk_odd = 0x12c
        self.hblk_even =0x12c
        self.lnint_oft = 0x20
        # if(self.index): # yuv path
        self.emblbuf=[]

    #     self._byptc = 0

    # @property
    # def byptc(self):
    #     return self._byptc

    # @byptc.setter
    # def byptc(self, xx):
    #     f_current_line = str(currentframe().f_back.f_lineno)
    #     print("[BYPTC] {:d} line no {}".format(xx, f_current_line))
    #     self._byptc = xx


class DATAPATH_CFG(object):
    def __init__(self,id):
        self.index=id     # datapaht index  0: DP0 1:DP1  (include ISP,IDP,EMBL,Security)
        self.setsrc=0     # datapaht index  0: DP0 1:DP1  (include ISP,IDP,EMBL,Security)
        self.en=0         # enable control  0: disable
        self.rgbiren =0   # enable rgbir input and output
        # self.rgbirsrc =int(id/2)   # enable rgbir input and output
        self.rgbir_updateen =1   # enable rgbir input and output
        self.bypisp   =0  #
        self.byptc   =0  #  bypass timing calculation when X8B AB mode or dual roi
        self.yuvin_mode   =0  # 0:as yuv 1:RAW24
        # self.abmode_frmb  =0  # xb8 abmode ,b frm ,this bit should set when the path select b frame of X8B AB for timing check
        # self.dualroi_roi1  =0  # xb8 abmode ,b frm ,this bit should set when the path select b frame of X8B AB for timing check
        self.input=DP_INPUT(id)    # input configuration
        # self.embl= DP_EMBL()        # embedded line
        # self.security =DP_SECURITY()
        # self.crypto =DP_SECURITY()
        self.isp =DP_ISP()          # ISP configuration
        self.safety =DP_SAFETY()   # tbd

        self.dobuf =[]    # corresponding output buf
        self.dibuf =[]


class DP_FSYNC_CFG():
    def __init__(self,id):
        self.index =id
        self.insrc =id     # fsin input source selcet
        self.outsrc =id    # fsync/fsin output source select
        self.en =0         # fsync/fsin enable
        self.trig_mode =0  # fsync trigger mode  0: reg 1: fsin
        self.out_mode =0   # 0 continous 1 : one time
        self.byp_fsin =0   # byapss fsin to fsync
        self.out_fsin =0   # output fsin enable
        self.polarity =0   # fsync/fsin output polarity
        self.oft_en  = 1   # fsync output delay enable ,
        self.act_len  =100  # fsync active len
        self.act_frm  =1   # fsync active frame number between 2 fsync
        self.act_oft  =1   # fsync delay line number
        self.extra_line =0


class OUTPUT_CFG(object):
    def __init__(self,id,chiptype=0):
        self.index=id   # output index : 0 : output 0 1: output 1 (include RT,MIPICHN,MIPITX)
        self.en= 0      # output enable control  0: disable
        self.src =id    # image source   0: DP0 1: DP1 ...
        self.idcsrc =id    # image source   0: IDC0 1: IDC1 ...
        self.emblsrc =id    # image source   0: IDC0 1: IDC1 ...

        self.rtmode =0  # retime mode   ,refer to hardware define,only 0 and 2 is valid

        # self.sram_merge =0

        self.yuv=DP_OUTPUT(id,1,0,chiptype)   # yuv output configuration
        self.rawmv=DP_OUTPUT(id,0,1,chiptype)  # rawmv output configuration

        self.fsync = DP_FSYNC_CFG(id) # fsync /fsin configuration

        self.mtx =MIPITX_CFG(id)   # mipit tx output configuration
        self.embl =DP_EMBL(id)        # embedded line(id)

        self.dpbuf =[]      # corresponding DP configuration
        self.chnlist =[]
        # self.emblbuf =[]      # corresponding EMBL configuration
        self.hmacout = 0


class TOPCTRL_CFG(object):
    def __init__(self,chiptype=0):
        self.en =1
        self.snr_auto_mode =1       # auto parse sensor setting as input parameter
        self.sds_auto_mode = 1
        self.cb_copy_snr =1        # colorbar timing copy sensor input parameter
        self.pg_copy_isp =1        # PGEN copy ISP output paramter for debug
        self.sim_copy_snr = 0
#        self.sim_en = 0             # just for simulation
        self.strm_default =0        # PGEN copy ISP output paramter for debug
        self.idp_hblk =  100       # PGEN copy ISP output paramter for debug
        # self.rgbir_hblk =240        # PGEN copy ISP output paramter for debug
        # self.bypmode  =1   # 1 : debug mode (byp duplicate img) 0 : normal mode (image and byp output different )
        self.isptp_mode = 0  # 0 : random  1: incremental
        self.isptp_seq = 0  # 0 : para first  1: serial first
        self.ispltm_mode =0   # 0 : local gamma & ptm 1: ltm
        self.ispintm_adj = 1  # 0 : isp input timing adjust disable  1:  enable
        # self.ispdcmp_safe_en =1
        # self.ispcore_safe_en =1
        # self.rgbirtp_mode =1c
        self.debug_en =0
        self.debug_sel =0x10
        self.debug_shift = 0 # 0 :shift bit
        self.debug_shift_dir =0 # 0 : right shift 1: left shift
        self.txmnt_en =0    # tx monitor enable ,only active for simualtion
        self.chip_type = chiptype
        self.check_timing = 1
        self.algo_disable= 0x0
        self.algo_disable_2= 0x0
        self.bcmode= 0  # boardcast mode 0: 0to 1,23 1: 0 to1 2: 2 to 3  3: 0 to 2
        self.bcen= 0  # boardcast enable
        self.tmfix_mode = 0  # 0 by increase dp clock , 1: by increase buf line mode
        self.rtfix_mode = 1  # 0 by increase out bandwidth , 1: by increase buf line mode
        self.slvid =0x48  # sccb slave id
        self.byp_sccbchk =0 # sccb slave id
        self.byp_sdschk = 0

# System  configuration start here

class SYSTEM_PLL_CFG(object):

    def __init__(self,chip_type):
        #sc reg: 10: sys_clk0, 18: sys_clk1, 20: tx1_clk0, 22: tx1_clk1,
        # 24: tx0_clk0, 25: tx0_clk1, 00: pad_clk
        if chip_type < 2:
            self.xclk =24000000   #  system input XCLK ,unit Hz
            self.sys_clk0=100000000  # SYS PLL ispclk output
            self.sys_clk1=240000000  # SYS PLL  sysclk output

            self.tx0_clk0 =320000000 # TX0PLL
            self.tx0_clk1   =160000000

            self.tx1_clk0 =288000000 # TX1PLL
            self.tx1_clk1   =192000000
        elif chip_type == 3:
            self.xclk =24000000   #  system input XCLK ,unit Hz
            self.sys_clk0=100000000  # SYS PLL ispclk output
            self.sys_clk1=240000000  # SYS PLL  sysclk output

            self.tx0_clk0 =320000000 # TX0PLL
            self.tx0_clk1   =160000000

            self.tx1_clk0 =288000000 # TX1PLL
            self.tx1_clk1   =192000000
        else:
            self.xclk =24000000   #  system input XCLK ,unit Hz
            self.sys_clk0= 240000000  # SYS PLL ispclk output
            self.sys_clk1= 420000000  # SYS PLL  sysclk output

            self.tx0_clk0 =  0 # TX0PLL
            self.tx0_clk1   =0

            self.tx1_clk0 =  0 # TX1PLL
            self.tx1_clk1   =0

class SYSTEM_CLOCK_CFG(object):
    def __init__(self,chip_type):
        if(chip_type<2 or (chip_type==3)):
            self.cb0clk =50000000
            self.cb1clk =50000000
            self.cb2clk =50000000
            self.cb3clk =50000000

            self.fe0clk =50000000  #org 72M
            self.fe1clk =50000000
            self.fe2clk =50000000
            self.fe3clk =50000000

            self.dpclk  =60000000

            self.do0clk =40000000
            self.do1clk =36000000

            self.sysclk =50000000
            # self.sysclk =24000000

            #self.busclk =50000000
            #self.perpclk =100000000
            self.perpclk =50000000

            self.secuclk =60000000

            self.snrcclk0 =24000000
            self.snrcclk1 =24000000
            self.snrcclk2 =24000000
            self.snrcclk3 =24000000
        else:
            self.cb0clk =140000000
            self.cb1clk =140000000
            self.cb2clk =140000000
            self.cb3clk =140000000

            self.fe0clk =210000000  #org 72M
            self.fe1clk =210000000
            self.fe2clk =210000000
            self.fe3clk =210000000

            self.dpclk  =210000000

            self.do0clk =150000000
            self.do1clk =100000000 #150

            # self.sysclk =200000000
            self.sysclk =210000000
            # self.sysclk =24000000

            #self.busclk =50000000
            #self.perpclk =100000000
            self.perpclk =50000000

            self.secuclk =140000000

            self.snrcclk0 =24000000
            self.snrcclk1 =24000000
            self.snrcclk2 =24000000
            self.snrcclk3 =24000000


class UART_CFG(object):
    def __init__(self):
        self.baudrate=115200
        self.mode =0
class ANALOG_CFG(object):
    def __init__(self,chiptype=0):
        #such as Regulator,VM,TM
        if chiptype == 0:
            self.rx0phy_shift_num =8
            self.rx1phy_shift_num =8
            self.rx2phy_shift_num =8
            self.rx3phy_shift_num =8
        else:
            self.rx0phy_shift_num =6
            self.rx1phy_shift_num =6
            self.rx2phy_shift_num =6
            self.rx3phy_shift_num =6

class GPIO_CFG(object):
    def __init__(self,id=0,spid =0):
        self.index =id    # pad index
        self.pull_en =0   # pad pull enable
        self.pull_sel =1 # 0 pull down,1 pull up
        self.input_en =0   # pad input enable, 0 : disable
        self.hold_en =1    # pad hold enable
        self.output_oen =1   # pad output enable 0: output  enable 1: output disable
        self.slew_rate_en =0    # sele rate enable
        self.schmitt_trig_en =0  # schemitter trigger enable selcec [1:0]
        self.driving_sel=1  # driving strength select [1:0]
        self.safemode_en =0  # safe mode enable , 1: pad output safeve val when enter safe mode 0 output normal val
        self.safevalue=0   #  safe vale when enter safe value
        self.debug_en =0
        self.insrc =0
        self.outsrc =0

class PAD_CFG(object):
    def __init__(self):
        self.peri_mask=0x0fff0000 #only contrl fsin and fsync as default
        self.gpio_mask=0xffffffff #disable control gpio and others
        self.peri_num =32  # peripheral number ,include sensor ctrl,spi,uart...
        self.peri_buf=[]
        self.gpio_num= 19 # gpio number ,
        self.gpio_buf=[]



class SYSTEM_PERIPHERAL_CFG(object):
    def __init__(self):
        #Uart,spi,sccb
        pass

class SYSTEM_CTRL_CFG(object):
    def __init__(self):
        self.cpu2xbus =0   # cpu double rate enable
        self.busclkinv =0  # bus clk invert when cpu double rate enable 1: inv
        #Uart,spi,sccb


class SYSTEM_ANALOG_CFG(object):
    def __init__(self,chip_type):
        if chip_type == 0:
            self.rx0phy_shift_num =8
            self.rx1phy_shift_num =8
            self.rx2phy_shift_num =8
            self.rx3phy_shift_num =8
        else:
            self.rx0phy_shift_num =6
            self.rx1phy_shift_num =6
            self.rx2phy_shift_num =6
            self.rx3phy_shift_num =6
        self.tpmen =1
        self.vmen =1




class SYSTEM_CFG(object):
    def __init__(self,chip_type):
        self.en =1
        self.pll=SYSTEM_PLL_CFG(chip_type)
        self.clkt=SYSTEM_CLOCK_CFG(chip_type)
        self.peri=SYSTEM_PERIPHERAL_CFG()
        self.ana=SYSTEM_ANALOG_CFG(chip_type)
        self.pad =PAD_CFG()
        self.ctrl = SYSTEM_CTRL_CFG()

# firmware  configuration start here

#class FW_SYS(object):
#    def __init__(self):
#        pass
#class FW_ALGO(object):
#    def __init__(self):
#        pass

#class FW_CFG(object):
#    def __init__(self):
#        self.sys=FW_SYS()
#        self.algo= FW_ALGO()
#        pass

# Safety  configuration start here


class ERROR_CFG(object):
    def __init__(self,id=0,spid =0):
        self.index =id
        self.gid,self.groupname = self.gid_gen(id)
        self.mask =1   # 0: make 1: unmask
        self.level =1 # 1, low 2 :mid 4: high
        self.proc_mode =0  # 0 : cpu 1 : host process
        self.en =1

    def gid_gen(self,id):
        group_dict={
        tuple(range(12))   :(0,"MIPIRX"),
        tuple(range(12,16)):(1,"IMAGE_MONITOR"),
        tuple(range(16,22)):(2,"IDC_PATH"),
        tuple(range(22,26)):(3,"IDP_PATH"),
        tuple(range(26,31)):(4,"EMB"),
        tuple(range(31,35)):(5,"RGBIR_TOP"),
        tuple(range(35,41)):(6,"RETIME"),
        tuple(range(41,48)):(7,"MIPITX"),
        tuple(range(48,50)):(8,"MIXPHY"),
        tuple(range(109,110)):(9,"PRERT"),
        tuple(range(83,84)):(10,"ISP"),
        tuple(range(50,54)):(11,"DMA"),
        tuple(range(54,55)):(12,"SPIS"),
        tuple(range(55,56)):(13,"SPIM"),
        tuple(range(56,60)):(14,"TIMER"),
        tuple(range(60,63)):(15,"WATCHDOG"),
        tuple(range(63,67)):(16,"ECM"),
        tuple(range(67,70)):(17,"SCCB"),
        tuple(range(70,77)):(18,"ECC"),
        tuple(range(77,83)):(19,"BIST"),
        tuple(range(84,85)):(20,"TPM"),
        tuple(range(85,87)):(21,"VM"),
        tuple(range(87,88)):(22,"TM"),
        tuple(range(88,93)):(23,"CLKCHK"),
        tuple(range(93,108)):(24,"CRYPTO"),
        tuple(range(108,109)):(25,"PVT"),
        tuple(range(109,128)):(26,"CLKMON"),
    }
        for key,val in group_dict.items():
            if id in key:
                # print("err",id,val)
                return  val
        raise RuntimeError(f"can't find group {id}")


class CLKMNT_CFG(object):
    def __init__(self):
        self.en =1
        self.plllock_en =1
        self.refclk_en =1
        self.oscclk_en =1

        self.refclk_freqdiv =0x0f
        self.oscclk_freqdiv =0xff

        self.testclk_buf=[]
        self.testclk_num=18
class TESTCLK_CFG(object):
    def __init__(self,id=0,spid=0):
        self.index =id
        self.src =id
        self.en =1
        self.winnum =1
        self.threshold = 200
        self.percision = 10000
        self.timeout_en = 1


class SAFETY_HW_CFG(object):
    def __init__(self):
        pass


class SAFETY_SW_CFG(object):
    def __init__(self):
        pass

class SAFETY_CFG(object):
    def __init__(self):
        self.en =1
        # self.hw=SAFETY_HW_CFG()
        # self.sw= SAFETY_SW_CFG()
        self.errpin_pol =0
        self.errpin_en =0
        self.errcnt_thres = 100
        self.miderr_timeout =0xffffff

        self.clkmnt = CLKMNT_CFG()

        self.err_num =128
        self.err_buf=[]

    def get_grp_errs(self,gid):
        return [err for err in self.err_buf if err.gid ==gid]

#class PGEN_CFG(object):
#    def __init__(self,id):
#        self.index=id
#        self.clk =0
#        self.format =0
#        self.hsize =0
#        self.vsize =0
#        self.hts =0
#        self.vts =0
#        self.hblk =0
#        self.vblk =0
#        self.mode =0
#        self.en =0


class PGEN_CFG(object):

    def __init__(self,id=0):
        self.index =id
        self.en =0
        self.format =0
        self.hsize =0
        self.vsize =0
        self.vsync_width =100
        self.hblank= 0
        self.hts =0
        self.vts =0
        self.fps =0
        self.preblank =10

        self.sclk =0
        self.ctrl0 =0
        self.ctrl1 =0


chip_obj_dict={
    "SENSOR_CFG":SENSOR_CFG,
    "SDS_CFG":SDS_CFG,
    "GPIO_CFG":GPIO_CFG,
    "PERI_CFG":GPIO_CFG, 
    "CB_CFG":CB_CFG,
    "ERR_CFG":ERROR_CFG,  
    "TESTCLK_CFG":TESTCLK_CFG,  
}


class MONITOR_LOG_CFG(object):
    def __init__(self):
        self.strm_level= 20 # 10, debug, 20 info 30 warn 40. error 50 fatal
        self.file_level= 40



class MONITOR_CFG(object):
    def __init__(self):
        self.log= MONITOR_LOG_CFG()
        self.hcmd =HCMDCTRL_CFG()
        self.en = 1               # monitor enable control
        self.err_chk=1            # error register check dr
        self.status_chk= 1       # status register dump
        self.img_chk  = 1        # image check ,include size, format,fps
        self.embl_chk = 1        # embeeded line chekc ,line number, vld byte ,crc
        self.crypto_chk = 0      # crypto hmac check
        self.embl_datachk = 0     # embedded line data content compare, check input source and output content
        self.embl_frmcrcchk = 1   # embedded line frame crc check
        self.embl_seichkloc =0    # embedded line sei content  location check, 0 : interal sram 1: sensor
        self.mem_chk = 0         # dump embedded line sram memory
        self.img_save =0         # image save as png .
        self.chk_times = 1     # monitor times
        self.chk_intrvl = 0       # monitor interval ,unit s
        self.sccbid =0x48        # monitor sccb slave id .
        self.outsel =0           # monitor port select , corresponding to oax4k mtx port
        self.fcpchk =1             # oax4k fcp check eanble.
        self.dumpreg_start = 0x3000   # dumpreg start addresss , support oax4k and sensor ,4k should start with 0x80xx_xxxx
        self.dumpreg_len =    0x00
        self.dumpreg_snrsrc = 0     # dumpreg sensor source ,

class HCMDCTRL_CFG(object):
    def __init__(self):
        self.send_en =1
        self.save_en =1
        self.send_mode =0 # 0 seq ,1: random
        self.send_times =2
        self.dly_mode  =0 #0 fix, 1: randomc
        self.dly_time  =1
