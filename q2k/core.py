import argparse
import copy
import errno
import enum as en
import glob
import os
import pathlib
import platform
import re
import subprocess
import sys
import traceback
import tkinter as tk
import pyparsing as pp
import termcolor as tc
import yaml

from q2k.reference import Q2KRef
from q2k.version import Q2K_VERSION
""" Q2K Keymap Utility - For converting from QMK Firmware keymaps to keyplus layout format """

class Defaults:
    """ A class for Q2K constants/default variables

    Attributes:
        VERSION(str) : Q2K version
        FROZEN (bool): Binary/Source build

        SRC(str)        : Path to source directory of this application
        LIBS(str)       : Path to local libs directory
        CACHE(str)      : Path to cache yaml
        QMK(str)        : Path to qmk directory
        KEYP(str)       : Path to keyplus yaml output directory
        KBF(str)        : Path to kbfirmware json output directory
        AVR_GCC(str)    : Path to avr-gcc compiler dependency
        INVALID_KC(str) : What to replace invalid QMK keycodes with
        PRINT_LINES(str): Cosmetic element for console output

        QMK_NONSTD_DIR(:obj:`list` of :obj:`str`) : List of non-standard QMK keyboard folders
        MCU_COMPAT(:obj:`list` of :obj:`str`)     : List of keyplus compatible MCUs

    """

    if getattr(sys, 'frozen', False):
        FROZEN = True
        SRC = ''       #os.getcwd()                               # If Frozen - $Q2K = [cwd]
    else:                                                         # If Live, use bundle_dir
        FROZEN = False
        SRC = os.path.dirname(os.path.abspath(__file__))          # else $Q2K is its own install dir

    VERSION = Q2K_VERSION
    # Directories
    LIBS = os.path.join(SRC, 'lib')                            # Local Libs                                              Default is $Q2K/libs/
    CACHE = os.path.join(SRC, '.cache', 'cache_kb.yaml')       # Cache                                                   Default is $Q2K/.cache/cache_kb.yaml

    if FROZEN:
        QMK = os.path.join(SRC, 'qmk_firmware')                # QMK Directory - To be provided by user                  Default is $Q2K/qmk_firmware/
        KEYP = os.path.join(SRC, 'q2k_out', 'keyplus')         # Output. This is a relative directory (default)          Default is $Q2K/q2k_out/keyplus/ (Frozen)
        KBF = os.path.join(SRC, 'q2k_out', 'kbfirmware')
    else:
        QMK = os.path.join(os.getcwd(), 'qmk_firmware')        # QMK Directory - To be provided by user                  Default is $Q2K/qmk_firmware/
        KEYP = os.path.join(os.getcwd(), 'q2k_out', 'keyplus') # Output. This is a relative directory.                   Default is [cwd]/q2k_out/keyplus/ (Live)
        KBF = os.path.join(os.getcwd(), 'q2k_out', 'kbfirmware')

    if platform.system() == 'Linux':                           # AVR-GCC Compiler.
        AVR_GCC = 'avr-gcc'                                    # avr-gcc for linux                                       Default is avr-gcc (Linux)
    elif platform.system() == 'Windows':
        AVR_GCC = os.path.join(SRC, 'avr-gcc', 'bin', 'avr-gcc.exe') # avr-gcc.exe for Windows
    # Lists
    QMK_NONSTD_DIR = ['handwired', 'converter', 'clueboard', 'lfkeyboards'] # Right now only lfkeyboards causes any issues, however it is good to be verbose here
    #MCU_COMPAT = ['atmega32u2', 'atmega32u4', 'at90usb1286']
    MCU_COMPAT = ['atmega32u4']                                              # Compatible MCU types (currently only 32u4)
    #KBF_MCU_COMPAT= ['atmega32u4', 'atmega32u2', 'at90usb1286']

    # Misc
    INVALID_KC = 'trns'                                       # What to set invalid KC codes to

    if platform.system() == 'Linux':
        PRINT_LINES = '────────────────────────────────────────────────────────────────────────'
    elif platform.system() == 'Windows':
        PRINT_LINES = '──────────────────────────────────────────────────────────────'

class _Console:
    """ A private class for handling output to application console

    Attributes:
        gui(bool)    : Flag for GUIs (True if GUI, False otherwise)
        errors(list) : List of printed errors
    """

    def __init__(self, gui):
        """Class constructor"""
        self.gui = gui
        self.errors = []

    def error(self, info, fatal=True):
        """ Prints non-fatal and fatal error messages to console"""
        if self.gui:
            msg = []
            for ind, line in enumerate(info):
                msg += [line, ' \n']
                if ind == 0:
                    warning = line
                    self.errors.append(line)
                    print('❌ ERROR:', line)
                else:
                    self.errors.append(line)
                    print('•', line)
            msg = ''.join(msg)
            if fatal:
                tk.messagebox.showerror('Error', msg)
                raise RuntimeError(warning)
        else:
            error_msg = tc.colored('❌ ERROR:', 'red', attrs=['reverse', 'bold'])
            e_bullet = tc.colored('•', 'red', attrs=['bold'])

            for ind, line in enumerate(info):
                if ind == 0:
                    self.errors.append(line)
                    line = tc.colored(line, 'red')
                    print(error_msg, line)
                else:
                    self.errors.append(line)
                    print(e_bullet, line)
            if fatal:
                exit()

    def bad_kc(self, kc_type, code):
        """ Prints bad keycode warnings to console"""
        if self.gui:
            bad_kc_msg = ['❌ ', 'Invalid ', kc_type, ': ', code]
            print(''.join(bad_kc_msg))
            del bad_kc_msg[0]
            self.errors.append(''.join(bad_kc_msg))
        else:
            message = ['❌ ', 'Invalid ', kc_type, ':']
            bad_kc_msg = [tc.colored(''.join(message), 'cyan')]
            bad_kc_msg += [' ', code]
            print(''.join(bad_kc_msg))
            message += [' ', code]
            self.errors.append(''.join(message))

    def warning(self, info, pause=False):
        """ Prints warnings and interactive warnings to console"""

        if self.gui:
            msg = []
            for ind, line in enumerate(info):
                msg += [line, ' \n']
                if ind == 0:
                    warning = line
                    self.errors.append(line)
                    print('▲ WARNING:', line)
                else:
                    self.errors.append(line)
                    print('•', line)
            msg = ''.join(msg)
            if pause:
                pause_out = ''.join([msg, '\nContinue?'])
                if not tk.messagebox.askyesno('Warning', pause_out):
                    raise RuntimeWarning(warning)

        else:
            warning_msg = tc.colored('▲ WARNING:', 'yellow', attrs=['bold'])
            w_bullet = tc.colored('•', 'yellow', attrs=['bold'])

            for ind, line in enumerate(info):
                if ind == 0:
                    self.errors.append(line)
                    line = tc.colored(line, 'yellow')
                    print(warning_msg, line)
                else:
                    self.errors.append(line)
                    print(w_bullet, line)
            if pause:
                print(w_bullet, 'Press [ENTER] to continue')
                input()


    def note(self, info):
        """ Prints progress and success notification to console"""
        if self.gui:
            for ind, line in enumerate(info):
                if ind == 0:
                    print('✔', line)
                else:
                    print('•', line)
        else:
            note_msg = tc.colored('✔', 'green', attrs=['bold'])
            n_bullet = tc.colored('•', 'green', attrs=['bold'])

            for ind, line in enumerate(info):
                if ind == 0:
                    print(note_msg, line)
                else:
                    print(n_bullet, line)

    def clear(self):

        self.errors = []

