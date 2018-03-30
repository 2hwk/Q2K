# Q2K Keyboard Map parSer

import os, errno, yaml, subprocess, glob

from kb_classes import *
from kb_global import *

def preproc_keymap(kbc):

    qdir = QMK_DIR +'keyboards/'
    
    kb = kbc.get_name()+'/'
    km = kbc.get_keymap()+'/keymap.c'
    kblibs = list(kbc.get_libs())
    rev = kbc.get_rev() 
    if rev != '':
        kblibs.append(rev)
        rev += '/'
    else:
        rev = ''

    # GCC -E
    cc = ['avr-gcc', '-E']
    # -D
    kbdefine = 'KEYBOARD_'+'_'.join(kblibs)
    # -ILIBS 
    # This is a bit dubious (using empty header files to replace core qmk headers) but it works fine I guess?
    QMK_KEYBOARD_H = 'QMK_KEYBOARD_H=\"'+kbc.get_name()+'.h\"'
    libs = ['-D', kbdefine, '-D', QMK_KEYBOARD_H, '-I'+LOCAL_INCLUDES]
    path = qdir
    for kbl in kblibs:
        kbl += '/'
        path += kbl
        libs.append('-I'+path)
    # KEYMAP
    keym = qdir+kb+'keymaps/'+km
    if rev != '' and not os.path.isfile(keym):
        keym = qdir+kb+rev+'keymaps/'+km

    # OUTPUT
    output = OUTPUT_DIR+kb+rev+km
    argkm = [keym, '-o', output]
    argv = cc + libs + argkm    # arguments:  cpp, -D [define], [ -I<libs> ], keymap, -o output
    # setup output path
    outputdir = output[:-9]
    if not os.path.exists(outputdir):
        try:
            os.makedirs(outputdir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
    #print(argv)
    subprocess.call(argv)

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
            if e.errno != errno.EEXIST and os.path.isdir(path):
                raise

    with open(kb_info_yaml, 'w') as f:
        yaml.dump(KBD_LIST, f)
    #print(yaml.dump(KBD_LIST))

