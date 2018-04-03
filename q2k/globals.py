#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2018 2Cas
# Licensed under the MIT license (http://opensource.org/licenses/MIT)

from pkg_resources import Requirement, resource_filename

#----------------------------------------------
#MODIFY these to suit your liking BEFORE running pip install
KB_INFO = 'cache/kb_info.yaml'   # cached kb_info yaml
QMK_DIR = ''                     # QMK directory location
OUT_DIR = 'keyplus_out/'         # Default out directory
#----------------------------------------------

KBD_LIST = []
MCU_COMPAT = ['atmega8u2', 'atmega16u2', 'atmega32u2', 'atmega32u4', 'atmega32u6', 'at90usb646', 'at90usb646', 'at90usb647', 'at90usb1286', 'at90usb1287']
local_libs = resource_filename(Requirement.parse("q2k"),"q2k/lib/")
LOCAL_INCLUDES = local_libs+'/'

# QMK -> Keyplus Keycode Mapping
# for keycodes only, functions are in qmk_to_keyp_func
qmk_to_keyp = {
    "KC_NO"                 :  " no ", #- giorgio, 2018
    "KC_TRNS"               :  "____",
    "KC_TRANSPARENT"        :  "____", #"trans",
    "XXXXXXX"               :  " no ",
    "_______"               :  "____",
    "RESET"                 :  "reset",
    "MAGIC_HOST_NKRO"       :  "kro_n",                       # FORCE NKRO
    "MAGIC_UNHOST_NKRO"     :  "kro_6",                       # FORCE 6KRO
    "MAGIC_TOGGLE_NKRO"     :  "kro_auto",                    # Set Auto NKRO

    # Alphas
    "KC_GRV"                :  "'`' ",
    "KC_GRAVE"              :  "'`' ",  #"grave",             # Grave (~`)kro_6
    "KC_1"                  :  " 1  ",
    "KC_2"                  :  " 2  ",
    "KC_3"                  :  " 3  ",
    "KC_4"                  :  " 4  ",
    "KC_5"                  :  " 5  ",
    "KC_6"                  :  " 6  ",
    "KC_7"                  :  " 7  ",
    "KC_8"                  :  " 8  ",
    "KC_9"                  :  " 9  ",
    "KC_0"                  :  " 0  ",
    "KC_MINS"               :  " -  ",
    "KC_MINUS"              :  "'-' ", #"minus",               # Minus (-_)
    "KC_EQL"                :  "'=' ",
    "KC_EQUAL"              :  "'=' ", #"equal",               # Equal (=+)
    "KC_Q"                  :  " q  ",
    "KC_W"                  :  " w  ",
    "KC_E"                  :  " e  ",
    "KC_R"                  :  " r  ",
    "KC_T"                  :  " t  ",
    "KC_Y"                  :  " y  ",
    "KC_U"                  :  " u  ",
    "KC_I"                  :  " i  ",
    "KC_O"                  :  " o  ",
    "KC_P"                  :  " p  ",
    "KC_LBRC"               :  " [  ",
    "KC_LBRACKET"           :  " [  ", #"left_bracket",        # Left Bracket ([)
    "KC_RBRC"               :  " ]  ",
    "KC_RBRACKET"           :  " ]  ", #"right_bracket",       # Right Bracket (])
    "KC_BSLS"               :  "'\\' ", #"bsls",
    "KC_BSLASH"             :  "'\\' ",                        # Backslash (\|)
    "KC_A"                  :  " a  ",
    "KC_S"                  :  " s  ",
    "KC_D"                  :  " d  ",
    "KC_F"                  :  " f  ",
    "KC_G"                  :  " g  ",
    "KC_H"                  :  " h  ",
    "KC_J"                  :  " j  ",
    "KC_K"                  :  " k  ",
    "KC_L"                  :  " l  ",
    "KC_SCLN"               :  " ;  ",
    "KC_SCOLON"             :  " ;  ", #"semicolon",          # Semicolon (;:)
    "KC_QUOT"               :  " \"\' \"", 
    "KC_QUOTE"              :  " \"\' \"", #"quot",           # Quote ('")
    "KC_Z"                  :  " z  ",
    "KC_X"                  :  " x  ",
    "KC_C"                  :  " c  ",
    "KC_V"                  :  " v  ",
    "KC_B"                  :  " b  ",
    "KC_N"                  :  " n  ",
    "KC_M"                  :  " m  ",
    "KC_COMM"               :  "',' ",
    "KC_COMMA"              :  "',' ", #"comma",              # Comma (,<)
    "KC_DOT"                :  "'.' ",                        # Period (.>)
    "KC_SLSH"               :  "'/' ",
    "KC_SLASH"              :  "'/' ", #"forward_slash",      # Forward Slash (/?)
    "KC_SPC"                :  " spc",
    "KC_SPACE"              :  " spc", #"spacebar",           # Spacebar

    # Modifiers
    "KC_RCTL"               :  "rctl",
    "KC_RCTRL"              :  "rctl", #"rctrl",              # Right Ctrl
    "KC_LCTL"               :  "lctl",
    "KC_LCTRL"              :  "lctl", #"lctrl",              # Left Ctrl
    "KC_RSFT"               :  "rsft",
    "KC_RSHIFT"             :  "rsft", #"rshift",             # Right Shift
    "KC_LSFT"               :  "lsft",
    "KC_LSHIFT"             :  "lsft", #"lshift",             # Left Shift
    "KC_LGUI"               :  "lgui",
    "KC_LWIN"               :  "lgui", #"lwin",
    "KC_LCMD"               :  "lgui",                        # Left GUI/Win
    "KC_RGUI"               :  "rgui",
    "KC_RWIN"               :  "rgui", #"rwin",                    
    "KC_RCMD"               :  "rgui",                        # Right GUI/Win
    "KC_LALT"               :  "lalt",                        # Left Alt
    "KC_RALT"               :  "ralt",                        # Right Alt
    "KC_BSPC"               :  "bspc",
    "KC_BSPACE"             :  "bspc", #"backspace",          # Backspace
    "KC_ENT"                :  " ent",
    "KC_ENTER"              :  " ent", #"enter",              # Enter
    "KC_TAB"                :  " tab",                        # Tab
    "KC_CAPS"               :  "caps",
    "KC_CLCK"               :  "caps",
    "KC_CAPSLOCK"           :  "caps", #"caps_lock""kp_ent",, # Caps Lock
    "KC_RGHT"               :  "rght",
    "KC_RIGHT"              :  "rght", #"right",              # right arrow
    "KC_UP"                 :  " up ",
    "KC_DOWN"               :  "down",
    "KC_LEFT"               :  "left",
    # Function
    "KC_ESC"                :  " esc",
    "KC_ESCAPE"             :  " esc", #"escape",             # Escape
    "KC_F1"                 :  " f1 ",

    "KC_F2"                 :  " f2 ",
    "KC_F3"                 :  " f3 ",
    "KC_F4"                 :  " f4 ",
    "KC_F5"                 :  " f5 ",
    "KC_F6"                 :  " f6 ",
    "KC_F7"                 :  " f7 ",
    "KC_F8"                 :  " f8 ",
    "KC_F9"                 :  " f9 ",
    "KC_F10"                :  " f10",
    "KC_F11"                :  " f11",
    "KC_F12"                :  " f12",
    "KC_PSCR"               :  "pscr",
    "KC_PSCREEN"            :  "pscr", #"print_screen",      # Print Screen
    "KC_SLCK"               :  "slck",
    "KC_SCROLLLOCK"         :  "slck", #"scroll_lock",       # Scroll Lock
    "KC_PAUS"               :  "paus", 
    "KC_BRK"                :  "paus",
    "KC_PAUSE"              :  "paus", #"pause",             # Pause/Break
    "KC_INS"                :  " ins",
    "KC_INSERT"             :  " ins", #"insert",            # Insert
    "KC_DEL"                :  " del",
    "KC_DELETE"             :  " del", #"delete",            # Delete
    "KC_HOME"               :  "home",                       # Home
    "KC_END"                :  " end",                       # End
    "KC_PGUP"               :  "pgup",                       # Page Up
    "KC_PGDN"               :  "pgdn",
    "KC_PGDOWN"             :  "pgdn", #"page_down",         # Page Down
    "KC_F13"                :  " f13",
    "KC_F14"                :  " f14",
    "KC_F15"                :  " f15",
    "KC_F16"                :  " f16",
    "KC_F17"                :  " f17",
    "KC_F18"                :  " f18",
    "KC_F19"                :  " f19",
    "KC_F20"                :  " f20",
    "KC_F21"                :  " f21",
    "KC_F22"                :  " f22",
    "KC_F23"                :  " f23",
    "KC_F24"                :  " f24",
    # Shifted
    "KC_TILDE"              :  "'~' ",
    "KC_TILD"               :  "'~' ",
    "KC_EXCLAIM"            :  "'!' ",
    "KC_EXLM"               :  "'!' ",
    "KC_AT"                 :  "'@' ",
    "KC_HASH"               :  "'#' ",
    "KC_DOLLAR"             :  "'$' ",
    "KC_DLR"                :  "'$' ",
    "KC_PERCENT"            :  "'%' ",
    "KC_PERC"               :  "'%' ",
    "KC_CIRCUMFLEX"         :  "'^' ",
    "KC_CIRC"               :  "'^' ",
    "KC_AMPERSAND"          :  "'&' ",
    "KC_AMPR"               :  "'&' ",
    "KC_ASTERISK"           :  "'*' ",
    "KC_ASTR"               :  "'*' ",
    "KC_LEFT_PAREN"         :  "'(' ",
    "KC_LPRN"               :  "'(' ",
    "KC_RIGHT_PAREN"        :  "')' ",
    "KC_RPRN"               :  "')' ",
    "KC_UNDERSCORE"         :  "'_' ",
    "KC_UNDS"               :  "'_' ",
    "KC_PLUS"               :  "'+' ",
    "KC_LEFT_CURLY_BRACE"   :  "'{' ",
    "KC_LCBR"               :  "'{' ",
    "KC_RIGHT_CURLY_BRACE"  :  "'}' ",
    "KC_RCBR"               :  "'}' ",
    "KC_PIPE"               :  "'|' ",
    "KC_COLON"              :  "':' ",
    "KC_COLN"               :  "':' ",
    "KC_DOUBLE_QUOTE"       :  "\' \"\'",
    "KC_DQT"                :  "\' \"\'",
    "KC_DQUO"               :  "\' \"\'",
    "KC_LEFT_ANGLE_BRACKET" :  "'<' ",
    "KC_LT"                 :  "'<' ",
    "KC_LABK"               :  "'<' ",
    "KC_RIGHT_ANGLE_BRACKET":  "'>' ",
    "KC_GT"                 :  "'>' ",
    "KC_RABK"               :  "'>' ",
    "KC_QUESTION"           :  "'?' ",
    "KC_QUES"               :  "'?' ",

    # Numpad
    "KC_NLCK"               :  "nlck", 
    "KC_NUMLOCK"            :  "nlck", #"num_lock",        # Num Lock
    "KC_P1"                 :  "kp_1",
    "KC_KP_1"               :  "kp_1",                     # Numpad 1
    "KC_P2"                 :  "kp_2",   
    "KC_KP_2"               :  "kp_2",                     # Numpad 2
    "KC_P3"                 :  "kp_3",   
    "KC_KP_3"               :  "kp_3",                     # Numpad 3
    "KC_P4"                 :  "kp_4",   
    "KC_KP_4"               :  "kp_4",                     # Numpad 4
    "KC_P5"                 :  "kp_5",   
    "KC_KP_5"               :  "kp_5",                     # Numpad 5
    "KC_P6"                 :  "kp_6",   
    "KC_KP_6"               :  "kp_6",                     # Numpad 6
    "KC_P7"                 :  "kp_7",   
    "KC_KP_7"               :  "kp_7",                     # Numpad 7
    "KC_P8"                 :  "kp_8",   
    "KC_KP_8"               :  "kp_8",                     # Numpad 8
    "KC_P9"                 :  "kp_9",   
    "KC_KP_9"               :  "kp_9",                     # Numpad 9
    "KC_P0"                 :  "kp_0",   
    "KC_KP_0"               :  "kp_0",                     # Numpad 0
    "KC_PDOT"               :  "kp_.",
    "KC_KP_DOT"             :  "kp_.",                     # Numpad .
    "KC_PCMM"               :  "kp_,",
    "KC_KP_COMMA"           :  "kp_,",                     # Numpad ,
    "KC_PSLS"               :  "kp_/",
    "KC_KP_SLASH"           :  "kp_/",                     # Numpad /
    "KC_PAST"               :  "kp_*",                      
    "KC_KP_ASTERISK"        :  "kp_*",                     # Numpad *
    "KC_PMNS"               :  "kp_-", 
    "KC_KP_MINUS"           :  "kp_-",                     # Numpad -
    "KC_PPLS"               :  "kp_+",
    "KC_KP_PLUS"            :  "kp_+",                     # Numpad +
    "KC_PEQL"               :  "kp_=",
    "KC_KP_EQUAL"           :  "kp_=",                     # Numpad =
    "KC_PENT"               :  "kp_ent",
    "KC_KP_ENTER"           :  "kp_ent", #"kp_enter",      # Numpad Enter

    # Misc Functions
    "KC_APP"                :  " app",
    "KC_APPLICATION____"    :  "application",              # Application
    "KC_LCAP"               :  "locking_caps_lock",
    "KC_EXEC"               :  "execute",
    "KC_EXECUTE"            :  "execute",                  # Execute
    "KC_SLCT"               :  "select",
    "KC_SELECT"             :  "select",                   # Select____
    "KC_AGIN"               :  "again", 
    "KC_AGAIN"              :  "again",                    # Again
    "KC_MENU"               :  "hid_menu",                 # Menu
    "KC_UNDO"               :  "undo",                     # Undo
    "KC_CUT"                :  " cut",                      # Cut
    "KC_COPY"               :  "copy",                     # Copy
    "KC_PSTE"               :  "paste", 
    "KC_PASTE"              :  "paste",                    # Paste
    "KC_FIND"               :  "find",                     # Find
    "KC_ALT_ERASE"          :  "alternate_erase",          #KC_LEFT_ANGLE_BRACKET Alt Erase
    "KC_CANCEL"             :  "cancel",                   # Cancel
    "KC_SYSREQ"             :  "sys_req",                  # SYSREQ
    "KC_PRIOR"              :  "prior",                   
    "KC_SEPERATOR"          :  "separator",               
    "KC_RETURN"             :  "return",                   
    "KC_OUT"                :  " out",                      
    "KC_OPER"               :  "oper",                     
    "KC_CLEAR_AGAIN"        :  "clear_again",              
    "KC_CRSEL"              :  "crsel",
    "KC_EXSEL"              :  "exsel",
    "KC_STOP"               :  "stop",

    "KC_LOCKING_CAPS"       :  "locking_caps_lock",        # Locking Caps Lock
    "KC_LNUM"               :  "locking_num_lock",
    "KC_LOCKING_NUM"        :  "locking_num_lock",         # Locking Num Lock
    "KC_LSCR"               :  "locking_scroll_lock",
    "KC_LOCKING_SCROLL"     :  "locking_scroll_lock",      # Locking Scroll Lock
    "KC_ERAS"               :  "alternate_erase",
    "KC_ALT_ERASE"          :  "alternate_erase",          # Alternate Erase
    "KC_CLR"                :  "clear", 
    "KC_CLEAR"              :  "clear",                    # Clear
    "KC_NUHS"               :  "iso#",
    "KC_NONUS_HASH"         :  "iso_hash",                 # ISO hash (#~)
    "KC_NUBS"               :  "iso\\",
    "KC_NONUS_BSLASH"       :  "iso\\",                    # ISO Backslash (\|)
    "KC_ZKHK"               :  " `  ",                        # JIS Grave
    "KC_RO"                 :  "international_1",          
    "KC_INT1"               :  "international_1",          # JIS \|
    "KC_KANA"               :  "international_2",
    "KC_INT2"               :  "international_2",          # JIS Katakana/Hiragana
    "KC_JYEN"               :  "international_3",
    "KC_INT3"               :  "international_3",          # JIS Y
    "KC_HENK"               :  "international_4",
    "KC_INT4"               :  "international_4",          # JIS Henkan
    "KC_MHEN"               :  "international_5",
    "KC_INT5"               :  "international_5",          # JIS Muhenkan
    "KC_HAEN"               :  "lang_1",
    "KC_LANG1"              :  "lang_1",                   # KR Hangul/ENG
    "KC_HANJ"               :  "lang_2",
    "KC_LANG2"              :  "lang_2",                   # KR Hanja
 

    # Media Controls
    "KC__MUTE"              :  "mute",
    "KC_MUTE"               :  "mute",
    "KC_AUDIO_MUTE"         :  "mute", #"audio_mute",      # Audio Mute
    "KC_VOLU"               :  "volu",
    "KC__VOLUP"             :  "volu",
    "KC_AUDIO_VOL_UP"       :  "volu", #"audio_vol_up",    # Audio Vol. Up
    "KC_VOLD"               :  "vold", 
    "KC__VOLDOWN"           :  "vold",
    "KC_AUDIO_VOL_DOWN"     :  "vold", #"audio_vol_down",  # Audio Vol. Down
    "KC_MNXT"               :  "mnxt",
    "KC_MEDIA_NEXT_TRACK"   :  "mnxt", #"media_next_track",# Media Next Track
    "KC_MPRV"               :  "mprv",
    "KC_MEDIA_PREV_TRACK"   :  "mprv", #"media_prev_track",# Media Prev Track
    "KC_MFFD"               :  "mffd",
    "KC_MEDIA_FAST_FORWARD" :  "mffd",#"media_fast_forward",# Media Fast Forward
    "KC_MRWD"               :  "mrwd",
    "KC_MEDIA_REWIND"       :  "mrwd", #"media_rewind",    # Media Rewind
    "KC_MSTP"               :  "mstp",
    "KC_MEDIA_STOP"         :  "mstp", #"media_stop",      # Media Stop
    "KC_MPLY"               :  "mply",
    "KC_MEDIA_PLAY_PAUSE"   :  "mply", #"media_play_pause",# Media Play/Pause
    "KKC_DELETEC_MSEL"      :  "msel",
    "KC_MEDIA_SELECT"       :  "msel", #"media_select",    # Media Select
    "KC_EJCT"               :  "mjct",
    "KC_MEDIA_EJECT"        :  "mjct", #"media_eject",     # Media Eject

    # WWW
    "kro_6KC_MAIL"          :  "mail",                     # Mail
    "KC_CALC"               :  "calc",
    "KC_CALCULATOR"         :  "calculator",               # Calculator
    "KC_MYCM"               :  "comp",
    "KC_MY_COMPUTER"        :  "my_computer",              # My Computer
    "KC_WSCH"               :  "www_search",
    "KC_WWW_SEARCH"         :  "www_search",               # WWW Search
    "KC_WHOM"               :  "www_home", 
    "KC_WWW_HOME"           :  "www_home",                 # WWW Home
    "KC_WBAK"               :  "www_back", 
    "KC_WWW_BACK"           :  "www_back",                 # WWW Back
    "KC_WFWD"               :  "www_forward",
    "KC_WWW_FORWARD"        :  "www_forward",              # WWW Forward
    "KC_WSTP"               :  "www_stop",
    "KC_WWW_STOP"           :  "www_stop",                 # WWW Stop
    "KC_WREF"               :  "www_refresh",
    "KC_WWW_REFRESH"        :  "www_refresh",              # WWW Refresh
    "KC_WFAV"               :  "www_favourites",
    "KC_WWW_FAVORITES"      :  "www_favourites",           # WWW Favourites
    
    # Mousekey
    "KC_MS_U"               :  "ms_u",
    "KC_MS_UP"              :  "ms_u", #"mouse_up",        # Mouse Up
    "KC_MS_D"               :  "ms_d",
    "KC_MS_DOWN"            :  "ms_d", #"mouse_down",      # Mouse Down
    "KC_MS_L"               :  "ms_l", 
    "KC_MS_LEFT"            :  "ms_l", #"mouse_left",      # Mouse Left
    "KC_MS_R"               :  "ms_r", 
    "KC_MS_RIGHT"           :  "ms_r", #"mouse_right",     # Mouse Right
    "KC_BTN1"               :  "btn1",
    "KC_MS_BTN1"            :  "btn1", #"mouse_btn1",      # MOUSE1
    "KC_BTN2"               :  "btn2", 
    "KC_MS_BTN2"            :  "btn2", #"mouse_btn2",      # MOUSE2
    "KC_BTN3"               :  "btn3",
    "KC_MS_BTN3"            :  "btn3", #"mouse_btn3",      # MOUSE3
    "KC_BTN4"               :  "btn4",
    "KC_MS_BTN4"            :  "btn4", #"mouse_btn4",      # MOUSE4
    "KC_BTN5"               :  "btn5",
    "KC_MS_BTN5"            :  "btn5", #"mouse_btn5",      # MOUSE5
    "KC_WH_U"               :  "wh_u",
    "KC_MS_WH_UP"           :  "wh_u", #"mouse_wh_up",     # Mouse Wheel Up
    "KC_WH_D"               :  "wh_d",
    "KC_MS_WH_DOWN"         :  "wh_d", #"mouse_wh_down",   # Mouse Wheel Down
    "KC_WH_L"               :  "wh_l", 
    "KC_MS_WH_LEFT"         :  "wh_l", #"mouse_wh_left",   # Mouse Wheel Left
    "KC_WH_R"               :  "wh_r", 
    "KC_MS_WH_RIGHT"        :  "wh_r", #"mouse_wh_right",  # Mouse Wheel Right

    # System
    "KC_PWR"                :  "system_power",
    "KC_POWER"              :  "system_power",
    "KC_SYSTEM_POWER"       :  "system_power",             # Power
    "KC_SLEP"               :  "system_sleep",
    "KC_SYSTEM_SLEEP"       :  "system_sleep",             # Sleep
    "KC_WAKE"               :  "system_wake",
    "KC_SYSTEM_WAKE"        :  "system_wake",              # Wake
}

