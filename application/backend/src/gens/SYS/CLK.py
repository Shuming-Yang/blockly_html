"""
This GENS mode code which be ported from GENS source code.
@@OAX4K dist define

Author: OVT AE
Date: 2024-11-05
"""
# WARNING
# pylint: disable=C0103, C0115, C0116, C0200, C0412, R0205, W0231, W0401, W0611, W0612, W0614
from Utility.Reg import REG8
from Utility.Reg import REG16
from Utility.Reg import REG32
from Utility.Entity import Entity
from Utility.Para import *
from Define.Para import *
from Define.Struct import SYSTEM_PLL_CFG
from Utility.Others import get_class_var
from Utility.Reg import REGOBJ
from RegTable.Regdefdist import *

clks_srcdiv_oft_dict = {
    'cb0clk': 0x94,
    'cb1clk': 0x96,
    'cb2clk': 0x98,
    'cb3clk': 0x9a,
    'do0clk': 0x84,
    'do1clk': 0x88,
    'dpclk': 0x7c,
    'fe0clk': 0x6c,
    'fe1clk': 0x70,
    'fe2clk': 0x74,
    'fe3clk': 0x78,
    'sysclk': 0x60,
    'perpclk': 0x68,
    'secuclk': 0xa0,
    'snrcclk0': 0x8c,
    'snrcclk1': 0x8e,
    'snrcclk2': 0x90,
    'snrcclk3': 0x92,
}

feclk_src_dict = {
    0: 0,
    1: 1,
    2: 4,
    3: 6
}

pllsrc_selcode_dict = {
    'sys_clk0': 0x10,
    'sys_clk1': 0x18,
    'tx0_clk0': 0x24,
    'tx0_clk1': 0x25,
    'tx1_clk0': 0x20,
    'tx1_clk1': 0x22,
    'xclk': 0x0,
}

mrx_phyclk_sel_dict = {
    (0,0): 0x0,
    (0,1): 0x2,
    (1,0): 0x0,
    (1,1): 0x2,
}


class CLOCK_ELM(object):
    def __init__(self, name, val, div=1, src=0):
        self.name = name
        self.freq = val
        self.div = div
        self.src = src
        self.mon = 1


class CLK_CFG(object):
    def __init__(self, chipcfg):
        self.chipcfg = chipcfg

    def config(self):
        pass


class CLK_REG(REGOBJ):
    def __init__(self, cfg, _uid=0):
        base = self.get_baseaddr('SYSTEM_CTRL', define_dist, 0)
        # print(" SC {:x} {:x}".format(uid, base))
        self.regtable = cfg.regtable
        self.base = base
        self.objr = []


