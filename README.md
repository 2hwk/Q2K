## Description
```
Q2K Keymap Parser 
ver. 0.0.90 dev4 (Pre-Alpha) 
by 2Cas (c) 2018
```

For parsing keymaps from QMK Firmware style keymap.c files to Keyplus YAML format.

## Requirements

Requires: `pip` `python3` `pyyaml` `pyparsing` `avr-gcc`

Tested on bash on Windows 10 and Ubuntu Linux

## Setup

First, install the required dependencies, then run

`sudo pip install q2k`

Once the Q2K package has been installed, `cd` into your local qmk directory and run with `q2k [options]`

## Run

`q2k [KEYBOARD NAME] [CMD LINE OPTIONS]`

Output keyplus YAML file will be found in <qmk root>/keyplus_out

For example:
```
q2k clueboard/66 -r rev2 => /keyplus_out/clueboard_66_rev2_default.yaml
q2k k_type -m default => /keyplus_out/k_type__default.yaml
```

``q2k -h`` provides a comprehensive list of accepted opts.

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

  -c layout   Select keymap template index. (Skips prompt for keymap selection)

## Understanding QMK's Keymap/Layout Structure - How this works

Keymap.c files, which you may be somewhat familiar with, actually contain only some of the required layout information in QMK.

The process is detailed more in depth at http://docs.qmk.fm, however the jist of it is that building a layout requires several files:

 * keymap.c contains keycodes data, representing the final output of pressing a particular key on the keyboard. This is actually passed as an array (through a macro) which maps into the keyboard matrix for readability.

 * keyboard.h (i.e. /gh60/gh60.h, clueboard/66/66.h) contains macro definitions (layout templates) which turn the one dimensional keycode array macro into a 2D matrix corresponding to the matrix column and pins

 * config.h which defines which amongst other things typically defines hardware pins to map rows and columns to on the microcontroller, as well as debouncing settings (at least when following QMK's default config.h template)

This script first pulls matrix col/row pins from config.h, keycode data from keymap.c and template data from <keyboard>.h (after exhaustively searching for exactly which <keyboard>.h header file contains the layout information). It then converts the keycodes and templates to keyplus notation (KC_RIGHT -> rght) and outputs a .yaml file that is compatible with keyplus firmware, as well as other keyplus format based keyboard firmware GUI builders.


## Limitations

There are several inherent limitations with Q2K that you should be aware of. 

Firstly, keyplus does NOT support the wide range of microcontrollers, functions and custom firmware functions that QMK supports. This is due to a range of reasons, such as features being planned for inclusion but still undergoing development to a ideological desire to stick to a more simple and streamlined firmware focused on wireless support. 

As such, when QMK-exclusive functions are defined in keymaps, an error will be displayed in the console, and the relevant keycode will be transcribed as a blank 'trns' instead. Converting keyboards with an incompatible microcontroller will prompt an incompatability warning in the terminal. (not actually implemented yet)
 
Secondly, QMK has a very loose and not well defined folder structure. It is natural then that as more boards are added to the QMK directory that some boards may have a non-standard enough folder structures to break this script in various ways, and that config.h and keyboard.h headers may be missed.

A failure to read matrix column and pin data from config.h a fairly common problem, which is a fairly trivial but annoying manual fix. In some cases, this matrix row/col pin information is not contained in config.h at all and may need to be pulled from one of many possibly locations, including but not limited to keymap.c, matrix.c, matrix.h, <keyboard>.h, etc, where often board makers will list row/pinout information within either comments or physical code.

Missing keyboard.h information whilst also non-fatal and less common than missing config.h data, will result in a compromised layout yaml with only a basic layout template that follows the keyboard matrix exactly. This should still work and function but the output won't be as readable as intended. 

On the other hand, a failure to read a keymap.c file will always result in a fatal termination. In this case, try converting a different keymap.c file for the same board, as particular keymaps may have unique #define declarations that can throw the script off.

Inevitably as QMK evolves over time, due to the above reasons and more, this script will become more and more broken than it already is (as active maintenace of this in the long run is unlikely). The last version/commit of QMK that has been verified to be (mostly) working will [always be linked here](https://github.com/qmk/qmk_firmware/tree/a09a042b8fe6a0369a7c479168492125efa24e59) in the worst case scenario that it blows up horribly. 

## Other Notes

tl;dr VERY alpha, not gaurenteed to work 100% for every keyboard with QMK support. Lots of caught and uncaught exceptions will be thrown. Flashing firmware always has an element of risk and I am not responsible if your keyboard soft or hard bricks itself. 
