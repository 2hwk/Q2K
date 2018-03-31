# Q2K Keyboard Map parSer

import os, errno, subprocess

from kb_classes import *
from kb_global import *

def preproc(kb, kblibs, arg_list):
    qdir = QMK_DIR + 'keyboards/'

    # Setting up -I and custom define options
    cc = ['avr-gcc', '-E']
    kbdefine = 'KEYBOARD_'+'_'.join(kblibs)
    QMK_KEYBOARD_H = 'QMK_KEYBOARD_H=\"'+kb+'.h\"'
    libs = ['-D', kbdefine, '-D', QMK_KEYBOARD_H, '-I'+LOCAL_INCLUDES]
    path = qdir
    for kbl in kblibs:
        kbl += '/'
        path += kbl
        libs.append('-I'+path)
    argv = cc + libs + arg_list
    #print(' '.join(argv))
    try:
        output = subprocess.check_output(argv)
        return output
    except subprocess.CalledProcessError as e:
        err_num = e.returncode
        print(err_num)
        if err_num == 1:
            output = e.output
            return output
        else:
            print('error')
            return

def preproc_header(kbc, path):
    qdir = QMK_DIR +'keyboards/'

    kb = kbc.get_name()
    kblibs = list(kbc.get_libs())
    rev = kbc.get_rev() 
    if rev != '':
        kblibs.append(rev)

    arg = [ '-D', 'QMK_KEYBOARD_CONFIG_H=\"config_common.h\"', '-dD', path ]
    
    output = str(preproc(kb, kblibs, arg)).replace('\\n', ' ')
    return output


def preproc_keymap(kbc):
    qdir = QMK_DIR +'keyboards/'

    kb = kbc.get_name()
    km = kbc.get_keymap()+'/keymap.c'
    kblibs = list(kbc.get_libs())
    rev = kbc.get_rev() 
    if rev != '':
        kblibs.append(rev)

    # KEYMAP
    keym = qdir+kb+'/keymaps/'+km
    if rev != '' and not os.path.isfile(keym):
        keym = qdir+kb+'/'+rev+'/keymaps/'+km

    # OUTPUT
    argkm = [keym]
    output = str(preproc(kb, kblibs, argkm)).replace('\\n', ' ')
    return output
