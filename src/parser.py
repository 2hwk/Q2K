# Q2K Keyboard Map parSer
import re
import pyparsing as pp

from kb_classes import *
from kb_global import *

from convert import convert_keymap

def clean_split(li, ch):

    newli = li.split(ch)
    while '' in newli:
        newli.remove('')
        if len(newli) == 0:
            del newli
            newli = []
    return newli

#def read_config_header(s):

def read_kb_keymap(kbc):

    rev = kbc.get_rev()
    revObj = kbc.get_rev_info(rev)
    km_loc = revObj.get_output_keymap()

    layer_list = read_keymap(km_loc)
    revObj.set_layout(layer_list)

    return layer_list

def read_keymap(s):

    layer_list = []    
    try:       
        with open(s, 'r') as f:
            data = f.readlines()
            new_data = []

            for i, line in enumerate(data):
               if line.startswith('#') == False:
                   new_data.append(line)

            data = ''.join(new_data)
            data_list = []

            LBRAC, RBRAC,EQ, COMMA = map(pp.Suppress,"{}=,")
            keycode = pp.Word(pp.alphas+'_', pp.alphanums+'_'+'('+')')
            headfunc_s = pp.Literal('const uint16_t')
            headfunc_m = pp.Literal('PROGMEM')
            headfunc_e = pp.Literal('keymaps[][MATRIX_ROWS][MATRIX_COLS]')
            header = pp.Group(headfunc_s + pp.Optional(headfunc_m) + headfunc_e + EQ + LBRAC)

            layer_string = pp.Word(pp.printables) | pp.Word(pp.nums)
            layern = pp.Group( layer_string + EQ)

            keycode_list = pp.Group(keycode + pp.ZeroOrMore(COMMA + keycode) + pp.Optional(COMMA))
            row = LBRAC + keycode_list + RBRAC
            keym_layer = LBRAC + pp.OneOrMore(row + pp.Optional(',')) + RBRAC

            km_func = pp.Suppress(header) + pp.OneOrMore( pp.Optional(layern) + keym_layer + pp.Optional(COMMA) ) + RBRAC

            for tokens, start, stop in km_func.scanString(data):
                data_list = tokens

    except FileNotFoundError:
       print('File not found - '+s)
       print('Parsing cannot continue without keymap, terminating')
       sys.exit()

    curr_layer = keymap_layer()
    curr_layer_name = '0'
    curr_keymap = []
    layer_index = 0
    col_len = 0

    next_layer = False
    layer_has_name = False
    
    for row in data_list:
        # Hit a comma, go to next row
        if row == ',':
            next_layer = False
            continue
        
        elif len(row) == 1 and len(row[0]) > 1 and row[0][0] == '[' and row[0][-1] == ']':
             # is a layer name
            if next_layer:
                 curr_layer = keymap_layer(curr_layer_name)
                 curr_layer.set_keymap(curr_keymap)
                 curr_layer.set_matrix_cols(col_len)
                 layer_list.append(curr_layer)
                 curr_keymap = []
            layer_has_name = True
            next_layer = False
            curr_layer_name = row[0][1:-1]
            layer_index += 1
            continue
        # append to current keymap
        elif next_layer == False:
            curr_keymap = curr_keymap + list(row)
            col_len = len(row)
            next_layer = True
        # exit and append keymap to layer list
        elif next_layer == True:
            layer_has_name = False
            curr_layer = keymap_layer(curr_layer_name)
            curr_layer.set_keymap(curr_keymap)
            curr_layer.set_matrix_cols(col_len)
            layer_list.append(curr_layer)
            layer_index += 1
            # ^ Previous Lines
            curr_layer_name = str(layer_index)
            curr_keymap = []
            # < Current Line
            curr_keymap = curr_keymap + list(row)
            next_layer = True
       
    curr_layer = keymap_layer(curr_layer_name)
    curr_layer.set_keymap(curr_keymap)
    curr_layer.set_matrix_cols(col_len)
    layer_list.append(curr_layer)

    if len(layer_list) == 0 or layer_list is None:
        print('Parsed and found no keymap')
        raise RuntimeError('Failed to parse keymap file '+s)

    layer_list = convert_keymap(layer_list)
    """
    for layer in layer_list:
        print(layer.get_name()) 
        print(layer.get_keymap())
    """
    return layer_list

