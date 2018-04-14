#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2018 2Cas
# Licensed under the MIT license (http://opensource.org/licenses/MIT)
import os

from q2k.classes import *
from q2k.console import note_out, error_out, bad_kc_out
from q2k.globals import QMK_DIR, OUT_KBF_DIR, KBD_LIST, KB_INFO, KBF_TRANSCODE, KBF_KC_LIST, KBF_FUNC_LIST

def check_keycode(kc, layer_list):

    if '(' in kc and ')' in kc:
        output = kbf_func(kc, layer_list)
    else:
        output = kbf_keycode(kc)
    return output

def kbf_func(func, layer_list):

    brac_index = func.index('(')+1
    qfunc = func[:brac_index]
    func_target = func[brac_index:-1]

    if func_target in layer_list:
        func_target = str(layer_list.index(func_target))

    if qfunc in KBF_TRANSCODE.keys():
        kbf_func = KBF_TRANSCODE[qfunc]+func_target+')'
        #bad_kc_out('FN','['+func+'] - set to '+kbf_func)
        return kbf_func
    elif qfunc in KBF_FUNC_LIST:
        return func
    else:
        kbf_func = 'KC_TRNS'
        bad_kc_out('FN','['+func+'] - set to KC_TRNS')
        return kbf_func

def kbf_keycode(kc):

    if kc in KBF_TRANSCODE.keys():
        kbf_kc = KBF_TRANSCODE[kc]
        #bad_kc_out('KC','['+kc+'] - set to '+kbf_kc)
        return kbf_kc
    elif kc in KBF_KC_LIST:
        return kc
    else:
        kbf_kc = 'KC_TRNS'
        bad_kc_out('KC','['+kc+'] - set to KC_TRNS')
        return kbf_kc

def keycode_func_parse_json(keycode, layer_list):

    func_list = []
    while '(' in keycode:
        split = keycode.split('(', 1)
        keycode = split[1][:-1]
        function = split[0]
        func_list.append(function)

    kc_data = ''
    for func in func_list:
        kc_data += '{"id": "'+func+'()","fields":['

    if keycode.isdigit():
        kc_data += keycode
    else:
        kc_data += '{"id": "'+check_keycode(keycode, layer_list)+'", "fields":[]}'

    for i in range(len(func_list)):
        kc_data += ']}'

    return kc_data


def create_kbfirmware_json(kbc, printout=False):

    kb_n = kbc.get_name()
    rev_n = kbc.get_rev()
    keymap_n = kbc.get_keymap()

    rev = kbc.get_rev_info(rev_n)
    matrix = rev.get_matrix_pins()
    layers = rev.get_layout() 

    template_matrix = layers[0].get_template()
    name = '"'+kb_n+'_'+rev_n+'"'
    keymap = '"'+keymap_n+'"'
    if matrix:
        m_rows = str(matrix[0]).replace("'", '"')
        m_cols = str(matrix[1]).replace("'", '"')
    else:
        m_rows, m_cols = '[]'

    json_out = '{"version":1,"keyboard":{"keys":['
    quantum = '"void matrix_init_user(void) {\\n}\\n\\nvoid matrix_scan_user(void) {\\n}\\n\\nbool process_record_user(uint16_t keycode, keyrecord_t *record) {\\n\\treturn true;\\n}"'
    id_list = []
    layer_names = []
    rmax = cmax = m_r_max = m_c_max = 0
    try:
        for n, layer in enumerate(layers):
            id = row_y = col_x = -1
            layer_names.append(layer.get_name())
            for i,row in enumerate(layer.get_layout()):
                row_y += 1
                for j, keycode in enumerate(row):
                    id += 1
                    col_x = col_x + 1
                    if n == 0:
                        keycodelist = [keycode]
                        id_list.append(keycodelist)
                    else:
                        id_list[id].append(keycode)

                    if n+1 == len(layers):
                        w = 1
                        h = 1
                        row_col = template_matrix[i][j].split('c')
                        r = row_col[0][1:]
                        c = row_col[-1]
                        if int(r) >= m_r_max:
                            m_r_max = int(r)+1
                        if int(c) >= m_c_max:
                            m_c_max = int(c)+1
                        kc_build = ''

                        for add in range(n+1, 16):
                            id_list[id].append('KC_TRNS')
                        for kc in id_list[id]:
                            kc = check_keycode(kc, layer_names)
                            kc_build += keycode_func_parse_json(kc, layer_names)+','
                        kc_build = kc_build[:-1]
                        json_out += ('{"id":'+str(id)+',"legend":"","state":{"x":'+str(col_x)+',"y":'+str(row_y)+
                                    ',"r":0,"rx":0,"ry":0,"w":'+str(w)+',"h":'+str(h)+'},"row":'+r+',"col":'+c+
                                    ',"keycodes":['+kc_build+']},')
                if col_x+1 > cmax:
                    cmax = col_x+1
                rmax = row_y+1
                col_x = -1
    except IndexError:
        error_out(['Layers have different layouts'])
        exit()
    json_out = json_out[:-1]
    json_out += '],"controller":1,"bounds":{"min":{"x":0,"y":0},"max":{"x":'+str(cmax)+',"y":'+str(rmax)+'}},'
    json_out += ('"rows":'+str(m_r_max)+',"cols":'+str(m_c_max)+',"pins":{"row":'+m_rows+',"col":'+m_cols+'},'+
                '"macros":{},"quantum":'+quantum+
                ',"settings":{"diodeDirection":0,"name":"","bootloaderSize":2,"rgbNum":0,"backlightLevels":3}}}')

    kblibs = kbc.get_libs()
    if rev_n:
        path_list = kblibs + [ rev_n, keymap_n]
    else:
        path_list = kblibs + [keymap_n]
    output_path = '_'.join(path_list)
    output_json = OUT_KBF_DIR+output_path+'.json'
    if not os.path.exists(OUT_KBF_DIR):
        try:
            os.makedirs(OUT_KBF_DIR)
        except OSError as e:
            if e.errno != errno.EEXIST and os.path.isdir(output_path):
                raise
    try:
        with open(output_json, 'w') as f:
            f.write(json_out)
    except:
        error_out(['Failed to pipe output to '+output_json])
        exit()

    if printout:
        print(json_out)

    note_out(['SUCCESS! Output is in: '+output_json, 'Note: Check WIRING + PINS + SETTINGS for unset values in KBFirmware'])
