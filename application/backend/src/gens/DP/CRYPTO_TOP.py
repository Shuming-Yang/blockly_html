# WARNING
# pylint: disable=C0103, C0114, C0115, C0209, C0412, W0231, W0401, W0612, W0613, W0614, W0622
from Utility.Reg import REGOBJ
from Utility.Entity import Entity
from Utility.Para import *
from Define.Para import *
from Utility.Others import *
from RegTable.Regdefdist import define_dist
from Define.board import SC_BASE_ADDR,CRYPTO_BASE_ADDR


crypto_host_offset_dict={
    0:0xb84,
    1:0xb9c,
    2:0xbb4,
    3:0xbcc,
}


crypto_slave_offset_dict={
    0:0xbec,
    1:0xbfc,
    2:0xc0c,
    3:0xc1c,
}


REG_DICT = {
    'BIT0': 0x1,
    'BIT1': 0x2,
    'BIT2': 0x4,
    'BIT3': 0x8,
    'BIT4': 0x10,
    'BIT5': 0x20,
    'BIT6': 0x40,
    'BIT7': 0x80,
}

gYUVdict = {
    0 : 2,
    1 : 1,
    2 : 0,
    3 : 2,
    4 : 0,
    5 : 3,
    6 : 4,
    7 : 5,
    13: 5
}


gRAWdict = {
    0 : 6,
    1 : 6,
    2 : 6,
    3 : 7,
    4 : 2,
    5 : 1,
    6 : 0,
    7 : 5,
    13: 0
}


sei_toggle_map = [
    [0, 1, 2, 3], # host0 sei source layout 0x8020eb94
    [1, 0, 2, 3], # host1 sei source layout 0x8020ebac
    [2, 0, 1, 3], # host2 sei source layout 0x8020ebc4
    [3, 0, 1, 2]  # host3 sei source layout 0x8020ebdc
]


class CRYPTO_GEMO_CFG(object):
    def __init__(self,id=0):
        self.en =0
        self.index =id
        self.b2h =0
        self.nr_rows =0
        self.row_len =0


class CRYPTO_HOST_CFG(object):
    def __init__(self,id=0):
        self.en =0
        self.index =id
        self.abmode = 0
        self.gemo0 =CRYPTO_GEMO_CFG(0)
        self.gemo1 =CRYPTO_GEMO_CFG(1)
        self.hmac =CRYPTO_HMAC_CFG()


class CRYPTO_HMAC_CFG(object):
    def __init__(self,id=0):
        self.index =id
        self.data_sel =0  # hash option to choose 16 bit from combine 24 bit in host point
        self.pre_embl_en =0
        self.pre_embl_num =0
        self.staline_en =0
        self.staline_num =0
        self.a_vcid =0
        self.b_vcid =1
        self.bchannel = 2
        self.pre_embl_src = 0 # 0x0, 0x1, 0x2 or 0x3


class CRYPTO_SLAVE_CFG(object):
    def __init__(self,id=0):
        self.en =0
        self.index =id
        self.abmode = 0
        self.format = 0
        self.hmac_path = 0
        self.gemo0 =CRYPTO_GEMO_CFG(0)
        self.gemo1 =CRYPTO_GEMO_CFG(1)
        self.hmac = CRYPTO_HMAC_CFG()


class CRYPTO_CFG(object):
    def __init__(self,chipcfg):
        self.en =0
        self.random_sel =0
        self.random_mode =0
        self.hst0= CRYPTO_HOST_CFG(0)
        self.hst1= CRYPTO_HOST_CFG(1)
        self.hst2= CRYPTO_HOST_CFG(2)
        self.hst3= CRYPTO_HOST_CFG(3)
        self.slv0= CRYPTO_SLAVE_CFG(0)
        self.slv1= CRYPTO_SLAVE_CFG(1)
        self.slv2= CRYPTO_SLAVE_CFG(2)
        self.slv3= CRYPTO_SLAVE_CFG(3)


class CRYPTO_REG(REGOBJ):
    def __init__(self,cfg,uid=0):
        self.base =self.get_baseaddr('CRYPTO',define_dist,uid)
        self.regtable=cfg.regtable
        self.objr=[]