class _ParseTxt:
    """" A private class containing functions for handling text parsing (with pyparsing) of QMK source files"""

    def layout_headers(data):
        """ Finds LAYOUT templates from QMK <keyboard>.h header"""

        data = str(data.replace('\\n', ' ').replace('\\r', ' ').replace('\\t', ' '))

        lparen, rparen, lbrac, rbrac, comma, bslash = map(pp.Suppress, "(){},\\")

        define = pp.Suppress(pp.Literal('#define'))
        name = pp.Word(pp.alphanums+'_')
        macrovar = pp.Word(pp.alphanums+'_#')
        layout_row = pp.Group(pp.OneOrMore(macrovar + pp.Optional(comma)) + pp.ZeroOrMore(bslash))
        layout = lparen + pp.ZeroOrMore(bslash) + pp.OneOrMore(layout_row) + rparen
        matrix_row = pp.ZeroOrMore(bslash) + pp.Optional(lbrac) +  pp.ZeroOrMore(bslash) + pp.OneOrMore(macrovar + pp.Optional(comma)) + pp.ZeroOrMore(rbrac) + pp.Optional(comma) + pp.ZeroOrMore(bslash)
        matrix = pp.ZeroOrMore(bslash) + lbrac +  pp.ZeroOrMore(bslash) + pp.OneOrMore(matrix_row) +  pp.ZeroOrMore(bslash) + rbrac +  pp.ZeroOrMore(bslash)

        header = define + name('name') + pp.ZeroOrMore(bslash) + layout('layout') + pp.ZeroOrMore(bslash) + matrix('array')
        header.ignore(pp.cStyleComment)

        hresults = list(header.scanString(data))
        names = []
        for tokens in hresults:
            i = 0
            while tokens[0].name in names:
                i += 1
                if not tokens[0].name.endswith(')'):
                    dupl_name = [tokens[0].name]
                    dupl_name += ['(', str(i), ')']
                    tokens[0].name = ''.join(dupl_name)
                else:
                    tokens[0].name = tokens[0].name[:-2]+str(i)+')'
            names.append(tokens[0].name)

        return hresults

    def config_headers(data):
        """ Finds matrix column and row pins from QMK config.h header"""

        data = str(data.replace('\\n', ' ').replace('\\r', ' ').replace('\\t', ' '))

        matrix_data = []
        matrix_row_pins = []
        matrix_col_pins = []
        matrix_diode_dir = []

        lbrac, rbrac, comma = map(pp.Suppress, "{},")
        define_rows = pp.Suppress(pp.Literal('define MATRIX_ROW_PINS'))
        define_cols = pp.Suppress(pp.Literal('define MATRIX_COL_PINS'))
        define_diodes = pp.Suppress(pp.Literal('define DIODE_DIRECTION'))

        pincode = pp.Word(pp.alphanums) | pp.Word(pp.nums)
        diode_var = pp.Word(pp.alphanums+'_')

        matrix_rows = define_rows + lbrac + pp.ZeroOrMore(pincode + pp.Optional(comma)) + rbrac
        matrix_rows.ignore(pp.cppStyleComment)
        matrix_cols = define_cols + lbrac + pp.ZeroOrMore(pincode + pp.Optional(comma)) + rbrac
        matrix_cols.ignore(pp.cppStyleComment)
        matrix_diodes = define_diodes + diode_var('diodes')
        matrix_diodes.ignore(pp.cppStyleComment)

        # Note: A lot of this code is superfluous as we run config.h through cpp, but it does not cost much to be robust.
        for token in matrix_rows.scanString(data):
            matrix_row_pins.append(list(token[0]))

        for token in matrix_cols.scanString(data):
            matrix_col_pins.append(list(token[0]))

        for token in matrix_diodes.scanString(data):
            matrix_diode_dir.append(token[0].diodes)

        if len(matrix_row_pins) == 1 and len(matrix_col_pins) == 1:
            matrix_data.append(matrix_row_pins[0])
            matrix_data.append(matrix_col_pins[0])
            diode_result = 'none'
            if len(matrix_diode_dir) == 1:
                if matrix_diode_dir[0] == 'COL2ROW':
                    diode_result = 'col_row'
                elif matrix_diode_dir[0] == 'ROW2COL':
                    diode_result = 'row_col'
                else:
                    diode_result = 'none'
            elif not matrix_diode_dir:
                diode_result = 'col_row' # Assume if there is no definition that it uses default COL2ROW setting
            matrix_data.append(diode_result)

        return matrix_data

    def rules_mk_mcu(data):
        """ Finds mcu data from rules.mk"""

        data = str(data.replace('\\n', ' ').replace('\\r', ' ').replace('\\t', ' '))

        equals = (pp.Suppress('='))

        mcu_tag = pp.Suppress(pp.Literal('MCU'))
        mcu_type = pp.Word(pp.alphanums+'_')

        mcu = mcu_tag + equals + mcu_type('mcu')
        mcu.ignore('#'+pp.restOfLine)

        return mcu.scanString(data)

    def keymaps(data):
        """ Finds keycode layers (keymaps) from QMK keymap.c"""

        data = str(data.replace('\\n', ' ').replace('\\r', ' ').replace('\\t', ' '))

        lbrac, rbrac, equals, comma = map(pp.Suppress, "{}=,")

        keycode = pp.Word(pp.alphanums+'_'+'('+')')
        layer_string = pp.Word(pp.printables) | pp.Word(pp.nums)

        keycode_list = pp.Group(pp.ZeroOrMore(keycode + pp.Optional(comma)))
        row = lbrac + keycode_list + rbrac

        layern = layer_string('layer_name') + equals
        km_layer_data = lbrac + pp.OneOrMore(row + pp.Optional(comma)) + rbrac
        km_layer = pp.Optional(layern) + km_layer_data('layer') + pp.Optional(comma)

        km_layer.ignore(pp.cppStyleComment+pp.pythonStyleComment)

        return km_layer.scanString(data)

    def keymap_functions(data):
        """ Finds legacy TMK/QMK style functions from QMK keymap.c"""

        data = str(data.replace('\\n', ' ').replace('\\r', ' ').replace('\\t', ' '))

        lsqbrac, rsqbrac, equals, comma = map(pp.Suppress, "[]=,")

        words = pp.Word(pp.alphanums+'_')
        function_h = pp.Literal('fn_actions[] = {')

        func_index = lsqbrac + pp.Word(pp.alphanums+'_') + rsqbrac + equals
        func_name = words
        func_params = pp.Combine('(' + pp.ZeroOrMore(words + pp.Optional(',')) + ')', adjacent=False)
        func = pp.Group(pp.Optional(func_index) + pp.Combine(func_name + func_params, adjacent=False))
        func_list = pp.Group(pp.ZeroOrMore(func + pp.Optional(comma)))
        eof = pp.Literal('}')
        function = pp.Suppress(function_h) + func_list('function') + pp.Suppress(eof)

        function.ignore(pp.cppStyleComment)

        results = list(function.scanString(data))

        return results

class _Cpp:
    """" A private class containing functions for opening QMK source files and passing input onto the avr-gcc preprocesso"""

    def __init__(self, kbo, dirs, console):
        self.__kb = kbo
        self.__dirs = dirs
        self.__console = console

    def __preproc(self, kblibs, arg_list, debug=False):
        """ Runs AVR-GCC Preprocessor, including all relevant header files and strips layout macros, comments and user-defined macros and defines"""

        # Setting up -I and custom define options
        qdir = os.path.join(self.__dirs['QMK dir'], 'keyboards')
        kb_n = self.__kb.name
        cpp = [Defaults.AVR_GCC, '-E']
        kbdefine = ['KEYBOARD'] + kblibs
        kbdefine = '_'.join(kbdefine)
        qmk_keyboard_h = 'QMK_KEYBOARD_H=\"'+ kb_n +'.h\"'
        locallib = '-I'+self.__dirs['Local libs']
        libs = ['-D', kbdefine, '-D', qmk_keyboard_h, locallib]
        path = qdir
        for kbl in kblibs:
            path = os.path.join(path, kbl)
            this_lib = '-I'+path+os.sep
            libs.append(this_lib)

        argv = cpp + libs + arg_list
        if debug: 
            print(' '.join(argv))

        try:
            if platform.system() == 'Linux':

                output = subprocess.check_output(argv)

            elif platform.system() == 'Windows':
                startup = subprocess.STARTUPINFO()
                startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW

                output = subprocess.check_output(argv, stdin=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startup)
            return output

        except subprocess.CalledProcessError as error:
            err_num = error.returncode
            if err_num == errno.EPERM:
                self.__console.warning(['Compiler returned error while reading '+argv[-1]])
            else:
                print(traceback.format_exc(), file=sys.stderr)

        except OSError as error:
            if error.errno == errno.ENOEXEC:
                self.__console.error(['Could not find avr-gcc compiler', 'Check if avr-gcc is installed in', Defaults.AVR_GCC])
            else:
                print(traceback.format_exc(), file=sys.stderr)

    def preproc_header(self, path):
        """ Initialize preprocessing of QMK config.h files"""

        kblibs = list(self.__kb.libs)
        if self.__kb.build_rev:
            kblibs.append(self.__kb.build_rev)

        arg = ['-D', 'QMK_KEYBOARD_CONFIG_H=\"config_common.h\"', '-dD', path]
        if os.path.isfile(path):
            output = str(self.__preproc(kblibs, arg))
            return output

    def preproc_keymap(self):
        """ Initialize preprocessing QMK keymap.c files"""

        qdir = os.path.join(self.__dirs['QMK dir'], 'keyboards')
        kb_n = self.__kb.name
        km_n = os.path.join(self.__kb.build_keymap, 'keymap.c')
        kblibs = list(self.__kb.libs)
        rev_n = self.__kb.build_rev
        if rev_n != '':
            kblibs.append(rev_n)

        # KEYMAP
        keym = os.path.join(qdir, kb_n, rev_n, 'keymaps', km_n)
        if not os.path.isfile(keym):
            keym = os.path.join(qdir, kb_n, 'keymaps', km_n)

        # OUTPUT
        argkm = [keym]
        if os.path.isfile(keym):
            output = str(self.__preproc(kblibs, argkm))
            return output
        else:
            self.__console.error(['Keymap cannot be read by preprocessor', 'Failed to parse keymap file'])

