"""
This GENS mode code which be ported from GENS source code.

Author: OVT AE
Date: 2024-11-05
"""
# WARNING
# pylint: disable=C0103, C0115, C0116, C0325, E0606, E0702, R0205, W0401, W0612, W0614, W0622
from Utility.Para import *


class REG8(object):
    def __init__(self, addr, val, save_en=1):
        self.addr = addr
        self.val = val & 0xff
        self.flag = 0
        self.default = val
        self.mask = 0x00
        self.save_en = 1 if save_en else 0
        self.type = 'REG8'
    def update(self, nval):
        self.val = nval
        valdiff = int(self.default) ^ int(self.val)
        self.mask = 1 if (valdiff & 0xff) else 0
        self.mask = self.mask & self.save_en
        self.flag = 1


class REG32(object):
    def __init__(self, addr, val, endian=0, save_en=1):
        self.type = 'REG32'
        self.flag = 0
        self.endian = endian
        self.default = val
        self.save_en = 0x0f if save_en else 0
        self.mask = 0x00
        if addr & 0x3 == 0:
            self.addr = addr
            self.val = val
        else:
            # pass
            raise MemoryError('REG32 addr should be the 4x')

    def update(self, nval, bitmask=0x0, save_force=0):
        self.val = self.val & bitmask | (nval & ~bitmask)
        valdiff = int(self.default) ^ int(self.val)
        mask_byte0 = 1 if (valdiff & 0xff       or save_force) else 0
        mask_byte1 = 1 if (valdiff & 0x0000ff00 or save_force) else 0
        mask_byte2 = 1 if (valdiff & 0x00ff0000 or save_force) else 0
        mask_byte3 = 1 if (valdiff & 0xff000000 or save_force) else 0
        self.mask = mask_byte0 | (mask_byte1 << 1) | (mask_byte2 << 2) |(mask_byte3 << 3)
        self.mask = self.mask & self.save_en
        self.flag = 1


class REG16(object):
    def __init__(self, addr, val, endian=0, save_en=0x03):
        self.type = 'REG16'
        self.flag = 0
        self.endian = endian
        self.default = val
        self.mask = 0x00
        self.save_en = 3 if save_en else 0
        if addr & 0x1 == 0:
            self.addr = addr
            self.val = val
        else:
            # pass
            raise MemoryError('REG16 addr should be the 2x')

    def update(self, nval):
        self.val = nval
        valdiff = int(self.default) ^ int(self.val)
        mask_byte0 = 1 if (valdiff & 0xff) else 0
        mask_byte1 = 1 if (valdiff & 0xff00) else 0
        self.mask = mask_byte0 | (mask_byte1 << 1)
        self.mask = self.mask & self.save_en
        self.flag = 1


class MEM32(object):
    def __init__(self, base, len=4):
        self.type = 'MEM32'
        self.flag = 0
        self.endian = 1
        self.len = len
        self.buf = []
        self.val = 0
        if base & 0x3 == 0:
            self.base = base
            for _ in range(int(self.len / 4)):
                self.buf.append([0, 0])
        else:
            # pass
            raise MemoryError('MEM32 addr should be the 4x')

    def update(self, addr, val):
        self.buf[int(addr / 4)] = [1, val]

    def getval(self, addr):
        flag, val = self.buf[int(addr / 4)]
        return val


class MEM8(object):
    def __init__(self, base, len=4):
        self.type = 'MEM8'
        self.flag = 0
        self.endian = 1
        self.len = len
        self.buf = []
        self.val = 0
        self.base = base
        for _ in range(int(self.len)):
            self.buf.append([0, 0])

    def update(self, addr, val):
        self.buf[int(addr)] = [1, val]

    def update32(self, addr, val):
        if addr & 0x3 == 0:
            self.buf[int(addr)] = [1, (val >> 24)]
            self.buf[int(addr) + 1] = [1, (val >> 16) & 0xff]
            self.buf[int(addr) + 2] = [1, (val >> 8) & 0xff]
            self.buf[int(addr) + 3] = [1, val & 0xff]
        else:
            raise MemoryError('MEM32 addr should be the 4x')

    def update16(self, addr, val):
        if addr & 0x1 == 0:
            self.buf[int(addr)] = [1, (val >> 8)]
            self.buf[int(addr) + 1] = [1, val & 0xff]
        else:
            raise MemoryError('MEM16 addr should be the 2x')

    def getval(self, addr):
        flag, val = self.buf[int(addr)]
        return val

    def getval32(self, addr):
        if addr & 0x3 == 0:
            flag, val0 = self.buf[int(addr) + 0]
            flag, val1 = self.buf[int(addr) + 1]
            flag, val2 = self.buf[int(addr) + 2]
            flag, val3 = self.buf[int(addr) + 3]
            val = (val0 << 24) | (val1 << 16) | (val2 <<8 ) | val3
            return val
        else:
            raise MemoryError('MEM32 addr should be the 4x')


