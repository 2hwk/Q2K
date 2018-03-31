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

def read_config_header(data):
    matrix_pins = []
    matrix_row_pins = []
    matrix_col_pins = []
    
    LBRAC, RBRAC, COMMA = map(pp.Suppress, "{},")
    define_rows = pp.Suppress(pp.Literal('#define MATRIX_ROW_PINS'))
    define_cols = pp.Suppress(pp.Literal('#define MATRIX_COL_PINS'))
    pincode = pp.Word(pp.alphanums) | pp.Word(pp.nums)

    array = LBRAC + pp.ZeroOrMore(pincode + pp.Optional(COMMA)) + RBRAC
    matrix_rows = pp.Group(define_rows + LBRAC + pp.ZeroOrMore(pincode + pp.Optional(COMMA)) + RBRAC)
    matrix_cols = pp.Group(define_cols + LBRAC + pp.ZeroOrMore(pincode + pp.Optional(COMMA)) + RBRAC)

    for tokens, start, stop in matrix_rows.scanString(data):
        matrix_row_pins = list(tokens[0])
    for tokens, start, stop in matrix_cols.scanString(data):
        matrix_col_pins = list(tokens[0])   

    if matrix_row_pins and matrix_col_pins:
        matrix_pins.append(matrix_row_pins)
        matrix_pins.append(matrix_col_pins)

    return matrix_pins


def read_keymap(data):
    layer_list = []    
    LBRAC, RBRAC,EQ, COMMA = map(pp.Suppress,"{}=,")

    integer = pp.Word(pp.nums)
    comment = pp.ZeroOrMore(pp.Suppress(pp.Group('#' + integer + pp.Word(pp.printables) + pp.Optional(integer))))
    keycode = pp.Word(pp.alphanums+'_'+'('+')')
    layer_string = pp.Word(pp.printables) | pp.Word(pp.nums)

    keycode_list = pp.Group(pp.ZeroOrMore(keycode + pp.Optional(COMMA)))
    row = comment + LBRAC + keycode_list + RBRAC + comment

    layern = pp.Group( layer_string + EQ)
    km_layer_data = comment + LBRAC + pp.OneOrMore(row + pp.Optional(COMMA)) + RBRAC + comment
    km_layer = pp.Optional(layern('layer_name')) + comment + km_layer_data('layer') + pp.Optional(COMMA) + comment  

    layer_list = []
    num_col = 0
    layer_index = -1
    for tokens, start, stop in km_layer.scanString(data):
        layer_index += 1
        if tokens.layer_name == '':
            curr_layer = keymap_layer(str(layer_index))
        else:
            curr_layer = keymap_layer(tokens.layer_name[0][1:-1]) 

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
    
    for layer in layer_list:
        print(layer.get_name()) 
        print(layer.get_keymap())
    
    if not layer_list:
        print('*** Parsed and found no keymap')
        print('*** Failed to parse keymap file')
        #raise RuntimeError('Failed to parse keymap file')
        exit()
    else:
        return layer_list


def read_layout_header(s):
    # Maybe not the most robust, can be improved
    layout_read = False
    array_read = False
    template_list = []
    try:
        with open(s, 'r') as f:
            for line in f:
                line = re.sub('\s', '', line)
                if not layout_read and not array_read:
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
                elif layout_read:
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
                                print('**# Current file '+s+' failed conversion')
                                return
                        curr_template.add_layout_line(line)
                    else:
                        # Syntax error in file
                        print('Missing \ in file '+s)
                        #raise SyntaxError('Missing \ in file '+s)
                        break
                elif array_read:
                    if line.endswith('\\'):
                        line = re.sub('\\\|[(){}]', '', line)
                        line = clean_split(line, ',')
                        for i, code in enumerate(line):
                            line[i] = re.sub('^[^##]*##', '', code)         # Remove chars before ##
                        for element in line:
                            if len(element) > 9:  
                                print('*** Current file '+s+' failed conversion')
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
                    print('*** Missing keycode key ['+col+'] in '+s)
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
                        print('*** Array key recovery failed')
                        raise RuntimeError('Missing macro variable in: '+s)

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
