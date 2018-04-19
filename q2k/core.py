import argparse
import glob
import pathlib
import errno
import os
import yaml
import sys
import re
import copy
import subprocess
import pyparsing as pp
import termcolor as tc
import pkg_resources as pkg
import enum as en

from q2k.reference import ref

class defaults:
    # Directories
    DEBUG = False
    if DEBUG:
        src = ''
    else:
        src = pkg.resource_filename(pkg.Requirement.parse("q2k"),"q2k/")
    libs = pkg.resource_filename(pkg.Requirement.parse("q2k"),"q2k/lib/")
    cache = src+'cache/cache_kb.yaml'
    qmk = ''
    keyp = 'q2k_out/keyplus/'
    kbf = 'q2k_out/kbfirmware/'
    # Lists
    qmk_nonstd_dir = ['handwired', 'converter', 'clueboard', 'lfkeyboards'] # Currently only lfkeyboards causes any issues, however it is good to be verbose here
    mcu_compat = ['atmega32u4', 'atmega32u2']                               # Compatible MCU types
    kbf_mcu_compat = ['atmega32u4', 'atmega32u2']

class _console:

    def __init__(self, gui):
        self.gui = gui
        self.errors = []

    def error(self, info):
        '''
        if self.gui:
            for line in info:
                self.errors.append(line)

        else:
        '''
        error_msg = tc.colored('❌ ERROR:', 'red', attrs=['reverse', 'bold'])
        e_bullet = tc.colored('•', 'red', attrs=['bold'])
            
        for info, line in enumerate(info):
            if not info:
                self.errors.append(line)
                line = tc.colored(line, 'red')
                print(error_msg + ' ' +line)
            else:
                self.errors.append(line)
                print(e_bullet + ' '+line)

    def bad_kc(self, kc_type, code):
        '''
        if self.gui:
            for line in info:
                self.errors.append(line)
        else:
        '''
        message = 'Invalid '+kc_type+': '+code
        bad_kc_msg = tc.colored('❌ Invalid '+kc_type+':', 'cyan')
        print(bad_kc_msg+' '+code)
        self.errors.append(message)

    def warning(self, info):
        '''
        if self.gui:
            for line in info:
                self.errors.append(line)
        else: 
        '''
        warning_msg = tc.colored('▲ WARNING:', 'yellow', attrs=['bold'])
        w_bullet = tc.colored('•', 'yellow', attrs=['bold'])
        
        for info, line in enumerate(info):
            if not info:
                self.errors.append(line)
                line = tc.colored(line, 'yellow')
                print(warning_msg + ' ' +line)
            else:
                self.errors.append(line)
                print(w_bullet + ' '+line)

    def note(self, info):
        '''
        if self.gui:
            return
        else:
        '''
        note_msg = tc.colored('✔', 'green', attrs=['bold'])
        n_bullet = tc.colored('•', 'green', attrs=['bold'])
        
        for info, line in enumerate(info):
            if not info:
                print(note_msg + ' ' +line)
            else:
                print(n_bullet + ' '+line)

