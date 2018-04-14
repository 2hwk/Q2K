#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2018 2Cas
# Licensed under the MIT license (http://opensource.org/licenses/MIT)
import argparse
from q2k.classes import *
from q2k.globals import KBD_LIST, KB_INFO, MCU_COMPAT

from q2k.parser import *
from q2k.convert import *
from q2k.cpp import *
from q2k.yaml import *
from q2k.console import error_out, warning_out, note_out
from q2k.json import *

def print_keyboard_list():

    printkb = []
    for kbo in KBD_LIST:
        printkb.append(kbo.get_name())
    print(printkb)    


def print_keymap_list(kb):

    printkm = []
    for kbo in KBD_LIST:
        if kbo.get_name() == kb:
            for km in kbo.get_keymap_list():
                printkm.append(km)
    print(printkm)


def print_revision_list(kb):

    printr = []
    for kbo in KBD_LIST:
        if kbo.get_name() == kb:
            for r in kbo.get_rev_list():
                printr.append(r)
    if len(printr) > 0:
        print(printr)
    else:
        print("None")


def search_keyboard_list(s):

    printkb = []
    for kbo in KBD_LIST:
        kbo_name = kbo.get_name()
        if kbo_name.find(s) != -1:
            printkb.append(kbo_name)
    print(printkb)
    

def check_parse_argv(kb, km='default', rev=''):

    for kbo in KBD_LIST:
        # Check keyboard
        if kbo.get_name() == kb:
            # Check Keymap
            if km not in kbo.get_keymap_list():
                warning_out(['Invalid Keymap - '+km,
                    'Valid Keymaps:'])
                print_keymap_list(kb)
                exit()
            # Check Revision
            # Case 1: Have Revisions
            if len(kbo.get_rev_list()) != 0 and rev not in kbo.get_rev_list():
                error_out(['Invalid Revision - '+rev,
                    'Valid Revisions:'])
                print_revision_list(kb)
                exit()
            # Case 2: No Revisions
            elif len(kbo.get_rev_list()) == 0 and rev != '':
                error_out(['Invalid Revision - '+rev,
                    'Valid Revisions:'])
                print_revision_list(kb)
                exit()
            # If KB matches, and KM and REV do not conflict, set values and return kb_info class
            kbo.set_rev(rev)
            kbo.set_keymap(km)

            return kbo
        else:
            continue
    
    # If we finish loop with no matches, keyboard name must be invalid
    error_out(['Invalid Keyboard Name - '+kb,
        'Valid Names:'])
    print_keyboard_list()
    exit()

def init_cache_info(kb_info_yaml):

    if os.path.isfile(kb_info_yaml):
        global KBD_LIST
        try:
            with open(kb_info_yaml, 'r') as f:
                KBD_LIST = yaml.load(f)
                note_out(['Using cached kb_info.yaml @ '+KB_INFO])

        except FileNotFoundError:
            warning_out(['Failed to load kb_info.yaml',
                'Generating new kb_info.yaml...'])
            write_info(kb_info_yaml)
            
            for kbo in KBD_LIST:
                skip_list = ['bantam44','helix']
                if kbo.get_name() in skip_list:
                    continue
                rev_list = kbo.get_rev_list()
                if not rev_list:
                    #find_rules_mk(kbo)
                    #find_config_header(kbo)
                    find_layout_header(kbo)
                else:
                    for rev in rev_list:
                        kbo.set_rev(rev)
                        #find_rules_mk(kbo)
                        #find_config_header(kbo)
                        find_layout_header(kbo)
                rev = ''
            dump_info(KBD_LIST, KB_INFO)
            

        except ImportError:
            warning_out(['Failed to load kb_info.yaml',
                'Generating new kb_info.yaml...'])
            write_info(kb_info_yaml)

    else:
            write_info(kb_info_yaml)
            '''
            for kbo in KBD_LIST:
                rev_list = kbo.get_rev_list()
                if not rev_list:
                    #find_rules_mk(kbo)
                    #find_config_header(kbo)
                    find_layout_header(kbo)
                else:
                    for rev in rev_list:
                        kbo.set_rev(rev)
                        #find_rules_mk(kbo)
                        #find_config_header(kbo)
                        find_layout_header(kbo)
                rev = ''
            dump_info(KBD_LIST, KB_INFO)
            '''
            note_out(['New kb_info.yaml successfully generated', 'Location: '+KB_INFO])


def find_rules_mk(kbo):
    rev = kbo.get_rev()
    revObj = kbo.get_rev_info(rev)
    kblibs = list(kbo.get_libs())
    if rev != '':
        kblibs.append(rev)

    qdir = QMK_DIR +'keyboards/'
    folders = []
    path = ''

    for kbl in kblibs:
        path += kbl+'/'
        folders.append(path)

    for kbl in reversed(folders):
        rules_mk = 'rules.mk'

        path = qdir+kbl+rules_mk
        mcu_list = read_rules_mk(path)
        if mcu_list:
            revObj.set_mcu_list(mcu_list)
            return mcu_list
        else:
            continue

    warning_out(['Rules.mk not found for '+kbo.get_name()])
    return

