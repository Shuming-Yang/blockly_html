"""
This GENS mode code which be ported from GENS source code.

Author: OVT AE
Date: 2024-11-01
"""
# WARNING
# pylint: disable=C0103
log_print_info_dict = {
    0: (__file__),
    1: (__name__),
}

bus_endian_dict = {
    0: "Little_Endian",
    1: "Big_Endian",
}

SYS_DELAY_MS_REG = 0x802080d0
SYS_DELAY_US_REG = 0x802080d4

# sensor_input_format_type_dict ={
#     "HDR4_COMB":0,
#     "HDR4_COMB+SPD":1,
#     # "HDR4_COMB+LFM":2,
#     "HDR3_COMB":2,
#     "HDR3_COMB+SPD":3,
#     # "HDR3_COMB+LFM":5,
#     "HDR4_4XNb":4,
#     "SINGLE_EXPO_HDR":5,
#     "DUAL_EXPO_HDR":6,
#     "TRIPLE_EXPO_HDR":7,
#     "LINEAR":8,
#     "SPD":9,
#     "LFM":10,
#     }


sensor_input_format_type_dict = {
    "HDR4_DCGSVSRAW": 0x00,    # x8b,X3C, 4x10 RAW
    "HDR4_DCGSVSCOMB": 0x01,  # X8AB,X3C,X4A  PWL12/16/20/24  or SPD
    "HDR4_DCGSVSCOMB_SPD": 0x02,  # X8B/HDR3+SPD

    "HDR3_DCGVSRAW": 0x10,  # 2775/2778/9716/x3a,   3X12,3x10
    "HDR3_DCGVSCOMB": 0x11,  # X8AB,X3C,X4A PWL12/PWL16/PWL20/RAW24
    "HDR3_DCGVSCOMB_SPD": 0x12,  # X3C,X8B/HDR3 pwl16/12+SPD
    "HDR3_DCGCOMB_VSRAW": 0x13,  # 2775/2778/9716/x3a 16+12,12+12
    "HDR3_DCGVSPWLRAW": 0x14,  # 2775 3X10 COMP

    "HDR3_LSVSRAW": 0x20,  # 10640,X1A,X2A,X1D   3x10/12 RAW, X1D,HCG+SPD+VS
    "HDR3_SLORVSRAW": 0x21,  # 2x11
    "HDR3_LSVSCOMB": 0x22,  # 10640,X1A,X2A   RAW20,RAW16,RAW12
    "HDR3_LMSRAW": 0x23,  # OV4689 3x10 L,M,S

    "HDR3_DCGSPDRAW": 0x30,  # x1d 3x10 ,triple   X1D,HCG+LCG+SPD
    "HDR3_DCGSPDCOMB": 0x31,  # X1D ,PWL12

    "HDR2_DCGRAW": 0x40,  # 2775/2778/9716/x3a 2x12,2X10
    "HDR2_DCGCOMB": 0x41,  # 2775/2778/9716/x3a DCG16,DCG12
    "HDR2_HORLVSRAW": 0X42,  # pwl10+10
    "HDR2_LMRAW": 0X43,  # 4689 2XRAW10 L+M

    # "LINEAR_RAW":0x50,  # 2312/10640/2775/ linea raw or LCG,LFM,SPD,YUV\
    "HDR1_LINEARRAW": 0x50,  # 2312/10640/2775/ linea raw or LCG,LFM,SPD,YUV\
    "HDR1_PWLRAW": 0x51,  # PWL RAW \

    "BYP_YUV": 0x60,  # X1E YUV422 bypassin
}

sensor_input_format_type_top_dict = {
    "HDR4_DCGSVS": 0,  # x8b,X3C, 4x10 RAW
    "HDR3_DCGVS": 1,  # 2775/2778/9716/x3a,   3X12,3x10 comp
    "HDR3_LSVS": 2,  # 10640,X1A,X2A,X1D   3x10/12 RAW,2x11, X1D,HCG+SPD+VS
    "HDR3_DCGSPD": 3,  # x1d 3x10 ,triple   X1D,HCG+LCG+SPD
    "HDR2_DCG": 4,  # 2775/2778/9716/x3a 2x12,2X10,4689
    "HDR1_RAW": 5,  # 2312/10640/2775/ linea raw or LCG
}

