"""
This GENS mode code which be ported from GENS source code.

Author: OVT AE
Date: 2024-11-05
"""
# WARNING
# pylint: disable=C0103, C0115, C0116, C0121, C0201, E1101, E0602, R0205, R1702, W0123, W0201, W0612, W0702
import gens_globals

class jsonReader(object):
    def __init__(self, json_file):
        pass
        #self.filename = json_file
        #with open(json_file) as read_content:
        #    self.jsonfile = json.load(read_content)

    def find_text(self, elem, _text_type, spliter='-'):
        tag_names = elem.split(spliter)
        root = gens_globals.TC_data
        for i,tag in enumerate(tag_names):
            try:
                root = root[tag]
                if i == (len(tag_names) - 1):
                    return True, root
            except:
                return False, ''

    #def save_json(self):
    #    with open(self.filename, 'w') as f:
    #        json.dump(self.jsonfile, f, indent=4)

    def change_elem(self, elem, text, spliter='-'):
        tag_names = elem.split(spliter)
        root = gens_globals.TC_data
        for i,tag in enumerate(tag_names):
            if i == (len(tag_names) - 1):
                if tag in root.keys():
                    root[tag] = int(text)
                else:
                    root.update({tag: int(text)})
            else:
                if tag in root.keys():
                    root = root[tag]
                else:
                    root.update({tag: {}})
                    root = root[tag]