class KBInfo:
    """" A container class for keyboard information"""

    def __init__(self, n=''):

        self.name = n                 # Name of keyboard
        self.libs = []                # Possible QMK lib folders (partly depreciated)
        self.rev_list = []            # List of rev obj names TODO: Depreciate this entirely
        self.rev_info = []            # A list of RevInfo objects

    def init_build(self):
        """ Initialize build variables"""

        self.build_rev = ''            # What revision to build with
        self.build_keymap = ''         # What keymap to build with
        self.build_template = ''       # What layout to build with

    def add_rev_list(self, rev, is_rev=True):
        """ Add new RevInfo attribute object to this KBInfo"""
        if is_rev:
            self.rev_list.append(rev)
        revo = RevInfo(rev, is_rev)
        self.rev_info.append(revo)

    def get_rev_info(self, rev_n):
        """ Accessor method for a particular RevInfo attribute object of this KBInfo object"""
        for revo in self.rev_info:
            if revo.name == rev_n:
                return revo
            if revo.name == 'n/a':
                return revo

    def del_rev_info(self, rev_n):
        """ Delete a particular RevInfo attribute object of this KBInfo object"""
        for i, revo in enumerate(self.rev_info):
            if revo.name == rev_n:
                del self.rev_info[i]
        if rev_n in self.rev_list:
            index = self.rev_list.index(rev_n)
            del self.rev_list[index]



class RevInfo:
    """" A container class for keyboard revision information"""

    def __init__(self, n='', is_rev=True):

        self.name = n                # Name of Revision
        self.mcu_list = []           # MCU list
        self.keymap_list = []        # List of layout NAMES
        self.template_list = []      # List of template NAMES
        self.template_loc = ''       # Location of <keyboard>.h
        self.is_rev = is_rev         # Does keyboard have revisions? (or just default)

    def init_build(self):
        """ Initialize build variables"""

        self.build_m_row_pins = []   # Row pins
        self.build_m_col_pins = []   # Column  pins
        self.build_diodes = 'none'   # Diode Direction

        self.build_layout = []       # list of KeycodeLayer objects (which form layout) -> Final yaml or json output comes from here
        self.build_templates = []    # list of LayoutTemplate objects

class LayoutTemplate:
    """" A container class for layout templates"""

    def __init__(self, n=''):
        self.name = n                # Name of template : e.g. LAYOUT, KEYMAP, LAYOUT_66_ANSI
        self.layout = []             # List of layout rows
        self.array = []              # Array holding index values (to be merged with keycode_layers)

    def convert_template_index(self, console=_Console(False), template_list=[]):
        """ Convert Template from macro variable strings to integer array index"""

        for i, row in enumerate(self.layout):
            for j, col in enumerate(row):
                try:
                    self.layout[i][j] = self.array.index(col)
                except ValueError:
                    macro_err_out = ''.join([self.name, ' - missing macro variable [', str(col), ']'])
                    console.warning([macro_err_out])
                    # Try to recover using a different keycode array
                    if template_list:
                        for template in template_list:
                            array2 = template.array
                            if len(array2) != len(self.array) or self.name == template.name:
                                continue
                            try:
                                index = array2.index(col)
                                self.layout[i][j] = index
                                self.array[index] = col
                                console.warning(['Macro variable recovery succeeded'])
                                break
                            except ValueError:
                                continue
                    if self.layout[i][j] == col:
                        self.layout[i][j] = -1
                        console.warning(['Array key recovery failed', 'Will assume this corresponds to KC_NO'])

class KeycodeLayer:
    """" A container class for keymap keycode layers"""

    def __init__(self, n=''):

        self.name = n                # Name of current layer
        self.keymap = []             # List of lists representing Raw [QMK] KEYMAP layers (keycode layers)
        self.layout = []             # List of lists output for converted [keyplus] keycode layers - our layout
        self.matrix_map = []         # Matrix mapping in [keyplus] format
        self.matrix_cols = 0

    def convert_keyplus_keymap(self, layer_names, functions, console):
        """ Convert this keycode layer's layout from QMK KC format to keyplus KC format"""

        for i, keyc in enumerate(self.keymap):
            if keyc.endswith(')') and '(' in keyc:
                self.keymap[i] = self.__func(keyc, layer_names, functions, console)
            else:
                self.keymap[i] = self.__keycode(keyc, functions, console)

    def convert_keyplus_matrix(self, col_limit):
        """ Convert this keycode layer's matrix mapping from integer array index to keyplus matrix map format"""

        matrix = copy.deepcopy(self.matrix_map)
        for i, row in enumerate(self.matrix_map):
            j = 0
            for col in row:
                int(col)
                if col != -1:
                    r_i = col // col_limit
                    c_i = col % col_limit
                    matrix[i][j] = ''.join(['r', str(r_i), 'c', str(c_i)])
                    j += 1
                else:
                    del matrix[i][j]
                    del self.layout[i][j]
        self.matrix_map = matrix

    def __func(self, qmk_func, layer_names, functions, console):
        """ Private method for looking up Q2Kref class to convert QMK functions to keyplus format"""
        invalid = Defaults.INVALID_KC

        # OSM Functions
        # OSM keys are defined non-dynamically
        if qmk_func in Q2KRef.keyp_mods.keys():
            keyp_func = Q2KRef.keyp_mods[qmk_func]
            return keyp_func
        else:
            # Break up into [qfunc]([func_target])
            brc = qmk_func.index('(')+1
            qfunc = qmk_func[:brc]
            func_target = qmk_func[brc:-1]

            # Layer Switching Functions e.g. LT(1), TT(2)
            if qfunc in Q2KRef.keyp_layer_func.keys() and func_target in layer_names:
                layer = str(layer_names.index(func_target))
                keyp_func = Q2KRef.keyp_layer_func[qfunc]+layer # ' L' + 2
                return keyp_func

            # Modifier/Multi-Modifier Functions - e.g. HYPR(KC), LCAG(KC), LCTL(KC)
            elif qfunc in Q2KRef.keyp_mods.keys() and func_target in Q2KRef.keyp_kc.keys():
                keycode = self.__keycode(func_target, functions, console, allow_quotes=False)
                # Wrap with quotes -> '[func]' - note: keyplus Format is [TAP]>[HOLD]
                keyp_func = ''.join(["'", Q2KRef.keyp_mods[qfunc], '-', keycode, "'"])
                return keyp_func

            # For Layer-Tap Keys e.g. LT(1, KC_SPACE), LM(3, MOD_CTL) - Format FN(HOLD,TAP)
            # Hold = Layer for these
            elif qfunc in Q2KRef.keyp_tap_layer.keys():

                # Split up into [TAP_LAYER], [HOLD_KC]
                split = func_target.split(',', 1)
                if len(split) != 2:
                    kc_err_out = ''.join(['[', qmk_func, '] - set to ', invalid])
                    console.bad_kc('FN', kc_err_out)
                    return invalid
                else:
                    layer_t = split[0].replace(' ', '')
                    keycode = split[1].replace(' ', '')

                # Check if [TAP_LAYER] references a layer
                if layer_t not in layer_names:
                    kc_err_out = ''.join(['[', qmk_func, '] - set to ', invalid])
                    console.bad_kc('FN', kc_err_out)
                    return invalid
                else:
                    layer = str(layer_names.index(layer_t))
                    hold = Q2KRef.keyp_tap_layer[qfunc]+layer

                    # For regular QMK Keycodes LT([HOLD],[TAP]) - KC_E, KC_ESC, etc.
                    if keycode in Q2KRef.keyp_kc.keys():
                        tap = self.__keycode(keycode, functions, console, allow_quotes=False)
                        # Wrap with quotes -> '[func]' - note: Keyplus Format is [TAP]>[HOLD]
                        keyp_func = ''.join(["'", tap, '>', hold, "'"])
                        return keyp_func

                    # [For legacy QMK Keycodes  LM([HOLD],[TAP]) - [TAP]= MOD_LCTL, etc.
                    elif keycode in Q2KRef.qmk_legacy_mod.keys():
                        tap = Q2KRef.qmk_legacy_mod[keycode]+'-none'
                        # Wrap with quotes -> '[func]' - note Keyplus Format is [TAP]>[HOLD]
                        keyp_func = ''.join(["'", tap, '>', hold, "'"])
                        return keyp_func

            # Modifier Tap e.g. RSFT_T(HOLD) - [HOLD]= KC_A, KC_B, etc.
            # Hold = Modifier
            elif qfunc in Q2KRef.keyp_tap_mod.keys() and func_target in Q2KRef.keyp_kc.keys():
                hold = Q2KRef.keyp_tap_mod[qfunc]+'-none'
                tap = self.__keycode(func_target, functions, console, allow_quotes=False)
                # Wrap with quotes -> '[func]' - note: Keyplus Format is [TAP]>[HOLD]
                keyp_func = ''.join(["'", tap, '>', hold, "'"])
                return keyp_func

            # Chained Quantum Functions [Legacy] - i.e. LCTL(LALT(KC_DEL))

            elif qfunc in Q2KRef.keyp_mods.keys() and ')' in func_target:
                target = func_target
                # Init functions with the first function
                functions = [Q2KRef.keyp_mods[qfunc]]
                # Recursively pipe func into functions until no more functions are left.
                while ')' in target:
                    brc = target.index('(')+1
                    func = target[:brc]
                    target = target[brc:-1]

                    if func in Q2KRef.keyp_mods.keys():
                        functions.append(Q2KRef.keyp_mods[func])
                # Check that this LAST element is a keycode
                if target in  Q2KRef.keyp_kc.keys():
                    final_kc = self.__keycode(target, functions, console, allow_quotes=False)
                    # Wrap with quotes -> '[func]' - i.e. S-a
                    keyp_func = ''.join(["'", ''.join(functions), '-', final_kc, "'"])
                    return keyp_func

            # Legacy TMK-style QMK Functions e.g. FUNC(x)
            # Sometimes these are used for layer switching, thus why we care.
            elif qfunc in Q2KRef.qmk_legacy_func:
                # Function list cannot be blank (else no func is defined)
                if functions:
                    index = int(func_target)
                    # Check array out of bounds (also no func defined)
                    if index < len(functions):
                        func_action = functions[index]
                        # Check for blank function (obviously no func defined)
                        if func_action:
                            keyp_func = func_action
                            return keyp_func

            # Legacy QMK Modkey format e.g. MT(MOD_LCTL, KC_Z) -> Ctrl+Z
            elif qfunc == 'MT(':
                split = func_target.split(',', 1)
                if len(split) != 2:
                    kc_err_out = ''.join(['[', qmk_func, '] - set to ', invalid])
                    console.bad_kc('FN', kc_err_out)
                    return invalid
                else:
                    modifier = split[0]
                    keycode = split[1]

                if modifier in Q2KRef.qmk_legacy_mod.keys() and keycode in Q2KRef.keyp_kc.keys():
                    mod = Q2KRef.qmk_legacy_mod[modifier]
                    keyc = self.__keycode(keycode, functions, console, allow_quotes=False)
                    # Wrap with quotes -> '[func]' i.e. S-a
                    keyp_func = ''.join(["'", mod, '-', keyc, "'"])
                    return keyp_func
        # Didn't get a match, so return [invalid]
        return invalid

    def __keycode(self, qmk_kc, functions, console, allow_quotes=True):
        """ Private method for looking up Q2Kref class to convert QMK keycodes to keyplus format"""

        invalid = Defaults.INVALID_KC
        if allow_quotes:

            # Normal Keycodes
            if qmk_kc in Q2KRef.keyp_kc.keys():
                keyp_kc = Q2KRef.keyp_kc[qmk_kc]
                return keyp_kc

            # Legacy TMK-style QMK FN Keycodes - KC_FNx
            # Sometimes these are used for layer switching, thus why we care.
            else:
                ind = 0
                for char in qmk_kc:
                    if char.isdigit():
                        break
                    ind += 1
                if qmk_kc[:ind] in Q2KRef.qmk_legacy_func:
                # Function list cannot be blank (else no func is defined)
                    if functions:
                        func_index = int(qmk_kc[ind:])
                        # Check array out of bounds (also no func defined)
                        if func_index < len(functions):
                            func_action = functions[func_index]
                            # Check for blank function (obviously no func defined)
                            if func_action:
                                keyp_kc = func_action
                                return keyp_kc
        else:
            # Fix final yaml output - caused by " and '
            if qmk_kc in Q2KRef.keyp_kc.keys():
                keyp_kc = Q2KRef.keyp_kc[qmk_kc]
                if keyp_kc == "\"\'\" ":                  # "'" -> quot
                    keyp_kc = 'quot'
                keyp_kc = keyp_kc.replace("'", '')        # Strip ' from all keycodes
                keyp_kc = keyp_kc.replace(' ', '')         # Strip whitespace
                return keyp_kc

        # If we didn't get a match, return [invalid]
        kc_err_out = ''.join(['[', qmk_kc, '] - set to ', invalid])
        console.bad_kc('KC', kc_err_out)
        return invalid