class CRYPTO_TOP(Entity):
    """description of class"""
    def __init__(self,chipcfg,uid=0):
        #self.cfg=mrx_cfg()
        self.cfg =CRYPTO_CFG(chipcfg)
        self.reg =CRYPTO_REG(chipcfg)
        self.setbuf=[]
        if chipcfg.oax4k_cfg.crypto.en:
            self._crypto_cfg_init(chipcfg)

    def _crypto_host_init(self,chipcfg_host,chipcfg):
        self_hosts= [self.cfg.hst0,self.cfg.hst1,self.cfg.hst2,self.cfg.hst3]
        self_host= self_hosts[chipcfg_host.index]
        self_host.en = chipcfg_host.en
        self_host.abmode = chipcfg_host.abmode
        self_host.gemo0 = chipcfg_host.gemo0
        self_host.gemo1 = chipcfg_host.gemo1
        inobj= chipcfg_host.inbuf[0]
        dpobj= chipcfg_host.dpbuf[0]
        doobj= chipcfg_host.dobuf[0]
        snrstrma = inobj.sensor_buf[dpobj.input.strmsrc]
        embobj =doobj.embl
        if embobj.hmac.inen:
            self_host.hmac.pre_embl_src = embobj.index
            print(f"[CRYPTO]: SEI{self_host.hmac.pre_embl_src} -> H{self_host.index}")
        self_host.hmac.data_sel = chipcfg_host.hmac.data_sel
        self_host.hmac.a_vcid = snrstrma.strm.vclist[0]
        if chipcfg_host.abmode:
            snrstrmb= inobj.sensor_buf[chipcfg_host.b_vc_id]
            self_host.hmac.b_vcid = snrstrmb.strm.vclist[0]
            self_host.hmac.bchannel = chipcfg_host.bchannel
            print(f"[CRYPTO]: SEI{self_host.hmac.bchannel} -> H{self_host.index}")
        self_host.hmac.pre_embl_num = snrstrma.embl.pre.num

    def _crypto_hosts_init(self,chipcfg):
        crypto_chipcfg= chipcfg.oax4k_cfg.crypto
        chipcfg_hosts=[crypto_chipcfg.hst0,crypto_chipcfg.hst1,crypto_chipcfg.hst2,crypto_chipcfg.hst3]
        for chipcfg_host in chipcfg_hosts:
            if chipcfg_host.en:
                self._crypto_host_init(chipcfg_host,chipcfg)

    def _crypto_slave_init(self,slave_chipcfg, outcfg):
        self_slaves= [self.cfg.slv0,self.cfg.slv1,self.cfg.slv2,self.cfg.slv3]
        self_slave= self_slaves[slave_chipcfg.index]
#        outimg = outcfg.yuv if outcfg.embl.chn==1 else outcfg.raw
        if outcfg.embl.chn==1:
            self_slave.format = gYUVdict[outcfg.yuv.format]
            self_slave.hmac_path = 1
        else:
            self_slave.format = gRAWdict[outcfg.rawmv.format]
            self_slave.hmac_path = 0
#        print('[CRYPTO] ####################################get format para {}'.format(self_slave.format))
        self_slave.en = slave_chipcfg.en
        self_slave.gemo0 = slave_chipcfg.gemo0
        self_slave.gemo1 = slave_chipcfg.gemo1
        self_slave.abmode = slave_chipcfg.abmode
#        self_slave.format = slave_chipcfg.format
        self_slave.hmac.data_sel = slave_chipcfg.hmac.data_sel
        if slave_chipcfg.abmode:
            self_slave.hmac.bchannel = slave_chipcfg.bchannel
        self_slave.hmac.pre_embl_en = slave_chipcfg.topembl
        self_slave.hmac.staline_en = slave_chipcfg.bottomembl
#        self_slave.hmac_path = slave_chipcfg.hmac_path

    def _crypto_slaves_init(self,chipcfg):
        crypto_chipcfg= chipcfg.oax4k_cfg.crypto
        slaves_chipcfg = [crypto_chipcfg.slv0,crypto_chipcfg.slv1,crypto_chipcfg.slv2,crypto_chipcfg.slv3]
        outs = [chipcfg.oax4k_cfg.out0, chipcfg.oax4k_cfg.out1, chipcfg.oax4k_cfg.out2, chipcfg.oax4k_cfg.out3]
        for i in range(4):
            if slaves_chipcfg[i].en:
                self._crypto_slave_init(slaves_chipcfg[i], outs[i])
