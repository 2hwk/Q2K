# Q2K Keyboard Map parSer

import sys, os, argparse

from kb_classes import *
from kb_global import * 

from parser import *
from convert import *
from cpp import *

def print_keyboard_list():

    printkb = []
    for kbc in KBD_LIST:
        printkb.append(kbc.get_name())
    print(printkb)    


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


def main():

    # Init kb_info file from cache
    init_cache_info(KB_INFO)
    # Read ARGV input from terminaL
    parser = argparse.ArgumentParser(description='Convert AVR C based QMK keymap and matrix files to YAML Keyplus format')
    parser.add_argument('keyboard', metavar='KEYBOARD', nargs='?', default='', help='The name of the keyboard whose keymap you wish to convert')
    parser.add_argument('-m', metavar='keymap', dest='keymap', default='default', help='The keymap folder to reference - default is /default/')
    parser.add_argument('-r', metavar='ver',dest='rev', default='', help='Revision of layout - default is n/a')
    parser.add_argument('-d', dest='dumpyaml', action='store_true', help='Append results to kb_info.yaml. (For debugging, May cause performance penalty)')
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
    # Recreate the associated functions with pyparsing
    # USE THE GCC PREPROCESSOR TO PROCESS MACROS with -dM
    if km_template is None or len(km_template) == 0:
        km_template = build_layout_from_keymap(km_layers)
    if args.choosemap >= 0:
        merge_layout_template(km_layers, km_template, args.choosemap)
    else:
        merge_layout_template(km_layers, km_template)
    # needs a version for failure at the <keyboard>.h reading stage
    if args.dumpyaml:
        dump_info(KB_INFO)