class _parse_txt:

    def layout_headers(data):

        LPAREN, RPAREN, LBRAC, RBRAC, COMMA = map(pp.Suppress, "(){},")
        BSLASH = pp.Suppress(pp.Literal('\\'))

        define = pp.Suppress(pp.Literal('#define'))
        name = pp.Word(pp.alphanums+'_')
        macrovar = pp.Word(pp.alphanums+'_#')
        layout_row = pp.Group(pp.OneOrMore(macrovar + pp.Optional(COMMA)) + pp.ZeroOrMore(BSLASH))
        layout =  LPAREN + pp.ZeroOrMore(BSLASH) + pp.OneOrMore(layout_row) + RPAREN
        matrix_row = pp.ZeroOrMore(BSLASH) + pp.Optional(LBRAC) +  pp.ZeroOrMore(BSLASH) + pp.OneOrMore(macrovar + pp.Optional(COMMA)) + pp.ZeroOrMore(RBRAC) + pp.Optional(COMMA) + pp.ZeroOrMore(BSLASH)
        matrix = pp.ZeroOrMore(BSLASH) + LBRAC +  pp.ZeroOrMore(BSLASH) + pp.OneOrMore(matrix_row) +  pp.ZeroOrMore(BSLASH) + RBRAC +  pp.ZeroOrMore(BSLASH)

        header = define + name('name') + pp.ZeroOrMore(BSLASH) + layout('layout') + pp.ZeroOrMore(BSLASH) + matrix('array')
        header.ignore(pp.cStyleComment)

        hresults = list(header.scanString(data))
        names = []
        for tokens, start, end in (hresults):
            i = 0
            while tokens.name in names:
                i += 1
                if not tokens.name.endswith(')'):
                    tokens.name += '('+str(i)+')'
                else:
                    tokens.name = tokens.name[:-2]+str(i)+')'
            names.append(tokens.name)
                
        return hresults

    def config_headers(data):

        data = str(data)
        matrix_pins = []
        matrix_row_pins = []
        matrix_col_pins = []
        
        LBRAC, RBRAC, COMMA = map(pp.Suppress, "{},")
        define_rows = pp.Suppress(pp.Literal('#define MATRIX_ROW_PINS'))
        define_cols = pp.Suppress(pp.Literal('#define MATRIX_COL_PINS'))
        pincode = pp.Word(pp.alphanums) | pp.Word(pp.nums)

        array = LBRAC + pp.ZeroOrMore(pincode + pp.Optional(COMMA)) + RBRAC
        matrix_rows = define_rows + LBRAC + pp.ZeroOrMore(pincode + pp.Optional(COMMA)) + RBRAC
        matrix_cols = define_cols + LBRAC + pp.ZeroOrMore(pincode + pp.Optional(COMMA)) + RBRAC

        for tokens, start, stop in matrix_rows.scanString(data):
            matrix_row_pins = list(tokens)
        for tokens, start, stop in matrix_cols.scanString(data):
            matrix_col_pins = list(tokens)

        if matrix_row_pins and matrix_col_pins:
            matrix_pins.append(matrix_row_pins)
            matrix_pins.append(matrix_col_pins)

        return matrix_pins

    def rules_mk(data):

        data = str(data)
        EQUALS = pp.Suppress('=')
        mcu_tag = pp.Suppress(pp.Literal('MCU'))
        mcu_type = pp.Word(pp.alphanums+'_')

        mcu = mcu_tag + EQUALS + mcu_type('mcu')
        mcu.ignore('#'+pp.restOfLine)

        return mcu.scanString(data)

    def keymaps(data):

        data = str(data)
        LBRAC, RBRAC,EQ, COMMA = map(pp.Suppress,"{}=,")

        integer = pp.Word(pp.nums)
        keycode = pp.Word(pp.alphanums+'_'+'('+')')
        layer_string = pp.Word(pp.printables) | pp.Word(pp.nums)

        keycode_list = pp.Group(pp.ZeroOrMore(keycode + pp.Optional(COMMA)))
        row = LBRAC + keycode_list + RBRAC

        layern = layer_string('layer_name') + EQ
        km_layer_data = LBRAC + pp.OneOrMore(row + pp.Optional(COMMA)) + RBRAC
        km_layer = pp.Optional(layern) + km_layer_data('layer') + pp.Optional(COMMA)
        km_layer.ignore(pp.cppStyleComment+pp.pythonStyleComment)

        return km_layer.scanString(data)

class _cpp:

    def __init__(self, kbo, dirs, console):
        self.__kb = kbo
        self.__dirs = dirs
        self.__console = console

    def __preproc(self, kblibs, arg_list, DEBUG=False):
        # Setting up -I and custom define options
        qdir = self.__dirs['QMK dir'] + 'keyboards/'
        kb = self.__kb.name
        cc = ['avr-gcc', '-E']
        kbdefine = 'KEYBOARD_'+'_'.join(kblibs)
        QMK_KEYBOARD_H = 'QMK_KEYBOARD_H=\"'+kb+'.h\"'
        libs = ['-D', kbdefine, '-D', QMK_KEYBOARD_H, '-I'+self.__dirs['Local libs']]
        path = qdir
        for kbl in kblibs:
            kbl += '/'
            path += kbl
            libs.append('-I'+path)
        argv = cc + libs + arg_list
        if DEBUG: print(' '.join(argv))
        try:
            output = subprocess.check_output(argv)
            return output
        except subprocess.CalledProcessError as e:
            err_num = e.returncode
            if err_num == 1:
                print(err_num)
                output = e.output
                return output
            else:
                self.console.warning(['Potentially catastrophic compilation error'])
                return
    
    def preproc_header(self, path):

        kblibs = list(self.__kb.libs)
        if self.__kb.build_rev:
            kblibs.append(self.__kb.build_rev)

        arg = [ '-D', 'QMK_KEYBOARD_CONFIG_H=\"config_common.h\"', '-dD', path ]
        if os.path.isfile(path):
            output = str(self.__preproc(kblibs, arg)).replace('\\n', ' ')
            return output

    def preproc_keymap(self):

        qdir = self.__dirs['QMK dir'] +'keyboards/'
        kb = self.__kb.name
        km = self.__kb.build_keymap+'/keymap.c'
        kblibs = list(self.__kb.libs)
        rev = self.__kb.build_rev
        if rev != '':
            kblibs.append(rev)

        # KEYMAP
        keym = qdir+kb+'/keymaps/'+km
        if rev != '' and not os.path.isfile(keym):
            keym = qdir+kb+'/'+rev+'/keymaps/'+km

        # OUTPUT
        argkm = [keym]
        if os.path.isfile(keym):
            output = str(self.__preproc(kblibs, argkm)).replace('\\n', ' ')
            return output
        else:
            self.__console.error(['Keymap cannot be read by preprocessor', 'Failed to parse keymap file'])
            exit()