# ===========================================================================================
# Cached Lists and Dictionaries
# ===========================================================================================
class _Cache:
    """" A private class for handling reading and writing from/to the application's cached list of KBInfo objects"""

    def __init__(self, dirs, console, f_cache=False):

        self.kbo_list = []

        self.__loc = dirs['Cache']
        self.__qmk = dirs['QMK dir']
        self.__console = console

        if not f_cache:
            self.__find()
        else:
            self.__write()

    def __find(self):
        """ Find cached cache_kb.yaml"""

        if os.path.isfile(self.__loc):
            try:
                with open(self.__loc, 'r') as f:
                    self.kbo_list = yaml.load(f)
                    self.__console.note(['Using cached list from '+self.__loc, '--cache to reset'])
            except:
                self.__console.warning(['Failed to load from '+self.__loc])
                self.__write()
        else:
            self.__write()


    # Writing cache file
    # We need to find: Keyboard names, Revision names, LAYOUT template names, keymap.c file directories.
    def __write(self):
        """ Write cache_kb.yaml from KBInfo object list"""

        self.__console.note([Defaults.PRINT_LINES, 'Generating new cache_kb.yaml in '+self.__loc])

        templist = []
        keymaplist = []
        qdir = os.path.join(self.__qmk, 'keyboards')

        # Processing keyboard names and revisions

        # List of directories. Anything with a rules.mk file is considered a 'valid' dir for now.
        # This is the exact same logic used by QMK.
        # Format: qmk/keyboards/ ...    [ <anything> / ] rules.mk => templist
        for filepath in glob.glob(os.path.join(qdir, '**', 'rules.mk'), recursive=True):
            filepath = os.path.split(filepath)[0]
            templist.append(filepath)

        # List of keymap folders
        # Format: qmk/keyboards/ ...    [ <anything>  / keymaps / <any keymap> ] / keymap.c
        for filepath in glob.glob(os.path.join(qdir, '**', 'keymaps', '**', 'keymap.c'), recursive=True):
            filepath = os.path.split(filepath)[0]
            # Important: If this exists in templist, then REMOVE it from templist.
            # i.e. removes  [ <? ... >/<keyboard>/<revisions>/keymaps/<any keymap>]
            # templist should now only contain [ <? ... > / <keyboard> / <revision> / ]
            if filepath in templist:
                templist.remove(filepath)
            filepath = filepath.replace(qdir+os.sep, '', 1)
            keymaplist.append(filepath)

        for child in templist:
            p_path = str(pathlib.Path(child).parent)            # Path of the parent directory of this child
            p_name = p_path.replace(qdir+os.sep, '', 1)

            # If parent directory of this child is NOT a keyboard or a revision directory (and not a non-standard (i.e. manufacturer) directory)
            if p_path not in templist and p_name not in Defaults.QMK_NONSTD_DIR:
                name = child.replace(qdir+os.sep, '', 1)
                # Assume for now that child is a KEYBOARD
                # Check if child is a non-standard/manufacturer directory. (if it is then just continue)
                if name not in Defaults.QMK_NONSTD_DIR:
                    # Thus this is a keyboard, not revision
                    kbo = KBInfo(name)
                    kblibs = name.split(os.sep)
                    kbo.libs = kblibs
                    self.kbo_list.append(kbo)
            # If parent directory is a manufacturer/non-standard directory
            elif p_name in Defaults.QMK_NONSTD_DIR:
                name = child.replace(qdir+os.sep, '', 1)
                # This is a keyboard, not revision
                kbo = KBInfo(name)
                kblibs = name.split(os.sep)
                kbo.libs = kblibs
                self.kbo_list.append(kbo)
            # If parent directory IS a keyboard directory.
            else:
                # This is a 'revision' of an existing keyboard
                rev = child.replace(p_path+os.sep, '', 1)
                for kbo in self.kbo_list:
                    if kbo.name == p_name:
                        kbo.add_rev_list(rev)
                        break

        # Per-revision variables - i.e. Templates

        # Adds default n/a revisions for keyboards with no revision
        total_kb_count = len(self.kbo_list)
        remove_kbo = []
        for kbo in self.kbo_list:
            if not kbo.rev_list:
                kbo.add_rev_list('n/a', is_rev=False)

            remove_revo = []
            for revo in kbo.rev_info:
                # Find + validate MCU then layouts while we are doing this.
                if self.__find_validate_mcu(kbo, revo):
                    self.__find_layout_names(kbo, revo)
                else:
                    remove_revo.append(revo)
            # deleting revisions
            for revo in remove_revo:
                kbo.del_rev_info(revo.name)
            # deleting keyboards
            if not kbo.rev_info:
                remove_kbo.append(kbo)

        for kbo in remove_kbo:
            self.kbo_list.remove(kbo)

        valid_kb_count = len(self.kbo_list)

        # Processing keymaps

        for km_path in keymaplist:
            # info list = [ <keyboard> / <rev> ] /keymaps/ [ <keymap> ]
            keymap_sep = os.sep+'keymaps'+os.sep
            info_list = km_path.split(keymap_sep)
            kb_name = info_list[0]            # <keyboard>/<rev>
            km_name = info_list[-1]           # <keymap>
            namelist = kb_name.split(os.sep)   # [<keyboard>] [<rev>]
            match = False

            # Attach keymaps to revisions (if they are revision specific)
            # OR attach them to all revisions (if they are universal)
            #   - Assume the format <keyboard>/<revision>
            #   - i.e. <revision> will be seen just before <keyboard>.
            #   - Go through namelist backwards. Cursor stores 2 values, current name and previous name.
            #   for example: keyboard/rev/??
            #       0 = [??], 1* = [rev] 2* = [keyboard]
            #       2* matches a keyboard, so 1* is revision.
            # TODO: Currently breaks if  <keyboard/??/revision> - no current examples of this occuring however.
            prev = 'n/a'                        # previous variable - init as n/a
            for i in range(0, len(namelist)):
                if i > 0:
                    # Ignore first iteration of this loop
                    # Rebuild full path - (can't use os.path.join here)
                    kb_name = (os.sep).join(namelist)

                # Go through our final kbo_list output list, find matching kb object.
                for kbo in self.kbo_list:
                    if kbo.name == kb_name:
                        if prev in kbo.rev_list:
                            # Tag keymap to this revision
                            revo = kbo.get_rev_info(prev)
                            revo.keymap_list.append(km_name)
                        # Keyboard has revisions - Add keymap to all of these revisions.
                        else:
                            for revo in kbo.rev_info:
                                revo.keymap_list.append(km_name)
                        match = True                   # If match found break out of loop
                        break
                if match:
                    break
                prev = namelist.pop()                  # End of loop, pop last element from list.

        # After collecting all information, dump KBInfo list to text file for faster processing in future

        if self.kbo_list:
            self.__save_cache()
            proc_msg = ' '.join(['Processed', str(total_kb_count), ' keyboards with', str(valid_kb_count), 'validated for conversion'])
            self.__console.note(['New cache_kb.yaml successfully generated', 'Location: '+ self.__loc, proc_msg])
        else:
            self.__console.warning(['No keyboard information found', 'Check QMK directory location in pref.yaml : '+self.__qmk])

    # Finding layout template names

    def __find_layout_names(self, kbo, revo):
        """ Find and populate layout templates list attribute from QMK source headers -> <keyboard>.h"""

        found = False
        rev_n = revo.name
        kblibs = list(kbo.libs)
        # Kblibs defines the search boundary for *.h and *.c files for the preprocessor.

        if revo.is_rev:
            kblibs.append(rev_n)
            # Add revision directory to search path if this keyboard has revisions.

        qdir = os.path.join(self.__qmk, 'keyboards') # qmk/keyboards

        folders = []
        path = ''
        for kbl in kblibs:
            path = os.path.join(path, kbl)
            folders.append(path)
        # Search in REVERSED order - i.e. revisions first, then keyboards.
        # Prioritises config.h data in revisions first.
        for kbl in reversed(folders):
            kb_h = os.path.split(kbl)[-1]+'.h'
            path = os.path.join(qdir, kbl, kb_h)
            try:
                # Open config.h file, if it exists
                with open(path, 'r', encoding='utf8') as f:
                    data = str(f.read())
            except FileNotFoundError:
                #self.__console.warning(['Layout header not found in '+path, 'Trying a different path...'])
                continue

            # Parse it for LAYOUT/KEYMAP macro templates
            token_list = _ParseTxt.layout_headers(data)
            for tokens in token_list:
                revo.template_list.append(tokens[0].name)

            # If LAYOUT/KEYMAP templates found, break from loop
            # Note: This means that some layouts will be missed.
            # However we wish to be paranoid about 'collisions' and duplicate KEYMAP macros.
            # Might be possible to pull data from rules.mk? - Limited in usefulness right now
            if revo.template_list:
                #self.__console.note(['Layout header found @ '+path])
                found = True
                revo.template_loc = path
                break

        if not found:
            if revo.is_rev:
                self.__console.warning(['Layout templates not found for '+ os.path.join(kbo.name, rev_n)])
            else:
                self.__console.warning(['Layout templates not found for '+ kbo.name])
            revo.template_loc = 'n/a'

    def __find_validate_mcu(self, kbo, revo):
        """ Find and populate list of possible mcus from QMK rules.mk file"""

        rev_n = revo.name
        kblibs = list(kbo.libs)

        if revo.is_rev:
            kblibs.append(rev_n)

        qdir = os.path.join(self.__qmk, 'keyboards')

        folders = []
        path = ''
        for kbl in kblibs:
            path = os.path.join(path, kbl)
            folders.append(path)

        for kbl in reversed(folders):
            rules_mk = 'rules.mk'
            path = os.path.join(qdir, kbl, rules_mk)
            mcu_list = []
            try:
                with open(path, 'r', encoding='utf8') as f:
                    data = str(f.read())
            except FileNotFoundError:
                #self.console.warning(['Rules.mk not found in '+path, 'Trying a different path...'])
                continue

            if not data:
                continue

            token_list = _ParseTxt.rules_mk_mcu(data)
            for tokens in token_list:
                mcu_list.append(tokens[0].mcu)

            if mcu_list:
                valid_mcu = self.__validate_mcu(mcu_list, kbo, revo)
                if valid_mcu:
                    revo.mcu_list = mcu_list
                    return True
                else:
                    return False
                break

        if revo.is_rev:
            self.__console.warning(['MCU information not found for '+os.path.join(kbo.name, rev_n)])
        else:
            self.__console.warning(['MCU information not found for '+kbo.name])
        return True

    def __validate_mcu(self, mcu_list, kbo, revo):
        """ Compare MCU type with keyplus compatible MCU list """

        kb_n = kbo.name
        rev_n = revo.name

        bad_mcu = []
        found = 0
        for mcu in mcu_list:
            if mcu in Defaults.MCU_COMPAT:
                found += 1
            else:
                bad_mcu.append(mcu)

        if found == len(mcu_list):
            return True
        elif found > 0:
            if revo.is_rev:
                mcu_err_out = ' '.join([os.path.join(kb_n, rev_n), 'might have invalid mcu', ', '.join(bad_mcu)])
            else:
                mcu_err_out = ' '.join([kb_n, 'might have invalid mcu', ', '.join(bad_mcu)])

            self.__console.warning([mcu_err_out])
            return True

        else:
            if revo.is_rev:
                mcu_err_out = ' '.join([os.path.join(kb_n, rev_n), 'has invalid mcu', ', '.join(bad_mcu)])
            else:
                mcu_err_out = ' '.join([kb_n, 'has invalid mcu', ', '.join(bad_mcu)])

            self.__console.error([mcu_err_out], fatal=False)
            return False

    def __save_cache(self):
        """ Intended private method to save cache to file"""
        path = os.path.split(self.__loc)[0]
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except OSError as error:
                if error.errno != errno.EEXIST and os.path.isdir(path):
                    raise
        try:
            with open(self.__loc, 'w') as f:
                yaml.dump(self.kbo_list, f)
        except:
            self.__console.error(['Failed to create '+self.__loc])

    def _clear_cache(self):
        """ intended private method to clear cache """
        if os.path.isfile(self.__loc):
            os.remove(self.__loc)
        self.kbo_list = []

    def _keyboard_list(self,):
        """ Accessor method for obtaining list of keyboard names from kb_list"""
        kb_names = []
        for kbo in self.kbo_list:
            kb_names.append(kbo.name)
        return kb_names

    def _keymap_list(self, keyboard, rev=''):
        """ Accessor method for obtaining list of keymaps of a particular keyboard/revision from kb_list"""
        km_names = []
        for kbo in self.kbo_list:
            if kbo.name == keyboard:
                revo = kbo.get_rev_info(rev)
                if revo:
                    for keym in revo.keymap_list:
                        km_names.append(keym)
                    return km_names
                else:
                    print_rev_list = ', '.join(self._rev_list(keyboard))
                    self.__console.error(['Revision required - Valid Revisions: '+print_rev_list])

    def _rev_list(self, keyboard):
        """ Accessor method for obtaining list of revisions of a particular keyboard from kb_list"""
        for kbo in self.kbo_list:
            if kbo.name == keyboard:
                return kbo.rev_list

    def _template_list(self, keyboard, rev=''):
        """ Accessor method for obtaining list of templates of a particular keyboard/revision from kb_list"""
        tp_names = []
        for kbo in self.kbo_list:
            if kbo.name == keyboard:
                revo = kbo.get_rev_info(rev)
                if revo:
                    for temp in revo.template_list:
                        tp_names.append(temp)
                    return tp_names
                else:
                    print_rev_list = ', '.join(self._rev_list(keyboard))
                    self.__console.error(['Revision required - Valid Revisions: '+print_rev_list])

