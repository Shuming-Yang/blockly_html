"""
This GENS mode code which be ported from GENS source code.

Author: OVT AE
Date: 2024-11-05
"""
# WARNING
# pylint: disable=C0103, C0115, C0116, C0200, C0204, W0212
from collections import OrderedDict


class Typed:
    _expected_type = type(None)
    def __init__(self, name=None):
        self._name = name

    def __set__(self, instance, value):
        if not isinstance(value, self._expected_type):
            raise TypeError('Expected ' + str(self._expected_type))
        instance.__dict__[self._name] = value


class Integer(Typed):
    _expected_type = int


class Float(Typed):
    _expected_type = float


class String(Typed):
    _expected_type = str


class OrderedMeta(type):
    def __new__(cls, clsname, bases, clsdict):
        d = dict(clsdict)
        order = []
        # print(clsdict.items())
        for name, value in clsdict.items():
            # print(type(value))
            if not callable(value) and not name.startswith("__") :
                order.append((name,value))
        d['_order'] = order
        # print(d)
        return type.__new__(cls, clsname, bases, d)

    @classmethod
    def __prepare__(cls, _clsname, _bases):
        return OrderedDict()


class Structure(metaclass=OrderedMeta):
    def as_csv(self):
        return ','.join(str(getattr(self,name)) for name in self._order)

    def parse_list(self, obj, tlist):
        # print(obj._order)
        for name, dft in obj._order:
            if type(getattr(obj, name)) in (int, float, str,bool):
                if type(getattr(obj, name)) in (bool, float):
                    raise RuntimeError(f"FW reg {obj} {name} should be int,acutal is {type(getattr(obj,name))} ")
                tlist.append((name, dft, getattr(obj,name)))
            elif isinstance(getattr(obj,name), list):
                tmp = dft
                new = getattr(obj, name)
                for i in range(len(new)):
                    tlist.append((name + str(i), tmp[0], new[i]))
                for i in range(tmp[1] - len(new)):
                    tlist.append((name + str(len(new) + i), tmp[0], 'x'))
            else:
                # print(obj,name)
                tmp = getattr(obj, name)
                self.parse_list(tmp, tlist)

    def get_class_varlist(self):
        tlist = []
        self.parse_list(self,tlist)
        # print(tlist)
        return tlist