# QMK -> Keyplus functions
qmk_to_keyp_func = {
    "MO("                :  " l",
    "TG("                :  "toggle_l",
    "TT("                :  " l",            #Feature not fully implemented in K+
    "OSL("               :  "sticky_l",
    "DF("                :  "set_l",
    "OSM(KC_LSFT)"       :  "sticky_lshift",
    "OSM(KC_LSHIFT)"     :  "sticky_lshift",
    "OSM(KC_LCTL)"       :  "sticky_lctrl",
    "OSM(KC_LCTRL)"      :  "sticky_lctrl",
    "OSM(KC_LALT)"       :  "sticky_lalt",
    "OSM(KC_LGUI)"       :  "sticky_lgui",
    "OSM(KC_LWIN)"       :  "sticky_lgui",
    "OSM(KC_LCMD)"       :  "sticky_lgui",
    "OSM(KC_RSFT)"       :  "sticky_rshift",
    "OSM(KC_RSHIFT)"     :  "sticky_rshift",
    "OSM(KC_RCTL)"       :  "sticky_rctrl",
    "OSM(KC_RCTRL)"      :  "sticky_rctrl",
    "OSM(KC_RALT)"       :  "sticky_ralt",
    "OSM(KC_RGUI)"       :  "sticky_rgui",
    "OSM(KC_RWIN)"       :  "sticky_rgui",
    "OSM(KC_RCMD)"       :  "sticky_rgui", 
}


