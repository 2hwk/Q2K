import yaml, glob, os, errno

from kb_classes import *
from kb_global import *
from keycodes import keyplus_yaml_template

def write_info(kb_info_yaml):
    # Parse Keyboard Names With Revisions First    
    for fn in glob.glob(QMK_DIR+'keyboards/**/rev*/.', recursive=True):
        fullpath = fn[:-2]
        kbname_w_rev = fullpath.replace(QMK_DIR+'keyboards/','')

        folders = kbname_w_rev.split('/')     
        rev = folders[-1]
        kbname = '/'.join(folders[:-1])
        kblibs = []
        for f in folders[:-1]:
            kblibs.append(f)

        for kbc in KBD_LIST:
            if kbc.get_name() == kbname:
                kbc.add_rev_list(rev)
                break
        else:
            # New kb_info class
            kbclass = kb_info(kbname)
            kbclass.set_libs(kblibs)
            kbclass.add_rev_list(rev)
            KBD_LIST.append(kbclass)

    # Then do the rest (together with keymaps)
    for fn in glob.glob(QMK_DIR+'keyboards/**/keymaps/**/keymap.c', recursive=True):
        fullpath = fn[:-9]
        keyboard_w_keymap = fullpath.replace(QMK_DIR+'keyboards/','')

        arg = keyboard_w_keymap.split('/keymaps/')
        kbname = arg[0]
        checkname = arg[0].split('/')
        if len(checkname) > 1:
            for i, folder in enumerate(checkname):
                if folder[:3] == 'rev':
                    kbnameL = []
                    for f in checkname[:i]:
                        kbnameL.append(f)
                    kbname= '/'.join(kbnameL)

        kbmap = arg[1]
        folders = kbname.split('/')
        kblibs = []
        #path = ''
        for f in folders:
            kblibs.append(f)
            
        for kbc in KBD_LIST:
            if kbc.get_name() == kbname:
                kbc.add_keymap_list(kbmap)
                break
        else:
            # New kb_info class
            kbclass = kb_info(kbname)
            kbclass.add_keymap_list(kbmap)
            kbclass.add_rev_list('n/a', True)
            kbclass.set_libs(kblibs)
            KBD_LIST.append(kbclass)

    # Dump KBD_LIST to text file for faster processing in future
    dump_info(kb_info_yaml)

def dump_info(kb_info_yaml):

    kb_info_path = '/'.join(kb_info_yaml.split('/')[:-1])
    if not os.path.exists(kb_info_path):
        try:
            os.makedirs(kb_info_path)
        except OSError as e:
            if e.errno != errno.EEXIST and os.path.isdir(kb_info_path):
                raise

    with open(kb_info_yaml, 'w') as f:
        yaml.dump(KBD_LIST, f)
    #print(yaml.dump(KBD_LIST))

def create_keyplus_yaml(kbc, printout=False):

    # Can't simply dump to yaml as we want to keep layout (array) as a human readable matrix (2D 'array').
    kb_n = kbc.get_name()
    rev_n = kbc.get_rev()
    keymap_n = kbc.get_keymap()

    rev = kbc.get_rev_info(rev_n)
    matrix = rev.get_matrix_pins()
    layers = rev.get_layout() 

    template_matrix = layers[0].get_template()
    name = '"'+kb_n+'_'+rev_n+'"'
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
            layout += '\n        '
            for keycode in row:
               layout += keycode+', '
        layout +='\n        ]\n      ],\n'

    # Load Template
    output_yaml_info = keyplus_yaml_template
    output_yaml_info = output_yaml_info.replace('<KB_NAME>', name)
    output_yaml_info = output_yaml_info.replace('<LAYOUT_NAME>', keymap_n)                              
    output_yaml_info = output_yaml_info.replace('<ROWS>', rows)                                 
    output_yaml_info = output_yaml_info.replace('<COLS>', cols)
    output_yaml_info = output_yaml_info.replace('<MATRIX_MAP>', template)
    output_yaml_info = output_yaml_info.replace('<LAYOUT>', layout)

    kblibs = kbc.get_libs()
    path_list = kblibs + [ rev_n, keymap_n]
    output_path = '_'.join(path_list)
    output_yaml = OUT_DIR+output_path+'.yaml'

    if not os.path.exists(OUT_DIR):
        try:
            os.makedirs(OUT_DIR)
        except OSError as e:
            if e.errno != errno.EEXIST and os.path.isdir(output_path):
                raise

    with open(output_yaml, 'w') as f:
        f.write(output_yaml_info)

    if printout:
        print(output_yaml_info)
    