class Q2KApp:
    """" A class for the q2k application"""

    def __init__(self, app_type, is_gui=False):
        self.__output = en.Enum('output', 'keyplus kbfirmware')
        self.format = self.__output[app_type]
        self.is_gui = is_gui
        self.console = _Console(is_gui)
        # self.dirs      # directories
        # self.build_kb  # KBInfo for build
        # self.build_rev # RevInfo for build
        # self.__args    # Cmd line arguments
        # self.__cache,  # kb_list cache
        if not is_gui:
            self.__read_args()                             # init self.__args
            self.__set_dirs()                              # Read pref.yaml (or create)
            self.__pop_cache_list()                        # Get cached kb info and put into list
            self.__check_args()
        else:
            self.__read_args()
            self.__set_dirs()                              # Skip reading cmd line (set kb with hook-in method)
            self.__pop_cache_list()                        # Get cached kb info and put into list

    def __read_args(self):
        """ Private method for reading argv input from terminal"""
        parser = argparse.ArgumentParser(description='Convert AVR C based QMK keymap and matrix files to YAML Keyplus format')
        parser.add_argument('keyboard', metavar='KEYBOARD', nargs='?', default='', help='The name of the keyboard whose keymap you wish to convert')
        parser.add_argument('-m', '--keymap', metavar='KEYMAP', dest='keymap', default='default', help='The keymap folder to reference - default is [default]')
        parser.add_argument('-t', '--template', metavar='LAYOUT', dest='template', default='', help='The layout template to reference')
        parser.add_argument('-r', '--rev', metavar='ver', dest='rev', default='', help='Revision of layout - default is n/a')
        parser.add_argument('--cache', dest='clearcache', action='store_true', help='Clear cached data (cache_kb.yaml)')
        parser.add_argument('--reset', dest='clearpref', action='store_true', help='Restore preferences in pref.yaml to default')
        parser.add_argument('--debug', dest='debug', action='store_true', help='See debugging information')
        parser.add_argument('-l', '-L', '--list', dest='listkeyb', action='store_true', help='List all valid KEYBOARD inputs')
        parser.add_argument('-M', '--keymaps', dest='listkeym', action='store_true', help='List all valid KEYMAPS for the current keyboard')
        parser.add_argument('-T', '--templatelist', dest='listkeyt', action='store_true', help='List all valid LAYOUTS for the current keyboard')
        parser.add_argument('-R', '--revlist', dest='listkeyr', action='store_true', help='List all valid REVISIONS for the current keyboard')
        parser.add_argument('-S', '--search', metavar='string', dest='searchkeyb', help='Search valid KEYBOARD inputs')
        self.__args = parser.parse_args()

    def __set_dirs(self):
        """ Private method for initializing directories from saved pref.yaml or creating them from the Q2KDefaults constants class"""

        if self.__args.clearpref:
            self.__generate_dirs()
        else:
            try:
                pref_yaml = os.path.join(Defaults.SRC, 'pref.yaml')
                with open(pref_yaml, 'r') as f:
                    self.dirs = yaml.load(f)

                    try:
                        # Check version, clear cache if versions do not match.
                        if self.dirs['version'] != Defaults.VERSION:
                            old_cache = self.dirs['Cache']
                            if os.path.isfile(old_cache):
                                os.remove(old_cache)
                            self.__generate_dirs()
                        else:
                            self.console.note([Defaults.PRINT_LINES, 'Using preferences from '+pref_yaml, '--reset to reset to defaults'])
                    # pref.yaml before version 1.1
                    except KeyError:
                        old_cache = self.dirs['Cache']
                        if os.path.isfile(old_cache):
                            os.remove(old_cache)
                        self.__generate_dirs()

            except FileNotFoundError:
                self.__generate_dirs()

            except AttributeError:
                self.__generate_dirs()

    def __generate_dirs(self):
        """ Private method for generating default directories, and saving them to pref.yaml"""

        dirs = {
            'version'                : Defaults.VERSION,
            'QMK dir'                : Defaults.QMK,
            'Keyplus YAML output'    : Defaults.KEYP,
            'Kbfirmware JSON output' : Defaults.KBF,
            'Local libs'             : Defaults.LIBS,
            'Cache'                  : Defaults.CACHE,
        }
        self.dirs = dirs
        try:
            pref_yaml = os.path.join(Defaults.SRC, 'pref.yaml')
            with open(pref_yaml, 'w') as f:
                f.write('# Q2K Folder Locations\n')
                yaml.dump(dirs, f, default_flow_style=False)
                self.console.note([Defaults.PRINT_LINES, 'New pref.yaml generated @ '+pref_yaml])

        except FileNotFoundError:
            self.console.error(['Failed to generate '+pref_yaml])

    def __pop_cache_list(self):
        """ Private method for generating or finding a cached list of KBInfo Objects """
        self.__cache = _Cache(self.dirs, self.console, self.__args.clearcache)

    def __check_args(self):
        """ Private method for parsing arguments from terminal"""

        if self.__args.listkeyb and not self.is_gui:
            print_kb_list = '[ '+', '.join(self.keyboard_list())+' ]'
            self.console.note(['Listing keyboards...', print_kb_list])
            exit()
        elif self.__args.listkeyr and not self.is_gui:
            print_rev_list = '[ '+', '.join(self.rev_list(self.__args.keyboard))+' ]'
            self.console.note(['Listing revisions for '+self.__args.keyboard+'...', print_rev_list])
            exit()
        elif self.__args.listkeym and not self.is_gui:
            print_km_list = '[ '+', '.join(self.keymap_list(self.__args.keyboard, self.__args.rev))+' ]'
            if self.__args.rev == '':
                self.console.note(['Listing keymaps for '+self.__args.keyboard+'...', print_km_list])
            else:
                self.console.note(['Listing keymaps for '+self.__args.keyboard+ os.sep +self.__args.rev+'...', print_km_list])
            exit()
        elif self.__args.listkeyt and not self.is_gui:
            print_temp_list = '[ '+', '.join(self.template_list(self.__args.keyboard, self.__args.rev))+' ]'
            if self.__args.rev == '':
                self.console.note(['Listing layout templates for '+self.__args.keyboard+'...', print_temp_list])
            else:
                self.console.note(['Listing layout templates for '+self.__args.keyboard+ os.sep +self.__args.rev+'...', print_temp_list])
            exit()
        elif self.__args.searchkeyb and not self.is_gui:
            print_search_list = '[ '+', '.join(self.search_keyboard_list(self.__args.searchkeyb))+' ]'
            self.console.note(['Searching for '+self.__args.searchkeyb+'...', print_search_list])
            exit()

        self.set_kb(self.__args.keyboard, self.__args.rev, self.__args.keymap, self.__args.template)

    def set_kb(self, keyboard='', rev='', keymap='', template=''):
        """ Sets the keyboard to be converted by the Q2KApp object. Intended hook-in method for GUIs"""

        kb_list = self.__cache.kbo_list
        build_kbo = ''

        if not keyboard:
            print_kb_list = ', '.join(self.keyboard_list())
            self.console.error(['No keyboard name given', 'Valid Names: '+print_kb_list])

        for kbo in kb_list:
            if kbo.name == keyboard:
                build_kbo = kbo
                break

        if build_kbo:
            # Check Revision
            # Case 1: Have Revisions
            if build_kbo.rev_list and rev not in build_kbo.rev_list:
                print_rev_list = ', '.join(self.rev_list(keyboard))
                self.console.error(['Invalid Revision - '+rev, 'Valid Revisions: '+print_rev_list])
            # Case 2: No Revisions
            elif not build_kbo.rev_list and rev != '':
                self.console.error(['Invalid Revision - '+rev, 'Valid Revisions: None'])

            build_revo = build_kbo.get_rev_info(rev)
            # Check Layout
            # Case 1: Have Layout Templates
            if build_revo.template_list and template not in build_revo.template_list:
                print_temp_list = ', '.join(self.template_list(keyboard, rev))
                self.console.error(['Invalid Template - '+template, 'Valid Layouts: '+print_temp_list])
            # Case 2: No Layout Templates
            elif not build_revo.template_list and template != '':
                self.console.error(['Invalid Template - '+template, 'Valid Layouts: None'])

            # Check keymap
            if keymap not in build_revo.keymap_list:
                print_km_list = ', '.join(self.keymap_list(keyboard))
                self.console.warning(['Invalid Keymap - '+template, 'Valid Keymaps: '+print_km_list])

            build_kbo.init_build()
            build_revo.init_build()
            build_kbo.build_keymap = keymap
            build_kbo.build_template = template
            build_kbo.build_rev = rev
            self.build_kb = build_kbo
            self.build_rev = build_revo
            if rev:
                build_info_out = ''.join(['Building ', keyboard, os.sep, rev, ':', keymap, ':', template])
            else:
                build_info_out = ''.join(['Building ', keyboard, ':', keymap, ':', template])
            self.console.note([Defaults.PRINT_LINES, build_info_out, Defaults.PRINT_LINES])
        else:
            print_kb_list = ', '.join(self.keyboard_list())
            self.console.error(['Invalid Keyboard Name - '+keyboard, 'Valid Names: '+print_kb_list])

    def refresh_dir(self):
        """ Refresh directory settings for this Q2KApp Object (from pref.yaml)"""
        self.__set_dirs()

    def refresh_cache(self):
        """ Refresh cached KBInfo list for this Q2KApp Object (from cache_kb.yaml)"""
        self.__cache = _Cache(self.dirs, self.console, True)

    def reset(self):
        """ Reset cache and directory settings for this Q2KApp Object (force generate new settings from defaults)"""
        self.clear_cache()
        self.__generate_dirs()

    def clear_cache(self):
        """ Clear cached KBInfo List """
        self.__cache._clear_cache()

    def keyboard_list(self):
        """ get accessor method for keyboard names (from cache)"""
        return self.__cache._keyboard_list()

    def rev_list(self, keyboard):
        """ get accessor method for keyboard revisions for this keyboard (from cache)"""
        return self.__cache._rev_list(keyboard)

    def template_list(self, keyboard, rev=''):
        """ get accessor method for layout templates for this keyboard revision (from cache)"""
        return self.__cache._template_list(keyboard, rev)

    def keymap_list(self, keyboard, rev=''):
        """ get accessor method for keymaps for this keyboard revision (from cache)"""
        return self.__cache._keymap_list(keyboard, rev)

    def search_keyboard_list(self, string):
        """ get all keyboard names (from cache) which match this string"""

        kb_names = self.__cache._keyboard_list()
        results = []
        for kb in kb_names:
            if kb.find(string) != -1:
                results.append(kb)
        return results

    def execute(self):
        """ Execute conversion of previously selected keyboard/rev/keymap """

        self.__cpp = _Cpp(self.build_kb, self.dirs, self.console)

        self.console.clear()            # Clear console
        self.__check_mcu()              # Check for MCU and Matrix Pins
        self.__get_config_header()
        self.__get_keycodes()           # Init Layout + Templates
        self.__get_templates()
        self.__merge_layout_template()  # Process Layout + Templates
        self.__convert_matrix_map()
        self.__create_output()          # Pipe output to yaml or json
        self.console.clear()            # Clear console

    def __check_mcu(self):
        """ Check MCU type for the current build"""

        kb_n = self.build_kb.name
        revo = self.build_rev
        rev_n = self.build_kb.build_rev

        for mcu in revo.mcu_list:
            if mcu in Defaults.MCU_COMPAT:
                continue
            else:
                self.console.warning(
                    ['Possible MCU incompatability detected',
                     ''.join([mcu, ' in ', kb_n, os.sep, rev_n, 'rules.mk']),
                     'Currently, keyplus supports only boards with the following microcontrollers:',
                     ', '.join(Defaults.MCU_COMPAT),
                     'If your board has a MCU on this list then ignore this warning as a false positive',
                     'Else layout files produced will not work with keyplus until your board\'s mcu is supported'], pause=True)
                return

        self.console.note(['No MCU incompatibility detected'])

    def __get_config_header(self):
        """ Get matrix data from config.h file for the current build"""

        rev = self.build_rev.name
        revo = self.build_rev
        kblibs = list(self.build_kb.libs)
        if rev != 'n/a':
            kblibs.append(rev)

        qdir = os.path.join(self.dirs['QMK dir'], 'keyboards')
        folders = []
        path = ''

        for kbl in kblibs:
            path = os.path.join(path, kbl)
            folders.append(path)

        for kbl in reversed(folders):
            config_h = 'config.h'
            path = os.path.join(qdir, kbl, config_h)
            data = self.__cpp.preproc_header(path)

            if not data:
                continue

            matrix_data = _ParseTxt.config_headers(data)
            if matrix_data:
                revo.build_m_row_pins = matrix_data[0]
                revo.build_m_col_pins = matrix_data[1]
                if len(matrix_data) > 2:
                    revo.build_diodes = matrix_data[2]

                self.console.note(['Matrix pinout data found @ '+path])
                if revo.build_diodes == 'none':
                    self.console.warning(['Matrix diode direction not found.'], pause=True)
                else:
                    self.console.note(['Matrix diode direction is: '+revo.build_diodes])
                return
            else:
                continue

        self.console.warning(['Config.h header not found for '+self.build_kb.name, 'Matrix row/col pins must be provided manually!'], pause=True)
        return

    def __get_keycodes(self, debug=False):
        """ Get keycodes from the keymap.c file for the current build"""

        revo = self.build_rev
        data = self.__cpp.preproc_keymap()
        token_list = _ParseTxt.keymaps(data)
        function_token_list = _ParseTxt.keymap_functions(data)

        layer_list = []
        layer_names = []
        num_col = 0
        layer_index = -1

        for tokens in token_list:
            layer_index += 1
            if tokens[0].layer_name == '':
                name = str(layer_index)
                curr_layer = KeycodeLayer(name)
                layer_names.append(name)
            else:
                name = tokens[0].layer_name[1:-1]
                curr_layer = KeycodeLayer(tokens[0].layer_name[1:-1])
                layer_names.append(name)

            for row in tokens[0].layer:
                # Hotfix for problem with QMK functions X(x,y) splitting into [ X(x, ] [ y) ]
                # Todo: Implement in pyparsing instead (proper fix)
                for i, element in enumerate(row):
                    if ')' in element and '(' not in element:
                        func = row[i-1]+','+row[i]
                        del row[i-1]
                        i -= 1
                        del row[i]
                        row.insert(i, func)
                if len(row) > curr_layer.matrix_cols:
                    num_col = len(row)
                curr_layer.keymap += (list(row))

            curr_layer.matrix_cols = num_col
            layer_list.append(curr_layer)

        # Functions Array
        # TODO: Move/integrate into keycodes class
        functions = []
        for tokens in function_token_list:
            for f_token in tokens[0].function:
                if len(f_token) < 2:
                    # Format - Index is implied by order, Function
                    index = None
                    function = f_token[0]
                else:
                    # Format - Index, Function
                    index = int(f_token[0])
                    function = f_token[1]

                # Explicitly defined functions (no layers) i.e. GRAVE_ESC
                if function in Q2KRef.keyp_actions.keys():
                    if index:
                        while len(functions) < index:
                            functions.append('')
                    functions.append(Q2KRef.keyp_actions[function])
                # else look at parameters
                else:
                    if index:
                        while len(functions) < index:
                            functions.append('')
                    brc = function.index('(')+1
                    func = function[:brc]
                    param = function[brc:-1].replace(' ','')
                    params = param.split(',')

                    if func in Q2KRef.keyp_actions.keys() and param in layer_names:
                        layer = str(layer_names.index(param))
                        functions.append(Q2KRef.keyp_actions[func]+layer)
                    elif func in Q2KRef.keyp_actions.keys() and ',' in param and len(params) == 2:

                        second = params[1].replace(' ','')
                        first = params[0].replace(' ','')

                        # ACTION_LAYER_TAP_KEY
                        # (HOLD, TAP) => Tap>Hold
                        if first in layer_names and second in Q2KRef.keyp_kc.keys():
                            layer = str(layer_names.index(first))
                            hold = Q2KRef.keyp_actions[func]+layer
                            tap = Q2KRef.keyp_kc[second]
                            if tap == "\"\'\" ":                  # "'" -> quot
                                tap = 'quot'
                            tap = tap.replace("'", '').replace(' ', '')        # Strip ' from all keycodes Strip whitespace
                            tap_hold = ''.join(["'", tap, '>', hold, "'"])
                            functions.append(tap_hold)

                        # ACTION_MOD_KEY
                        elif first in Q2KRef.qmk_legacy_mod.keys() and second in Q2KRef.keyp_kc.keys():
                            mod = Q2KRef.qmk_legacy_mod[first]
                            key = Q2KRef.keyp_kc[second]
                            if key == "\"\'\" ":                  # "'" -> quot
                                key = 'quot'
                            key = key.replace("'", '').replace(' ', '')  # Strip whitespace, strip quotes
                            mod_key = ''.join(["'", mod, '-', key, "'"])
                            functions.append(mod_key)

                        else:
                            functions.append('')
                    else:
                        functions.append('')

        if self.__args.debug or debug:
            self.console.note(['Keycodes'])
            for layer in layer_list:
                print('Layer '+layer.name)
                print(layer.keymap)

        if not layer_list:
            self.console.error(['Parsed and found no keymap', 'Failed to parse keymap file'])
        else:
            revo.build_layout = layer_list

        self.__convert_keycodes(layer_names, functions)

    def __convert_keycodes(self, layer_names, functions):
        """ Convert keycodes to keyplus format for the current build"""

        for layer in self.build_rev.build_layout:
            if self.format == self.__output.keyplus:
                layer.convert_keyplus_keymap(layer_names, functions, self.console)
            #elif self.format == self.__output.kbfirmware:
                #layer.convert_kbf_keymap(layer_list, self.console)

    def __get_templates(self, debug=False):
        """ Get layout templates for the current build from <keyboard>.h"""

        revo = self.build_rev

        if revo.template_list:
            keyboard_h = revo.template_loc

            with open(keyboard_h, 'r', encoding='utf8') as f:
                data = str(f.read())

            token_list = _ParseTxt.layout_headers(data)
            for tokens in token_list:
                curr_template = LayoutTemplate(tokens[0].name)

                for row in tokens[0].layout:
                    layout_row = list(row)
                    curr_template.layout.append(layout_row)

                array = list(tokens[0].array)
                for i, element in enumerate(array):
                    array[i] = re.sub('^[^##]*##', '', element)

                curr_template.array = array
                revo.build_templates.append(curr_template)
            self.__convert_template_index()

        else:
            self.__generate_matrix_template()

        if self.__args.debug or debug:
            self.console.note(['Templates'])
            for template in revo.build_templates:
                print(template.name)
                for row in template.layout:
                    print(row)
                print('Array')
                print(template.array)

    def __generate_matrix_template(self, index=0):
        """ Create a layout template based upon the keycode array in keymap.c"""

        revo = self.build_rev
        layer = revo.build_layout[index]

        if not self.build_rev.build_m_col_pins:
            col_limit = layer.matrix_cols
        else:
            col_limit = len(self.build_rev.build_m_col_pins)

        matrix = []
        row = []
        for i in range(len(layer.keymap)):
            if i % col_limit == 0:
                if i >= col_limit:
                    matrix.append(row)
                row = []
                row.append(i)
            else:
                row.append(i)
        matrix.append(row)
        matrix_template = LayoutTemplate('!MATRIX LAYOUT')
        matrix_template.layout = matrix

        revo.build_templates.append(matrix_template)
        self.build_kb.build_template = '!MATRIX LAYOUT'

    def __convert_template_index(self):
        """ Convert retrieved layout templates to array index format"""

        for template in self.build_rev.build_templates:
            template.convert_template_index(self.console, self.build_rev.build_templates)

    def __merge_layout_template(self, debug=False):
        """ Merge array index format layout template with keyplus format keycode layers"""

        selected = self.build_kb.build_template
        layers = self.build_rev.build_layout
        templates = self.build_rev.build_templates

        for temp in templates:
            if temp.name == selected:
                template = temp
                break
        self.console.note(['Building with template: '+selected])
        for layer_count, layer in enumerate(layers):

            layout_template = template.layout
            layout = copy.deepcopy(layout_template)
            keycode_array = layer.keymap
            max_index = len(keycode_array)

            try:
                for i, rows in enumerate(layout_template):
                    for j, ind in enumerate(rows):
                        if ind < max_index:
                            layout[i][j] = keycode_array[ind]
                        elif template.name != '!MATRIX LAYOUT':
                            self.console.warning(['Corrupt or incompatible layout template or keymap',
                                                  'Invalid array value: '+str(ind),
                                                  'Trying again with default matrix layout...'])
                            self.__generate_matrix_template(layer_count)
                            self.__merge_layout_template()
                            return
                        else:
                            self.console.error(['Corrupt or incompatible keymap', 'Invalid array value: '+str(ind)])
            except TypeError:
                self.console.error(['Corrupt layout template, invalid array index: '+str(ind)])

            layer.layout = layout
            layer.matrix_map = layout_template
            if not self.__args.debug or debug:
                self.console.note(['Layer '+layer.name])
            if debug:
                layout_count = 0
                for row in layout:
                    layout_count += len(row)
                    print(str(len(row)) +'\t| '+str(row))
                print(layout_count)
                print('Matrix Map')
                array_count = 0
                for row in layout_template:
                    array_count += len(row)
                    print(str(len(row)) +'\t| '+str(row))
                print(array_count)
                print(str(max_index)+'\t| '+str(keycode_array))

    def __convert_matrix_map(self, debug=False):
        """ Convert array index format layout to keyplus matrix map format"""

        layers = self.build_rev.build_layout

        for layer in layers:
            if not self.build_rev.build_m_col_pins:
                col_limit = layer.matrix_cols
            else:
                col_limit = len(self.build_rev.build_m_col_pins)
            if self.format == self.__output.keyplus:
                layer.convert_keyplus_matrix(col_limit)
            #elif self.format == self.__output.kbfirmware:
                #layer.convert_kbfirmware_matrix(col_limit)

            if self.__args.debug or debug:
                self.console.note(['Layer '+layer.name])
                for row in layer.layout:
                    print(str(len(row)) +'\t| '+str(row))
                print('Array')
                for row in layer.matrix_map:
                    print(str(len(row)) +'\t| '+str(row))

    def __create_output(self):
        """ Generate output based upon application type (kbfirmware/keyplus)"""

        if self.format == self.__output.keyplus:
            self.__create_keyplus_yaml()
        #elif self.format == self.__output.kbfirmware:
            #layer.convert_kbfirmware_matrix(col_limit)

    def __create_keyplus_yaml(self, debug=False):
        """ Create keyplus format layout.yaml file"""

        # Can't simply dump to yaml as we want to keep layout (array) as a human readable matrix (2D 'array').
        out_dir = self.dirs['Keyplus YAML output']
        kb_n = self.build_kb.name.replace('/', '_').replace('\\', '_')
        rev_n = self.build_rev.name
        if rev_n == 'n/a': rev_n = ''
        keymap = self.build_kb.build_keymap

        rev = self.build_rev
        layers = rev.build_layout

        errors = []
        for error in self.console.errors:
            error = ''.join(['# ', error, '\n'])
            errors.append(error)

        template_matrix = layers[0].matrix_map
        if rev_n:
            name = [kb_n, rev_n]
        else:
            name = [kb_n]

        if rev.build_m_row_pins and rev.build_m_col_pins:
            rows = str(rev.build_m_row_pins)
            cols = str(rev.build_m_col_pins)
            diodes = rev.build_diodes
        else:
            rows = '# ------- Input row pins here ------- '
            cols = '# ------- Input col pins here ------- '
            diodes = rev.build_diodes

        template = []
        for i, row in enumerate(template_matrix):
            for col in row:
                template += [col, ', ']
            if i+1 < len(template_matrix):
                template.append('\n        ')

        layout = []
        keycode_define = []
        for i, layer in enumerate(layers):
            layout += ['      [ # layer ', str(i), '\n        [']
            for row in layer.layout:
                layout.append('\n          ')
                for keycode in row:
                    if len(keycode) < 4:
                        repeat = 4 - len(keycode)
                        for j in range(repeat):
                            keycode += ' '
                    # tap>hold must be explicitly declared for now
                    if '>' in keycode and keycode != "'>' ":
                        if keycode not in keycode_define:
                            keycode_define.append(keycode)
                    layout += [keycode, ', ']
            layout.append('\n        ]\n      ],\n')

        keycodes = []
        if keycode_define:
            keycodes.append('keycodes:')
        for keyc in keycode_define:
            split = keyc.split('>', 1)
            tap = split[0][1:]
            hold = split[1][:-1]

            kc_template = Q2KRef.keyplus_yaml_keycode_template
            kc_template = kc_template.substitute(KEYCODE=keyc, TAP=tap, HOLD=hold)
            keycodes.append(kc_template)

        # Convert lists to strings
        errors = ''.join(errors)
        name = '_'.join(name)
        template = ''.join(template)
        layout = ''.join(layout)
        keycodes = ''.join(keycodes)

        # Load Template
        output_yaml_info = Q2KRef.keyplus_yaml_template
        output_yaml_info = output_yaml_info.substitute(
            ERRORS=errors, KB_NAME=name, LAYOUT_NAME=keymap,
            DIODES=diodes, ROWS=rows, COLS=cols,
            MATRIX_MAP=template, LAYOUT=layout, KEYCODES=keycodes
        )

        kblibs = self.build_kb.libs
        if rev_n:
            path_list = kblibs + [rev_n, keymap]
        else:
            path_list = kblibs + [keymap]
        output_path = '_'.join(path_list)
        output_yaml = os.path.join(out_dir, output_path+'.yaml')
        if not os.path.exists(out_dir):
            try:
                os.makedirs(out_dir)
            except OSError as error:
                if error.errno != errno.EEXIST and os.path.isdir(out_dir):
                    raise
        try:
            with open(output_yaml, 'w') as f:
                f.write(output_yaml_info)
        except:
            self.console.error(['Failed to pipe output to '+output_yaml])

        if self.__args.debug or debug:
            print(output_yaml_info)

        self.console.note(['SUCCESS! Output is in: '+output_yaml])


def q2keyplus():
    """" Hook-in function for q2k-cli command line interface"""
    q2k = Q2KApp('keyplus')
    q2k.execute()

#def q2kbfirmware():
#    q2k = application('kbfirmware')
#    q2k.execute()

# Just here as an example for reference

#def q2keyplus_gui(keyboard, rev, keymap, template):
#    q2k = application('keyplus', is_gui=True)
#    q2k.set_kb(keyboard, rev, keymap, template)
#    q2k.execute()
