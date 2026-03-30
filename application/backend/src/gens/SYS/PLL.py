"""
This GENS mode code which be ported from GENS source code.
@@OAX4K dist define

Author: OVT AE
Date: 2024-11-05
"""
# WARNING
# pylint: disable=C0103, C0115, C0116, C0412, R1720, R0205, R1716, W0231, W0401, W0611, W0614
from Utility.Reg import REG8
from Utility.Reg import REG16
from Utility.Reg import REG32
from Utility.Entity import Entity
from Utility.Para import *
from Define.Struct import SYSTEM_PLL_CFG
from Utility.Others import get_class_var
from Utility.Reg import REGOBJ
from RegTable.Regdefdist import *
from Define.Para import *


class OAX4K_MIPI_PLL_CFG(object):
    def __init__(self, _chipcfg):
        self.cntstep = 0
        self.precision = 0
        self.cp = 0
        self.lpf = 0
        self.loopdiv = 0
        self.outclk_prediv = 0
        self.dsm = 0
        self.cnt_ref = 0
        self.cntck = 0
        self.div_clk0 = 0
        self.div_clk1 = 0
        self.prediv = 0
        self.div_phy = 0
        self.outprediv_byp = 0
        self.clk0 = 0
        self.clk1 = 0
        self.phyclk = 0


class OAX4K_SYS_PLL_CFG(object):
    def __init__(self, _chipcfg):
        self.cp = 0
        self.lpf = 0
        self.cnt_ref = 0
        self.precision = 0
        self.prediv = 0
        self.loopdiv = 0
        self.div_clk0 = 0
        self.div_clk1 = 0
        self.clk0 = 0
        self.clk1 = 0


class PLL_CFG(object):
    def __init__(self, chipcfg):
        self.mpll0 = OAX4K_MIPI_PLL_CFG(chipcfg)
        self.mpll1 = OAX4K_MIPI_PLL_CFG(chipcfg)
        self.spll = OAX4K_SYS_PLL_CFG(chipcfg)
        self.refclk = 0

    def config(self):
        pass


class PLL_REG(REGOBJ):
    def __init__(self, cfg, _uid=0):
        self.base = self.get_baseaddr('ANALOG', define_dist, 0)
        # print(" SC {:x} {:x}".format(uid,base))
        self.regtable = cfg.regtable
        self.objr = []


