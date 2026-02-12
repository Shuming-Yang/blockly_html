"""
This GENS mode code which be ported from GENS source code.

Author: OVT AE
Date: 2024-11-01
"""
# WARNING
# pylint: disable=C0103, C0116, C0200, W0212, W0401, W0612, W0613, W0614, W0718
import tkinter as tk
# from tkinter import ttk
from tkinter import messagebox
import traceback
# import os
# import shutil
from Chip import OAX4K
from Case.TestCase import TestCase
from RegTable.RegGen import RegGen
from TestCfg import TestCfg
from Utility.Para import *
from Define.Para import *
import gens_globals
import draw_utils

def tests_gen(cfg):
    TS = TestCase(cfg)
    reggen = RegGen(cfg)
    chips = []
    cfg.testcase = "Default"
    for case in TS._parse_new(cfg):
        # case =TS._parse_new(cfg,sheet_name)
        if case != []:
            case.regdist = reggen._regtable_dist_gen()
            print("-------------Parse Test Case ------------------")
            chip = OAX4K(case)
            chip.start()
            chip.save(cfg.setmode, cfg.bootmode)
            chips.append(chip)
    return chips


class start_gens():
    """Gens GUI class
    """
    def embcb(self):
        if self.emb_en.get() == '1':
            gens_globals.EmbEn = '1'
            self.TopNum_entry.config(state="normal")
            self.BtmNum_entry.config(state="normal")
            self.StatNum_entry.config(state="normal")
        else:
            gens_globals.EmbEn = '0'
            self.TopNum_entry.config(state="disabled")
            self.BtmNum_entry.config(state="disabled")
            self.StatNum_entry.config(state="disabled")

    def set_format_vc(self, *args):
        try:
            imgdt = x8b_snr_input_itdtvc_dict[0, self.box.get()]
        except KeyError:
            print("Not found")
        else:
            tmp = ""
            for i in range(len(imgdt[0])):
                if i != 0:
                    tmp += " "
                tmp += hex(imgdt[0][i][0])
            self.snrformat.set(tmp)

    def rgbircb(self):
        gens_globals.rgbir_en = self.rgbir_en.get()
        if self.rgbir_en.get() == '1':
            self.exphblk_entry.config(state="normal")
            self.cam_2.config(state="disabled")
            self.cam_3.config(state="disabled")
        else:
            self.exphblk_entry.config(state="disabled")
            self.cam_2.config(state="normal")
            self.cam_3.config(state="normal")


    def button_event(self):
        # print(self.datapath_outfile.get())
        gens_globals.SEOFDLY = self.dlyText.get()
        gens_globals.FilenameOut = self.out_entry.get()
        gens_globals.raw_format = self.box.get()
        if gens_globals.raw_format == 'YUV422':
            gens_globals.output_format = 'RAW12'
        else:
            gens_globals.output_format = self.outdt.get()
        gens_globals.pixelmode = "0" if self.pixelmode.get() == 'VC ID' else "1"
        gens_globals.SNRCLK = self.snrclkbox.get()[0:-3]+"000000"
        if self.emb_en.get() == '1':
            gens_globals.EmbEn = '1'
            gens_globals.TopNum = self.TopNum_entry.get()
            gens_globals.BtmNum = self.BtmNum_entry.get()
            gens_globals.StatNum = self.StatNum_entry.get()
        else:
            gens_globals.EmbEn = '0'
            gens_globals.TopNum = '0'
            gens_globals.BtmNum = '0'
            gens_globals.StatNum = '0'
        gens_globals.snr_vsize = self.Height_entry.get()
        gens_globals.snr_hsize = self.width_entry.get()
        gens_globals.snr_hts = self.hts_entry.get()
        gens_globals.snr_vts = self.vts_entry.get()
        gens_globals.snr_mipi_lane = self.mipi_lane.get()
        gens_globals.do0clk = 100000000
        gens_globals.do1clk = 100000000
        #gens_globals.do0clk = int((int(self.MIPI0_entry.get())/4)/ int(gens_globals.snr_mipi_lane))
        #gens_globals.do1clk = int((int(self.MIPI0_entry.get())/4)/ int(gens_globals.snr_mipi_lane))
        gens_globals.sclk = self.sclk_entry.get()
        if gens_globals.do0clk < 52500000:
            if messagebox.askyesno("Warning", "dpclk > 4x doclk, try to adjust DO0 CLK to 100MHz"):
                gens_globals.do0clk = 100000000

        gens_globals.snrmnum = self.vc0.get()
        tmp = self.snrformat.get().split()
        for i in range(len(tmp)):
            gens_globals.snr_vc0type[i] = int(tmp[i], 0)

        try:
            tcfg = TestCfg()
            chips = tests_gen(tcfg)
            outputok = 1
        except RuntimeError as e:
            messagebox.showerror('GENS Error',f'GENS input error {e}')
            print(traceback.format_exc())
            outputok = 0
        except Exception:
            print(traceback.format_exc())
            outputok = 0
        finally:
            if outputok == 1:
                messagebox.showinfo('GENS Done' , 'Output file: ' + gens_globals.FilenameOut)
            self.destroy()


    def on_closing(self):
        print("close win")
        self.destroy()

    def __init__(self, frame):
        bgColor = "lightblue"
        labelframe = tk.LabelFrame(frame, bg=bgColor, width = 60, text='input')
        row_num = 0 # snr type

        row_num = 1
        tk.Label(labelframe, bg=bgColor, text='Cam Num:').grid(column=0, row=row_num)
        self.vc0 = tk.StringVar(labelframe)   # 設定文字變數，並綁定第二個 Checkbutton
        draw_utils.draw_item_Rbb(labelframe, row_num, 1, '1x Cam', 1, self.vc0, self.set_format_vc)
        draw_utils.draw_item_Rbb(labelframe, row_num, 2, '2x Cam', 2, self.vc0, self.set_format_vc)
        self.cam_2 = draw_utils.draw_item_Rbb(labelframe, row_num, 3, '3x Cam', 3, self.vc0, self.set_format_vc)
        self.cam_3 = draw_utils.draw_item_Rbb(labelframe, row_num, 4, '4x Cam', 4, self.vc0, self.set_format_vc)
        self.vc0.set(1)

        row_num = 2 # Input CLK
        self.snrclkbox = draw_utils.draw_item_Cbb(labelframe, row_num, 0 ,"XCLK:", snrclkbox_values)
        #self.MIPI0_entry  = draw_utils.draw_item_Ety(labelframe, row_num, 2 ,"MIPI Data rate:", "1600000000")
        row_num = 3 # Input format
        self.box = draw_utils.draw_item_Cbb(labelframe, row_num, 0 ,"Format Type:", list(idc_mem_hsize_div_dict.keys()))
        self.box.bind('<<ComboboxSelected>>', self.set_format_vc)
        self.box.current(14)
        self.snrformat = tk.StringVar(labelframe)
        self.snrformat.set("0x2c")
        self.snrfmt_type = tk.Entry(labelframe, width=20, textvariable=self.snrformat)
        self.snrfmt_type.grid(row=row_num, column=2, columnspan=2, sticky=tk.S + tk.E)

        row_num = 4 # snr lane
        self.mipi_lane = draw_utils.draw_item_Cbb(labelframe, row_num, 0 ,"Snr Lane Num:", ['4', '2', '1'])
        self.pixelmode = draw_utils.draw_item_Cbb(labelframe, row_num, 2 ,"Pixel mode:", ['VC ID', 'INTERLEAVE'])
        row_num = 5 # Resolution
        self.width_entry = draw_utils.draw_item_Ety(labelframe, row_num, 0 ,"Width:", gens_globals.snr_hsize)
        self.Height_entry = draw_utils.draw_item_Ety(labelframe, row_num, 2 ,"Height:", gens_globals.snr_vsize)
        row_num = 6 # VTS/HTS
        self.vts_entry = draw_utils.draw_item_Ety(labelframe, row_num, 0 ,"VTS: ", gens_globals.snr_vts)
        self.hts_entry = draw_utils.draw_item_Ety(labelframe, row_num, 2 ,"HTS: ", gens_globals.snr_hts)
        row_num = 7 # SCLK
        self.sclk_entry = draw_utils.draw_item_Ety(labelframe, row_num, 0 ,"SCLK(Hz): ", gens_globals.sclk)

        self.dlyText = tk.StringVar(labelframe)   # 設定文字變數，並綁定第二個 Checkbutton
        self.dly_btn4 = tk.Checkbutton(labelframe, text='SOF delay en', bg=bgColor,
                            variable=self.dlyText, onvalue='1', offvalue='0')
        self.dly_btn4.grid(row=row_num, column=3)
        self.dly_btn4.deselect()

        row_num = 8 # RGBIR EXP
        self.rgbir_en = tk.StringVar(labelframe)   # 設定文字變數，並綁定第二個 Checkbutton
        self.check_rgbbtn1 = tk.Checkbutton(labelframe, bg=bgColor, text='RGBIR Enable:',
                            variable=self.rgbir_en, onvalue='1', offvalue='0', command=self.rgbircb)
        self.check_rgbbtn1.grid(row=row_num, column=0, columnspan=2)
        self.check_rgbbtn1.deselect()
        tk.Label(labelframe, bg=bgColor, text='RGBIR EXP HBLK: ').grid(row=row_num, column=2, sticky=tk.E)
        self.exphblk = tk.StringVar()
        self.exphblk_entry = tk.Entry(labelframe, width=12)
        self.exphblk_entry.insert(0, gens_globals.rgbirexphblk)
        self.exphblk_entry.grid(row=row_num, column=3)
        self.exphblk_entry.config(state="disabled")

        # emb
        row_num = 9
        self.emb_en = tk.StringVar(labelframe)   # 設定文字變數，並綁定第二個 Checkbutton
        self.check_embbtn1 = tk.Checkbutton(labelframe, bg=bgColor, text='Embedded line Enable:',
                            variable=self.emb_en, onvalue='1', offvalue='0', command=self.embcb)
        self.check_embbtn1.grid(row=row_num, column=0, columnspan=2)
        self.check_embbtn1.select()
        row_num = 10 # Top emb
        tk.Label(labelframe, bg=bgColor, text='Top Num:').grid(row=row_num, column=0, sticky=tk.E)
        self.TopNum = tk.StringVar()
        self.TopNum_entry = tk.Entry(labelframe, width=10)
        self.TopNum_entry.insert(0, gens_globals.TopNum)
        self.TopNum_entry.grid(row=row_num, column=1, sticky=tk.E)
        row_num = 11 # btm emb
        tk.Label(labelframe, bg=bgColor, text='Btm Num:').grid(row=row_num, column=0, sticky=tk.E)
        self.BtmNum = tk.StringVar()
        self.BtmNum_entry = tk.Entry(labelframe, width=10)
        self.BtmNum_entry.insert(0, gens_globals.BtmNum)
        self.BtmNum_entry.grid(row=row_num, column=1, sticky=tk.E)
        row_num = 12 # stat emb
        tk.Label(labelframe, bg=bgColor, text='Stat Num:').grid(row=row_num, column=0, sticky=tk.E)
        self.StatNum = tk.StringVar()
        self.StatNum_entry = tk.Entry(labelframe, width=10)
        self.StatNum_entry.insert(0, gens_globals.StatNum)
        self.StatNum_entry.grid(row=row_num, column=1, sticky=tk.E)
        labelframe.grid(column=0, row=0, padx=1, pady=1, sticky=tk.S + tk.N + tk.W)
        # -----Output----
        Outframe = tk.LabelFrame(frame, bg=bgColor, width = 60, text='Output')

        row_num = 0
        self.outdt = draw_utils.draw_item_Cbb(Outframe, row_num, 0 ,"Data format:", ['RAW12', 'YUV422-8'])
        row_num = 1
        tk.Label(Outframe, bg=bgColor, text='Output file:').grid(row=row_num, column=0, sticky=tk.E)
        self.datapath_outfile = tk.StringVar()
        self.out_entry = tk.Entry(Outframe, width=53)
        self.out_entry.insert(0, gens_globals.FilenameOut)
        self.out_entry.grid(row=row_num, column=1, columnspan=2, sticky=tk.E)
        row_num = 2
        tk.Button(Outframe, text="Start Gens Datapath", width=45,
                    command=self.button_event).grid(row=row_num, column=0, columnspan=4)

        Outframe.grid(column=0, row=1, padx=1, pady=1, sticky=tk.S + tk.N + tk.W)

    def destroy(self):
        pass


#if __name__ == "__main__":
#    start_gens()