sensor_expo_num_dict = {
    "HDR4_DCGSVS": 4,  # x8b,X3C, 4x10 RAW
    "HDR3_DCGVS": 3,  # 2775/2778/9716/x3a,   3X12,3x10 comp
    "HDR3_LSVS": 3,  # 10640,X1A,X2A,X1D   3x10/12 RAW,2x11, X1D,HCG+SPD+VS
    "HDR3_DCGSPD": 3,  # x1d 3x10 ,triple   X1D,HCG+LCG+SPD
    "HDR2_DCG": 2,  # 2775/2778/9716/x3a 2x12,2X10
    "HDR1_RAW": 1,  # 2312/10640/2775/ linea raw or LCG
}

sensor_input_format_name_dict = {
    "3XRAW12": 0,
    "3XRAW10": 1,
    "2XRAW12": 2,
    "2XRAW11": 3,
    "YUV422": 4,
    "RAW12": 5,
    "12+12RAW": 6,
    "16+12RAW": 7,
    "RAW24": 8,
    "RAW20": 9,
    "RAW16": 10,
    "RAW14": 11,
    "2XRAW10": 12,
    "RAW10": 13,
    "4XRAW12": 14,
    "4XRAW10": 15,
}

input_format_dict = {
    # "3XRAW12":0,
    # "3XRAW10":1,
    # "2XRAW12":2,
    # "2XRAW11":3,
    # "YUV422":4,
    # "RAW12":5,
    # "12+12RAW":6,
    # "16+12RAW":7,
    # "RAW24":8,
    # "RAW20":9,
    # "RAW16":10,
    # "RAW14":11,
    # "2XRAW10":12,
    # "RAW10":13,
    # "4XRAW12":14,
    # "4XRAW10":15,
    "3X12RAW": 0,
    "3X10RAW": 1,
    "2X12RAW": 2,
    "2X11RAW": 3,
    "YUV422": 4,
    "RAW12": 5,
    "LFM_RAW8": 0x45,  # LFM case, receive as RAW12
    "COM12": 0x85,
    "12+12RAW": 6,
    "10+10RAW": 6,
    "16+12RAW": 7,
    "COM24": 8,
    "COM20": 9,
    "COM16": 10,
    "COM14": 11,
    "2X10RAW": 12,
    "2X10RAWCB": 12,
    # "COM12": 12,
    "4X12RAW": 14,
    "4X10RAW": 15,
    "RAW10": 0x0d,
    "SPD_RAW10": 0x8d,
    "12+SPD10": 0x86,
    "16+SPD10": 0x87,
    "24+LFM": 0x88
}

input_format_vldbit_dict_new = {
    "3X12RAW": 48,
    "3X10RAW": 40,
    "2X12RAW": 48,
    "2X11RAW": 48,
    "2X10RAW": 40,  # tbd for rgbir debug only,actual should 40
    "2X10RAWCB": 48,  # tbd for rgbir debug only,actual should 40
    "YUV422": 64,
    "RAW12": 48,
    "12+12RAW": 48,
    "16+12RAW": 48,
    "12+SPD10": 48,
    "16+SPD10": 48,
    "24+LFM": 96,
    "COM24": 96,
    "COM20": 80,
    "COM16": 64,
    "COM14": 56,
    "COM12": 48,
    "4X12RAW": 48,
    "4X10RAW": 40,
    "RAW10": 40,
    "RAW8": 32,
    "3XRAW12": 48,
    "3XRAW10": 40,
    "2XRAW12": 48,
    "2XRAW11": 48,
    "RAW24": 96,
    "RAW20": 80,
    "RAW16": 64,
    "RAW14": 56,
    "2XRAW10": 40,
    "4XRAW12": 48,
    "4XRAW10": 40,
}

