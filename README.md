## Description
```
Q2K Keymap Utility
by 2Cas (c) 2018
```

For parsing keymaps from QMK Firmware style keymap.c files to Keyplus YAML format.

Tested on bash on Windows 10 (q2k-cli only), Windows 10 and Ubuntu Linux

!!! PRE-ALPHA AND VERY MUCH WIP !!! 

## Running Executable Binaries (WIN/Linux)

### Requirements

`avr-gcc`

### Setup

Before running, please read this [basic guide on converting from QMK->Keyplus](https://github.com/angustrau/keyplus/blob/b86cc28d33f796523717e38e28e8d620d2707778/doc/porting_from_qmk.md).

If your keyboard does NOT have an ATmega based MCU (with native USB support) such as the ATmega32u4 or similar, Keyplus is currently not compatible with your keyboard. Keyplus is also currently in an alpha state, which means that bugs and problems may arise. Be warned. I would highly recommend generating and saving a QMK Firmware based .hex file which you can revert to if this process does not work out for you.

Remember to install the required dependencies, especially the ``avr-gcc`` compiler which this program heavily leans upon to function. 

For Ubuntu Linux, you can install ``avr-gcc`` by running ``apt-get install gcc-avr`` with sudo permissions.

For Windows, you will need [this avr-gcc compiler](http://andybrown.me.uk/2015/03/08/avr-gcc-492/) installed in the avr-gcc folder at the same level as ``q2k_util.exe``

### Instructions

1) Go to the releases tab (or /bin) and get the latest executable ``q2k_util`` zip folder and extract, then run ``./q2k_util``

2) After initialising the program, you will need to select your QMK Firmware Directory folder location. You can either choose to clone or create a symbolic link to your ``qmk_firmware`` directory in the newly extracted ``q2k-<version>`` program directory, OR select your QMK Firmware directory location.

3) You may also choose an output folder. By default, this is set to ``q2k-<version>/q2k_out/keyplus``. You may wish to change this to another folder, such as your local keyplus installation's ``layouts`` folder.

4) Click the Generate Keyboard List button to populate the drop-down menus with keyboard info. This may take a while to initialise.

5) Select your keyboard, revision, keymap and layout template type with the drop-down menus. The layout template names should be more or less descriptive, however if you are unsure, selecting LAYOUT or KEYMAP should provide a good universal template that will work with any layout configuration (wkl, split shift, split backspace, iso, etc.)

6) Click the Convert button. Note that:

* Missing keycodes corresponding to QMK features that keyplus does not support will both be printed in the console as well as in the output .yaml file as comments. 

* If any errors occur during this process, they will both generate an error message popup as well as being displayed in the console. In some cases these errors are recoverable, however you may have to do some manual processing of layout.yaml files after the script has finished. 

7) After successful conversion, your layout.yaml file is now ready to be loaded in by the [``keyplus_flasher``](https://github.com/ahtn/keyplus) keyplus flashing utility.

8) If you update QMK after using this utility, you will have to click Generate Keyboard List again to update the drop-down menus for any new keyboards or keymaps.

### FAQ & Errors

* **My keyboard does not show up in the program**

Check your MCU type. If it is of a type not supported by keyplus, currently the program will completely exclude it from the drop-down menu listings. 

* **avr-gcc is missing?**

This means you have not installed the avr-gcc compiler required by the program to function. Please read the setup section again and install ``avr-gcc``

* **My layout file isn't working**

This could be down to several factors.

If any error messages were returned, read them carefully and ensure that you have fixed the problems with the layout file manually - i.e. for boards with no specified matrix pins, find the matrix pinout manually and input it in the layout file.

Try pressing the reset button and generating a new cache, and try again.

