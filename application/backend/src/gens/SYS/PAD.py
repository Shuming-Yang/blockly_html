"""
This GENS mode code which be ported from GENS source code.
@@OAX4K dist define

Author: OVT AE
Date: 2024-11-05
"""
# WARNING
# pylint: disable=C0103, C0115, C0116, C0200, C0412, R0205, R0914, R0915, W0231, W0401, W0611, W0612, W0614
from Utility.Reg import REG8
from Utility.Reg import REG16
from Utility.Reg import REG32
from Utility.Entity import Entity
from Utility.Para import *
from Define.Struct import SYSTEM_PLL_CFG
from Define.Struct import GPIO_CFG
from Utility.Others import get_class_var
from Utility.Reg import REGOBJ
from RegTable.Regdefdist import *


class PAD_CFG(object):
    def __init__(self, _chipcfg):
        # such as GPIO,UART,SPI
        self.spwdn_buf = [GPIO_CFG(i) for i in range(4)]
        self.srst_buf = [GPIO_CFG(i) for i in range(4)]
        self.cclk_buf = [GPIO_CFG(i) for i in range(4)]
        self.fsync_buf = [GPIO_CFG(i) for i in range(4)]
        self.gpio_buf = [GPIO_CFG(i) for i in range(17)]
        self.bistsel_buf = [GPIO_CFG(i) for i in range(2)]
        self.uart_buf = [GPIO_CFG(i) for i in range(2)]
        self.spi_buf = [GPIO_CFG(i) for i in range(6)]
        self.sccbid_buf = [GPIO_CFG(i) for i in range(2)]  # sccb id ,jatg,fsin
        self.rsvd_buf = [GPIO_CFG(i) for i in range(2)]  # sccb id ,jatg,fsin
        self.fsin_buf = [GPIO_CFG(i) for i in range(4)]  # sccb id ,jatg,fsin
        self.debug_en = 0
        self.peri_mask = 0
        self.gpio_mask = 0
        # self.txd = PAD_IO_CFG()
        # self.rxd = PAD_IO_CFG()
        # self.spick = PAD_IO_CFG()
        # self.ssn = PAD_IO_CFG()
        # self.miso = PAD_IO_CFG()
        # self.mosi = PAD_IO_CFG()
        # self.miso1 = PAD_IO_CFG()
        # self.mosi1 = PAD_IO_CFG()


class PAD_REG(REGOBJ):
    def __init__(self, cfg, _uid=0):
        base = self.get_baseaddr('PAD', define_dist, 0)
        # print(" SC {:x} {:x}".format(uid, base))
        self.regtable = cfg.regtable
        self.base = base
        self.objr = []