class CLOCK(Entity):
    """description of class"""
    def __init__(self, chipcfg):
        self.cfg = CLK_CFG(chipcfg)
        self.reg = CLK_REG(chipcfg)
        self.regtable = chipcfg.regtable
        self.setbuf = []
        self.clkdst_buf = []
        self.bootmode = chipcfg.bootmode
        self._clk_init(chipcfg)

    def _clk_init(self,cfg):
        clkobj = cfg.oax4k_cfg.sys.clkt
        varlist = get_class_var(clkobj)
        # print(varlist)
        for item, val in varlist:
            clk = CLOCK_ELM(str(item), val)
            self.clkdst_buf.append(clk)
        clkobj = cfg.oax4k_cfg.sys.pll
        varlist = get_class_var(clkobj)
        # print(varlist)
        asicpll_src_dict = {}
        # for (name,val) in list(reversed(varlist)):
        for name, val in varlist:
            asicpll_src_dict[val] = pllsrc_selcode_dict[name]

        mipi0_src_dict, mipi1_src_dict = {}, {}
        for name, val in varlist:
            if name in ('tx0_clk0', 'tx0_clk1'):
                mipi0_src_dict[val] = pllsrc_selcode_dict[name]
            elif name in ('tx1_clk0', 'tx1_clk1'):
                mipi1_src_dict[val] = pllsrc_selcode_dict[name]

        # print(mipi_src_dict)
        for dst in self.clkdst_buf:
            if dst.name in ('do0clk',):
                self.find_clksrc(mipi0_src_dict, dst)
            elif dst.name in ('do1clk',):
                self.find_clksrc(mipi1_src_dict, dst)
            else:
                self.find_clksrc(asicpll_src_dict, dst)
        if self.bootmode:
            self._clk_pramreg_init(cfg)

    def _clk_pramreg_init(self, cfg):
        offset = 0x60
        fw = cfg.oax4k_cfg.fw
        sysctrl = self.cfg.chipcfg.oax4k_cfg.sys.ctrl
        for clk in self.clkdst_buf:
            if clk.name =='sysclk':
                offset = clks_srcdiv_oft_dict['sysclk']
                defval = self.reg.readreg32(offset)
                newval = defval & 0xffff0000 | (clk.div | ((clk.src | BIT7 | (sysctrl.cpu2xbus << 6)) << 8)) | 0xffff0000
                fw.sys.setload.table.append((offset + 0x8000, newval))
            if clk.name =='perpclk':
                offset = clks_srcdiv_oft_dict['perpclk']
                defval = self.reg.readreg32(offset)
                newval = defval & 0xffff8000 | (clk.div | (clk.src << 8)) | 0xffff0000
                fw.sys.setload.table.append((offset + 0x8000, newval))
        # clk = self.clkdst_buf[]
        fw.sys.setload.setcnt = len(fw.sys.setload.table)

    def find_clksrc(self, srcbuf, clk,mode=0):
        i = 0
        for key, _ in srcbuf.items():
            if mode:
                if key == clk.freq:
                    clk.src = int(srcbuf[key])
                    break
                else:
                    i = i + 1
                    if i >= len(srcbuf):
                        raise RuntimeError (f"can't find fitable clock source for clk {clk.freq}")
                    else:
                        continue
            else:
                if (key % clk.freq == 0 and key != 0):
                    clk.src = int(srcbuf[key])
                    clk.div = int(key/clk.freq)
                    if clk.div > 15:
                        # print(" {} divder value {} too large,change another ".format(clk.name,clk.div))
                        continue
                    else:
                        # print(" {} divder value {} {} {} in {}".format(clk.name,clk.div,clk.freq,clk.src,srcbuf))
                        break
                else:
                    i = i + 1
                    if i >= len(srcbuf):
                        raise RuntimeError (f"can't find fitable clock source for clk {clk.name} in {srcbuf} ")
                    else:
                        continue

    def clkset_src_div_en(self, clk):
        # print(clk.name, clk.div, clk.src)
        chip = self.cfg.chipcfg.oax4k_cfg
        fw = chip.fw
        sysctrl = self.cfg.chipcfg.oax4k_cfg.sys.ctrl
        inlist = [chip.dp0.input.portsrc, chip.dp1.input.portsrc, chip.dp2.input.portsrc, chip.dp3.input.portsrc]
        offset = clks_srcdiv_oft_dict[clk.name]
        # print("cfg clk name {}".format(clk.name))
        if (clk.name == 'sysclk' or 'perp' in clk.name or ('snrcclk' in clk.name or 'cb' in clk.name)):
            if 'cb' in clk.name:
                self.reg.writereg16(offset, clk.div | ((clk.src | BIT7 | BIT6) << 8))
            elif 'sysclk' in clk.name or 'perp' in clk.name:
                # if(not self.bootmode):
                if 'sysclk' in clk.name:
                    self.reg.writereg16(offset, clk.div | ((clk.src | BIT7 | (sysctrl.cpu2xbus << 6)) << 8))
                else:
                    self.reg.writereg16(offset, clk.div | (clk.src << 8), mask=BIT15)
                    # newval = defval & 0xffff0000 | (clk.div | ((clk.src | BIT7 | (sysctrl.cpu2xbus << 6)) << 8))
                    # fw.sys.setload.table.append((offset + 0x8000, newval))
            else:
                self.reg.writereg16(offset, clk.div | ((clk.src | BIT7) << 8))
        else:
            self.reg.writereg16(offset, clk.div | (clk.src << 8))
        if ('fe' in clk.name and 'clk' in clk.name):
            # tmp = self.reg.readreg8(offset+2)
            # portidx = int(clk.name.strip('feclk'))
            # self.reg.writereg8(offset+2,tmp&0x0f | (inlist[portidx]<<4)) # tmp,for test only
            self.reg.writereg8(offset + 3, 0xff) # enable clk
        elif ('snrcclk' in clk.name or 'cb' in clk.name):
            pass
        else:
            self.reg.writereg16(offset + 2, 0xffff) # enable clk
            if clk.name == 'dpclk':
                self.reg.writereg32(offset + 4, 0xffffffff)

    def reset_release(self):
        """
        relase all reset for fpga
        """
        # self.reg.writereg32(0x50, 0xf0ffffff)
        # self.reg.writereg32(0x54, 0xffffffff)
        # self.reg.writereg32(0x58, 0xffffffff)

        # self.reg.writereg8(SYS_DELAY_US_REG, 10)
        # self.reg.writereg32(0x5c, 0)
        # self.reg.writereg32(0x50, 1)
        self.reg.writereg8(0x53, 0) # release tmp,vm,
        self.reg.writereg32(0x54, 0)
        self.reg.writereg32(0x58, 0)
        # self.reg.writereg32(0x5c, 0)

    def pre_rt_set(self):
        chip = self.cfg.chipcfg.oax4k_cfg
        outlist = [chip.out0, chip.out1, chip.out2, chip.out3]
        dplist = [chip.dp0, chip.dp1, chip.dp2, chip.dp3]
        for out in outlist:
            rtsel, yuvsel, rawsel, idcsel = out.src,out.yuv.sel,out.rawmv.sel,out.rawmv.idcsel
        byte0 = chip.out0.idcsrc | (chip.out1.idcsrc << 2) | (chip.out2.idcsrc << 4) | (chip.out3.idcsrc << 6)
        byte1 = chip.out0.src | (chip.out1.src << 2) | (chip.out2.src << 4) | (chip.out3.src << 6)
        # byte1 = chip.out0.yuv.sel | (chip.out1.yuv.sel << 2) | (chip.out2.yuv.sel << 4) | (chip.out3.yuv.sel << 6)
        byte2 = chip.out0.rawmv.sel | (chip.out1.rawmv.sel << 4)
        byte3 = chip.out2.rawmv.sel | (chip.out3.rawmv.sel << 4)
        # print("!!!!!!r32 0x{:x}".format(r32))
        self.reg.writereg8(0x34, byte0)
        self.reg.writereg8(0x35, byte1)
        self.reg.writereg8(0x36, byte2)
        self.reg.writereg8(0x37, byte3)
        byte0 = chip.out0.yuv.sel | (chip.out1.yuv.sel << 2) | (chip.out2.yuv.sel << 4) | (chip.out3.yuv.sel << 6)
        # byte0 = chip.out0.rawmv.format | (chip.out1.rawmv.format << 4)
        # byte1 = chip.out2.rawmv.format | (chip.out3.rawmv.format << 4)
        byte2 = chip.out0.yuv.format | (chip.out1.yuv.format << 4)
        byte3 = chip.out2.yuv.format | (chip.out3.yuv.format << 4)
        self.reg.writereg8(0x38, byte0)
        # self.reg.writereg8(0x39, byte1)
        self.reg.writereg8(0x3a, byte2)
        self.reg.writereg8(0x3b, byte3)
        # chip.out0.rawmv.format = chip.out0.rawmv.format if chip.out0.rawmv.format != 13 else (6 if(dplist[chip.out0.idcsrc].yuvin_mode) else 8)
        # if output format is yuv ,select 2xraw12
        # chip.out1.rawmv.format = chip.out1.rawmv.format if chip.out1.rawmv.format != 13 else (6 if(dplist[chip.out1.idcsrc].yuvin_mode) else 8)
        # chip.out2.rawmv.format = chip.out2.rawmv.format if chip.out2.rawmv.format != 13 else (6 if(dplist[chip.out2.idcsrc].yuvin_mode) else 8)
        # chip.out3.rawmv.format = chip.out3.rawmv.format if chip.out3.rawmv.format != 13 else (6 if(dplist[chip.out3.idcsrc].yuvin_mode) else 8)
        rawmv0_format = chip.out0.rawmv.format if chip.out0.rawmv.format != 13 else (6 if(dplist[chip.out0.idcsrc].yuvin_mode) else 8)
        # if output format is yuv ,select 2xraw12
        rawmv1_format = chip.out1.rawmv.format if chip.out1.rawmv.format != 13 else (6 if(dplist[chip.out1.idcsrc].yuvin_mode) else 8)
        rawmv2_format = chip.out2.rawmv.format if chip.out2.rawmv.format != 13 else (6 if(dplist[chip.out2.idcsrc].yuvin_mode) else 8)
        rawmv3_format = chip.out3.rawmv.format if chip.out3.rawmv.format != 13 else (6 if(dplist[chip.out3.idcsrc].yuvin_mode) else 8)
        # byte0 = fmt0 | fmt1
        # byte1 = fmt2 | fmt3

        byte0 = rawmv0_format | (rawmv1_format << 4)
        byte1 = rawmv2_format | (rawmv3_format << 4)
        self.reg.writereg8(0x3c, byte0)
        self.reg.writereg8(0x3d, byte1)
        # self.reg.writereg8(0x38, 0x12)
        # self.reg.writereg8(0x39, 0x34)
        # self.reg.writereg16(0x3a, 0x78)
        # self.reg.writereg32(0x80208100, 0x12345678)
        # self.reg.writereg8(0x80208105, 0x55)
        # self.reg.writereg16(0x80208106, 0x33aa)

        # print("!!!{:x} {:x}".format(self.reg.readreg8(0x38),self.reg.readreg16(0x3a)))
        isp_flag_align = chip.topctrl.ispintm_adj
        isp_test_pattern_order = chip.topctrl.isptp_seq

        byte0 = chip.in0.cben | (chip.in1.cben << 1) | (chip.in2.cben << 2) | (chip.in3.cben << 3) | (chip.out1.mtx.dup_en << 4) |\
            (chip.out3.mtx.dup_en << 5) | (isp_flag_align << 7) | (isp_test_pattern_order << 6)
        self.reg.writereg8(0x30, byte0, mask=BIT0|BIT1|BIT2|BIT3)
        byte2 = chip.out0.rawmv.idcsel | (chip.out1.rawmv.idcsel << 2) | (chip.out2.rawmv.idcsel << 4) | (chip.out3.rawmv.idcsel << 6)
        self.reg.writereg8(0x32, byte2)
        # self.reg.writereg8(0x33, byte3)
        byte0 = chip.out0.emblsrc|(chip.out1.emblsrc<<2)|(chip.out2.emblsrc<<4)|(chip.out3.emblsrc<<6)
        byte1 = 0
        byte2 = chip.out0.embl.ovipre.src| (chip.out1.embl.ovipre.src<<2) |(chip.out2.embl.ovipre.src<<4) |(chip.out3.embl.ovipre.src<<6)
        byte3 = chip.out0.embl.ovipost.src|(chip.out1.embl.ovipost.src<<2)|(chip.out2.embl.ovipost.src<<4)|(chip.out3.embl.ovipost.src<<6)
        self.reg.writereg8(0xac, byte0)
        self.reg.writereg8(0xae, byte2)
        self.reg.writereg8(0xaf, byte3)
        byte0 = chip.out0.embl.ovipre.intsel | (chip.out1.embl.ovipre.intsel<<4)
        byte1 = chip.out2.embl.ovipre.intsel | (chip.out3.embl.ovipre.intsel<<4)
        byte2 = chip.out0.embl.ovipost.intsel | (chip.out1.embl.ovipost.intsel<<4)
        byte3 = chip.out2.embl.ovipost.intsel | (chip.out3.embl.ovipost.intsel<<4)
        self.reg.writereg8(0xb0, byte0)
        self.reg.writereg8(0xb1, byte1)
        self.reg.writereg8(0xb2, byte2)
        self.reg.writereg8(0xb3, byte3)

    def _input_clk_sel(self):
        chip = self.cfg.chipcfg.oax4k_cfg
        dps = [chip.dp0,chip.dp1,chip.dp2,chip.dp3]
        dis = [chip.in0,chip.in1,chip.in2,chip.in3]

        for inport in dis:
            if inport.en:
                cbsel = inport.index %2
                cbclksel = inport.cben | (cbsel<<1)
                orgval = self.reg.readreg8(0x6e + inport.index * 4)
                newval = orgval & 0xf0 | (cbclksel<<2)
                self.reg.writereg8(0x6e + inport.index * 4, newval)
                if (inport.lane_num ==4 and(inport.index %2 ==0)):
                    orgval = self.reg.readreg8(0x6e + (inport.index + 1) * 4)
                    newval = orgval & 0xf0 | (cbclksel<<2)
                    self.reg.writereg8(0x6e + (inport.index + 1) * 4, newval)
                else:
                    if inport.lane_num > 2:
                        raise RuntimeError("lane number is too large")

        for i in range(len(dps)):
            if(dps[i].en and dps[i].input.idcen):
                di = dps[i].dibuf[0]
                feclksel = feclk_src_dict[dps[i].input.portsrc]
                # phypclksel =0  #tbd  ,
                # if(di.lane_num ==4 and(di.index %2 ==0)):
                #     cbclksel =di.cben
                #     self.reg.writereg8(0x6e+dps[i].index*4,phypclksel | (cbclksel<<2)|(feclksel<<4))
                #     self.reg.writereg8(0x6e+(dps[i].index+1)*4,phypclksel | (cbclksel<<2)|(feclksel<<4))
                # else:
                #     if(di.lane_num >2):
                #         raise RuntimeError("lane number is too large")
                #     cbclksel= di.cben | (di.cben<<1)
                # orgval=self.reg.readreg8(0x6e+dps[i].index*4)
                orgval = self.reg.readreg8(0x6e+dps[i].index*4)
                newval = orgval &0x0f |(feclksel<<4)
                self.reg.writereg8(0x6e+dps[i].index*4, newval)
                # print(dps[i].en,"!!!")
                # self.reg.writereg8(0x72,self.reg.readreg8(0x72)&0xf3)
                # self.reg.writereg8(0x76,self.reg.readreg8(0x76)&0xf3)
                # self.reg.writereg8(0x7a,self.reg.readreg8(0x7a)&0xf3)

    def _clk_mon_set(self):
        # r9cval = self.reg.readreg8(0x9c)
        # r9dval = self.reg.readreg8(0x9d)
        ctrl = self.cfg.chipcfg.oax4k_cfg.sys.ctrl
        oax4000cfg = self.cfg.chipcfg.oax4k_cfg
        # self.reg.writereg8(0x9c,r9cval|BIT4 | (ctrl.busclkinv<<7))
        self.reg.writereg8(0x9c, BIT4 | (ctrl.busclkinv << 7), mask=NBIT4&NBIT7)
        # self.reg.writereg8(0x9d,r9dval|BIT0|BIT1|BIT2)
        mrx02pclksel = mrx_phyclk_sel_dict[(oax4000cfg.in0.en, oax4000cfg.in2.en)]
        mrx13pclksel = mrx_phyclk_sel_dict[(oax4000cfg.in1.en, oax4000cfg.in3.en)]
        self.reg.writereg8(0x9d, BIT0|BIT1|BIT2|(mrx02pclksel<<4)|(mrx13pclksel<<6))
        self.reg.writereg32(0x4c, 0xffffffff)  # reset and releas clock test
        self.reg.writereg32(0x4c, 0)
        self.reg.writereg8(0x51, 0, mask=NBIT2&NBIT0)  # [0]=0,not swrst SPI SHA to support dynamic read spi flash again after spi flash boot.
        self.reg.writereg8(0xa2, 0xff)
        self.reg.writereg8(0xa4, 0xff)  # enable clock test
        self.reg.writereg8(0xa5, 0xff)
        self.reg.writereg8(0xa6, 0xff)
        r0val = self.reg.readreg8(0x00)
        # self.reg.writereg8(0x0, r0val|BIT0)
        self.reg.writereg8(0x0, BIT0, mask=NBIT0)

    def _mem_poweron(self):
        self.reg.writereg32(0x08, 0x0aa00025)
        # self.reg.writereg32(0x0c,0x0aa00aa0)
        # self.reg.writereg32(0x10,0x00ff0aa0)

    def _sys_misc(self):
        # self.reg.writereg8(0x32, 0x1)
        self.reg.writereg8(0x40, 0x00)  # enable memory check ,disable rom err check for fpga ,asic should enable

    def start(self):
        topctrl = self.cfg.chipcfg.oax4k_cfg.topctrl
        if topctrl.txmnt_en != 1:
            for clk in self.clkdst_buf:
                self.clkset_src_div_en(clk)
        self.reset_release()
        self.pre_rt_set()
        self._input_clk_sel()
        self._clk_mon_set()
        # self._mem_poweron()
        self._sys_misc()
