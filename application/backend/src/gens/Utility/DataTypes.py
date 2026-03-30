"""
This GENS mode code which be ported from GENS source code.

Author: OVT AE
Date: 2024-11-05
"""
# WARNING
# pylint: disable=C0103, C0115, C0116, W0102
class DefaultDic(dict):
    def __init__(self, default_val='', init_dic={}, **kwargs):
        self.default_val = default_val
        super().__init__(**kwargs)
        for key,val in init_dic.items():
            self[key] = val

    def __missing__(self, key):
        return self.default_val

    def find_key(self, value):
        for key, val in self.items():
            if val == value:
                return key
        return None


def dprint(cls, char):
    print(f"{cls} {char}")