input_format_vldbit_dict_new96 = {
    "3X12RAW": 96,
    "3X10RAW": 80,
    "2X12RAW": 96,
    "2X11RAW": 96,
    "2X10RAW": 80,  # tbd for rgbir debug only,actual should 40
    "2X10RAWCB": 96,  # tbd for rgbir debug only,actual should 40
    "YUV422": 64,
    "RAW12": 96,
    "12+12RAW": 96,
    "16+12RAW": 64,
    "12+SPD10": 80,
    "16+SPD10": 64,
    "24+LFM": 96,
    "COM24": 96,
    "COM20": 80,
    "COM16": 64,
    "COM14": 56,
    "COM12": 96,
    "4X12RAW": 96,
    "4X10RAW": 80,
    "RAW10": 80,
    "SPD_RAW10": 80,
    "RAW8": 64,
    "LFM_RAW8": 64,
    "3XRAW12": 96,
    "3XRAW10": 80,
    "2XRAW12": 96,
    "2XRAW11": 96,
    "RAW24": 96,
    "RAW20": 80,
    "RAW16": 64,
    "RAW14": 56,
    "2XRAW10": 80,
    "4XRAW12": 96,
    "4XRAW10": 00,
}

precb_format_vcdt_dict = {
    "3X12RAW": (3, [0x2c, 0x2c, 0x2c], [0, 1, 2], 1, 3),
    "3X10RAW": (3, [0x2b, 0x2b, 0x2b], [0, 1, 2], 1, 3),
    "2X12RAW": (2, [0x2c, 0x2c], [0, 1], 0, 2),
    "2X10RAW": (2, [0x2b, 0x2b], [0, 1], 0, 2),  # tmp, for colorbar rgbir debug only ,actual should 2b
    "2X10RAWCB": (2, [0x2c, 0x2c], [0, 1], 0, 2),  # tmp, for colorbar rgbir debug only ,actual should 2b
    "2X11RAW": (2, [0x2c, 0x2c], [0, 1], 0, 3),
    "YUV422": (1, [0x1e], [0], 0, 1),
    "RAW12": (1, [0x2c], [0], 0, 1),
    "12+12RAW": (2, [0x2c, 0x2c], [0, 1], 1, 3),
    "12+SPD10": (2, [0x2c, 0x2c], [0, 1], 1, 3),
    "16+12RAW": (2, [0x2e, 0x2c], [0, 1], 1, 3),
    "COM24": (1, [0x27], [0], 0, 4),
    "COM20": (1, [0x2f], [0], 0, 4),
    "COM16": (1, [0x2e], [0], 0, 4),
    "COM14": (1, [0x2d], [0], 0, 4),
    "COM12": (1, [0x2c], [0], 0, 4),
    "4X12RAW": (4, [0x2c, 0x2c, 0x2c, 0x2c], [0, 1, 2, 3], 0, 4),
    "4X10RAW": (4, [0x2b, 0x2b, 0x2b, 0x2b], [0, 1, 2, 3], 0, 4),
    "RAW10": (1, [0x2b], [0], 0, 1),
    "LFM_RAW8": (1, [0x2a], [0], 0, 1),
    "SPD_RAW10": (1, [0x2b], [0], 0, 1),
}

image_mode_dict = {
    "VCID": 0,
    "PIXINTL": 1,
    "LINEINTL": 2,
}

fwpara_base_dict = {  # Tmp ,for FPGA sensor setting save
    0: 0x801C5C00,
    1: 0x801C5C00,
}
# serdes_cfg_base_dict = {
#     0:0x801db000,
#     1:0x801db040,
#     2:0x801db080,
#     3:0x801db0c0,
# }


