#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2018 2Cas
# Licensed under the MIT license (http://opensource.org/licenses/MIT)

# A class for listing keyboards and QMK folder structure associated with keyboards (can be dumped and loaded to yaml)

class kb_info:

    def __init__(self, n=''):
        self._kbname = n
        self._rev_list = []
        self._keymap_list = []       
        self._klibs = []

        self.current_keymap = ''
        self.current_rev = ''
        self.rev_info = []

    def set_rev(self, rev):
        self.current_rev = rev

    def set_keymap(self, keymap):
        self.current_keymap = keymap
        
    def set_libs(self, lib):
        self._klibs = lib

    def add_rev_list(self, rev, flag=False):
        if not flag:
            self._rev_list.append(rev)
        revObj = rev_info(rev, flag)
        self.rev_info.append(revObj)

    def add_keymap_list(self, km):
        self._keymap_list.append(km)

    def add_lib(self, lib):
        self._klibs.append(lib)
        print(lib)
        
    def get_name(self):
        return self._kbname

    def get_keymap(self):
        return self.current_keymap

    def get_libs(self):
        return self._klibs

    def get_rev(self):
        return self.current_rev

    def get_rev_info(self, rev):
        for r in self.rev_info:
           if r._rname == rev:
               return r
           if r._rname == 'n/a':
               return r
    def get_keymap_list(self):
        return self._keymap_list

    def get_rev_list(self):
        """
        _rev_list = []        
        for r in self.rev_info:
            if r.isDefault == False:
                _rev_list.append(r._rname)
        return _rev_list
        """
        return self._rev_list

# A class for listing revision info and 
class rev_info:
    def __init__ (self, n='', flag=False):
        self._rname = n
        self.isDefault = flag

        self.build_m_row_pins = []
        self.build_m_col_pins = []
        self.build_layout = []
        self.build_templates = []

        self.mcuL = []

    def set_mcu_list(self, mcu):
        self.mcuL = mcu

    def set_layout(self, lot_list):
        self.build_layout = lot_list

    def set_templates(self, temp_list):
        self.build_templates = temp_list

    def set_matrix_pins(self, r, c):
        self.build_m_row_pins = r
        self.build_m_col_pins = c

    def get_rev_name(self):
        return self._rname

    def get_mcu_list(self):
        return self.mcuL

    def get_layout(self):
        return self.build_layout

    def get_templates(self):
        return self.build_templates

    def get_matrix_pins(self):
        matrix = []
        matrix.append(self.build_m_row_pins)
        matrix.append(self.build_m_col_pins)
        return matrix


# A class for linking matrices in <keyboard>.h with (preprocessed) keymap.c layouts
class layout_template:

    def __init__(self, n=''):
        self.layout_name = n
        self.layout = []
        self.array = []

    def set_array(self, a):
        self.array = a

    def set_layout(self, l):
        self.layout = l

    def add_layout_line(self, l):
        self.layout.append(l)

    def add_array_item(self, item):
        self.array = self.array+item

    def get_name(self):
        return self.layout_name

    def get_array(self):
        return self.array

    def get_layout(self):
        return self.layout

# A class for storing keymap layers
class keymap_layer:

    def __init__(self, n=''):
        self.keymap = []
        self.layer_name = n

        self.layout = []
        self.template = []
        self.matrix_cols = 0

    def set_keymap(self, k):
        self.keymap = k

    def set_matrix_cols(self, c):
        self.matrix_cols = c
    
    def set_template(self, m):
        self.template = m

    def set_layout(self, l):
        self.layout = l

    def add_keymap_item(self, l):
        self.keymap = self.keymap+l

    def get_name(self):
        return self.layer_name

    def get_keymap(self):
        return self.keymap

    def get_layout(self):
        return self.layout

    def get_template(self):
        return self.template

    def get_matrix_cols(self):
        return self.matrix_cols