class REGOBJ(object):
    def __init__(self):
        self.name = 'REGOBJ'
        self.base = 0
        self.regtable = {}
        self.objr = []

    def get_baseaddr_list(self, name, defdist, printen=0):
        baselist = []
        for key in defdist.keys():
            if name in key:
                baselist.extend(defdist[key])
        if not baselist:
            raise MemoryError(f"{name} can't find base")
        baselist =list(set(baselist))

        sorted_baselist=sorted(baselist)
        if printen:
            print(f" {name} found baselist {sorted_baselist:x}")
        return sorted_baselist

    def get_baseaddr(self, name, defdist, id, printen=0):
        baselist = []
        for key in defdist.keys():
            if name in key:
                baselist.extend(defdist[key])

        if not baselist:
            raise MemoryError(f"{name} can't find base")

        sorted_baselist = sorted(baselist)
        if printen:
            print(f" {name+str(id)} found base {sorted_baselist[id]:x}")
        return sorted_baselist[id]

    def writereg8(self, offset, val, save_force=0, newreg=0, endian=0, default_val=0, mask=0x00):
        val = val & 0xff
        mask = mask & 0xff

        addr = offset if(offset & BIT31) else self.base + offset
        if newreg:
            reg = REG32(addr & NBIT0 & NBIT1, default_val, endian)
        else:
            reg = self.regtable[addr & NBIT0 & NBIT1]
        setval = val
        defval = reg.val
        if offset & 0x03 == 0:
            # if(reg.endian==0): # little endian
            #    bitmask= 0xffffff00
            bitmask = 0xffffff00 | (mask << 0) if (reg.endian == 0) else 0x00ffffff | (mask << 24)
            val = val if (reg.endian == 0) else (val << 24)
            res_val = (defval if(reg.endian == 0) else defval >> 24) & 0xff
        elif offset & 0x03 == 1:
            # bitmask = 0xffff00ff
            bitmask = 0xffff00ff | (mask << 8) if (reg.endian == 0) else 0xff00ffff | (mask << 16)
            val = (val << 8) if (reg.endian == 0) else (val << 16)
            res_val = ((defval >> 8) if(reg.endian == 0) else defval >> 16) & 0xff
        elif offset & 0x03 == 2:
            # bitmask = 0xff00ffff
            # val = val << 16
            bitmask = 0xff00ffff | (mask << 16) if (reg.endian == 0) else 0xffff00ff | (mask << 8)
            val = (val << 16) if (reg.endian == 0) else (val << 8)
            res_val = ((defval >> 16) if (reg.endian == 0) else defval >> 8) & 0xff
        else:
            # val = val << 24
            # bitmask = 0x00ffffff
            bitmask = 0x00ffffff | (mask << 24) if (reg.endian == 0) else 0xffffff00 | (mask << 0)
            val = (val << 24) if (reg.endian == 0) else (val << 0)
            res_val = ((defval >> 24) if(reg.endian == 0) else defval) & 0xff
        if((defval & ~bitmask ) != (val & ~bitmask) or save_force):
            setval = (setval & ~mask) | (res_val &mask)
            reg.update(val, bitmask, save_force)
            self.objr.append((addr, setval, 1, 1 if reg.mask else 0))

    def writereg16(self, offset, val, save_force=0, newreg=0, endian=0, default_val=0, mask=0x0000):
        if offset & BIT0:
            raise("writereg16 should 2x")
        # if(offset &BIT31):
        #     addr =offset &NBIT1
        #     reg=self.regtable[addr]
        # else:
        #     addr =self.base+(offset &NBIT1)
        addr = offset if (offset & BIT31) else self.base + offset
        if newreg:
            reg = REG32(addr & NBIT1, default_val, endian)
        else:
            reg = self.regtable[addr & NBIT1]
        # reg = self.regtable[addr & NBIT1]
        val = val & 0xffff
        mask = mask & 0xffff
        setval = val
        # setval = setval if(reg.endian) else self.swap(setval, 1)
        # setval = val if(reg.endian) else self.swap(val, 1)
        defval = reg.val
        if offset & 0x03 == 0:
            bitmask = 0xffff0000 | (mask << 0) if(reg.endian == 0) else 0x0000ffff | (mask << 16)
            val = val if (reg.endian == 0) else (val << 16)
            res_val = ((defval >> 0) if (reg.endian == 0) else defval >> 16) & 0xffff
            # bitmask= 0xffff0000
        elif offset & 0x03 == 2:
            bitmask = 0x0000ffff | (mask << 16) if (reg.endian == 0) else 0xffff0000 | (mask >> 0)
            val = (val << 16) if (reg.endian == 0) else (val << 0)
            # bitmask= 0x0000ffff
            res_val = ((defval >> 16) if(reg.endian == 0) else defval >> 0) & 0xffff
            # val = val << 16
        if((defval  & ~bitmask)!= (val & ~bitmask) or save_force):
            setval = (setval & ~mask) | (res_val & mask)
            setval = setval if(reg.endian) else self.swap(setval, 1)
            mask = mask if(reg.endian) else self.swap(mask, 1)
            reg.update(val,bitmask,save_force)
            regmask = reg.mask >> 2 if(reg.mask >> 2) else reg.mask & 0x03
            self.objr.append((addr, setval, 2, self.maskswap(regmask, 1) if(reg.endian) else regmask))

    def swap(self, val, mode=0):
        b0 = val & 0xff
        b1 = (val >> 8) & 0xff
        b2 = (val >> 16) & 0xff
        b3 = (val >> 24) & 0xff
        nval = ((b0 << 8) | b1) if(mode) else ((b0 << 24) | (b1 << 16) | (b2 << 8) | b3)
        return nval

    def maskswap(self, val, mode=0):
        b0 = val & BIT0
        b1 = (val >> 1) & BIT0
        b2 = (val >> 2) & BIT0
        b3 = (val >> 3) & BIT0
        nval = ((b0 << 1) | b1) if(mode) else ((b0 << 3) | (b1 << 2) | (b2 << 1) | b3)
        return nval

    def writereg32(self, offset, val, save_force=0, newreg=0, endian=0, default_val=0, mask=0x0000):
        if offset & 0x03:
            raise("writereg16 should 4x")
        addr = offset if(offset &BIT31) else self.base+offset
        if newreg:
            reg = REG32(addr,default_val,endian)
        else:
            if addr in self.regtable:
                reg = self.regtable[addr]
            else:
                for reg_addr in self.regtable:
                    if reg_addr >= 0x8020cc00 and reg_addr <= 0x8020cd00:
                        print(f"{reg_addr:x}")
                raise RuntimeError(f"addr 0x{addr:x} not in regtable")
        # reg=self.regtable[addr]
        val = val & 0xffffffff
        # reg=self.regtable[self.base+offset]
        mask = mask & 0xffffffff
        setval = val
        # setval = val if(reg.endian) else self.swap(val)
        # bitmask = mask if(reg.endian) else self.swap(mask)
        bitmask = mask
        defval = reg.val
        # if(defval != val or save_force):
        if ((defval  & ~bitmask) != (val & ~bitmask) or save_force):
            setval = (setval & ~mask) | (defval & mask)
            setval = setval if (reg.endian) else self.swap(setval)
            mask = mask if(reg.endian) else self.swap(mask)
            reg.update(val, bitmask, save_force)
            self.objr.append((addr, setval, 4, self.maskswap(reg.mask) if(reg.endian) else reg.mask))

    def readreg8(self, offset):
        shiftwd = (offset & 0x03) * 8
        addr = offset if (offset & BIT31) else self.base+offset
        # offset = offset & NBIT0 & NBIT1
        reg = self.regtable[addr & NBIT0 & NBIT1]
        # reg = self.regtable[self.base + offset]
        if reg.endian == 0:  # little endian
            getval = (reg.val >> shiftwd) & 0xff
        else:
            getval = (reg.val >> (24 - shiftwd)) & 0xff
        # if(offset == 0x127b):
        #     print("shiftwd {},addr {} reg {}, getval {}".format(shiftwd,addr,addr&NBIT0&NBIT1,getval))
        return getval

    def readreg16(self, offset):
        if offset & BIT0:
            raise("readreg16 should 2x")
        shiftwd = (offset & 0x03) * 8
        addr = offset if(offset & BIT31) else self.base + offset
        reg = self.regtable[addr & NBIT1]
        #offset = offset & NBIT1
        #reg = self.regtable[self.base + offset]
        if reg.endian == 0:  # little endian
            getval = (reg.val >> shiftwd) & 0xffff
        else:
            getval = (reg.val >> (16 - shiftwd)) & 0xffff
        # getval = (reg.val >> shiftwd) & 0xffff
        return getval

    def readreg32(self,offset):
        if offset & 0x03:
            raise("readreg32 should 4x")
        addr = offset if(offset & BIT31) else self.base + offset
        reg = self.regtable[addr]
        # reg = self.regtable[self.base + offset]
        getval = reg.val
        return getval
