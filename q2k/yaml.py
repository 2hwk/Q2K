#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2018 2Cas
# Licensed under the MIT license (http://opensource.org/licenses/MIT)

import yaml, glob, os, errno, pathlib

from q2k.classes import *
from q2k.console import note_out, error_out
from q2k.globals import QMK_DIR, OUT_DIR, KBD_LIST, KB_INFO, keyplus_yaml_template


def special_file_dir(string):
    
    special_dir = ['handwired', 'converter', 'clueboard', 'lfkeyboards'] # Currently only lfkeyboards causes any issues, however it is good to be verbose here
    if string in special_dir:
        return True
    else:
        return False

def write_info(kb_info_yaml):
    templist = []
    keymaplist = []

    for fn in glob.glob(QMK_DIR+'keyboards/**/rules.mk', recursive=True):
        fn = fn[:-9]
        templist.append(fn)

    for fn in glob.glob(QMK_DIR+'keyboards/**/keymaps/**/keymap.c', recursive=True):
        fn = fn[:-9]
        if fn in templist:
            templist.remove(fn)
        fn = fn.replace(QMK_DIR+'keyboards/', '', 1)
        keymaplist.append(fn)

    for child in templist:
        p_path = str(pathlib.Path(child).parent)
        p_name = p_path.replace(QMK_DIR+'keyboards/', '', 1)

        if p_path not in templist and not special_file_dir(p_name):
            name = child.replace(QMK_DIR+'keyboards/', '', 1)
            # If in special dir list, then is part of the directory not keyboard
            if not special_file_dir(name):
               # This is a keyboard, not revision
               kb_obj = kb_info(name)
               kblibs = name.split('/')
               kb_obj.set_libs(kblibs) 
               KBD_LIST.append(kb_obj)   
        elif special_file_dir(p_name):
            name = child.replace(QMK_DIR+'keyboards/', '', 1)
            # This is a keyboard, not revision
            kb_obj = kb_info(name)
            kblibs = name.split('/')
            kb_obj.set_libs(kblibs)
            KBD_LIST.append(kb_obj)
        else:
            # This is a 'revision' of an existing keyboard
            rev = child.replace(p_path+'/', '')
            for kb_obj in KBD_LIST:
                if kb_obj.get_name() == p_name:
                    kb_obj.add_rev_list(rev)
                    break

    for kb_obj in KBD_LIST:
        if not kb_obj.get_rev_list():
            kb_obj.add_rev_list('n/a', True)

    for km_path in keymaplist:
        info_list = km_path.split('/keymaps/')
        kb_name = info_list[0]
        km_name = info_list[-1]
        namelist = kb_name.split('/')
        match = False
        for i in range(0, len(namelist)):
            if i > 0: 
                kb_name = '/'.join(namelist)

            for kb_obj in KBD_LIST:
                if kb_obj.get_name() == kb_name:
                    kb_obj.add_keymap_list(km_name)
                    match = True
                    break
            if match:
                break
            namelist.pop()

    if KBD_LIST:
        # Dump KBD_LIST to text file for faster processing in future
        dump_info(KBD_LIST, kb_info_yaml)
    else:
        error_out(['No keyboard information found', 'Is current directory a qmk root directory?', 'cd <qmk_dir>'])
        exit()

def dump_info(target, kb_info_yaml):

    kb_info_path = '/'.join(kb_info_yaml.split('/')[:-1])
    if not os.path.exists(kb_info_path):
        try:
            os.makedirs(kb_info_path)
        except OSError as e:
            if e.errno != errno.EEXIST and os.path.isdir(kb_info_path):
                raise
    try:
        with open(kb_info_yaml, 'w') as f:
            yaml.dump(target, f)
    except:
        error_out(['Failed to create '+kb_info_yaml])

def create_keyplus_yaml(kbo, printout=False):

    # Can't simply dump to yaml as we want to keep layout (array) as a human readable matrix (2D 'array').
    kb_n = kbo.get_name()
    rev_n = kbo.get_rev()
    keymap_n = kbo.get_keymap()

    rev = kbo.get_rev_info(rev_n)
    matrix = rev.get_matrix_pins()
    layers = rev.get_layout() 

    template_matrix = layers[0].get_template()
    name = '"'+kb_n+'_'+rev_n+'"'
    keymap = '"'+keymap_n+'"'
    if matrix:
        rows = str(matrix[0])
        cols = str(matrix[1])
    else:
        rows, cols = ''
   
    template = ''
    for i, row in enumerate(template_matrix):
        for col in row:
            template += (col+', ')
        if i+1 < len(template_matrix):
            template += '\n        '

    
    layout = ''
    for i, layer in enumerate(layers):
        layout += '      [ # layer '+str(i)+'\n        ['
        for row in layer.get_layout():
            layout += '\n          '
            for keycode in row:
               if len(keycode) < 4:
                   repeat = 4 - len(keycode)
                   for i in (range(repeat)):
                       keycode+=' '
               layout += keycode+', '
        layout +='\n        ]\n      ],\n'

    # Load Template
    output_yaml_info = keyplus_yaml_template
    output_yaml_info = output_yaml_info.replace('<KB_NAME>', name)
    output_yaml_info = output_yaml_info.replace('<LAYOUT_NAME>', keymap)                              
    output_yaml_info = output_yaml_info.replace('<ROWS>', rows)                                 
    output_yaml_info = output_yaml_info.replace('<COLS>', cols)
    output_yaml_info = output_yaml_info.replace('<MATRIX_MAP>', template)
    output_yaml_info = output_yaml_info.replace('<LAYOUT>', layout)

    kblibs = kbo.get_libs()
    if rev_n:
        path_list = kblibs + [ rev_n, keymap_n]
    else:
        path_list = kblibs + [keymap_n]
    output_path = '_'.join(path_list)
    output_yaml = OUT_DIR+output_path+'.yaml'
    if not os.path.exists(OUT_DIR):
        try:
            os.makedirs(OUT_DIR)
        except OSError as e:
            if e.errno != errno.EEXIST and os.path.isdir(output_path):
                raise
    try:
        with open(output_yaml, 'w') as f:
            f.write(output_yaml_info)
    except:
        error_out(['Failed to pipe output to '+output_yaml])
        exit()

    if printout:
        print(output_yaml_info)

    note_out(['SUCCESS! Output is in: '+output_yaml])
