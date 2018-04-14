#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2018 2Cas
# Licensed under the MIT license (http://opensource.org/licenses/MIT)

import re, copy
import pyparsing as pp

from q2k.classes import *
from q2k.console import error_out, warning_out, note_out

def clean_split(line, char):

    newline = line.split(char)
    while '' in newline:
        newline.remove('')
        if not newline:
            newline = []
    return newline


def read_rules_mk(path):
    mcu_list = []
    try:
        with open(path, 'r') as f:
            data = str(f.read())
    except FileNotFoundError:
        warning_out(['Rules.mk not found in '+path,
            'Trying a different path...'])
        return
    
    EQUALS = pp.Suppress('=')
    mcu_tag = pp.Suppress(pp.Literal('MCU'))
    mcu_type = pp.Word(pp.alphanums+'_')

    mcu = mcu_tag + EQUALS + mcu_type('mcu')
    mcu.ignore('#'+pp.restOfLine)

    for tokens, start, end in mcu.scanString(data):
        mcu_list.append(tokens.mcu)
    
    return mcu_list


def read_config_header(data):

    data = str(data)
    matrix_pins = []
    matrix_row_pins = []
    matrix_col_pins = []
    
    LBRAC, RBRAC, COMMA = map(pp.Suppress, "{},")
    define_rows = pp.Suppress(pp.Literal('#define MATRIX_ROW_PINS'))
    define_cols = pp.Suppress(pp.Literal('#define MATRIX_COL_PINS'))
    pincode = pp.Word(pp.alphanums) | pp.Word(pp.nums)

    array = LBRAC + pp.ZeroOrMore(pincode + pp.Optional(COMMA)) + RBRAC
    matrix_rows = define_rows + LBRAC + pp.ZeroOrMore(pincode + pp.Optional(COMMA)) + RBRAC
    matrix_cols = define_cols + LBRAC + pp.ZeroOrMore(pincode + pp.Optional(COMMA)) + RBRAC

    for tokens, start, stop in matrix_rows.scanString(data):
        matrix_row_pins = list(tokens)
    for tokens, start, stop in matrix_cols.scanString(data):
        matrix_col_pins = list(tokens)   

    if matrix_row_pins and matrix_col_pins:
        matrix_pins.append(matrix_row_pins)
        matrix_pins.append(matrix_col_pins)

    return matrix_pins


def read_keymap(data):

    data = str(data)
    layer_list = []    
    LBRAC, RBRAC,EQ, COMMA = map(pp.Suppress,"{}=,")

    integer = pp.Word(pp.nums)
    keycode = pp.Word(pp.alphanums+'_'+'('+')')
    layer_string = pp.Word(pp.printables) | pp.Word(pp.nums)

    keycode_list = pp.Group(pp.ZeroOrMore(keycode + pp.Optional(COMMA)))
    row = LBRAC + keycode_list + RBRAC

    layern = layer_string('layer_name') + EQ
    km_layer_data = LBRAC + pp.OneOrMore(row + pp.Optional(COMMA)) + RBRAC
    km_layer = pp.Optional(layern) + km_layer_data('layer') + pp.Optional(COMMA)
    km_layer.ignore(pp.cppStyleComment+pp.pythonStyleComment)

    layer_list = []
    num_col = 0
    layer_index = -1
    for tokens, start, stop in km_layer.scanString(data):
        layer_index += 1
        if tokens.layer_name == '':
            curr_layer = keymap_layer(str(layer_index))
        else:
            curr_layer = keymap_layer(tokens.layer_name[1:-1]) 

        for row in tokens.layer:
            buff = ''
            for i, element in enumerate(row):
                if ')' in element and '(' not in element:
                    func = ''
                    func = row[i-1]+','+row[i] 
                    del row[i-1]
                    i -= 1
                    del row[i]
                    row.insert(i, func)

            num_col = len(row)
            curr_layer.add_keymap_item(list(row))
        
        curr_layer.set_matrix_cols(num_col)
        layer_list.append(curr_layer)
    """
    for layer in layer_list:
        print(layer.get_name()) 
        print(layer.get_keymap())
    """
    if not layer_list:

        error_out(['Parsed and found no keymap',
            'Failed to parse keymap file'])
        exit()
    else:
        return layer_list

def read_layout_header(path):

    template_list = []
    try:
        with open(path, 'r') as f:
            data = str(f.read())
    except FileNotFoundError:
        warning_out(['Layout header not found in '+path,
            'Trying a different path...'])
        return
    
    LPAREN, RPAREN, LBRAC, RBRAC, COMMA = map(pp.Suppress, "(){},")
    BSLASH = pp.Suppress(pp.Literal('\\'))

    define = pp.Suppress(pp.Literal('#define'))
    name = pp.Word(pp.alphanums+'_')
    macrovar = pp.Word(pp.alphanums+'_#')
    layout_row = pp.Group(pp.OneOrMore(macrovar + pp.Optional(COMMA)) + pp.ZeroOrMore(BSLASH))
    layout =  LPAREN + pp.ZeroOrMore(BSLASH) + pp.OneOrMore(layout_row) + RPAREN

    matrix_row = pp.ZeroOrMore(BSLASH) + pp.Optional(LBRAC) +  pp.ZeroOrMore(BSLASH) + pp.OneOrMore(macrovar + pp.Optional(COMMA)) + pp.ZeroOrMore(RBRAC) + pp.Optional(COMMA) + pp.ZeroOrMore(BSLASH)
    matrix = pp.ZeroOrMore(BSLASH) + LBRAC +  pp.ZeroOrMore(BSLASH) + pp.OneOrMore(matrix_row) +  pp.ZeroOrMore(BSLASH) + RBRAC +  pp.ZeroOrMore(BSLASH)

    header = define + name('name') + pp.ZeroOrMore(BSLASH) + layout('layout') + pp.ZeroOrMore(BSLASH) + matrix('array')
    header.ignore(pp.cStyleComment)

    for tokens, start, end in header.scanString(data):
        curr_template = layout_template(tokens.name)

        for row in tokens.layout:
            layout_row = list(row)
            curr_template.add_layout_line(layout_row)
       
        array = list(tokens.array)
        for i, element in enumerate(array):
            array[i] = re.sub('^[^##]*##', '', element) 

        curr_template.set_array(array)
        template_list.append(curr_template)
    
    # Translate macro k vars to array indices
    for x, t in enumerate(template_list):
        layout = t.get_layout()
        array = t.get_array()
        for i, row in enumerate(layout):
            for j, col in enumerate(row):
                try:
                    layout[i][j] = array.index(col)
                except ValueError:
                    warning_out(['Missing macro variable ['+col+'] in '+path])
                    # Try to recover using a different keycode array
                    for y, t2 in enumerate(template_list):                    
                        array2 = t2.get_array()
                        if len(array2) != len(array) or x == y:
                            continue
                        try:
                            index = array2.index(col)
                            layout[i][j] = index
                            array[index] = col                            
                            warning_out(['Macro variable recovery succeeded'])
                            break
                        except ValueError:
                            continue
                    if layout[i][j] == col:
                        error_out(['Array key recovery failed',
                            'Missing macro variable in: '+path])
                        #exit()
        t.set_layout(layout)

    """
    for k in template_list:
        layout = k.get_layout()
        array = k.get_array()
        print(k.get_name())
        for line in layout:
            print(line)
        print('array')
        print(array)
    """
    return template_list
