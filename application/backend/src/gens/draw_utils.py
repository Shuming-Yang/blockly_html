# WARNING
# pylint: disable=C0103, C0114, C0116, W0611
import tkinter as tk
from tkinter import ttk
import gens_globals
backcolor = "lightblue",

def draw_item_Ety(frame, nrom, ncolumn, textin, import_text):
    ele = tk.Label(frame, bg=backcolor, text=textin)
    ele.grid(row=nrom, column=ncolumn)
    ele = tk.Entry(frame, width=12)
    ele.insert(0, import_text)
    ele.grid(row=nrom, column= ncolumn+1)
    return ele

def draw_item_Cbb(frame, nrom, ncolumn, textin, import_data):
    tk.Label(frame, bg=backcolor, text=textin).grid(row=nrom, column=ncolumn)
    ele = ttk.Combobox(frame, width=12, values=import_data)
    ele.current(0)
    ele.grid(row=nrom, column=ncolumn+1)
    return ele


def draw_item_Rbb(frame, nrom, ncolumn, textin, val, variablein, Cmdin):
    ele = tk.Radiobutton(frame,
                         command=Cmdin,
                         font=("Consolas", 10),
                         anchor='w',
                         width=6,
                         text=textin,
                         value=val,
                         bg=backcolor,
                         variable=variablein)
    ele.grid(column=ncolumn, row=nrom)
    return ele