#        for slave_chipcfg in slaves_chipcfg:
#            if(slave_chipcfg.en):
#                self._crypto_slave_init(slave_chipcfg, )
#        pass

    def _crypto_cfg_init(self,chipcfg):
        self.cfg.random_mode =chipcfg.oax4k_cfg.crypto.random_mode
        self.cfg.random_sel =chipcfg.oax4k_cfg.crypto.random_sel
        self._crypto_hosts_init(chipcfg)
        self._crypto_slaves_init(chipcfg)

    def _crypto_hsts_start(self):
        crytpo_hosts= [self.cfg.hst0,self.cfg.hst1,self.cfg.hst2,self.cfg.hst3]
        for host in crytpo_hosts:
            if host.en:
                baseaddr =crypto_host_offset_dict[host.index]
                #0xb84
                self.reg.writereg32(baseaddr+0,host.gemo0.b2h)
                self.reg.writereg16(baseaddr+4,host.gemo0.nr_rows)
                self.reg.writereg16(baseaddr+0x06,host.gemo0.row_len * 2)
                if host.gemo1.en:
                    self.reg.writereg32(baseaddr+0x08,host.gemo1.b2h)
                    self.reg.writereg16(baseaddr+0x0c,host.gemo1.nr_rows)
                    self.reg.writereg16(baseaddr+0x0e,host.gemo1.row_len * 2)
                hmac_r1 =0xb | (host.hmac.data_sel<<4)
                self.reg.writereg8(baseaddr+0x11,hmac_r1)
                hmac_r2 = host.hmac.pre_embl_num |(host.hmac.pre_embl_en<<3) | (host.hmac.staline_en<<7)  |(host.hmac.staline_num<<4)
                self.reg.writereg8(baseaddr+0x12,hmac_r2)
                hmac_r3 = host.hmac.a_vcid | (host.hmac.b_vcid<<4)
                self.reg.writereg8(baseaddr+0x13,hmac_r3)
                #handle toggle signal
                embl_toggle = 0x10
                if host.index == host.hmac.pre_embl_src:
                    embl_toggle = 0x10
                else:
                    for i in range(len(sei_toggle_map[host.index])):
                        if host.hmac.pre_embl_src == sei_toggle_map[host.index][i]:
                            embl_toggle = 1 << (i + 4)
                            break
                if(host.abmode and host.gemo1.en):
                    if host.index == 0:
                        for i in range(len(sei_toggle_map[0])):
                            if host.hmac.bchannel == sei_toggle_map[0][i]:
                                embl_toggle |= (1 << (i + 4))
                                break
                    else:
                        raise RuntimeError(f"AB mode cannot apply on route{host.index}")
                hamc_r0 = (host.gemo0.en<<0) |  (host.gemo1.en<<1) | 0x08 | (embl_toggle)
                self.reg.writereg8(baseaddr+0x10,hamc_r0)
                print("[CRYPTO]: id:{},b2h:{},size:{}*{},b_size:{}*{},vc_id:{},{},pre_embl_en:{},pre_embl_num:{:x},embl_toggle:{}".format(host.index,host.gemo0.b2h,
                        host.gemo0.row_len,host.gemo0.nr_rows,host.gemo1.row_len,host.gemo1.nr_rows,
                        host.hmac.a_vcid,host.hmac.b_vcid,host.hmac.pre_embl_en,host.hmac.pre_embl_num,embl_toggle))
#                 print("[CRYPTO]:a_add:{:x},val:{:d}".format(baseaddr+0x04,host.gemo0.nr_rows));
#                 print("[CRYPTO]:a_add:{:x},val:{:d}".format(baseaddr+0x06,host.gemo0.row_len * 2));
#                 print("[CRYPTO]:b_add:{:x},val:{:d}".format(baseaddr+0x0c,host.gemo1.nr_rows));
#                 print("[CRYPTO]:b_add:{:x},val:{:d}".format(baseaddr+0x0e,host.gemo1.row_len * 2));

    def _crypto_slvs_start(self):
        crytpo_slvs= [self.cfg.slv0,self.cfg.slv1,self.cfg.slv2,self.cfg.slv3]
        crytpo_hosts= [self.cfg.hst0,self.cfg.hst1,self.cfg.hst2,self.cfg.hst3]
        i = 0
        for slave in crytpo_slvs:
            if slave.en:
                val = self.reg.readreg8(SC_BASE_ADDR + 0x53) &(~REG_DICT['BIT0'])
                self.reg.writereg8(SC_BASE_ADDR + 0x53, val)#for otp transfer
                self.reg.writereg8(CRYPTO_BASE_ADDR + 0xbee + 0x10*i,slave.format | (slave.hmac_path<<7)) #raw16,path:raw
#                 embl_val = slave.hmac.pre_embl_num |(slave.hmac.pre_embl_en<<3) | (slave.hmac.staline_num<<4) |(slave.hmac.staline_en<<7)
                embl_val = (slave.hmac.pre_embl_en<<3)|(slave.hmac.staline_en<<7)
                self.reg.writereg8(CRYPTO_BASE_ADDR + 0xbef + 0x10*i,embl_val) #if add sei and sta to hash
                if slave.abmode:
                    self.reg.writereg8(CRYPTO_BASE_ADDR + 0xbee + 0x10*slave.hmac.bchannel,slave.format| (slave.hmac_path<<7))#raw16,path:raw
                    self.reg.writereg8(CRYPTO_BASE_ADDR + 0xbef + 0x10*slave.hmac.bchannel,embl_val)#if add sei and sta to hash
                self.reg.writereg8(CRYPTO_BASE_ADDR + 0xc67, self.reg.readreg8(CRYPTO_BASE_ADDR + 0xc67) | BIT2)#slave hmac value dma handling to embline big endian enable
            i += 1

    def _crypto_cmmn_start(self):
#         interruption
        self.reg.writereg32(0xcbc,0xffffff)
        self.reg.writereg32(0xcc0,0x3f3f3f3f)
        self.reg.writereg32(0xcc4,0xffffffff)
        self.reg.writereg32(0xcc8,0x1fffffff)
        self.reg.writereg32(0xccc,0xfffff)
#         global error enable
        self.reg.writereg8(0xc67,0x12)
        r96val = self.reg.readreg8(0xc96)
        self.reg.writereg8(0xc96,r96val | 0x80)
        self.reg.writereg8(0xc3d,self.cfg.random_sel|(self.cfg.random_mode<<1))

    def start(self):
        self._crypto_cmmn_start()
        self._crypto_hsts_start()
        self._crypto_slvs_start()
