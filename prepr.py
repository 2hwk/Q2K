# Q2K Keyboard Map parSer

import sys, os, argparse
import subprocess, glob
import yaml
import re

from kb_classes import *
from v3parser import *
from convert import *


KBD_LIST = []
#N_MCU = [ "chibios_test", "ergodox_infinity", "handwired/magiforce61", "handwired/MS_sculpt_mobile", "infinity60", "jm60", "k_type", "kinesis", "lfkeyboards/smk65", "lfkeyboards/lfk87", "mechmini/v1", "subatomic", "tkc1800", "uk78", "vision_division", "whitefox"]
#V_USB = [ "bfake", "bmini", "jj40", "mt40", "pearl", "ps2avrGB", "ymd96" ]

#QMK_DIR = '/mnt/c/Users/Evan/Documents/qmk/qmk_firmware-master/'
QMK_DIR = 'qmk/'
KB_INFO = 'src/kb_info.yaml'
OUTPUT_DIR = 'out/'

def print_keyboard_list():

    printkb = []
    for kbc in KBD_LIST:
        printkb.append(kbc.get_name())
    print(printkb)    
# Q2K Keyboard Map parSer

import sys, os, argparse
import subprocess, glob
import yaml
import re

from kb_classes import *
from v3parser import *
from convert import *


KBD_LIST = []
#N_MCU = [ "chibios_test", "ergodox_infinity", "handwired/magiforce61", "handwired/MS_sculpt_mobile", "infinity60", "jm60", "k_type", "kinesis", "lfkeyboards/smk65", "lfkeyboards/lfk87", "mechmini/v1", "subatomic", "tkc1800", "uk78", "vision_division", "whitefox"]
#V_USB = [ "bfake", "bmini", "jj40", "mt40", "pearl", "ps2avrGB", "ymd96" ]

#QMK_DIR = '/mnt/c/Users/Evan/Documents/qmk/qmk_firmware-master/'
QMK_DIR = 'qmk/'
KB_INFO = 'src/kb_info.yaml'
OUTPUT_DIR = 'out/'

def print_keyboard_list():

    printkb = []
    for kbc in KBD_LIST:
        printkb.append(kbc.get_name())
    print(printkb)    


def print_keymap_list(kb):

    printkm = []
    for kbc in KBD_LIST:


def print_keymap_list(kb):

    printkm = []
    for kbc in KBD_LIST:
        if kbc.get_name() == kb:
            for km in kbc.get_keymap_list():
                printkm.append(km)
    print(printkm)


def print_revision_list(kb):

    printr = []
    for kbc in KBD_LIST:
        if kbc.get_name() == kb:
            for r in kbc.get_rev_list():
                printr.append(r)
    if len(printr) > 0:
        print(printr)
    else:
        print("None")


def search_keyboard_list(s):

    printkb = []
    for kbc in KBD_LIST:
        kbc_name = kbc.get_name()
        if kbc_name.find(s) != -1:
            printkb.append(kbc_name)
    print(printkb)
    

def check_parse_argv(kb, km='default', rev=''):

    for kbc in KBD_LIST:
        # Check keyboard
        if kbc.get_name() == kb:
            # Check Keymap
            if km not in kbc.get_keymap_list():
                print('*** Invalid Keymap - '+km)
                print('Valid Keymaps:')
                print_keymap_list(kb)
                sys.exit()
            # Check Revision
            # Case 1: Have Revisions
            if len(kbc.get_rev_list()) != 0 and rev not in kbc.get_rev_list():
                print('*** Invalid Revision - '+rev)
                print('Valid Revisions:')
                print_revision_list(kb)
                sys.exit()
            # Case 2: No Revisions
            elif len(kbc.get_rev_list()) == 0 and rev != '':
                print('*** Invalid Revision - '+rev)
                print('Valid Revisions:')
                print_revision_list(kb)
                sys.exit()
            # If KB matches, and KM and REV do not conflict, set values and return kb_info class
            kbc.set_rev(rev)
            #if rev != '':
                #kbc.add_lib(rev)
            kbc.set_keymap(km)
            return kbc
        else:
            continue
    
    # If we finish loop with no matches, keyboard name must be invalid
    print('*** Invalid Keyboard Name - '+kb)
    print('Valid Names:')
    print_keyboard_list()
    sys.exit()

def init_cache_keymap(kbc):

    kb = kbc.get_name()+'/'
    km = kbc.get_keymap()+'/keymap.c'
    rev = kbc.get_rev()
    revObj = kbc.get_rev_info(rev)

    if rev == '':
        output = OUTPUT_DIR+kb+km
    else:
        rev += '/'
        output = OUTPUT_DIR+kb+rev+km

    if os.path.isfile(output):
        print('Using cached '+km+' file')  
    else:  
        print('Generating '+km+'...')
        preproc_keymap(kbc)

    revObj.set_output_keymap(output)
    #return output


