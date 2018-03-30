import copy

from kb_classes import *
from keycodes import *

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
    print('________________________________________')
    return layers


def func(qmk_func, layer_list):
    # Currently only handles layer switching functions
    try:
        q_index = qmk_func.index('(')+1
        qfunc = qmk_func[:q_index]
        layer_name = qmk_func[q_index:-1]
        layer = str(layer_list.index(layer_name))
        keyp_func = qmk_to_keyp_func[qfunc]+layer
    except KeyError:
        print('Invalid func: ['+qmk_func+'] - set to trns')
        keyp_func = 'trns'

    except ValueError:
        print('Invalid func: ['+qmk_func+'] - set to trns')
        keyp_func = 'trns'

    return keyp_func


def keycode(qmk_kc):

    try:
        keyp_kc = qmk_to_keyp[qmk_kc]
    except KeyError:
        print('Invalid kc: ['+qmk_kc+'] - set to trns')
        #keyp_kc = '____'
        keyp_kc = 'trns'
    return keyp_kc


def build_layout_from_keymap(layers):
    template_list = []

    keymap = layers[0].get_keymap()
    col_limit = layers[0].get_matrix_cols()
    
    matrix = []
    keymap_len = len(keymap)
    for i in range(keymap_len):
        if i % col_limit == 0:
            if i > col_limit:
               matrix.append(row)
            row = []
            row.append(i)
        else:
            row.append(i)
    matrix_template = layout_template('MATRIX LAYOUT')
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
        print('Building with template: '+templates[0].get_name())
    elif select < 0:
        print('Select KEYMAP template:')
        for i, templ in enumerate(templates):
            print('['+str(i)+']\t'+ templ.get_name())

        while True:
            try:
                index = int(input())
            except ValueError:
                print('err: Enter valid template number')
                continue

            if index >= len(templates) or index < 0:
                print('err: Enter valid template number')
                continue
            else:
                break

    for l in layers:    
    
        layout_template = templates[index].get_layout()
        layout = copy.deepcopy(layout_template)
        keycode_array = l.get_keymap()
        max_index = len(keycode_array)

        for i, rows in enumerate(layout_template):
            for j, ind in enumerate(rows):
                if ind < max_index:
                    layout[i][j] = keycode_array[ind]
                else:
                    print('error has occured: invalid array value: '+str(ind))
                    print('fatal error: corrupt layout template or keymap')
                    raise IndexError('Layout contains index which is out of range')
                    
        col_limit = l.get_matrix_cols()
        layout_template = convert_keyplus_matrix(layout_template, col_limit)

        l.set_keymap(layout)
        l.set_matrix(layout_template)

        """
        print(l.get_name())
        layerprint = l.get_keymap()
        
        for row in layerprint:
            print(row)

        for row in layout_template:
            print(row)
       """
    print('SUCCESS!')


def convert_keyplus_matrix(matrix, col_limit):

     m = copy.deepcopy(matrix)
     for i,row in enumerate(matrix):
            for j,col in enumerate(row):
                int(col)
                r = col // col_limit
                c = col % col_limit
                m[i][j] = 'r'+str(r)+'c'+str(c)
     return m