output_yuv_format_dict = {
    ("YUV422-8", 1): 0,
    ("YUV422-10", 1): 1,
    ("YUV422-12", 1): 2,
    ("RGB565", 1): 3,
    ("RGB888", 1): 4,
    ("YUV420-8", 1): 5,
    ("YUV420-10", 1): 6,
    ("YUV420-12", 1): 7,
}
embl_chn_dist = {1: 'YUV', 0: 'RAWMV'}
yuv_sel_dist = {0: 'ISPHV', 1: 'PGEN0', 2: 'ISPMV'}
ispyuv_sel_dist = {0: 0, 1: 0, 2: 0, 3: 2, 4: 1, 5: 3, 6: 3, 7: 3}
raw_sel_dist = {0: 'IDC', 1: 'TXLP', 2: 'PGEN1', 3: 'ISPRAW', 4: 'ISPMV'}
output_raw_format_dict = {
    ("RAW12L", 1): 0,
    ("RAW12S", 1): 1,
    ("RAW12V", 1): 2,
    ("RAW14", 1): 3,
    ("RAW16", 1): 4,
    ("RAW20", 1): 5,
    ("RAW24", 1): 6,
    ("RAW2X11", 2): 7,
    ("RAW2X12", 2): 8,
    ("RAW3X10", 3): 9,
    ("RAW3X12", 3): 10,
    ("RAW12+12", 2): 11,
    ("RAW12M", 1): 12,
    ("YUV422-12", 1): 13,
    ("RAW10", 1): 14,
}
mipitx_datatype_dict = {
    "RAW12L": 0x2c,
    "RAW12S": 0x2c,
    "RAW12V": 0x2c,
    "RAW12M": 0x2c,
    "RAW10": 0x2b,
    "RAW14": 0x2d,
    "RAW16": 0x2e,
    "RAW20": 0x2f,
    "RAW24": 0x27,
    "RAW2X11": 0x2c,
    "RAW2X12": 0x2c,
    "RAW3X10": 0x2b,
    "RAW3X12": 0x2c,
    "RAW12+12": 0x2c,
    "YUV422-8": 0x1e,
    "YUV422-10": 0x1f,
    "YUV422-12": 0x1b,
    "RGB565": 0x22,
    "RGB888": 0x24,
    "YUV420-8": 0x18,  # tbd
    "YUV420-10": 0x19,
    "YUV420-12": 0x31,  # from 31 to 1b, gaia don't support
}
rt_byterate_dict = {
    "RAW12L": (1, 12),
    "RAW12S": (1, 12),
    "RAW12V": (1, 12),
    "RAW12M": (1, 12),
    "RAW14": (2, 14),
    "RAW16": (2, 8),
    "RAW10": (1, 10),
    "RAW20": (2, 10),
    "RAW24": (2, 12),
    "RAW2X11": (2, 12),
    "RAW2X12": (2, 12),
    "RAW3X10": (3, 10),
    "RAW3X12": (3, 12),
    "RAW12+12": (2, 12),
    "YUV422-8": (2, 8),
    "YUV422-10": (2, 10),
    "YUV422-12": (2, 12),
    "RGB565": (2, 8),
    "RGB888": (2, 8),
    "YUV420-8": (2, 8),  # tbd
    "YUV420-10": (2, 10),
    "YUV420-12": (2, 12),
}

colorbar_wordcnt_dict = {
    "3X12RAW": (12, 3),
    "3X10RAW": (10, 3),
    "2X12RAW": (12, 2),
    "2X11RAW": (12, 2),
    "2X10RAW": (10, 2),  # tbd for rgbir debug only,actual should 10
    "2X10RAWCB": (12, 2),  # tbd for rgbir debug only,actual should 10
    "YUV422": (16, 1),
    "RAW12": (12, 1),
    "RAW10": (10, 1),
    "12+12RAW": (12, 2),
    "16+12RAW": (12, 2),  # tbd
    "24+LFM": (24, 1),
    "COM24": (24, 1),
    "COM20": (20, 1),
    "COM16": (16, 1),
    "COM14": (14, 1),
    "COM12": (12, 1),
    "4X10RAW": (10, 4),
    "4X12RAW": (12, 4),
    "SPD_RAW10": (10, 1),
    "LFM_RAW8": (8, 1),
}


'''
raw8/10/12, yuv422 take_byte = 2
raw14 take_byte = 0x6
16/20/24 take_byte = 0xa
'''
snr_embl_takebyte_dict = {
    "3X12RAW": 2,
    "3X10RAW": 2,
    "2X12RAW": 2,
    "2X11RAW": 2,
    "RAW3X12": 2,
    # "RAW3X10": 2,
    # "RAW2X12": 2,
    # "RAW2X11": 2,
    "YUV422-8": 2,
    "YUV422-10": 2,
    "YUV422-12": 2,
    "RAW12L": 2,
    "RAW12S": 2,
    "RAW12VS": 2,
    "RAW12M": 2,
    "RAW10": 2,
    "12+12RAW": 2,
    "16+12RAW": 2,
    "RAW12+12": 2,
    "RAW16+12": 2,
    "RAW24": 10,
    "RAW20": 10,
    "RAW16": 10,
    "RAW14": 6,
    "RAW12": 2,
    "RAW4X10": 2,
}