class kb_info:

    def __init__(self, n=''):

        self.name = n                       # Name of keyboard
        self.libs = []                      # Possible QMK lib folders (partly depreciated)
        self.rev_list = []                  # List of rev obj names
        self.rev_info = []                  # A list of rev_info objects

    def init_build(self):

        self.build_rev = ''                 # What revision to build with
        self.build_keymap = ''              # What keymap to build with
        self.build_template = ''            # What layout to build with

    def add_rev_list(self, rev, flag=False):
        if not flag:
            self.rev_list.append(rev)
        revo = rev_info(rev, flag)
        self.rev_info.append(revo)

    def get_rev_info(self, rev):
        for r in self.rev_info:
            if r.name == rev:
               return r
            if r.name == 'n/a':
               return r

# A class for listing revision info
class rev_info:

    def __init__ (self, n='', flag=False):

        self.name = n                  # Name of Revision
        self.keymap_list = []              # List of layout NAMES
        self.template_list = []            # List of template NAMES
        self.template_loc = ''             # Location of <keyboard>.h
        self.is_default = flag             # Does keyboard have revisions? (or just default)

    def init_build(self):

        self.build_mcu_list = []                 # MCU list
        self.build_m_row_pins = []               # Row pins
        self.build_m_col_pins = []               # Column pins
        self.build_layout = []                   # list of keycode_layers objects (which form layout) -> Final yaml/json output comes from here
        self.build_templates = []                # list of layout_template objects

# A class for linking matrix mapping in <keyboard>.h with (preprocessed) keymap.c keycode layers.
class layout_template:

    def __init__(self, n=''):
        self.name = n                      # Name of template : e.g. LAYOUT, KEYMAP, LAYOUT_66_ANSI
        self.layout = []                   # List of layout rows
        self.array = []                    # Array holding index values (to be merged with keycode_layers)

    def convert_template_index(self, console=_console(False), template_list=[]):

        for i, row in enumerate(self.layout):
            for j, col in enumerate(row):
                try:
                    self.layout[i][j] = self.array.index(col)
                except ValueError:
                    console.warning([self.name+' - missing macro variable ['+str(col)+']'])
                    # Try to recover using a different keycode array
                    if template_list:
                        for t in template_list:                    
                            array2 = t.array
                            if len(array2) != len(self.array) or self.name == t.name:
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
                        console.error(['Array key recovery failed', 'Will assume this corresponds to KC_NO'])

# A class for storing keycode layers
class keycode_layer:

    def __init__(self, n=''):

        self.name = n                      # Name of current layer
        self.keymap = []                   # List of lists representing Raw [QMK] KEYMAP layers (keycode layers)
        self.layout = []                   # List of lists output for converted [keyplus] keycode layers/layout
        self.matrix_map = []               # Matrix mapping in [keyplus] format
        self.matrix_cols = 0

    def convert_keyplus_keymap(self, layer_list, console):

        for i, kc in enumerate(self.keymap):
            if kc.endswith(')') and '(' in kc:
                self.keymap[i] = self.__func(kc, layer_list, console)
            else:
                self.keymap[i] = self.__keycode(kc, console)

    def convert_keyplus_matrix(self, col_limit):
        matrix = copy.deepcopy(self.matrix_map)
        for i, row in enumerate(self.matrix_map):
            j = 0
            for col in row:
                int(col)
                if col != -1:
                    r = col // col_limit
                    c = col % col_limit
                    matrix[i][j] = 'r'+str(r)+'c'+str(c)
                    j += 1
                else:
                    del matrix[i][j]
                    del self.layout[i][j]
                    j = max(j-1, 0)
        self.matrix_map = matrix

    def __func(self, qmk_func, layer_list, console):
        # Currently only handles layer switching functions
        # TODO: support keyplus s- + c- style modifiers
        if qmk_func in ref.keyp_func_list.keys():
            keyp_func = ref.keyp_func_list[qmk_func]
        else:
            try:
                brac_index = qmk_func.index('(')+1
                qfunc = qmk_func[:brac_index]
                func_target = qmk_func[brac_index:-1]

                if func_target in layer_list:
                    layer = str(layer_list.index(func_target))
                    keyp_func = ref.keyp_func_list[qfunc]+layer
                else:
                    console.bad_kc('FN','['+qmk_func+'] - set to trns')
                    keyp_func = 'trns'
            except KeyError:
                console.bad_kc('FN','['+qmk_func+'] - set to trns')
                keyp_func = 'trns'
            except ValueError:
                console.bad_kc('FN','['+qmk_func+'] - set to trns')
                keyp_func = 'trns'

        return keyp_func

    def __keycode(self, qmk_kc, console):
        try:
            keyp_kc = ref.keyp_kc_list[qmk_kc]
        except KeyError:
            console.bad_kc('KC','['+qmk_kc+'] - set to trns')
            keyp_kc = 'trns'
        return keyp_kc

