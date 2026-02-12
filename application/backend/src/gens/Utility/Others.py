"""
This GENS mode code which be ported from GENS source code.

Author: OVT AE
Date: 2024-11-05
"""
# WARNING
# pylint: disable=C0103, C0116, C0200, R0912, R0914, W0622
import os
import re
import shutil

def get_dict_key(dict, value, valtype=0, loc=0):
    """
    0:normal
    1:list
    """
    keys = []
    for key, val in dict.items():
        # print("!!!!!!!!!!!!!!!!!!!!!!",type(valtype),type(list),isinstance(valtype,list))
        # if(isinstance(valtype,list)):
        if valtype and isinstance(val,list):
            # print("!!!!!!!!!!!!!!!!!!!!!!",valtype)
            if val[loc] == value:
                keys.append(key)

        else:
            if val == value:
                keys.append(key)
    if keys:
        return keys[0]
    # raise ("value can't find in dict")
    return []


def int_inc(val, base=1):
    newval = val // base + (1 if (val % base) else 0)
    # print(newval * base, val)
    return int(newval * base)


def reverse_dict(dict):
    newdist = {}
    for key, val in dict.items():
        newdist[val] = key
    return newdist
    #raise ("value can't find in dict")


def get_class_var(obj, prefix="", spilter='.', level=0):
    objlist = dir(obj)
    # print(objlist)
    if level == 0:
        level = 100
    else:
        level = level - 1
    varlist = []
    for item in objlist:
        if not callable(getattr(obj,item)) and not item.startswith("__") :
            if objlist[0] == "__class__":
                if prefix == "":
                    newprefix = item
                else:
                    newprefix = prefix + spilter + item
                if level > 0:
                    tmplist = get_class_var(getattr(obj, item), newprefix, spilter, level)
                    varlist.extend(tmplist)
                if (isinstance(getattr(obj, item), int) or isinstance(getattr(obj, item), str)):
                    if prefix != "":
                        newchar = prefix + spilter + item
                    else:
                        newchar = item
                    newval = getattr(obj, item)
                    # print(newchar, newval)
                    varlist.append((newchar, newval))
                else:
                    continue
            else:
                return []
    return varlist


def get_class_object(obj, prefix="", spilter='.', level=0):
    objlist = dir(obj)
    # print(objlist)
    if level == 0:
        level = 100
    else:
        level = level - 1
    varlist = []
    for item in objlist:
        if not callable(getattr(obj,item)) and not item.startswith("__") :
            if objlist[0] == "__class__" :
                if prefix == "":
                    newprefix = item
                else:
                    newprefix = prefix + spilter + item

                if level > 0:
                    tmplist = get_class_object(getattr(obj, item), newprefix, spilter, level)
                    varlist.extend(tmplist)
                if(isinstance(getattr(obj, item), int) or isinstance(getattr(obj, item), list)):
                    continue
                else:
                    if prefix != "":
                        newchar = prefix + spilter + item
                    else:
                        newchar = item
                    varlist.append((newchar))
            else:
                return []
    return varlist


def get_class_list(obj, prefix="", spilter='.', level=0):
    objlist = dir(obj)
    if level == 0:
        level=100
    else:
        level=level-1
    varlist=[]
    for item in objlist:
        if not callable(getattr(obj,item)) and not item.startswith("__") :
            if objlist[0] == "__class__":
                if prefix == "":
                    newprefix = item
                else:
                    newprefix = prefix + spilter + item
                if level > 0:
                    tmplist = get_class_list(getattr(obj, item), newprefix, spilter, level)
                    varlist.extend(tmplist)
                if isinstance(getattr(obj, item), list):
                    if prefix != "":
                        newchar = prefix + spilter + item
                    else:
                        newchar = item
                    varlist.append(newchar)
                else:
                    continue
            else:
                return []
    return varlist

