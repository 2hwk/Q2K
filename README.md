## Description
```
Q2K Keymap Parser 
ver. 1.0.8.a3 (Pre-Alpha) 
by 2Cas (c) 2018
```

For parsing keymaps from QMK Firmware style keymap.c files to Keyplus YAML format.
!!! PRE-ALPHA AND WIP !!! 

## Requirements

Requires (pip): `python3-pip` `python3-tkinter` `avr-gcc` 
          `pyyaml` `pyparsing` `termcolor`

Requires (exec): ``avr-gcc``

Tested on bash on Windows 10 (q2k-cli only), Windows 10 and Ubuntu Linux

## Setup
**Using PyPI and pip**
Install the required dependencies, then run

`pip3 install q2k`

Once the Q2K package has been installed...

GUI: run with `q2k`, point to qmk root and final output directories, then hit Generate Keyboard List, select your keyboard (and options) and Convert.

Command Line: `cd` into your local qmk directory and run with `q2k-cli [options]`

**Using Executables (WIN/Linux)**

Go to the releases tab (or /bin) and get the latest executable q2k_util file. Run like a traditional program (Click/Use terminal ./q2k_util)

For the windows version, you will need [http://andybrown.me.uk/2015/03/08/avr-gcc-492/](this avr-gcc compiler installed in the avr-gcc folder at the same level as q2k_util.exe

## Run
`q2k` for simple tkinter based GUI

OR

`q2k-cli [KEYBOARD NAME] [CMD LINE OPTIONS]`

Output keyplus YAML file will be found in <qmk root>/keyplus_out 
This, along with the QMK directory can be changed from relative to fixed reference by modifying pref.yaml in q2k's dist-package folder.

Usage example:
```
q2k-cli clueboard/66 -r rev2 -t LAYOUT => keyplus_out/clueboard_66_rev2_default.yaml
q2k-cli k_type -m default => keyplus_out/k_type_default.yaml
```

``q2k-cli -h`` provides a comprehensive list of accepted opts.

## Commands

```
Usage: q2k-cli [KEYBOARD] [-h] [-m keymap] [-r ver] [-L] [-M] [-R] [-S string] [-c keymap] 

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
```

## Understanding QMK's Keymap/Layout Structure - How this works

Keymap.c files, which you may be somewhat familiar with, actually contain only some of the required layout information in QMK.

The process is detailed more in depth at http://docs.qmk.fm, however the jist of it is that building a layout requires several files:

 * keymap.c contains keycodes data, representing the final output of pressing a particular key on the keyboard. This is actually passed as an array (through a macro) which maps into the keyboard matrix for readability.

 * [keyboard].h (i.e. /gh60/gh60.h, clueboard/66/66.h) contains macro definitions (layout templates) which turn the one dimensional keycode array macro into a 2D matrix corresponding to the matrix column and pins

 * config.h which defines which amongst other things typically defines hardware pins to map rows and columns to on the microcontroller, debouncing settings and diode direction (at least when following QMK's default config.h template)

First the program pulls matrix col/row pins from config.h, keycode data from keymap.c and template data from [keyboard].h (after exhaustively searching for exactly which [keyboard].h header file contains the layout information). 

It then converts the keycodes and templates to keyplus notation (KC_RIGHT -> rght) and outputs a .yaml file that is compatible with keyplus firmware, as well as other keyplus format based keyboard firmware GUI builders.

## Keyplus

Disregarding keyplus's unique wireless capabilities, the first major difference with keyplus is your layout does NOT need to be baked into the firmware at compile time and layouts can be updated without recompiling firmware or even flashing into bootloader mode. 

This paradigm shift can be initially hard to wrap your head around, as it is possible to update layouts without updating firmware, and update firmware without updating layouts. Treat the two as seperate entities in the case of keyplus. For example, a side effect of this is that boards which use the same microcontroller (32u4, 32u2, etc) can use the same BLANK hex file (no layout baked).

The second major difference is how layouts are defined. All (non-wireless) settings, matrix mapping data and keycode data are all in the one file, a layout .yaml file. As previously stated, all the settings in this .yaml file can be updated WITHOUT putting your keyboard into bootloader mode. Advanced features involving custom functions (as in QMK) may require recompiling firmware however, so there is a limit to what can adjusted on the fly.

This utility will generate this layout.yaml file automatically for you, however if you don't already have a precompiled hex, you will need to compile a firmware hex file. (Read the keyplus readme for more details.)

## Changing Firmware

Changing firmwares from QMK to Keyplus thus involves several more steps than just simply running this utility. Layouts can be updated without flashing only after a keyplus firmware hex is flashed onto your board. This process is thankfully a one-off, and once you have successfully flashed the firmware to your board once, you can stop messing with flashing and compiling.

* Compile a 32u4 keyplus firmware hex by runnnig `make` (with the correct bootloader type, i.e. `make BOARD=atmel-dfu`). This can have an initial layout if you desire, otherwise can be left blank.

* Place your keyboard into bootloader mode. Hit the hardware reset button.

* Use a flashing program of your choice (`QMK Toolbox` being the preferred method) to flash the keyplus hex file.

* (Optional) Update the bootloader to the keyplus bootloader for 100% integration with keyplus layout and firmware loader, and driverless windows bootloader support.

* Run the keyplus flasher to either initialise the layout (if none was baked into the firmware) or update the layout.

* From now onwards, the keyplus flasher is all you need to update the layout. The program can also update firmware if the bootloader was switched to `kp_boot_32u4`, otherwise `dfu-programmer` and `QMK toolbix` are needed to flash keyplus firmware updates.

## Limitations

There are several inherent limitations with this bridging utility that you should be aware of. 

**Keyplus**


Firstly, keyplus currently ONLY supports atmega and xmega based mcus. 32a and cortex-m4 ARM based keyboards will NOT work with keyplus, although you can still export these as layout files, they will not work without the firmware support.

Keyplus only supports boards running its own kp_32u4 bootloader OR the default atmel-dfu bootloader (>90% of boards). Boards with non-dfu based bootloaders, such as the newer revisions of the planck and OLKB keyboards (LUFA/QMK LUFA) and clone pro micros (Caterina) will have to UPDATE their bootloader, which is usually done with an ardunio ISP. 

Thankfully, there is an included program with keyplus that will attempt to flash the custom kp_32u4 bootloader to your pro micro/device, however it is NOT gaurenteed to work (and obviously entails the risks of messing with the bootloader, which could soft-brick your board) 

**Q2K**

For obvious reasons it is impractical to parse through hand-written and custom C code functions and attempt to extract data from this. You may have to recreate such code similarly by hand. i.e. code which turns on particular backlight colours when a particular layer is selected, playing audio through onboard speakers on the keyboard, etc.

If a QMK-exclusive function which is not supported by keyplus is defined in a keymap, an error will be displayed in the console, and the relevant keycode will be transcribed as a blank 'trns' instead, which is displayed in the console. 

Additionally converting keyboards with an incompatible microcontroller or bootloader will prompt an incompatability warning in the terminal. (This is only partially implemented).

**QMK**

QMK has a very loose and not well defined folder structure, and does not really impose many rules or guidelines on formatting. It is natural then that as more boards are added to the QMK directory that some boards may have a non-standard enough folder structures/keymap formatting to break this script in various ways, and that config.h and keyboard.h headers may be missed. I'd like to think my code is as robust as it possibly could be to guard against this, but I feel that failure on this front is kind of inevitable.

A failure to read matrix column and pin data from config.h a fairly common problem, which is a fairly trivial but annoying manual fix. In some cases, this matrix row/col pin information is not contained in config.h at all and may need to be pulled from one of many possible locations, including but not limited to keymap.c, matrix.c, matrix.h, keyboard.h, etc, where often board makers will list row/pinout information within either comments or physical code. When this occurs, a warning will be printed to the console.

Missing keyboard.h information whilst also non-fatal and less common than missing config.h data, will result in a compromised layout yaml with only a basic layout template that follows the keyboard matrix exactly. This should still work and function but the output won't be as readable as intended. A warning will be printed to the console when this occurs.

On the other hand, a failure to read a keymap.c file will always result in a fatal termination. In this case, try converting a different keymap.c file for the same board, as particular keymaps may have unique #define declarations that can throw the script off.

Inevitably as QMK evolves over time, due to the above reasons and more, this script will become more and more broken than it already is (as active maintenace of this in the long run is unlikely). The last version/commit of QMK that has been verified to be (mostly) working will [always be linked here](https://github.com/qmk/qmk_firmware/tree/3bb647910a09146309cef59eedd78be72697c88f) in the worst case scenario that it blows up horribly. 

## Other Notes

tl;dr VERY alpha, not gaurenteed to work 100% for every keyboard with QMK support. Lots of caught and uncaught exceptions will be thrown. Flashing firmware always has an element of risk and I am not responsible if your keyboard bricks itself. 

## Future Development

* KBfirmware support has been dropped indefinitely. (Will focus purely on keyplus for now until everything is fleshed out)
* The GUI and front end code could be improved (but it's unlikely to change much). 
* Still a few edge cases where <keyboard>.h files are missed. 
* Reading of LED/RGB data, Bootloader type, MCU (in anticipation of changes on K+ Layout side) and updating conversion dictionary AND logic for keyplus's implementation of tap and hold, etc.
* I'd like to be able to export cached kb data (cache_kb.yaml) out into a more readable form - might be useful on QMK side of things.
* Better documentation of code now that no more major overhauls are pending.
* Documentation, documentation, documentation.
* Proper Windows Support? Maybe. For now Bash on Win10 works.
          
## License

Distributed under the OSI: MIT License.

## Credit

Credit to Jack Humbert + QMK Firmware Contributors and _spindle/ahtn + keyplus contributors, without which this would not be possible.