def check_mcu_list(kbo):
    kb = kbo.get_name()
    rev = kbo.get_rev()
    revObj = kbo.get_rev_info(rev)
    mcu_list = revObj.get_mcu_list()

    for mcu in mcu_list:
        if mcu in MCU_COMPAT:
            continue
        else:
            warning_out(
                ['Possible MCU incompatability detected', 
                'MCU type: '+mcu+' in '+kb+'/'+rev+' rules.mk', 
                'Currently, keyplus supports only boards with the following microcontrollers:',
                str(MCU_COMPAT),
                'If your board has a MCU on this list then ignore this warning as a false positive',
                'Else layout files produced may not work with keyplus until your board\'s mcu is supported',
                'Press [ENTER] to continue'])
            input()
            return
    note_out(['No MCU incompatability detected'])


def find_config_header(kbo):
    rev = kbo.get_rev()
    revObj = kbo.get_rev_info(rev)
    kblibs = list(kbo.get_libs())
    if rev != '':
        kblibs.append(rev)

    qdir = QMK_DIR +'keyboards/'
    folders = []
    path = ''

    for kbl in kblibs:
        path += kbl+'/'
        folders.append(path)

    for kbl in reversed(folders):
        config_h = 'config.h'

        path = qdir+kbl+config_h
        data = preproc_header(kbo, path)
        matrix_pins = read_config_header(data)
        if matrix_pins:
            revObj.set_matrix_pins(matrix_pins[0], matrix_pins[1])
            note_out(['Matrix pinout data found @ '+path])
            return matrix_pins
        else:
            continue

    warning_out(['Config.h header not found for '+kbo.get_name(),
        'Matrix row/col pins must be provided manually!']) 

    return


def preproc_read_keymap(kbo):
    rev = kbo.get_rev()
    revObj = kbo.get_rev_info(rev)

    data = preproc_keymap(kbo)
    layer_list = read_keymap(data)
    revObj.set_layout(layer_list)

    return layer_list


def find_layout_header(kbo):

    rev = kbo.get_rev()
    revObj = kbo.get_rev_info(rev)
    # qmk/keyboards/
    kblibs = list(kbo.get_libs())
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
        #data = preproc_header(kbo, path)
        #matrix_layout = read_layout_header(data)
        matrix_layout = read_layout_header(path)
        if matrix_layout:
            revObj.set_templates(matrix_layout)
            note_out(['Layout header found @ '+path])
            return matrix_layout
        else:
            continue
    warning_out(['Keyboard layout header not found for '+kbo.get_name(), 'Reverting to basic layout...']) 
    return

# Hook in for main q2k binary
def main():  
    # Init kb_info file from cache
    init_cache_info(KB_INFO)

    # Read ARGV input from terminaL
    parser = argparse.ArgumentParser(description='Convert AVR C based QMK keymap and matrix files to YAML Keyplus format')
    parser.add_argument('keyboard', metavar='KEYBOARD', nargs='?', default='', help='The name of the keyboard whose keymap you wish to convert')
    parser.add_argument('-m', '--keymap', metavar='keymap', dest='keymap', default='default', help='The keymap folder to reference - default is /default/')
    parser.add_argument('-r', '--rev', metavar='ver',dest='rev', default='', help='Revision of layout - default is n/a')
    parser.add_argument('-d', '--dump', dest='dumpyaml', action='store_true', help='Append results to kb_info.yaml. (For debugging, May cause performance penalty)')
    parser.add_argument('-L', '--list', dest='listkeyb', action='store_true',help='List all valid KEYBOARD inputs')
    parser.add_argument('-M', '--keymaps', dest='listkeym', action='store_true',help='List all valid KEYMAPS for the current keyboard')
    parser.add_argument('-R', '--revlist', dest='listkeyr', action='store_true',help='List all valid REVISIONS for the current keyboard')
    parser.add_argument('-S', '--search', metavar='string', dest='searchkeyb', help='Search valid KEYBOARD inputs')
    parser.add_argument('-p', '--print', dest='presult', action='store_true',help='Print result of keymap conversion to terminal')
    parser.add_argument('-t', '--template', metavar='layout', type=int, default=-1, dest = 'choosemap', help= 'Select keymap template index')
    args = parser.parse_args()

    if args.listkeyb:
        print_keyboard_list()
        sys.exit()

    if args.listkeym:
        note_out(['Listing keymaps for '+args.keyboard+'...'])
        print_keymap_list(args.keyboard)
        sys.exit()

    if args.listkeyr:
        note_out(['Listing revisions for '+args.keyboard+'...'])
        print_revision_list(args.keyboard)
        sys.exit()

    if args.searchkeyb:
        note_out(['Searching...'])
        search_keyboard_list(args.searchkeyb)
        sys.exit()

    current_kbo = check_parse_argv(args.keyboard, args.keymap, args.rev)        # Check the cmd line arguments
    mcu_list = find_rules_mk(current_kbo)                                       # Find and check MCU type
    check_mcu_list(current_kbo)
    find_config_header(current_kbo)                                             # Pass config.h through CPP for matrix pinout
    km_layers = preproc_read_keymap(current_kbo)                                # Check cache/run preprocessor for keymap.c
    km_template = find_layout_header(current_kbo)                               # Find layout templates in <keyboard>.h
    #km_template = current_kbo.get_rev_info(current_kbo.get_rev()).get_templates()
    km_layers = convert_keymap(km_layers)                                       # Convert extracted keymap.c data to keyplus format
    if not km_template:
        km_template = build_layout_from_keymap(km_layers)
    merge_layout_template(km_layers, km_template, args.choosemap)               # Merge layout templates + arrays from <keyboard>.h with matrix from keymap.c
    note_out(['Conversion succeeded, piping output'])

    if args.dumpyaml:
        dump_info(KBD_LIST, KB_INFO)

    if args.presult:
        create_keyplus_yaml(current_kbo, True)
    else:
        create_keyplus_yaml(current_kbo)