# image_mode_dict ={
#    "VCID":0,
#    "PIXINTL":1,
#    "LINEINTL":2,
# }

snr_input_itdtvc_dict = {
    (0, "3X12RAW"): ([[0x2c], [0x2c], [0x2c]], ([0x2c], [0x2c], [0x2c]), (0, 1, 2)),
    (1, "3X12RAW"): ([[0x2c]], [[0x2c]], (0)),
    (0, "3X10RAW"): (([0x2b], [0x2b], [0x2b]), ([0x2b], [0x2b], [0x2b]), (0, 1, 2)),
    (1, "3X10RAW"): ([[0x2b]], [[0x2b]], (0)),
    (0, "2X12RAW"): (([0x2c], [0x2c]), ([0x2c], [0x2c]), (0, 1)),
    (0, "2X10RAW"): (([0x2b], [0x2b]), ([0x2b], [0x2b]), (0, 1)),
    (1, "2X12RAW"): ([[0x2c]], [[0x2c]], (0)),
    (0, "2X11RAW"): (([0x2c], [0x2c]), ([0x2c], [0x2c]), (0, 1)),
    (1, "2X11RAW"): ([[0x2c]], [[0x2c]], (0)),
    (0, "YUV422"): ([[0x1e]], [[0x1e]], (0)),
    (1, "YUV422"): ([[0x1e]], [[0x1e]], (0)),
    (0, "RAW12"): ([[0x2c]], [[0x2c]], (0)),
    (1, "RAW12"): ([[0x2c]], [[0x2c]], (0)),
    (0, "RAW10"): ([[0x2b]], [[0x2b]], (0)),
    (0, "12+12RAW"): (([0x2c], [0x2c]), ([0x2c], [0x2c]), (0, 1)),
    (0, "10+10RAW"): (([0x2b], [0x2b]), ([0x2b], [0x2b]), (0, 1)),
    (1, "12+12RAW"): ([[0x2c]], [[0x2c]], (0)),
    (0, "16+12RAW"): (([0x2e], [0x2c]), ([0x2e], [0x2c]), (0, 1)),
    (0, "COM24"): ([[0x27]], [[0x27]], (0)),
    (0, "COM20"): ([[0x2f]], [[0x2f]], (0)),
    (0, "COM16"): ([[0x2e]], [[0x2e]], (0)),
    (0, "COM14"): ([[0x2d]], [[0x2d]], (0)),
    (0, "COM12"): ([[0x2c]], [[0x2c]], (0)),
    (1, "COM12"): ([[0x2c]], [[0x2c]], (0)),
    (0, "4X10RAW"): (([0x2b], [0x2b], [0x2b], [0x2b]), ([0x2b], [0x2b], [0x2b], [0x2b]), (0, 1, 2, 3)),
    (1, "4X10RAW"): (([0x2b], [0x2b], [0x2b], [0x2b]), ([0x2b], [0x2b], [0x2b], [0x2b]), (0)),
}