def preproc_keymap(kbc):

    qdir = QMK_DIR +'keyboards/'
    
    kb = kbc.get_name()+'/'
    km = kbc.get_keymap()+'/keymap.c'
    kblibs = list(kbc.get_libs())
    if kbc.get_rev() != '':
        kblibs.append(rev)
        rev = kbc.get_rev()+'/'
    else:
        rev = ''

    # GCC -E
    cc = ['cpp']
    # -D
    kbdefine = 'KEYBOARD_'+'_'.join(kblibs)
    # -ILIBS 
    # This is a bit dubious (using empty header files to replace core qmk headers) but it works fine I guess?
    locallib = 'src/include'
    libs = ['-D', kbdefine, '-I'+locallib]
    path = qdir
    for kbl in kblibs:
        kbl += '/'
        path += kbl
        libs.append('-I'+path)
    # KEYMAP
    keym = qdir+kb+'keymaps/'+km
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
    print(argv)
    subprocess.call(argv)


def init_cache_info(kb_info_yaml):

    if os.path.isfile(kb_info_yaml):
        global KBD_LIST
        try:
            with open(kb_info_yaml, 'r') as f:
                KBD_LIST = yaml.load(f)
                print('Using Cached kb_info.yaml')

        except FileNotFoundError:
            print('Failed to load kb_info.yaml')
            print('Generating new kb_info.yaml...')
            write_info(kb_info_yaml)

        except ImportError:
            print('Failed to load kb_info.yaml')
            print('Generating new kb_info.yaml...')
            write_info(kb_info_yaml)
    else:
            print('Generating kb_info.yaml...')
            write_info(kb_info_yaml)


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
    dump_yaml(kb_info_yaml)

def dump_yaml(kb_info_yaml):

    with open(kb_info_yaml, 'w') as f:
        yaml.dump(KBD_LIST, f)
    #print(yaml.dump(KBD_LIST))

def main():

    # Init kb_info file from cache
    init_cache_info(KB_INFO)
    # Read ARGV input from terminaL
    parser = argparse.ArgumentParser(description='Convert AVR C based QMK keymap and matrix files to YAML Keyplus format')
    parser.add_argument('keyboard', metavar='KEYBOARD', nargs='?', default='', help='The name of the keyboard whose keymap you wish to convert')
    parser.add_argument('-m', metavar='keymap', dest='keymap', default='default', help='The keymap folder to reference - default is /default/')
    parser.add_argument('-r', metavar='ver',dest='rev', default='', help='Revision of layout - default is n/a')
    parser.add_argument('-L', dest='listkeyb', action='store_true',help='List all valid KEYBOARD inputs')
    parser.add_argument('-M', dest='listkeym', action='store_true',help='List all valid KEYMAPS for the current keyboard')
    parser.add_argument('-R', dest='listkeyr', action='store_true',help='List all valid REVISIONS for the current keyboard')
    parser.add_argument('-S', metavar='string', dest='searchkeyb', help='Search valid KEYBOARD inputs')
    parser.add_argument('-c', metavar='keymap', type=int, default=-1, dest = 'choosemap', help= 'Select keymap template index')
    args = parser.parse_args()

    if args.listkeyb:
        print_keyboard_list()
        sys.exit()

    if args.listkeym:
        print("Listing keymaps for "+args.keyboard+"...")
        print_keymap_list(args.keyboard)
        sys.exit()

    if args.listkeyr:
        print("Listing revisions for "+args.keyboard+"...")
        print_revision_list(args.keyboard)
        sys.exit()

    if args.searchkeyb:
        print("Searching...")
        search_keyboard_list(args.searchkeyb)
        sys.exit()
    
    # Check the cmd line arguments
    current_kbc = check_parse_argv(args.keyboard, args.keymap, args.rev)

    # Check config.h for matrix pinout

    # Check cache/run preprocessor for keymap.c
    init_cache_keymap(current_kbc)
    #km_loc = init_cache_keymap(current_kbc)
    # Parse this keymap file and return raw layout data
    km_layers = read_kb_keymap(current_kbc)
    #km_layers = read_keymap(km_loc)

    '''
    for l in km_layers:
       print(l.get_name()) 
       print(l.get_keymap())
    '''
    # Find layout templates in <keyboard>.h
    km_template = find_layout_header(current_kbc)
    
    # TO DO: Needs to have an error message!
    # Merge layout templates + arrays from <keyboard>.h with matrix from keymap.c
    if km_template is None or len(km_template) == 0:
        km_template = build_layout_from_keymap(km_layers)
    if args.choosemap >= 0:
        merge_layout_template(km_layers, km_template, args.choosemap)
    else:
        merge_layout_template(km_layers, km_template)
    # needs a version for failure at the <keyboard>.h reading stage
    
    dump_yaml(KB_INFO)


if __name__ == "__main__":
    main()