class _cache:

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
        if os.path.isfile(self.__loc):
            try:
                with open(self.__loc, 'r') as f:
                    self.kbo_list = yaml.load(f)
                    self.__console.note(['Using cached list from '+self.__loc, '--cache to reset'])
            except:
                self.__console.warning(['Failed to load from '+self.__loc, 'Generating new cache_kb.yaml...'])
                self.__write()
        else:
                self.__write()

    def __write(self):

        templist = []
        keymaplist = []

        for fn in glob.glob(self.__qmk+'keyboards/**/rules.mk', recursive=True):
            fn = fn[:-9]
            templist.append(fn)

        for fn in glob.glob(self.__qmk+'keyboards/**/keymaps/**/keymap.c', recursive=True):
            fn = fn[:-9]
            if fn in templist:
                templist.remove(fn)
            fn = fn.replace(self.__qmk+'keyboards/', '', 1)
            keymaplist.append(fn)

        for child in templist:
            p_path = str(pathlib.Path(child).parent)
            p_name = p_path.replace(self.__qmk+'keyboards/', '', 1)

            if p_path not in templist and p_name not in defaults.qmk_nonstd_dir:
                name = child.replace(self.__qmk+'keyboards/', '', 1)
                # If in special dir list, then is part of the directory not keyboard
                if name not in defaults.qmk_nonstd_dir:
                   # This is a keyboard, not revision
                   kbo = kb_info(name)
                   kblibs = name.split('/')
                   kbo.libs = kblibs 
                   self.kbo_list.append(kbo)   
            elif p_name in defaults.qmk_nonstd_dir:
                name = child.replace(self.__qmk+'keyboards/', '', 1)
                # This is a keyboard, not revision
                kbo = kb_info(name)
                kblibs = name.split('/')
                kbo.libs = kblibs
                self.kbo_list.append(kbo)
            else:
                # This is a 'revision' of an existing keyboard
                rev = child.replace(p_path+'/', '')
                for kbo in self.kbo_list:
                    if kbo.name == p_name:
                        kbo.add_rev_list(rev)
                        break

        for kbo in self.kbo_list:
            if not kbo.rev_list:
                kbo.add_rev_list('n/a', True)
            self.__find_layout_names(kbo)

        for km_path in keymaplist:
            info_list = km_path.split('/keymaps/')
            kb_name = info_list[0]
            km_name = info_list[-1]
            namelist = kb_name.split('/')
            match = False
            prev = 'n/a'
            for i in range(0, len(namelist)):
                if i > 0: 
                    kb_name = '/'.join(namelist)

                for kbo in self.kbo_list:
                    if kbo.name == kb_name:
                        if prev in kbo.rev_list:
                            revo = kbo.get_rev_info(prev)
                            revo.keymap_list.append(km_name)
                        else:
                            for revo in kbo.rev_info:
                                revo.keymap_list.append(km_name)
                        match = True
                        break
                if match:
                    break
                prev = namelist.pop()

        if self.kbo_list:
            # Dump cache info to text file for faster processing in future
            self.__save_cache()
            self.__console.note(['New cache_kb.yaml successfully generated', 'Location: '+self.__loc])
        else:
            self.__console.error(['No keyboard information found', 'Check QMK directory location in pref.yaml : '+self.__qmk])
            if not self.__console.gui: exit()
        

    def __find_layout_names(self, kbo):
        
        rev_list = list(kbo.rev_list)
        if not rev_list:
            rev_list.append('n/a')
        
        for rev in rev_list:
            found = False
            revo = kbo.get_rev_info(rev)
            # qmk/keyboards/
            kblibs = list(kbo.libs)
            if rev != 'n/a':
                kblibs.append(rev)
            qdir = self.__qmk +'keyboards/'

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

                try:
                    with open(path, 'r') as f:
                        data = str(f.read())
                except FileNotFoundError:
                    #self.__console.warning(['Layout header not found in '+path, 'Trying a different path...'])
                    continue

                token_list = _parse_txt.layout_headers(data)
                #template_list = []
                for tokens, start, end in token_list:
                    revo.template_list.append(tokens.name)

                if revo.template_list:
                    #self.__console.note(['Layout header found @ '+path])
                    found = True
                    revo.template_loc = path
                    break

            if rev != 'n/a' and not found:
                self.__console.warning(['Layout templates not found for '+kbo.name+'/'+rev])
                revo.template_loc = 'n/a'
            elif not found:
                self.__console.warning(['Layout templates not found for '+kbo.name])
                revo.template_loc = 'n/a'

    def __save_cache(self):

        path = '/'.join(self.__loc.split('/')[:-1])
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except OSError as e:
                if e.errno != errno.EEXIST and os.path.isdir(path):
                    raise
        try:
            with open(self.__loc, 'w') as f:
                yaml.dump(self.kbo_list, f)
        except:
            self.__console.error(['Failed to create '+self.__loc])

    def _clear_cache(self):
        if os.path.isfile(self.__loc):
            os.remove(self.__loc)

    def _keyboard_list(self,):
        kb_names = []
        for kbo in self.kbo_list:
            kb_names.append(kbo.name)
        return kb_names

    def _keymap_list(self, keyboard, rev=''):
        km_names = []
        for kbo in self.kbo_list:
            if kbo.name == keyboard:
                revo = kbo.get_rev_info(rev)
                if revo:
                    for km in revo.keymap_list:
                        km_names.append(km)
                    return km_names
                else: 
                    self.__console.error(['Revision # required - Valid Revisions:'])
                    print(self._rev_list(keyboard))

    def _rev_list(self, keyboard):

        for kbo in self.kbo_list:
            if kbo.name == keyboard:
                return kbo.rev_list

    def _template_list(self, keyboard, rev=''):
        tp_names = []
        for kbo in self.kbo_list:
            if kbo.name == keyboard:
                revo = kbo.get_rev_info(rev)
                if revo:
                    for tp in revo.template_list:
                        tp_names.append(tp)
                    return tp_names
                else: 
                    self.__console.error(['Revision # required - Valid Revisions:'])
                    print(self._rev_list(keyboard))

