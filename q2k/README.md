## Description

Q2K Keymap Parser ver. 0.0.90 dev1 by 2Cas (c) 2018

For parsing keymaps from QMK Firmware style keymap.c files to Keyplus YAML format


## Requirements

Requires: pip python3 pyyaml pyparsing avr-gcc

Tested on bash on Windows 10 and Ubuntu Linux


## Setup

pip install q2k

cd into your local qmk directory (you only really need the <qmk root>/keyboards/ folder)

Output YAML file is in /keyplus_out

## Run
Run with:
q2k [KEYBOARD NAME] [CMD LINE OPTIONS]

For example:
q2k clueboard/66 -r rev2
q2k k_type -m default

Run with -h for cmd line options

## Commands
Usage: q2k [KEYBOARD] [-h] [-m keymap] [-r ver] [-L] [-M] [-R] [-S string] [-c keymap] 

positional arguments:

  KEYBOARD    The name of the keyboard whose keymap you wish to convert

  
optional arguments:

  -h, --help  show this help message and exit

  -m keymap   The keymap folder to reference - default is /default/

  -r ver      Revision of layout - default is n/a

  -d          Append results to cache/kb_info.yaml file. For debugging, may cause
              performance loss

  -L          List all valid KEYBOARD inputs

  -M          List all valid KEYMAPS for the current keyboard

  -R          List all valid REVISIONS for the current keyboard

  -S string   Search valid KEYBOARD inputs

  -P          Print result of keymap conversion to terminal

  -c keymap   Select keymap template index. (Skips prompt for keymap selection)

## Understanding QMK's Keymap/Layout Structure - How this works

"Keymaps" in keymap.c files actually contain only a part of what is required to create a working layout for QMK. 

The process is detailed more in depth at http://docs.qmk.fm, however the jist of it is that building a layout requires several files:

 * keymap.c contains keycodes data, representing the final output of pressing a particular key on the keyboard. This is actually passed as an array (through a macro) which maps into the keyboard matrix for readability.

 * <keyboard>.h (i.e. /gh60/gh60.h, clueboard/66/66.h) contains the macro definitions (what I will call templates from now onwards) which turn the one dimensional keycode array macro into a 2D matrix corresponding to the matrix column and pins defined in...

 * config.h which contains information related to keyboard matrix pinouts and debouncing settings (at least by QMK's defaults)

This script thus first pulls matrix col/row pins from config.h, keycode data from keymap.c and template data from <keyboard>.h (after exhaustively searching for exactly which <keyboard>.h header file contains the layout information). It then converts the keycodes and templates to keyplus notation (KC_RIGHT -> rght) and outputs a .yaml file that is compatible with keyplus firmware, as well as other keyplus format based keyboard firmware GUI builders.


## Limitations

There are several inherent limitations with Q2K that you should be aware of. 

Firstly, keyplus does NOT support the wide range of microcontrollers, functions and custom firmware functions that QMK supports. This is due to a range of reasons, such as features being planned for inclusion but still undergoing development to a ideological desire to stick to a more simple and streamlined firmware focused on wireless support. 

As such, when QMK-exclusive functions are defined in keymaps, an error will be displayed in the console, and the relevant keycode will be transcribed as a blank 'trns' instead. Converting keyboards with an incompatible microcontroller will prompt an incompatability warning in the terminal. (not actually implemented yet)
 
Secondly, QMK has what we will call an INTERESTING folder structure which means that technically, many of the header files that contain important information could be almost anywhere within a keyboards subdirectory, and this script will sometimes fail to find this data. 

A failure to read matrix column and pin data from config.h a fairly common problem, which is thankfully a fairly trivial but annoying manual fix. In some cases, this information is not contained in config.h at all.
 and may need to be pulled from one of many possibly locations, including but not limited to keymap.c, matrix.c, matrix.h, <keyboard>.h, etc, where often board makers will list row/pinout information within either comments or physical code.

Missing <keyboard>.h information whilst also non-fatal and less common than missing config.h data, will result in a compromised layout yaml. This should still work and function but the output won't be as readable as intended. 

On the other hand, a failure to read a keymap.c file will always result in a fatal termination. In this case, trying a different, more vanilla keymap.c file for the same board will work. 

As QMK is constantly evolving over time, this script will become more and more broken than it already is (as maintenace of this script will definitely fall behind). The last version/commit of QMK that has been verified to be (mostly) working will [always be linked here](https://github.com/qmk/qmk_firmware/tree/a09a042b8fe6a0369a7c479168492125efa24e59) in the worst case that it totally borks. 

## Other Notes

tl;dr VERY alpha, not gaurenteed to work 100% for every keyboard with QMK support. Lots of caught and uncaught exceptions will be thrown.

Matrix layout in a small but substantial number of boards is NOT stored in config.h and will not be captured as such by this script. You will have to pull this manually \ from one of many possibly locations, including but not limited to keymap.c, matrix.c, matrix.h, <keyboard>.h, etc.