x8b_snr_input_itdtvc_dict = {
    # (img_mode, format): ([id0, id1, id2], [dt0, dt1, dt2], [vcid0, vcid1, vcid2])
    (0, "3X12RAW"): ([[0x2c], [0x2c], [0x2c]], ([0x2c], [0x2c], [0x2c]), (0, 1, 2)),
    (1, "3X12RAW"): ([[0x2c]], [[0x2c]], (0)),
    (0, "3X10RAW"): (([0x2b], [0x2b], [0x2b]), ([0x2b], [0x2b], [0x2b]), (0, 1, 2)),
    (1, "3X10RAW"): ([[0x2b]], [[0x2b]], (0)),
    (0, "2X12RAW"): (([0x2c], [0x2c]), ([0x2c], [0x2c]), (0, 1)),
    (1, "2X12RAW"): ([[0x2c]], [[0x2c]], (0)),
    (0, "2X11RAW"): (([0x2c], [0x2c]), ([0x2c], [0x2c]), (0, 1)),
    (1, "2X11RAW"): ([[0x2c]], [[0x2c]], (0)),
    (0, "YUV422"): ([[0x1e]], [[0x1e]], (0)),
    (1, "YUV422"): ([[0x1e]], [[0x1e]], (0)),
    (0, "RAW12"): ([[0x2c]], [[0x2c]], (0)),
    (1, "RAW12"): ([[0x2c]], [[0x2c]], (0)),
    (0, "RAW10"): ([[0x2b]], [[0x2b]], (0)),
    (0, "12+12RAW"): (([0x2c], [0x2c]), ([0x2c], [0x2c]), (0, 1)),
    (0, "12+SPD10"): (([0x2c], [0x2b]), ([0x2c], [0x2b]), (0, 1)),
    (0, "16+SPD10"): (([0x2a], [0x2b]), ([0x2e], [0x2b]), (0, 1)),
    (1, "12+12RAW"): ([[0x2c]], [[0x2c]], (0)),
    (0, "16+12RAW"): (([0x2e], [0x2c]), ([0x2e], [0x2c]), (0, 1)),
    (0, "24+LFM"): ([[0x2c], [0x2a]], [[0x27], [0x2a]], (0, 1)),
    (0, "COM24"): ([[0x2c]], [[0x27]], (0)),
    (0, "COM20"): ([[0x2b]], [[0x2f]], (0)),
    (0, "COM16"): ([[0x2a]], [[0x2e]], (0)),
    (0, "COM14"): ([[0x2d]], [[0x2d]], (0)),
    (0, "COM12"): ([[0x2c]], [[0x2c]], (0)),
    (0, "4X10RAW"): (([0x2b], [0x2b], [0x2b], [0x2b]), ([0x2b], [0x2b], [0x2b], [0x2b]), (0, 1, 2, 3)),
    (1, "4X10RAW"): (([0x2b], [0x2b], [0x2b], [0x2b]), ([0x2b], [0x2b], [0x2b], [0x2b]), (0)),
    (0, "4X12RAW"): (([0x2c], [0x2c], [0x2c], [0x2c]), ([0x2c], [0x2c], [0x2c], [0x2c]), (0, 1, 2, 3)),
}

x8b_eco_snr_input_itdtvc_dict = {
    # (img_mode, format): ([id0, id1, id2], [dt0, dt1, dt2], [vcid0, vcid1, vcid2])
    (0, "3X12RAW"): ([[0x2c], [0x2c], [0x2c]], ([0x2c], [0x2c], [0x2c]), (0, 1, 2)),
    (1, "3X12RAW"): ([[0x2c]], [[0x2c]], (0)),
    (0, "3X10RAW"): (([0x2b], [0x2b], [0x2b]), ([0x2b], [0x2b], [0x2b]), (0, 1, 2)),
    (1, "3X10RAW"): ([[0x2b]], [[0x2b]], (0)),
    (0, "2X12RAW"): (([0x2c], [0x2c]), ([0x2c], [0x2c]), (0, 1)),
    (1, "2X12RAW"): ([[0x2c]], [[0x2c]], (0)),
    (0, "2X11RAW"): (([0x2c], [0x2c]), ([0x2c], [0x2c]), (0, 1)),
    (1, "2X11RAW"): ([[0x2c]], [[0x2c]], (0)),
    (0, "YUV422"): ([[0x1e]], [[0x1e]], (0)),
    (1, "YUV422"): ([[0x1e]], [[0x1e]], (0)),
    (0, "RAW12"): ([[0x2c]], [[0x2c]], (0)),
    (1, "RAW12"): ([[0x2c]], [[0x2c]], (0)),
    (0, "RAW10"): ([[0x2b]], [[0x2b]], (0)),
    (0, "12+12RAW"): (([0x2c], [0x2c]), ([0x2c], [0x2c]), (0, 1)),
    (0, "12+SPD10"): (([0x2c], [0x2b]), ([0x2c], [0x2b]), (0, 1)),
    (0, "16+SPD10"): (([0x2e], [0x2b]), ([0x2e], [0x2b]), (0, 1)),
    (1, "12+12RAW"): ([[0x2c]], [[0x2c]], (0)),
    (0, "16+12RAW"): (([0x2e], [0x2c]), ([0x2e], [0x2c]), (0, 1)),
    (0, "24+LFM"): ([[0x27], [0x2a]], [[0x27], [0x2a]], (0, 1)),
    (0, "COM24"): ([[0x27]], [[0x27]], (0)),
    (0, "COM20"): ([[0x2f]], [[0x2f]], (0)),
    (0, "COM16"): ([[0x2e]], [[0x2e]], (0)),
    (0, "COM14"): ([[0x2d]], [[0x2d]], (0)),
    (0, "COM12"): ([[0x2c]], [[0x2c]], (0)),
    (0, "4X10RAW"): (([0x2b], [0x2b], [0x2b], [0x2b]), ([0x2b], [0x2b], [0x2b], [0x2b]), (0, 1, 2, 3)),
    (1, "4X10RAW"): (([0x2b], [0x2b], [0x2b], [0x2b]), ([0x2b], [0x2b], [0x2b], [0x2b]), (0)),
}