class application:

    def __init__(self, app_type, is_gui=False):

        self.__output = en.Enum('output', 'keyplus kbfirmware')
        self.format = self.__output[app_type]
        self.is_gui = is_gui
        self.console = _console(is_gui)
        # self.dirs      # directories
        # self.build_kb  # kb_info for build
        # self.build_rev # rev_info for build
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
            self.__pop_cache_list()

    def __read_args(self):
        # Read ARGV input from terminal
        parser = argparse.ArgumentParser(description='Convert AVR C based QMK keymap and matrix files to YAML Keyplus format')
        parser.add_argument('keyboard', metavar='KEYBOARD', nargs='?', default='', help='The name of the keyboard whose keymap you wish to convert')
        parser.add_argument('-m', '--keymap', metavar='KEYMAP', dest='keymap', default='default', help='The keymap folder to reference - default is /default/')
        parser.add_argument('-t', '--template', metavar='LAYOUT', dest='template', default='', help='The layout template to reference')
        parser.add_argument('-r', '--rev', metavar='ver',dest='rev', default='', help='Revision of layout - default is n/a')
        parser.add_argument('--cache', dest='clearcache', action='store_true', help='Clear cached data (cache_kb.yaml)')
        parser.add_argument('--reset', dest='clearpref', action = 'store_true', help='Restore preferences in pref.yaml to default')
        parser.add_argument('--debug', dest='debug', action='store_true', help='See debugging information')
        parser.add_argument('-l', '-L', '--list', dest='listkeyb', action='store_true',help='List all valid KEYBOARD inputs')
        parser.add_argument('-M', '--keymaps', dest='listkeym', action='store_true',help='List all valid KEYMAPS for the current keyboard')
        parser.add_argument('-T', '--templatelist', dest='listkeyt', action='store_true',help='List all valid LAYOUTS for the current keyboard')
        parser.add_argument('-R', '--revlist', dest='listkeyr', action='store_true',help='List all valid REVISIONS for the current keyboard')
        parser.add_argument('-S', '--search', metavar='string', dest='searchkeyb', help='Search valid KEYBOARD inputs')
        self.__args = parser.parse_args()

    def __set_dirs(self):

        if self.__args.clearpref:
            self.__generate_dirs()
        else:
            try:
                with open(defaults.src+'pref.yaml', 'r') as f:
                    self.dirs = yaml.load(f)
                    self.console.note(['Using preferences from '+defaults.src+'/pref.yaml', '--reset to reset to defaults'])

            except FileNotFoundError:
                self.__generate_dirs()

            except AttributeError:
                self.__generate_dirs()

    def __generate_dirs(self):

        dirs = {
            'QMK dir' : defaults.qmk,
            'Keyplus YAML output' : defaults.keyp,
            'Kbfirmware JSON output' : defaults.kbf,
            'Local libs' : defaults.libs,
            'Cache' : defaults.cache,            
        }
        self.dirs = dirs

        with open(defaults.src+'pref.yaml', 'w') as f:
            f.write('# Q2K Folder Locations\n')
            yaml.dump(dirs, f, default_flow_style = False)
            self.console.note(['New pref.yaml generated'])

    def __pop_cache_list(self):

        self.__cache = _cache(self.dirs, self.console, self.__args.clearcache)

    def __check_args(self):

        if self.__args.listkeyb and not self.is_gui:
            self.console.note(['Listing keyboards...'])
            print(self.keyboard_list())
            exit()
        elif self.__args.listkeyr and not self.is_gui:
            self.console.note(['Listing revisions for '+self.__args.keyboard+'...'])
            print(self.rev_list(self.__args.keyboard))
            exit()
        elif self.__args.listkeym and not self.is_gui:
            if self.__args.rev == '':
                self.console.note(['Listing keymaps for '+self.__args.keyboard+'...'])
                print(self.keymap_list(self.__args.keyboard))
            else:
                self.console.note(['Listing keymaps for '+self.__args.keyboard+'/'+self.__args.rev+'...'])
                print(self.keymap_list(self.__args.keyboard, self.__args.rev))
            exit()
        elif self.__args.listkeyt and not self.is_gui:
            if self.__args.rev == '':
                self.console.note(['Listing layout templates for '+self.__args.keyboard+'...'])
                self.template_list(self.__args.keyboard, self.__args.rev)
            else:
                self.console.note(['Listing layout templates for '+self.__args.keyboard+'/'+self.__args.rev+'...'])
                self.template_list(self.__args.keyboard)
            exit()
        elif self.__args.searchkeyb and not self.is_gui:
            self.console.note(['Searching...'])
            print(self.search_keyboard_list(self.__args.searchkeyb))
            exit()

        self.set_kb(self.__args.keyboard, self.__args.rev, self.__args.keymap, self.__args.template)

    # Intended hook-in for GUIs
    def set_kb(self, keyboard='', rev='', keymap='', template=''):

        kb_list = self.__cache.kbo_list
        build_kbo = ''

        if not keyboard:
            self.console.error(['No keyboard name given', 'Valid Names:'])
            if not self.is_gui:
                print(self.keyboard_list())
            exit()

        for kbo in kb_list:
            if kbo.name == keyboard:
                build_kbo = kbo
                break

        if build_kbo:
            # Check Revision
            # Case 1: Have Revisions
            if len(build_kbo.rev_list) > 0 and rev not in build_kbo.rev_list:
                self.console.error(['Invalid Revision - '+rev, 'Valid Revisions:'])
                if not self.is_gui:
                    print(self.rev_list(keyboard))
                exit()
            # Case 2: No Revisions
            elif len(build_kbo.rev_list) < 1 and rev != '':
                self.console.error(['Invalid Revision - '+rev, 'Valid Revisions:'])
                print(self.rev_list(keyboard))
                exit()

            build_revo = build_kbo.get_rev_info(rev)
            # Check Layout
            # Case 1: Have Layout Templates
            if len(build_revo.template_list) > 0 and template not in build_revo.template_list:
                self.console.error(['Invalid Template - '+template, 'Valid Layouts:'])
                if not self.is_gui:
                    print(self.template_list(keyboard, rev))
                exit()
            # Case 2: No Layout Templates
            elif len(build_revo.template_list) < 1 and template != '':
                self.console.error(['Invalid Template - '+template, 'Valid Layouts: None'])
                #print(self.template_list(keyboard, rev))
                exit()

            # Check Keymap
            if keymap not in build_revo.keymap_list:
                self.console.warning(['Invalid Keymap - '+template, 'Valid Keymaps:'])
                if not self.is_gui:
                    print(self.keymap_list(keyboard))
                exit()

            build_kbo.init_build()    
            build_revo.init_build()
            build_kbo.build_keymap = keymap
            build_kbo.build_template = template
            build_kbo.build_rev = rev
            self.build_kb = build_kbo
            self.build_rev = build_revo
        else:
            self.console.error(['Invalid Keyboard Name - '+keyboard, 'Valid Names:'])
            if not self.is_gui:
                print(self.keyboard_list())
            exit()

    def refresh_dir(self):
        self.__set_dirs()

    def reset_dir_defaults(self):
        self.__generate_dirs()

    def refresh_cache(self):
        self.__cache = _cache(self.dirs, self.console, True)

    def clear_cache(self):
        self.__cache._clear_cache()

    def keyboard_list(self):

        return self.__cache._keyboard_list()

    def rev_list(self, keyboard):

        return self.__cache._rev_list(keyboard)

    def template_list(self, keyboard, rev=''):

        return self.__cache._template_list(keyboard, rev)

    def keymap_list(self, keyboard, rev=''):

        return self.__cache._keymap_list(keyboard, rev)

    def search_keyboard_list(self, string):

        kb_names = self.__cache._keyboard_list()
        results = []
        for kb in kb_names:
            if kb.find(string) != -1:
                results.append(kb)
        return results

    def execute(self):

        self.__cpp = _cpp(self.build_kb, self.dirs, self.console)

        self.__check_mcu()              # Check for MCU and Matrix Pins
        self.__get_config_header()
        self.__get_keycodes()           # Init Layout + Templates
        self.__get_templates()
        self.__convert_keycodes()       # Process Layout + Templates
        self.__merge_layout_template()
        self.__convert_matrix_map()
        self.__create_output()          # Pipe output to yaml/json

    def __check_mcu(self):
        self.__get_mcu()
        kb = self.build_kb.name
        rev = self.build_rev.name
        revo = self.build_rev

        for mcu in revo.build_mcu_list:
            if mcu in defaults.mcu_compat:
                continue
            else:
                self.console.warning(
                    ['Possible MCU incompatability detected', 
                    'MCU type: '+mcu+' in '+kb+'/'+rev+' rules.mk', 
                    'Currently, keyplus supports only boards with the following microcontrollers:',
                    str(defaults.mcu_compat),
                    'If your board has a MCU on this list then ignore this warning as a false positive',
                    'Else layout files produced may not work with keyplus until your board\'s mcu is supported',
                    'Press [ENTER] to continue'])
                if not self.is_gui:
                    input()
                return

        self.console.note(['No MCU incompatability detected'])

    def __get_mcu(self):

        rev = self.build_rev.name
        revo = self.build_rev
        kblibs = list(self.build_kb.libs)
        if rev != 'n/a':
            kblibs.append(rev)

        qdir = self.dirs['QMK dir'] +'keyboards/'
        folders = []
        path = ''

        for kbl in kblibs:
            path += kbl+'/'
            folders.append(path)

        for kbl in reversed(folders):
            rules_mk = 'rules.mk'

            path = qdir+kbl+rules_mk
            mcu_list = []
            try:
                with open(path, 'r') as f:
                    data = str(f.read())
            except FileNotFoundError:
                self.console.warning(['Rules.mk not found in '+path, 'Trying a different path...'])
                return

            token_list = _parse_txt.rules_mk(data)
            for tokens, start, end in token_list:
                mcu_list.append(tokens.mcu)

            if mcu_list:
                revo.build_mcu_list = mcu_list
                return
            else:
                continue

        self.__console.warning(['Rules.mk not found for '+kbo.get_name()])
        return

    def __get_config_header(self):

        rev = self.build_rev.name
        revo = self.build_rev
        kblibs = list(self.build_kb.libs)
        if rev != 'n/a':
            kblibs.append(rev)

        qdir = self.dirs['QMK dir'] +'keyboards/'
        folders = []
        path = ''

        for kbl in kblibs:
            path += kbl+'/'
            folders.append(path)

        for kbl in reversed(folders):
            config_h = 'config.h'

            path = qdir+kbl+config_h
            data = self.__cpp.preproc_header(path)

            matrix_pins = _parse_txt.config_headers(data)
            if matrix_pins:
                revo.build_m_row_pins = matrix_pins[0]
                revo.build_m_col_pins = matrix_pins[1]  
                self.console.note(['Matrix pinout data found @ '+path])
                return
            else:
                continue

        self.console.warning(['Config.h header not found for '+self.build_kb.name, 'Matrix row/col pins must be provided manually!']) 
        return

    def __get_keycodes(self, DEBUG=False):

        rev = self.build_rev.name
        revo = self.build_rev
        data = self.__cpp.preproc_keymap()
        token_list = _parse_txt.keymaps(data)

        layer_list = []
        num_col = 0
        layer_index = -1
        for tokens, start, stop in token_list:
            layer_index += 1
            if tokens.layer_name == '':
                curr_layer = keycode_layer(str(layer_index))
            else:
                curr_layer = keycode_layer(tokens.layer_name[1:-1]) 

            for row in tokens.layer:
                # Annoying fix for problem with QMK functions X(x,y)
                for i, element in enumerate(row):
                    if ')' in element and '(' not in element:
                        func = ''
                        func = row[i-1]+','+row[i] 
                        del row[i-1]
                        i -= 1
                        del row[i]
                        row.insert(i, func)

                num_col = len(row)
                curr_layer.keymap += (list(row))
            
            curr_layer.matrix_cols = num_col
            layer_list.append(curr_layer)

        if self.__args.debug or DEBUG:
            self.console.note(['Keycodes'])
            for layer in layer_list:
                print('Layer '+layer.name) 
                print(layer.keymap)

        if not layer_list:
            self.console.error(['Parsed and found no keymap', 'Failed to parse keymap file'])
            exit()
        else:
            revo.build_layout = layer_list

    def __convert_keycodes(self, DEBUG=False):

        layers = self.build_rev.build_layout
        layer_list = []
        for layer in layers:
            layer_list.append(layer.name)

        for layer in layers:
            if self.format == self.__output.keyplus:
                layer.convert_keyplus_keymap(layer_list, self.console)
            #elif self.format == self.__output.kbfirmware:
                #layer.convert_kbf_keymap(layer_list, self.console)

    def __get_templates(self, DEBUG=False):

        rev = self.build_rev.name
        revo = self.build_rev

        if revo.template_list:
            keyboard_h = revo.template_loc

            with open(keyboard_h, 'r') as f:
                data = str(f.read())
            
            token_list = _parse_txt.layout_headers(data)
            for tokens, start, end in token_list:
                curr_template = layout_template(tokens.name)

                for row in tokens.layout:
                    layout_row = list(row)
                    curr_template.layout.append(layout_row)
                   
                array = list(tokens.array)
                for i, element in enumerate(array):
                    array[i] = re.sub('^[^##]*##', '', element) 

                curr_template.array = array
                revo.build_templates.append(curr_template)
            self.__convert_template_index()

        else:
            self.__generate_matrix_template()

        if self.__args.debug or DEBUG:
            self.console.note(['Templates'])
            for template in revo.build_templates:
                print(template.name)
                for row in template.layout:
                    print(row)
                print('Array')
                print(template.array)

    def __generate_matrix_template(self, index=0):

        rev = self.build_rev.name
        revo = self.build_rev
        layer = revo.build_layout[index]

        col_limit = layer.matrix_cols
        matrix = []
        for i in range(len(layer.keymap)):
            if i % col_limit == 0:
                if i >= col_limit:
                   matrix.append(row)
                row = []
                row.append(i)
            else:
                row.append(i)
        matrix.append(row)
        matrix_template = layout_template('!MATRIX LAYOUT')
        matrix_template.layout = matrix

        revo.build_templates.append(matrix_template)
        self.build_kb.build_template = '!MATRIX LAYOUT'

    def __convert_template_index(self):

        for template in self.build_rev.build_templates:
            template.convert_template_index(self.console, self.build_rev.build_templates)

    def __merge_layout_template(self, DEBUG=False):

        selected = self.build_kb.build_template
        layers = self.build_rev.build_layout
        templates = self.build_rev.build_templates

        for t in templates:
            if t.name == selected:
                template = t
                break

        self.console.note(['Building with template: '+selected])
        for x, layer in enumerate(layers):   

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
                            self.console.warning(['Corrupt/incompatible layout template or keymap', 
                                'Invalid array value: '+str(ind),
                                'Trying again with default matrix layout...'])
                            self.__generate_matrix_template(x)
                            merge_layout_template()
                            exit()
                        else:
                            self.console.error(['Corrupt/incompatible keymap',
                                'Invalid array value: '+str(ind)])
                            exit()
            except TypeError:
                self.console.error(['Corrupt layout template, invalid array index: '+str(ind)])
                exit()

            if not self.build_rev.build_m_col_pins:
                col_limit = layer.matrix_cols
            else:
                col_limit = len(self.build_rev.build_m_col_pins)

            layer.layout = layout
            layer.matrix_map = layout_template
            if not self.__args.debug or DEBUG:
                self.console.note(['Layer '+layer.name])
            if DEBUG:
                for row in layout:
                    print(str(len(row)) +'\t| '+str(row))
                print('Array')
                for row in layout_template:
                    print(str(len(row)) +'\t| '+str(row))

    def __convert_matrix_map(self, DEBUG=False):
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

            if self.__args.debug or DEBUG:
                self.console.note(['Layer '+layer.name])
                for row in layer.layout:
                    print(str(len(row)) +'\t| '+str(row))
                print('Array')
                for row in layer.matrix_map:
                    print(str(len(row)) +'\t| '+str(row))

    def __create_output(self, DEBUG=False):
        if self.format == self.__output.keyplus:
            self.__create_keyplus_yaml()
        #elif self.format == self.__output.kbfirmware:
            #layer.convert_kbfirmware_matrix(col_limit)

    def __create_keyplus_yaml(self, DEBUG=False):

        # Can't simply dump to yaml as we want to keep layout (array) as a human readable matrix (2D 'array').
        out_dir = self.dirs['Keyplus YAML output']
        kb_n = self.build_kb.name
        rev_n = self.build_rev.name
        if rev_n == 'n/a': rev_n = ''
        keymap = self.build_kb.build_keymap

        rev = self.build_rev
        layers = rev.build_layout
        errors = ''
        for error in self.console.errors:
            errors += '# '+error+'\n'

        template_matrix = layers[0].matrix_map
        if rev_n:
            name = kb_n+'_'+rev_n
        else:
            name = kb_n

        if rev.build_m_row_pins and rev.build_m_col_pins:
            rows = str(rev.build_m_row_pins)
            cols = str(rev.build_m_col_pins)
        else:
            rows = cols = ''
       
        template = ''
        for i, row in enumerate(template_matrix):
            for col in row:
                template += (col+', ')
            if i+1 < len(template_matrix):
                template += '\n        '

        layout = ''
        for i, layer in enumerate(layers):
            layout += '      [ # layer '+str(i)+'\n        ['
            for row in layer.layout:
                layout += '\n          '
                for keycode in row:
                   if len(keycode) < 4:
                       repeat = 4 - len(keycode)
                       for i in (range(repeat)):
                           keycode+=' '
                   layout += keycode+', '
            layout +='\n        ]\n      ],\n'

        # Load Template
        output_yaml_info = ref.keyplus_yaml_template
        output_yaml_info = output_yaml_info.replace('<ERRORS>', errors)
        output_yaml_info = output_yaml_info.replace('<KB_NAME>', name)
        output_yaml_info = output_yaml_info.replace('<LAYOUT_NAME>', keymap)                              
        output_yaml_info = output_yaml_info.replace('<ROWS>', rows)                                 
        output_yaml_info = output_yaml_info.replace('<COLS>', cols)
        output_yaml_info = output_yaml_info.replace('<MATRIX_MAP>', template)
        output_yaml_info = output_yaml_info.replace('<LAYOUT>', layout)

        kblibs = self.build_kb.libs
        if rev_n:
            path_list = kblibs + [rev_n, keymap]
        else:
            path_list = kblibs + [keymap]
        output_path = '_'.join(path_list)
        output_yaml = out_dir+output_path+'.yaml'
        if not os.path.exists(out_dir):
            try:
                os.makedirs(out_dir)
            except OSError as e:
                if e.errno != errno.EEXIST and os.path.isdir(out_dir):
                    raise
        try:
            with open(output_yaml, 'w') as f:
                f.write(output_yaml_info)
        except:
            self.console.error(['Failed to pipe output to '+output_yaml])
            exit()

        if self.__args.debug or DEBUG:
            print(output_yaml_info)

        self.console.note(['SUCCESS! Output is in: '+output_yaml])

def q2keyplus():

    q2k = application('keyplus')
    q2k.execute()
'''
def q2kbfirmware():
    q2k = application('kbfirmware')
    q2k.execute()
'''

# Just here as an example for reference (for now)
'''
def q2keyplus_gui(keyboard, rev, keymap, template):
    q2k = application('keyplus', is_gui=True)
    q2k.set_kb(keyboard, rev, keymap, template)
    q2k.execute()
'''

if __name__ == '__main__':
    q2keyplus()
