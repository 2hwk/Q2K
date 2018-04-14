#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2018 2Cas
# Licensed under the MIT license (http://opensource.org/licenses/MIT)

import copy

from q2k.classes import *
from q2k.console import *

from q2k.globals import KEYP_FUNC_LIST, KEYP_KC_LIST

def convert_keymap(layers):

    l_list = []
    for ln in layers:
        name = ln.get_name()
        l_list.append(name)
    for l in layers:
        layer = l.get_keymap()
        for i, kc in enumerate(layer):
            if kc.endswith(')') and '(' in kc:
                layer[i] = func(kc, l_list)
            else:
                layer[i] = keycode(kc)
        l.set_keymap(layer)
    return layers

def func(qmk_func, layer_list):
    # Currently only handles layer switching functions
    if qmk_func in KEYP_FUNC_LIST.keys():
        keyp_func = KEYP_FUNC_LIST[qmk_func]
    else:

        try:
            brac_index = qmk_func.index('(')+1
            qfunc = qmk_func[:brac_index]
            func_target = qmk_func[brac_index:-1]
            if func_target in layer_list:
                layer = str(layer_list.index(func_target))
                keyp_func = KEYP_FUNC_LIST[qfunc]+layer
            else:
                bad_kc_out('FN','['+qmk_func+'] - set to trns')
                keyp_func = 'trns'
        except KeyError:
            bad_kc_out('FN','['+qmk_func+'] - set to trns')
            keyp_func = 'trns'
        except ValueError:
            bad_kc_out('FN','['+qmk_func+'] - set to trns')
            keyp_func = 'trns'

    return keyp_func


def keycode(qmk_kc):

    try:
        keyp_kc = KEYP_KC_LIST[qmk_kc]
    except KeyError:
        bad_kc_out('KC','['+qmk_kc+'] - set to trns')
        keyp_kc = 'trns'
    return keyp_kc


def build_layout_from_keymap(layers, layer_index=0):
    template_list = []

    keymap = layers[layer_index].get_keymap()
    col_limit = layers[layer_index].get_matrix_cols()
    matrix = []
    keymap_len = len(keymap)
    for i in range(keymap_len):
        if i % col_limit == 0:
            if i >= col_limit:
               matrix.append(row)
            row = []
            row.append(i)
        else:
            row.append(i)
    matrix.append(row)
    matrix_template = layout_template('!MATRIX LAYOUT')
    matrix_template.set_layout(matrix)

    template_list.append(matrix_template)
  
    return template_list            

def merge_layout_template(layers, templates, select=-1):

    if select >= 0:
        index = select
    if templates is None or len(templates) == 0:
        temp = build_layout_from_keymap(layers)
        merge_layout_template(layers, temp)
    if len(templates) == 1:
        index = 0
    elif select < 0:
        print('Select KEYMAP template:')
        for i, templ in enumerate(templates):
            print('['+str(i)+']\t'+ templ.get_name())

        while True:
            try:
                index = int(input())
            except ValueError:
                error_out(['Enter valid template number'])
                continue

            if index >= len(templates) or index < 0:
                error_out(['Enter valid template number'])
                continue
            else:
                break
    note_out(['Building with template: '+templates[index].get_name()])
    for x, l in enumerate(layers):    
        layout_name = templates[index].get_name()
        layout_template = templates[index].get_layout()
        layout = copy.deepcopy(layout_template)
        keycode_array = l.get_keymap()
        max_index = len(keycode_array)

        try:
            for i, rows in enumerate(layout_template):
                for j, ind in enumerate(rows):
                    if ind < max_index:
                        layout[i][j] = keycode_array[ind]
                    elif layout_name != '!MATRIX LAYOUT':
                        warning_out(['Corrupt/incompatible layout template or keymap', 
                            'Invalid array value: '+str(ind),
                            'Trying again with default matrix layout...'])
                        matrix_template = build_layout_from_keymap(layers, x)
                        merge_layout_template(layers, matrix_template)
                        exit()
                    else:
                        error_out(['Corrupt/incompatible keymap',
                            'Invalid array value: '+str(ind)])
                        exit()
        except TypeError:
            error_out(['Corrupt layout template, invalid array index: '+str(ind)])
            exit()
                    
        col_limit = l.get_matrix_cols()
        layout_template = convert_keyplus_matrix(layout_template, col_limit)
          
        l.set_layout(layout)
        l.set_template(layout_template)
        note_out(['Layer '+l.get_name()])
        """
        print(l.get_name())
        for row in layout: #l.get_keymap()
            print(row)

        for row in layout_template: #l.get_template()
            print(row)
        """

def convert_keyplus_matrix(matrix, col_limit):

     m = copy.deepcopy(matrix)
     for i,row in enumerate(matrix):
            for j,col in enumerate(row):
                int(col)
                r = col // col_limit
                c = col % col_limit
                m[i][j] = 'r'+str(r)+'c'+str(c)
     return m