# QMK Keycodes currently not Supported 
keyp_missing = {
    # Setting Mouse Acceleration
    "KC_ACL0",
    "KC_MS_ACCEL0",
    "KC_ACL1",
    "KC_MS_ACCEL1",
    "KC_ACL2",
    "KC_MS_ACCEL2",
    # Thermal Printer???
    "PRINT_ON",
    "PRINT_OFF",
    # Arr Gee Bee
    "RGB_TOG",
    "RGB_VAI",
    "RGB_VAD",
    "RGB_SAI",
    "RGB_MOD",
    "RGB_HUD",
    "RGB_SAD",
    "RGB_HUI",
    # Backlight
    "BL_STEP",
    # QMK Modifiers
    "LCTL(",
    "LALT(",
    "LGUI(",
    "LCMD(",
    "LWIN(",
    "RCTL(",
    "RSFT(",
    "RALT(",
    "RGUI(",
    "RCMD(",
    "RWIN(",
    "KC_HYPR",
    "KC_MEH",
    "HYPR(",
    "MEH(",
    "LCAG(",
    "ALTG(",
    "SGUI(",
    "SCMD(",
    "SWIN(",
    "LCA(",
    "LCTL_T(",
    "CTL_T(",
    "RCTL_T(",
    "LSFT_T(",
    "RSFT_T(",
    "LALT_T(",
    "ALT_T(",
    "RALT_T(",
    "ALGR_T(",
    "LGUI_T(",
    "LCMD_T(",
    "RWIN_T(",
    "GUI_T(",
    "RGUI_T(",
    "RCMD_T(",
    "RWIN_T(",
    "C_S_T(",
    "MEH_T(",
    "LCAG_T(" ,
    "RCAG_T(",
    "ALL_T(",
    "SCMD_T(",
    "SWIN_T(",
    "LCA_T(",
}

keyplus_yaml_template = '''
# Generated by Q2K KeyMap parSer by 2Cas (c) 2018
# This file is released into the public domain as per the CC0 Public Domain
# Dedication (http://creativecommons.org/publicdomain/zero/1.0/)
---

version: 0
report_mode: auto_nkro # options: auto_nkro, 6kro, nkro

devices:
  <KB_NAME> :
    id : 0
    layout : <LAYOUT_NAME>
    layout offset: 0
    scan_mode:
      mode: col_row # options: col_row, pins, none
      rows: <ROWS>
      cols: <COLS>
      # Maps how keys are physically wired, to how they appear visually
      matrix_map: [
        <MATRIX_MAP>
      ]
      # Debounce settings
      debounce:
         debounce_time_press: 5
         debounce_time_release: 5
         trigger_time_press: 1
         trigger_time_release: 1
         parasitic_discharge_delay_idle: 10.0
         parasitic_discharge_delay_debouncing: 10.0

layouts:
  <LAYOUT_NAME> :
    default_layer: 0
    layers: [
<LAYOUT>    ]
'''