def find_layout_header(kbc):

    rev = kbc.get_rev()
    revObj = kbc.get_rev_info(rev)
    # qmk/keyboards/
    kblibs = list(kbc.get_libs())
    if rev != '':
        kblibs.append(rev)
    qdir = QMK_DIR +'keyboards/'

    folders = []
    path = ''
    for kbl in kblibs:
        path += kbl+'/'
        folders.append(path)

    for kbl in reversed(folders):
        kbl_f = kbl.split('/')
        kb_h = kbl_f[-2]        
        kb_h += '.h'

        path = qdir+kbl+kb_h
        
        m_l = read_layout_header(path)
        if m_l is None or len(m_l) < 1:
            continue
        else:
            revObj.set_templates(m_l)
            return m_l
    print('keyboard layout header not found for '+kbc.get_name())
    print('reverting to basic layout') 
    return


def read_layout_header(s):
    # Maybe not the most robust, can be improved
    layout_read = False
    array_read = False
    template_list = []
    try:
        with open(s, 'r') as f:
            for line in f:
                line = re.sub('\s', '', line)
                if layout_read == False and array_read == False:
                    # ------- Find layout -------------
                    if line.startswith('#define') and line.endswith('(\\'): #define ___ (\ macro
                        line = line.replace('#define','')
                        layout_name = line[:-2]                # Strip (\, save as curr layout name
                        curr_template = layout_template(layout_name)
                        layout_read = True
                        continue
                    # Array Start (case 2) cont.
                    # ) \ 
                    # { \ <- here 
                    # < array >
                    if line.startswith('{\\'):
                        array_read = True
                        continue
                    if line.endswith('(\\'):
                        array_read = True
                        continue
                elif layout_read == True:
                    if line == '\\' or line.startswith('//') or (line.startswith('/*') and line.endswith('*/\\')):
                        continue
                    # If Layout ended: go to array
                    if line.startswith(')\\') or line.endswith(')\\'):
                        layout_read = False
                        # Array Start (case 2)
                        # ) \ <- here
                        # { \ 
                        # < array >
                        template_list.append(curr_template)
                        continue
                    elif line.startswith('){\\'):
                        layout_read = False
                        # Array Start (case 1)
                        # ) { \ <- here
                        # < array >
                        # array started, so end layout reading and push to template_list
                        template_list.append(curr_template)
                        # ----
                        array_read = True
                        continue
                    # else layout has not ended
                    elif line.endswith('\\'):
                        line = line.replace('\\','')
                        line = clean_split(line, ',')
                        for element in line:
                            if len(element) > 15:  
                                print('Current file '+s+' failed conversion')
                                return
                        curr_template.add_layout_line(line)
                    else:
                        # Syntax error in file
                        print('Missing \ in file '+s)
                        #raise SyntaxError('Missing \ in file '+s)
                        break
                elif array_read == True:
                    if line.endswith('\\'):
                        line = re.sub('\\\|[(){}]', '', line)
                        line = clean_split(line, ',')
                        for i, code in enumerate(line):
                            line[i] = re.sub('^[^##]*##', '', code)         # Remove chars before ##
                        for element in line:
                            if len(element) > 9:  
                                print('Current file '+s+' failed conversion')
                                return
                        curr_template.add_array_item(line)
                    else:
                        array_read = False
                #print(line)
    except FileNotFoundError:
        #print('File not found - '+s)
        list = []
        return list


    # translate macro k vars to array indices
    for x, t in enumerate(template_list):
        layout = t.get_layout()
        array = t.get_array()
        #print(k.get_name())
        for i, row in enumerate(layout):
            for j, col in enumerate(row):
                try:
                    layout[i][j] = array.index(col)
                except ValueError:
                    print('Missing keycode key ['+col+'] in '+s)
                    # Try to recover using a different keycode array
                    for y, t2 in enumerate(template_list):                    
                        array2 = t2.get_array()
                        if len(array2) != len(array) or x == y:
                            continue
                        try:
                            index = array2.index(col)
                            layout[i][j] = index
                            array[index] = col                            
                            print('Array key recovery succeeded!')
                            break
                        except ValueError:
                            continue
                    if layout[i][j] == col:
                        print('Array key recovery failed')
                        raise RuntimeError('missing macro variable in: '+s)

                    #print("File: "+s)
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