class PLL(Entity):
    """description of class"""
    def __init__(self, chipcfg):
        self.cfg = PLL_CFG(chipcfg)
        self.reg = PLL_REG(chipcfg)
        self.setbuf = []
        self.pll_init(chipcfg)

    def pll_init(self, chipcfg):
        syscfg = chipcfg.oax4k_cfg.sys
        self.cfg.refclk = syscfg.pll.xclk
        self.cfg.mpll0.phyclk = syscfg.clkt.do0clk * 16
        self.cfg.mpll0.clk0 = syscfg.pll.tx0_clk0
        self.cfg.mpll0.clk1 = syscfg.pll.tx0_clk1
        self.cfg.mpll1.phyclk = syscfg.clkt.do1clk * 16
        self.cfg.mpll1.clk0 = syscfg.pll.tx1_clk0
        self.cfg.mpll1.clk1 = syscfg.pll.tx1_clk1
        self.cfg.spll.clk0 = syscfg.pll.sys_clk0
        self.cfg.spll.clk1 = syscfg.pll.sys_clk1
        self.pll_init_mipi(chipcfg)
        self.pll_init_sys(chipcfg)

    def pll_init_mipi(self, _chipcfg):
        self.mipipll_autocfg(self.cfg.mpll0, 0)
        self.mipipll_autocfg(self.cfg.mpll1, 1)

    def pll_init_sys(self, _chipcfg):
        self.syspll_autocfg(self.cfg.spll)

    def clkx_div_gen(self, vco, clk):
        clk_div = vco // clk
        if clk_div <= 16:
            plldiv = clk_div - 1
        elif clk_div > 16 and clk_div <= 32:
            if clk_div % 2 == 0:
                plldiv = clk_div // 2 - 1 + 16
            else:
                raise RuntimeError(f"can't find fitable VCO for {vco} {clk}")
        else:
            raise RuntimeError(f"can't find fitable clk_div for {vco} {clk}")
        return plldiv

    def pll_prediv_loopdiv_gen(self, fvco, refclk):
        # for prediv in range (8):
        for prediv in [2,3,0,1,4,5,6,7]:
            predivclk = int(refclk / (prediv + 1))
            if predivclk >= 4000000 and predivclk <= 24000000:
                if fvco % predivclk == 0:
                    loopdiv = int(fvco / predivclk)
                    return (1, prediv, loopdiv)
        return (0,0,0)

    def mipipll_autocfg(self, pll, index=0):
        # pll = self.cfg.mpll0
        refclk = self.cfg.refclk
        phyclk = pll.phyclk
        pll.div_phy = 0
        cal_success = 0

        for  div_phy in range(15):
            for  outdiv in [1, 2, 4]:  # use default setting , outdiv =0
                fvco = phyclk * (1 + div_phy) * outdiv if(div_phy) else phyclk
                pll.div_phy = div_phy
                pll.outclk_prediv = outdiv
                if (fvco >= 1300000000 and fvco <= 2600000000 ):  # tbd
                    clk0 = pll.clk0
                    clk1 = pll.clk1
                    # print(phyclk, clk0, clk1, fvco)
                    if (fvco % clk0 or fvco % clk1):
                        continue
                        # raise RuntimeError("can't find fitable VCO for {} {} {} {}".format(fvco, clk0, clk1, refclk))
                    else:
                        pll.div_clk0 = self.clkx_div_gen(fvco // outdiv,clk0)
                        pll.div_clk1 = self.clkx_div_gen(fvco // outdiv,clk1)
                        cal_success, pll.prediv, pll.loopdiv = self.pll_prediv_loopdiv_gen(fvco, refclk)
                        if cal_success:
                            break
            if cal_success:
                break

        if cal_success == 0:
            raise RuntimeError(f"can't find fitable VCO for {fvco} {clk0} {clk1} {refclk}")
        else:
            print(f"mipi pll{index} auto gen success fvco {fvco} prediv {pll.prediv} loopdiv {pll.loopdiv} c0div {pll.div_clk0} c1div {pll.div_clk1} outprediv{pll.outclk_prediv} phydiv{pll.div_phy}")

    def syspll_autocfg(self, pll):
        # pll = self.cfg.spll
        refclk = self.cfg.refclk

        def min_common_mul(a, b):
            m = min(a, b)
            n = max(a, b)
            while m != 0:
                r = n % m
                n = m
                m = r
            return a*b//n

        cal_success = 0
        for outdiv in range(16):
            fvco = min_common_mul(pll.clk0, pll.clk1) * (outdiv + 1)
            if (fvco >= 1000000000 and fvco <= 2000000000):
                clk0 = pll.clk0
                clk1 = pll.clk1
                if (fvco % clk0 or fvco % clk1):
                    continue
                else:
                    pll.div_clk0 = self.clkx_div_gen(fvco, clk0)
                    pll.div_clk1 = self.clkx_div_gen(fvco, clk1)
                    cal_success, pll.prediv, pll.loopdiv = self.pll_prediv_loopdiv_gen(fvco, refclk)
                    if cal_success:
                        break

        if cal_success == 0:
            raise RuntimeError(f"can't find fitable VCO for {fvco} {clk0} {clk1} {refclk}")
        else:
            print(f"pll auto gen success fvco {fvco} prediv {pll.prediv} loopdiv {pll.loopdiv} c0div {pll.div_clk0} c1div {pll.div_clk1}")

    def start(self):
        tx0 = self.cfg.mpll0
        tx1 = self.cfg.mpll1
        sys = self.cfg.spll
        tx_outclk_prediv_valmap = {
            1: (1, 1),
            2: (0, 1),  # 1,0 also ok
            4: (0, 0),
        }

        tx0_prediv_h, tx0_prediv_l = tx_outclk_prediv_valmap[tx0.outclk_prediv]
        tx1_prediv_h, tx1_prediv_l = tx_outclk_prediv_valmap[tx1.outclk_prediv]
        r64 = (tx0_prediv_l << 0)| (tx0_prediv_h << 2) | (tx1_prediv_l << 4)| (tx1_prediv_h << 6)
        r74 = tx0.div_clk0 | (tx0.div_clk1 << 8) | (tx0.loopdiv << 16) | (tx0.prediv << 28)
        r80 = tx1.div_clk0 | (tx1.div_clk1 << 8) | (tx1.loopdiv << 16) | (tx1.prediv << 28)
        r6c = sys.div_clk0 | (sys.div_clk1 << 8) | (sys.loopdiv << 16) | (sys.prediv << 28)
        self.reg.writereg8(0x8020805e, BIT0 | BIT1 | BIT2, mask=BIT3|BIT4|BIT5|BIT6|BIT7)
        # self.reg.writereg8(SYS_DELAY_US_REG, 10)
        self.reg.writereg8(0x64, r64, mask=BIT1|BIT3|BIT5|BIT7)
        self.reg.writereg8(0x73, tx0.div_phy)
        self.reg.writereg32(0x6c, r6c, save_force=1)
        self.reg.writereg32(0x74, r74)
        self.reg.writereg32(0x80, r80)
        self.reg.writereg8(0x7f, tx1.div_phy)
        self.reg.writereg8(0x04, BIT4 | BIT5 | BIT6, mask=0X8f)
        self.reg.writereg8(0x04, 0, mask=0X8f)
        self.reg.writereg8(0x8020805e, 0, mask=BIT3|BIT4|BIT5|BIT6|BIT7)