class PAD(Entity):
    """description of class"""
    def __init__(self, chipcfg):
        self.cfg = PAD_CFG(chipcfg)
        self.reg = PAD_REG(chipcfg)
        self.regtable = chipcfg.regtable
        self.setbuf = []
        self._pad_cfg_init(chipcfg)

    def _pad_cfg_init(self, chipcfg):
        out0 = chipcfg.oax4k_cfg.out0
        out1 = chipcfg.oax4k_cfg.out1
        out2 = chipcfg.oax4k_cfg.out2
        out3 = chipcfg.oax4k_cfg.out3
        outlist = [out0, out1, out2, out3]
        self.cfg.spwdn_buf = chipcfg.oax4k_cfg.sys.pad.peri_buf[0: 4]
        self.cfg.srst_buf = chipcfg.oax4k_cfg.sys.pad.peri_buf[4: 8]
        self.cfg.cclk_buf = chipcfg.oax4k_cfg.sys.pad.peri_buf[8: 12]
        self.cfg.fsync_buf = chipcfg.oax4k_cfg.sys.pad.peri_buf[12: 16]
        self.cfg.uart_buf = chipcfg.oax4k_cfg.sys.pad.peri_buf[16: 18]
        self.cfg.spi_buf = chipcfg.oax4k_cfg.sys.pad.peri_buf[18: 24]
        self.cfg.sccbid_buf = chipcfg.oax4k_cfg.sys.pad.peri_buf[24: 26]
        self.cfg.rsvd_buf = chipcfg.oax4k_cfg.sys.pad.peri_buf[26: 28]
        self.cfg.fsin_buf = chipcfg.oax4k_cfg.sys.pad.peri_buf[28: 32]
        self.cfg.gpio_buf = chipcfg.oax4k_cfg.sys.pad.gpio_buf[0: 17]
        self.cfg.bistsel_buf = chipcfg.oax4k_cfg.sys.pad.gpio_buf[17: 19]
        self.cfg.gpio_mask = chipcfg.oax4k_cfg.sys.pad.gpio_mask
        self.cfg.peri_mask = chipcfg.oax4k_cfg.sys.pad.peri_mask
        self.cfg.debug_en = chipcfg.oax4k_cfg.topctrl.debug_en
        self.cfg.rsvd_buf[0].driving_sel = 4  # xtal freq
        for item in self.cfg.cclk_buf:
            item.driving_sel = 0
        for out in outlist:
            if out.fsync.en:
                if out.fsync.out_fsin:
                    if (out.fsync.byp_fsin or out.fsync.trig_mode):
                        raise RuntimeError ("can't bypass or use fsin trigger  and output fsin at the same time ")
                    fsin_obj = self.cfg.fsin_buf[out.fsync.outsrc]
                    fsin_obj.output_oen = 0
                    fsin_obj.input_en = 0
                    fsin_obj.outsrc = out.fsync.index
                else:
                    fsync_obj = self.cfg.fsync_buf[out.fsync.outsrc]
                    fsin_obj = self.cfg.fsin_buf[out.fsync.insrc]
                    fsync_obj.output_oen = 0
                    fsync_obj.input_en = 0
                    # fsync_obj.outsrc = out.fsync.outsrc
                    fsync_obj.outsrc = out.fsync.index
                    if(out.fsync.trig_mode or out.fsync.byp_fsin):
                        fsin_obj.output_oen = 1
                        fsin_obj.input_en = 1
                        fsinrt_obj = self.cfg.fsin_buf[out.fsync.index]
                        fsinrt_obj.insrc = out.fsync.insrc

    def mask32to64(self, mask32):
        mask64 = 0
        for _ in range(32):
            mask64 = mask64 << 2
            if mask32 & BIT31:
                mask64 = mask64 | 3
            mask32 = mask32 << 1
        return mask64

    def start(self):
        pwdnbuf = self.cfg.spwdn_buf
        srstbuf = self.cfg.srst_buf
        cclkbuf  = self.cfg.cclk_buf
        fsyncbuf = self.cfg.fsync_buf
        gpiobuf = self.cfg.gpio_buf
        bistselbuf = self.cfg.bistsel_buf
        spibuf = self.cfg.spi_buf
        uartbuf = self.cfg.uart_buf
        fsinbuf = self.cfg.fsin_buf
        miscbuf = self.cfg.sccbid_buf + self.cfg.rsvd_buf + self.cfg.fsin_buf
        pe = 0
        ps0 = 0
        ie0 = 0
        he0 = 0
        outen = 0
        slew_ctrl = 0
        schm_trig = 0
        ds_sel = 0
        safe_val = 0
        state_mode = 0
        safeval = 0
        debug_en = 0
        b0buf = pwdnbuf + srstbuf + cclkbuf + fsyncbuf + uartbuf + spibuf + miscbuf + gpiobuf + bistselbuf
        # print("len of b0buf {}".format(len(b0buf)))
        for i in range(len(b0buf)):
            pe =pe |(b0buf[i].pull_en<<i)
            ps0 =ps0 |(b0buf[i].pull_sel<<i)
            ie0  = ie0 | (b0buf[i].input_en<<i)
            he0 = he0 | (b0buf[i].hold_en<<i)
            outen = outen |  (b0buf[i].output_oen<<i)
            slew_ctrl = slew_ctrl |  (b0buf[i].slew_rate_en<<i)
            schm_trig = schm_trig |(b0buf[i].schmitt_trig_en<<i*2) #aaa
            ds_sel = ds_sel |(b0buf[i].driving_sel<<i*2)
            state_mode = state_mode | (b0buf[i].safemode_en<<i)
            safeval = safeval |  (b0buf[i].safevalue<<i)
            debug_en =debug_en | (b0buf[i].debug_en<<i) #tbd

        if self.cfg.debug_en:
            debug_en = 0x001fffc0  # fsin don't use as debug pin,uart,spi also
            outen = outen & 0xffffffff
        b0 = fsinbuf[0].outsrc |(fsinbuf[1].outsrc<<2) |(fsinbuf[2].outsrc<<4) |(fsinbuf[3].outsrc<<6)
        b1 = fsyncbuf[0].outsrc |(fsyncbuf[1].outsrc<<2) |(fsyncbuf[2].outsrc<<4) |(fsyncbuf[3].outsrc<<6)
        b2 = fsinbuf[0].insrc |(fsinbuf[1].insrc<<2) |(fsinbuf[2].insrc<<4) |(fsinbuf[3].insrc<<6)
        r68 = b0 | (b1<<8)| (b2<<16)
        # print(len(b0buf))
        self.reg.writereg32(0x20,outen&0xffffffff,mask=self.cfg.peri_mask)
        self.reg.writereg32(0x24,outen>>32,mask=self.cfg.gpio_mask)
        self.reg.writereg32(0x00,pe&0xffffffff,mask=self.cfg.peri_mask)
        self.reg.writereg32(0x04,pe>>32,mask=self.cfg.peri_mask)
        self.reg.writereg32(0x08,ps0&0xffffffff,mask=self.cfg.gpio_mask)
        self.reg.writereg32(0x0c,ps0>>32,mask=self.cfg.gpio_mask)
        self.reg.writereg32(0x10,ie0&0xffffffff,mask=self.cfg.peri_mask)
        self.reg.writereg32(0x14,ie0>>32,mask=self.cfg.gpio_mask)
        self.reg.writereg32(0x18,he0&0xffffffff,mask=self.cfg.peri_mask)
        self.reg.writereg32(0x1c,he0>>32,mask=self.cfg.gpio_mask)
        self.reg.writereg32(0x28,slew_ctrl&0xffffffff,mask=self.cfg.peri_mask)
        self.reg.writereg32(0x2c,slew_ctrl>>32,mask=self.cfg.gpio_mask)
        peri_mask64 = self.mask32to64(self.cfg.peri_mask)
        gpio_mask64 = self.mask32to64(self.cfg.gpio_mask)
        self.reg.writereg32(0x30,schm_trig&0xffffffff,mask=peri_mask64&0xffffffff)
        self.reg.writereg32(0x34,(schm_trig>>32)&0xffffffff,mask=peri_mask64>>32)
        self.reg.writereg32(0x38,(schm_trig>>64)&0xffffffff,mask=gpio_mask64&0xffffffff)
        self.reg.writereg32(0x3c,(schm_trig>>96)&0xffffffff,mask=gpio_mask64>>32)
        self.reg.writereg32(0x40,ds_sel&0xffffffff,mask=peri_mask64&0xffffffff)
        self.reg.writereg32(0x44,(ds_sel>>32)&0xffffffff,mask=peri_mask64>>32)
        self.reg.writereg32(0x48,(ds_sel>>64)&0xffffffff,mask=gpio_mask64&0xffffffff)
        self.reg.writereg32(0x4c,(ds_sel>>96)&0xffffffff,mask=gpio_mask64>>32)
        self.reg.writereg32(0x50,state_mode&0xffffffff,mask=self.cfg.peri_mask)
        self.reg.writereg32(0x54,state_mode>>32,mask=self.cfg.gpio_mask)
        self.reg.writereg32(0x58,safeval&0xffffffff,mask=self.cfg.peri_mask)
        self.reg.writereg32(0x5c,safeval>>32,mask=self.cfg.gpio_mask)
        self.reg.writereg32(0x60,debug_en)
        self.reg.writereg32(0x64,0)  # tbd
        self.reg.writereg32(0x68,r68)  # tbd
        self.reg.writereg8(0x80209600, 0x44)