vsnr_fmt_dict = {
    'RAW8': 0,
    'RAW10': 1,
    'RAW12': 2,
    'RAW14': 3,
    'RAW16': 4,
    'RAW20': 5,
    'RAW24': 6,
    'COM12': 2,
    'COM14': 3,
    'COM16': 4,
    'COM20': 5,
    'COM24': 6,
    '2X10RAW': 7,
    '2X12RAW': 8,
    '12+12RAW': 8,
    '12+10RAW': 9,
    '14+10RAW': 10,
    '16+10RAW': 11,
    '3X10RAW': 12,
    '3X12RAW': 14,
    '4X10RAW': 16,
    'YU422-8': 17,
    'YUV422-10': 18,
    'YUV422-12': 19,
    '4X12RAW': 20,
    '16+12RAW': 22,
}

idc_mem_hsize_div_dict = {
    "3X12RAW": (8, 8, 3),
    "3X10RAW": (8, 8, 3),
    "2X12RAW": (8, 8, 2),
    "2X10RAW": (8, 8, 2),
    "2X11RAW": (8, 8, 2),
    "YUV422": (8, 8, 1),
    "RAW12": (8, 8, 1),
    "12+12RAW": (8, 8, 2),
    "16+12RAW": (4, 8, 2),
    "COM24": (4, 4, 1),
    "24+LFM": (4, 8, 2),
    "COM20": (4, 4, 1),
    "COM16": (4, 4, 1),
    "COM14": (4, 4, 1),
    "COM12": (8, 8, 1),
    "4X12RAW": (8, 8, 4),
    "4X10RAW": (8, 8, 4),
    "RAW10": (8, 8, 1),
    "12+SPD10": (8, 8, 2),
    "16+SPD10": (4, 8, 2),
}

chip_type_dict = {
    0: 'JUPITER',
    1: 'UV440',
    2: 'CHIP',
    3: 'CHIPDBG',
}

iptvc_format_dict = {
    "YUV422-8": "YUV422",
    "YUV422-10": "YUV422_10",
    "YUV422-12": "YUV422_12",
    "RGB565": "RGB565",
    "RGB888": "RGB24",
    "YUV420-8": "YUV420_UYVY",
    "YUV420-10": "YUV420_UYVY_10",
    "YUV420-12": "YUV420_UYVY_12",
    "RAW12L": "RAW_BG12",
    "RAW12S": "RAW_BG12",
    "RAW12V": "RAW_BG12",
    "RAW12M": "RAW_BG12",
    "RAW14": "RAW_BG14",
    "RAW16": "RAW_BG16",
    "RAW20": "RAW_BG20",
    "RAW24": "RAW_BG24",
    "RAW2X11": "RAW_BG12",
    "RAW2X12": "RAW_BG12",
    "RAW3X10": "RAW_BG10",
    "RAW3X12": "RAW_BG12",
    "RAW12+12": "RAW_BG12",
    "RAW10": "RAW_BG10",
}

fmt_bitwidth_dict = {
    0x18: 16,
    0x19: 20,
    0x31: 24,
    0x1e: 16,
    0x1f: 20,
    0x1b: 24,
    0x22: 16,
    0x24: 24,
    0x2a: 8,
    0x2b: 10,
    0x2d: 14,
    0x2c: 12,
    0x2e: 16,
    0x2f: 20,
    0x27: 24,
}
snrclkbox_values = ['24MHz',
    '21MHz',
    '20MHz',
    '16MHz',
    '15MHz',
    '14MHz',
    '12MHz',
    '10MHz',
    '8MHz']