[Note: Currently there is an issue with the windows ``keyplus_flasher`` and it will not work with ANY layouts as of 0.30.0. As such the layout file is probably fine if you are on windows, it's just the binary needs updating.]

If you are sure this was not the issue, then it could be an error in keyplus itself, or some kind of incompatability between your keyboard and keyplus. Try opening an issue there.

* **Certain keycodes aren't working**

Did you select the correct layout template? Try a different one, or just use KEYMAP/LAYOUT if available. Did you receive any error messages? Read them carefully. Some QMK specific functions are not supported in keyplus, so the corresponding keycodes aren't translated. Check the console output or the comments in your layout.yaml file to see if any of these were ignored. 

Try pressing the reset button and generating a new cache, and try again.

If you are sure this was not the issue, then it could be an error in keyplus itself, or some kind of incompatability between your keyboard and keyplus. Try opening an issue there.

* **Other non-listed problems**

If any other errors occur, first try using the Reset button to clear the cache and preference files to their default values. If this fails, try deleting pref.yaml entirely as well as the ``q2k-<version>/.cache`` folder. If clearing the cache and pref.yaml files do not solve your issue, then [create a new issue in github](https://github.com/2Cas/Q2K/issues) if it does not exist and I will get to it ASAP.


## Using PyPI and pip to install q2k module (for developers)

### Requirements

 `python3-pip` `python3-tkinter` `avr-gcc` `pyyaml` `pyparsing` `termcolor`

### Instructions

Install the required dependencies, then run

`pip3 install q2k`

Display GUI: run with `q2k`

Command Line: `cd` into your local qmk directory then run with `q2k-cli [options]`

### Command Line Options 

`q2k-cli [KEYBOARD NAME] [CMD LINE OPTIONS]`

Output keyplus YAML file by default will be found in <qmk root>/keyplus_out 
          
You may modify the `pref.yaml` file generated by `q2k` to change the input and output directories. Note that changing directories using the UI ``q2k`` will also change the directories used by ``q2k-cli``

Usage example:
```
q2k-cli clueboard/66 -r rev2 -t LAYOUT => keyplus_out/clueboard_66_rev2_default.yaml
q2k-cli k_type -m default => keyplus_out/k_type_default.yaml
```

``q2k-cli -h`` provides a comprehensive list of accepted opts.

```
usage: q2k-cli [KEYBOARD] [-r REV] [-m KEYMAP] [-t LAYOUT]  [-h] [--cache] [--reset]
               [--debug] [-l] [-M] [-T] [-R] [-S string]
               

positional arguments:
  KEYBOARD              The name of the keyboard whose keymap you wish to
                        convert

optional arguments:
  -h, --help            show this help message and exit
  -m KEYMAP, --keymap KEYMAP
                        The keymap folder to reference - default is [default]
  -t LAYOUT, --template LAYOUT
                        The layout template to reference
  -r ver, --rev REV     Revision of layout - default is n/a
  --cache               Clear cached data (cache_kb.yaml)
  --reset               Restore preferences in pref.yaml to default
  --debug               See debugging information
  -l, -L, --list        List all valid KEYBOARD inputs
  -M, --keymaps         List all valid KEYMAPS for the current keyboard
  -T, --templatelist    List all valid LAYOUTS for the current keyboard
  -R, --revlist         List all valid REVISIONS for the current keyboard
  -S string, --search string
                        Search valid KEYBOARD inputs
```

## Changing Firmware

Read [this](https://github.com/angustrau/keyplus/blob/08190a03b666325c53557651868a3cb0e8010392/doc/porting_from_qmk.md)

## How this works

Keymap.c files, which you may be somewhat familiar with, actually contain only some of the required layout information in QMK.

The process is detailed more in depth at http://docs.qmk.fm, however the jist of it is that building a layout requires several files:

 * keymap.c contains keycodes data, representing the final output of pressing a particular key on the keyboard. This is actually passed as an array (through a macro) which maps into the keyboard matrix for readability.

 * [keyboard].h (i.e. /gh60/gh60.h, clueboard/66/66.h) contains macro definitions (layout templates) which turn the one dimensional keycode array macro into a 2D matrix corresponding to the matrix column and pins

 * config.h which defines which amongst other things typically defines hardware pins to map rows and columns to on the microcontroller, debouncing settings and diode direction (at least when following QMK's default config.h template)

First the program pulls matrix col/row pins from config.h, keycode data from keymap.c and template data from [keyboard].h (after exhaustively searching for exactly which [keyboard].h header file contains the layout information). 

It then converts the keycodes and templates to keyplus notation (KC_RIGHT -> rght) and outputs a single layout.yaml file that is compatible with keyplus firmware, as well as other keyplus format based keyboard firmware GUI builders.

### Limitations

There are several inherent limitations with this conversion utility that you should be aware of. 

#### Keyplus

Firstly, keyplus currently ONLY supports atmega and xmega based mcus. 32a and cortex-m4 ARM based keyboards will NOT work with keyplus and thus is not supported by q2k.

Keyplus only supports boards running its own kp_32u4 bootloader OR the default atmel-dfu bootloader (>90% of boards). Boards with non-dfu based bootloaders, such as the newer revisions of the planck and OLKB keyboards (LUFA/QMK LUFA) and clone pro micros (Caterina) will have to UPDATE their bootloader, which is usually done with an ardunio ISP. 

Thankfully, there is an included program with keyplus that will attempt to flash the custom kp_32u4 bootloader to your pro micro/device, however it is NOT gaurenteed to work, i.e. if particular locking fuses have been set.

#### Q2K

For obvious reasons it is impractical to parse through hand-written and custom C code functions and attempt to extract data from this. You may have to recreate such code similarly by hand. i.e. code which turns on particular backlight colours when a particular layer is selected, playing audio through onboard speakers on the keyboard, etc.

If a QMK-exclusive function which is not supported by keyplus is defined in a keymap, an error will be displayed in the console, and the relevant keycode will be transcribed as a blank 'trns' instead, which is displayed in the console and printed in the final output.

Additionally converting keyboards with an incompatible microcontroller or bootloader will prompt an incompatability warning in the terminal. (This is not implemented for bootloaders yet).

#### QMK

QMK has a very loose and not well defined folder structure, and does not really impose many rules or guidelines on formatting. It is natural then that as more boards are added to the QMK directory that some boards may have a non-standard enough folder structures/keymap formatting to break this script in various ways, and that config.h and keyboard.h headers may be missed. I'd like to think my code is as robust as it possibly could be to guard against this, but I feel that failure on this front is kind of inevitable.

A failure to find and read matrix column and pin data from config.h a fairly common problem, which is a fairly trivial but annoying manual fix. In some cases, this matrix row/col pin information is not contained in config.h at all and may need to be pulled from one of many possible locations, including but not limited to keymap.c, matrix.c, matrix.h, keyboard.h, etc, where often board makers will list row/pinout information within either comments or physical code. Please note that it is often (though not always) the case that when this occurs, the keyboard is using some kind of custom matrix code, and thus may not work once converted to keyplus format. A warning is displayed when this occurs.

Failing to find layout templates (read from [keyboard].h) whilst also non-fatal and less common than missing config.h data, will result in a compromised layout yaml with only a basic layout template that follows the keyboard matrix exactly. This should still work and function but the output won't be as readable as intended. A warning is displayed when this occurs.

By contrast, a failure to read a keymap.c file will always result in a fatal termination and a failed conversion. In this case, try converting a different keymap.c file for the same board, as particular keymaps may have unique #define declarations that can throw the script off.

It is inevitable that as QMK evolves over time, due to the above reasons and more, this script will become more and more broken than it already is (as active maintenace of this in the long run is unlikely). The last version/commit of QMK that has been verified to be (mostly) working will [always be linked here](https://github.com/qmk/qmk_firmware/tree/3bb647910a09146309cef59eedd78be72697c88f) in the worst case scenario that it blows up horribly. 

## Other Notes/Warnings

tl;dr VERY alpha, not gaurenteed to work 100% for every keyboard with QMK support. Lots of caught and uncaught exceptions will be thrown. Flashing firmware always has an element of risk and I am not responsible if your keyboard bricks itself. 

## Future Development

* KBfirmware support has been dropped indefinitely. (Will focus purely on keyplus for now until everything is fleshed out)
* The GUI and front end code could be improved (but it's unlikely to change much). 
* Still a few edge cases where <keyboard>.h files are missed. 
* Reading of LED/RGB data, Bootloader type (in anticipation of changes on K+ Layout side) and updating conversion dictionary AND logic for keyplus's implementation of tap and hold, etc.
* Better documentation of code
* Documentation, documentation, documentation
* Improve run times - Currently very sluggish on windows.
          
## License

Distributed under the OSI: MIT License.

## Credit

Credit to Jack Humbert + QMK Firmware Contributors and _spindle/ahtn + keyplus contributors, without which this would not be possible.
