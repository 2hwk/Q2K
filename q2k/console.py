#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2018 2Cas
# Licensed under the MIT license (http://opensource.org/licenses/MIT)

import sys
from termcolor import colored, cprint

def error_out(info):

    error = colored('❌ ERROR:', 'red', attrs=['reverse', 'bold'])
    e_bullet = colored('•', 'red', attrs=['bold'])
    
    for info, line in enumerate(info):
        if not info:
            line = colored(line, 'red')
            print(error + ' ' +line)
        else:
            print(e_bullet + ' '+line)


def bad_kc_out(kc_type, code):

    bad_kc = colored('❌ Invalid '+kc_type+':', 'cyan')
    #code = colored(code, 'cyan')
    print(bad_kc+' '+code)


def warning_out(info):

    warning = colored('▲ WARNING:', 'yellow', attrs=['bold'])
    w_bullet = colored('•', 'yellow', attrs=['bold'])
    
    for info, line in enumerate(info):
        if not info:
            line = colored(line, 'yellow')
            print(warning + ' ' +line)
        else:
            print(w_bullet + ' '+line)


def note_out(info):

    note = colored('✔', 'green', attrs=['bold'])
    n_bullet = colored('•', 'green', attrs=['bold'])
    
    for info, line in enumerate(info):
        if not info:
            #line = colored(line, 'green')
            print(note + ' ' +line)
        else:
            print(n_bullet + ' '+line)