# Hook in for q2kb binary
def kbfirmware():
    # Init kb_info file from cache
    init_cache_info(KB_INFO)
    # Read ARGV input from terminaL
    parser = argparse.ArgumentParser(description='Convert AVR C based QMK keymap and matrix files to YAML Keyplus format')
    parser.add_argument('keyboard', metavar='KEYBOARD', nargs='?', default='', help='The name of the keyboard whose keymap you wish to convert')
    parser.add_argument('-m', '--keymap', metavar='keymap', dest='keymap', default='default', help='The keymap folder to reference - default is /default/')
    parser.add_argument('-r', '--rev', metavar='ver',dest='rev', default='', help='Revision of layout - default is n/a')
    parser.add_argument('-d', '--dump', dest='dumpyaml', action='store_true', help='Append results to kb_info.yaml. (For debugging, May cause performance penalty)')
    parser.add_argument('-L', '--list', dest='listkeyb', action='store_true',help='List all valid KEYBOARD inputs')
    parser.add_argument('-M', '--keymaps', dest='listkeym', action='store_true',help='List all valid KEYMAPS for the current keyboard')
    parser.add_argument('-R', '--revlist', dest='listkeyr', action='store_true',help='List all valid REVISIONS for the current keyboard')
    parser.add_argument('-S', '--search', metavar='string', dest='searchkeyb', help='Search valid KEYBOARD inputs')
    parser.add_argument('-p', '--print', dest='presult', action='store_true',help='Print result of keymap conversion to terminal')
    parser.add_argument('-t', '--template', metavar='layout', type=int, default=-1, dest = 'choosemap', help= 'Select keymap template index')
    args = parser.parse_args()

    if args.listkeyb:
        print_keyboard_list()
        sys.exit()

    if args.listkeym:
        note_out(['Listing keymaps for '+args.keyboard+'...'])
        print_keymap_list(args.keyboard)
        sys.exit()

    if args.listkeyr:
        note_out(['Listing revisions for '+args.keyboard+'...'])
        print_revision_list(args.keyboard)
        sys.exit()

    if args.searchkeyb:
        note_out(['Searching...'])
        search_keyboard_list(args.searchkeyb)
        sys.exit()
    
    current_kbo = check_parse_argv(args.keyboard, args.keymap, args.rev)        # Check the cmd line arguments
    mcu_list = find_rules_mk(current_kbo)                                       # Find and check MCU type
    check_mcu_list(current_kbo)
    find_config_header(current_kbo)                                             # Pass config.h through CPP for matrix pinout
    km_layers = preproc_read_keymap(current_kbo)                                # Check cache/run preprocessor for keymap.c
    km_template = find_layout_header(current_kbo)                               # Find layout templates in <keyboard>.h
    if not km_template:
        km_template = build_layout_from_keymap(km_layers)
    merge_layout_template(km_layers, km_template, args.choosemap)               # Merge layout templates + arrays from <keyboard>.h with matrix from keymap.c
    note_out(['Merge succeeded, piping output'])

    if args.dumpyaml:
        dump_info(KBD_LIST, KB_INFO)

    if args.presult:
        create_kbfirmware_json(current_kbo, True)
    else:
        create_kbfirmware_json(current_kbo)