def get_class_listvar_new(obj, listbuf, objdist, prefix="", spilter='-'):
    classlist = []
    for item in listbuf:
        orgitem = item
        items = item.split('.')
        newobj = obj
        if len(items) > 1:
            for i in range(len(items) - 1):
                newobj = getattr(newobj, items[i])
                item = items[i]
            item = items[i + 1]
            # print(item,newobj)

        if item.endswith("_list"):
            itemname = item.split("_list")[0]
            item_num = itemname + "_num"
            if len(prefix.split(spilter)) >= 3:
                tmpspilter = "_"
            else:
                tmpspilter = "-"
            if prefix != "":
                newprefix = prefix + tmpspilter + item.upper()
            else:
                newprefix = item.upper()
            # print(newprefix, itemname, item_num, getattr(newobj, item))
            buftmp = getattr(newobj, item)
            # buftmp = []
            # for i in range(getattr(newobj, item_num)):
            #     tmp = 0
            #     buftmp.append((item, tmp))
            if buftmp != []:
                classlist.append((orgitem, [(item, buftmp)]))
                # print(buftmp)
        elif item.endswith("_buf"):
            itemname = item.split("_buf")[0]
            item_num = itemname + "_num"
            item_cfg = itemname.upper() + "_CFG"
            if len(prefix.split(spilter)) >= 3:
                tmpspilter = "_"
            else:
                tmpspilter = "-"
            if prefix != "":
                newprefix = prefix + tmpspilter + itemname.upper()
            else:
                newprefix = itemname.upper()
            buftmp = []
            buforg = getattr(newobj, item)
            if hasattr(newobj, "index"):
                superidx = getattr(newobj, "index")
            else:
                superidx = 0
            if hasattr(newobj, item_num):
                objnum = getattr(newobj, item_num)
            else:
                objnum = 1
            # print(superidx, objnum)
            for i in range(objnum):
                tmpobj = objdist[item_cfg](i, superidx)
                tmpobj.index = i
                if i < len(buforg):
                    tmpobj = buforg[i]
                buftmp.append(tmpobj)
            if buftmp:
                for i in range(len(buftmp)):
                    # print(orgitem, buftmp[i], newprefix + str(i))
                    # classlist.extend(orgitem, get_class_var(buftmp[i], newprefix + str(i)))
                    classlist.append((orgitem, get_class_var(buftmp[i], newprefix + str(i))))
    return classlist
    # setattr(newobj, item, buftmp)

def find_file(dir, file_name):
    ''' find file in the director recursively and return the path,
    The function resembles the grep command of unix system. 
    If not found, return []. Else return all the files under the directory as a list.
    '''
    ret = []
    def _find(dir, file_name):
        for sub_dir in os.listdir(dir):
            file_path = ''.join([dir,'\\', sub_dir])
            if os.path.isfile(file_path) and file_name == sub_dir:
                ret.append(file_path)
            elif os.path.isdir(file_path):
                _find(file_path, file_name)
    _find(dir, file_name)
    # if(len(ret) == 0):
    #     print("do not find file {} in {}".format(file_name, dir))
    # elif (len(ret) > 1):
    #     print("find {} files named {} in {}".format(len(ret), file_name, dir))
    return ret


def copy_file(source_file_name, source_dir, dest):
    files = find_file(source_dir, source_file_name)
    if len(files) != 1:
        raise RuntimeError(f"{len(files)} files {source_file_name} found while copy file to dest {dest}")
    shutil.copy(files[0], dest)


def str_to_int(val):
    if val == '':
        return 0
    if '0x' in val or '0X' in val:
        base = 16
    else:
        base = 10
    return int(val, base)


def endwithnum(parastr):
    pattn = re.compile(r'.*[0-9]*$')
    return True if pattn.match(parastr) else False


def split_str_num(parastr):
    obj = re.search(r'[0-9]*$', parastr)
    idxstr = obj.group()
    elemstr = parastr.rstrip(idxstr)
    return elemstr, idxstr


def find_bit_num(dat):
    cnt = 0
    while dat:
        cnt += 1
        dat = dat & (dat - 1)
    return cnt
