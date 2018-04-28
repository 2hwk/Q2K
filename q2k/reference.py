import string
class Q2KRef:
    ''' a class containing class variables (lists, dictionaries) mapping conversion between QMK and keyplus in q2k'''
    # QMK -> Keyplus Keycode Mapping
    # for keycodes only, functions are in KEYP_FUNC_LIST
    keyp_kc = {
        "KC_NO"                            :          " no ", #- giorgio, 2018
        "KC_TRNS"                          :          "____",
        "KC_TRANSPARENT"                   :          "____", #"trans",
        "XXXXXXX"                          :          " no ",
        "_______"                          :          "____",
        "RESET"                            :          "boot",
        "MAGIC_HOST_NKRO"                  :          "kro_n",                       # FORCE NKRO
        "MAGIC_UNHOST_NKRO"                :          "kro_6",                       # FORCE 6KRO
        "MAGIC_TOGGLE_NKRO"                :          "kro_auto",                    # Set Auto NKRO
        "KC_GESC"                          :          "gesc",

        # Alphas
        "KC_GRV"                           :          "'`' ",
        "KC_GRAVE"                         :          "'`' ",  #"grave",             # Grave (~`)kro_6
        "KC_1"                             :          " 1 ",
        "KC_2"                             :          " 2 ",
        "KC_3"                             :          " 3 ",
        "KC_4"                             :          " 4 ",
        "KC_5"                             :          " 5 ",
        "KC_6"                             :          " 6 ",
        "KC_7"                             :          " 7 ",
        "KC_8"                             :          " 8 ",
        "KC_9"                             :          " 9 ",
        "KC_0"                             :          " 0 ",
        "KC_MINS"                          :          "'-' ",
        "KC_MINUS"                         :          "'-' ", #"minus",              # Minus (-_)
        "KC_EQL"                           :          "'=' ",
        "KC_EQUAL"                         :          "'=' ", #"equal",              # Equal (=+)
        "KC_Q"                             :          " q  ",
        "KC_W"                             :          " w  ",
        "KC_E"                             :          " e  ",
        "KC_R"                             :          " r  ",
        "KC_T"                             :          " t  ",
        "KC_Y"                             :          " y  ",
        "KC_U"                             :          " u  ",
        "KC_I"                             :          " i  ",
        "KC_O"                             :          " o  ",
        "KC_P"                             :          " p  ",
        "KC_LBRC"                          :          "'[' ",
        "KC_LBRACKET"                      :          "'[' ", #"left_bracket",        # Left Bracket ([)
        "KC_RBRC"                          :          "']' ",
        "KC_RBRACKET"                      :          "']' ", #"right_bracket",       # Right Bracket (])
        "KC_BSLS"                          :          "'\\' ", #"bsls",
        "KC_BSLASH"                        :          "'\\' ",                        # Backslash (\|)
        "KC_A"                             :          " a  ",
        "KC_S"                             :          " s  ",
        "KC_D"                             :          " d  ",
        "KC_F"                             :          " f  ",
        "KC_G"                             :          " g  ",
        "KC_H"                             :          " h  ",
        "KC_J"                             :          " j  ",
        "KC_K"                             :          " k  ",
        "KC_L"                             :          " l  ",
        "KC_SCLN"                          :          "';' ",
        "KC_SCOLON"                        :          "';' ", #"semicolon",          # Semicolon (;:)
        "KC_QUOT"                          :          "\"\'\" ", 
        "KC_QUOTE"                         :          "\"\'\" ", #"quot",            # Quote ('")
        "KC_Z"                             :          " z  ",
        "KC_X"                             :          " x  ",
        "KC_C"                             :          " c  ",
        "KC_V"                             :          " v  ",
        "KC_B"                             :          " b  ",
        "KC_N"                             :          " n  ",
        "KC_M"                             :          " m  ",
        "KC_COMM"                          :          "',' ",
        "KC_COMMA"                         :          "',' ", #"comma",              # Comma (,<)
        "KC_DOT"                           :          "'.' ",                        # Period (.>)
        "KC_SLSH"                          :          "'/' ",
        "KC_SLASH"                         :          "'/' ", #"forward_slash",      # Forward Slash (/?)
        "KC_SPC"                           :          " spc",
        "KC_SPACE"                         :          " spc", #"spacebar",           # Spacebar

        # Modifiers
        "KC_RCTL"                          :          "rctl",
        "KC_RCTRL"                         :          "rctl", #"rctrl",              # Right Ctrl
        "KC_LCTL"                          :          "lctl",
        "KC_LCTRL"                         :          "lctl", #"lctrl",              # Left Ctrl
        "KC_RSFT"                          :          "rsft",
        "KC_RSHIFT"                        :          "rsft", #"rshift",             # Right Shift
        "KC_LSFT"                          :          "lsft",
        "KC_LSHIFT"                        :          "lsft", #"lshift",             # Left Shift
        "KC_LGUI"                          :          "lgui",
        "KC_LWIN"                          :          "lgui", #"lwin",
        "KC_LCMD"                          :          "lgui",                        # Left GUI/Win
        "KC_RGUI"                          :          "rgui",
        "KC_RWIN"                          :          "rgui", #"rwin",                    
        "KC_RCMD"                          :          "rgui",                        # Right GUI/Win
        "KC_LALT"                          :          "lalt",                        # Left Alt
        "KC_RALT"                          :          "ralt",                        # Right Alt
        "KC_BSPC"                          :          "bspc",
        "KC_BSPACE"                        :          "bspc", #"backspace",          # Backspace
        "KC_ENT"                           :          " ent",
        "KC_ENTER"                         :          " ent", #"enter",              # Enter
        "KC_TAB"                           :          " tab",                        # Tab
        "KC_CAPS"                          :          "caps",
        "KC_CLCK"                          :          "caps",
        "KC_CAPSLOCK"                      :          "caps", #"caps_lock""kp_ent",, # Caps Lock
        "KC_RGHT"                          :          "rght",
        "KC_RIGHT"                         :          "rght", #"right",              # right arrow
        "KC_UP"                            :          " up ",
        "KC_DOWN"                          :          "down",
        "KC_LEFT"                          :          "left",
        # Function 
        "KC_ESC"                           :          " esc",
        "KC_ESCAPE"                        :          " esc", #"escape",             # Escape
        "KC_F1"                            :          " f1 ",

        "KC_F2"                            :          " f2 ",
        "KC_F3"                            :          " f3 ",
        "KC_F4"                            :          " f4 ",
        "KC_F5"                            :          " f5 ",
        "KC_F6"                            :          " f6 ",
        "KC_F7"                            :          " f7 ",
        "KC_F8"                            :          " f8 ",
        "KC_F9"                            :          " f9 ",
        "KC_F10"                           :          " f10",
        "KC_F11"                           :          " f11",
        "KC_F12"                           :          " f12",
        "KC_PSCR"                          :          "pscr",
        "KC_PSCREEN"                       :          "pscr", #"print_screen",       # Print Screen
        "KC_SLCK"                          :          "slck",
        "KC_SCROLLLOCK"                    :          "slck", #"scroll_lock",        # Scroll Lock
        "KC_PAUS"                          :          "paus", 
        "KC_BRK"                           :          "paus",
        "KC_PAUSE"                         :          "paus", #"pause",              # Pause/Break
        "KC_INS"                           :          " ins",
        "KC_INSERT"                        :          " ins", #"insert",             # Insert
        "KC_DEL"                           :          " del",
        "KC_DELT"                          :          " del",
        "KC_DELETE"                        :          " del", #"delete",             # Delete
        "KC_HOME"                          :          "home",                        # Home
        "KC_END"                           :          " end",                        # End
        "KC_PGUP"                          :          "pgup",                        # Page Up
        "KC_PGDN"                          :          "pgdn",
        "KC_PGDOWN"                        :          "pgdn", #"page_down",          # Page Down
        "KC_F13"                           :          " f13",                     
        "KC_F14"                           :          " f14",
        "KC_F15"                           :          " f15",
        "KC_F16"                           :          " f16",
        "KC_F17"                           :          " f17",
        "KC_F18"                           :          " f18",
        "KC_F19"                           :          " f19",
        "KC_F20"                           :          " f20",
        "KC_F21"                           :          " f21",
        "KC_F22"                           :          " f22",
        "KC_F23"                           :          " f23",
        "KC_F24"                           :          " f24",
        # Shifted
        "KC_TILDE"                         :          "'~' ",
        "KC_TILD"                          :          "'~' ",
        "KC_EXCLAIM"                       :          "'!' ",
        "KC_EXLM"                          :          "'!' ",
        "KC_AT"                            :          "'@' ",
        "KC_HASH"                          :          "'#' ",
        "KC_DOLLAR"                        :          "'$' ",
        "KC_DLR"                           :          "'$' ",
        "KC_PERCENT"                       :          "'%' ",
        "KC_PERC"                          :          "'%' ",
        "KC_CIRCUMFLEX"                    :          "'^' ",
        "KC_CIRC"                          :          "'^' ",
        "KC_AMPERSAND"                     :          "'&' ",
        "KC_AMPR"                          :          "'&' ",
        "KC_ASTERISK"                      :          "'*' ",
        "KC_ASTR"                          :          "'*' ",
        "KC_LEFT_PAREN"                    :          "'(' ",
        "KC_LPRN"                          :          "'(' ",
        "KC_RIGHT_PAREN"                   :          "')' ",
        "KC_RPRN"                          :          "')' ",
        "KC_UNDERSCORE"                    :          "'_' ",
        "KC_UNDS"                          :          "'_' ",
        "KC_PLUS"                          :          "'+' ",
        "KC_LEFT_CURLY_BRACE"              :          "'{' ",
        "KC_LCBR"                          :          "'{' ",
        "KC_RIGHT_CURLY_BRACE"             :          "'}' ",
        "KC_RCBR"                          :          "'}' ",
        "KC_PIPE"                          :          "'|' ",
        "KC_COLON"                         :          "':' ",
        "KC_COLN"                          :          "':' ",
        "KC_DOUBLE_QUOTE"                  :          "\'\"\' ",
        "KC_DQT"                           :          "\'\"\' ",
        "KC_DQUO"                          :          "\'\"\' ",
        "KC_LEFT_ANGLE_BRACKET"            :          "'<' ",
        "KC_LT"                            :          "'<' ",
        "KC_LABK"                          :          "'<' ",
        "KC_RIGHT_ANGLE_BRACKET"           :          "'>' ",
        "KC_GT"                            :          "'>' ",
        "KC_RABK"                          :          "'>' ",
        "KC_QUESTION"                      :          "'?' ",
        "KC_QUES"                          :          "'?' ",

        # Numpad
        "KC_NLCK"                          :          "nlck", 
        "KC_NUMLOCK"                       :          "nlck", #"num_lock",           # Num Lock
        "KC_P1"                            :          "kp_1",
        "KC_KP_1"                          :          "kp_1",                        # Numpad 1
        "KC_P2"                            :          "kp_2",   
        "KC_KP_2"                          :          "kp_2",                        # Numpad 2
        "KC_P3"                            :          "kp_3",   
        "KC_KP_3"                          :          "kp_3",                        # Numpad 3
        "KC_P4"                            :          "kp_4",   
        "KC_KP_4"                          :          "kp_4",                        # Numpad 4
        "KC_P5"                            :          "kp_5",   
        "KC_KP_5"                          :          "kp_5",                        # Numpad 5
        "KC_P6"                            :          "kp_6",   
        "KC_KP_6"                          :          "kp_6",                        # Numpad 6
        "KC_P7"                            :          "kp_7",   
        "KC_KP_7"                          :          "kp_7",                        # Numpad 7
        "KC_P8"                            :          "kp_8",   
        "KC_KP_8"                          :          "kp_8",                        # Numpad 8
        "KC_P9"                            :          "kp_9",   
        "KC_KP_9"                          :          "kp_9",                        # Numpad 9
        "KC_P0"                            :          "kp_0",   
        "KC_KP_0"                          :          "kp_0",                        # Numpad 0
        "KC_PDOT"                          :          "kp_.",
        "KC_KP_DOT"                        :          "kp_.",                        # Numpad .
        "KC_PCMM"                          :          "kp_,",
        "KC_KP_COMMA"                      :          "kp_,",                        # Numpad ,
        "KC_PSLS"                          :          "kp_/",
        "KC_KP_SLASH"                      :          "kp_/",                        # Numpad /
        "KC_PAST"                          :          "kp_*",                      
        "KC_KP_ASTERISK"                   :          "kp_*",                        # Numpad *
        "KC_PMNS"                          :          "kp_-", 
        "KC_KP_MINUS"                      :          "kp_-",                        # Numpad -
        "KC_PPLS"                          :          "kp_+",
        "KC_KP_PLUS"                       :          "kp_+",                        # Numpad +
        "KC_PEQL"                          :          "kp_=",
        "KC_KP_EQUAL"                      :          "kp_=",                        # Numpad =
        "KC_PENT"                          :          "kp_ent",
        "KC_KP_ENTER"                      :          "kp_ent", #"kp_enter",         # Numpad Enter

        # Misc Functions
        "KC_APP"                           :          " app",
        "KC_APPLICATION"                   :          " app",                        # Application
        "KC_LCAP"                          :          "locking_caps_lock",
        "KC_EXEC"                          :          "execute",
        "KC_EXECUTE"                       :          "execute",                     # Execute
        "KC_SLCT"                          :          "select",
        "KC_SELECT"                        :          "select",                      # Select____
        "KC_AGIN"                          :          "again", 
        "KC_AGAIN"                         :          "again",                       # Again
        "KC_HELP"                          :          "help",
        "KC_MENU"                          :          "hid_menu",                    # Menu
        "KC_UNDO"                          :          "undo",                        # Undo
        "KC_CUT"                           :          " cut",                        # Cut
        "KC_COPY"                          :          "copy",                        # Copy
        "KC_PSTE"                          :          "paste", 
        "KC_PASTE"                         :          "paste",                       # Paste
        "KC_FIND"                          :          "find",                        # Find
        "KC_ALT_ERASE"                     :          "alternate_erase",             # Alt Erase
        "KC_CANCEL"                        :          "cancel",                      # Cancel
        "KC_SYSREQ"                        :          "sys_req",                     # SYSREQ
        "KC_PRIOR"                         :          "prior",                   
        "KC_SEPERATOR"                     :          "separator",               
        "KC_RETURN"                        :          "return",                   
        "KC_OUT"                           :          " out",                      
        "KC_OPER"                          :          "oper",                     
        "KC_CLEAR_AGAIN"                   :          "clear_again",              
        "KC_CRSEL"                         :          "crsel",
        "KC_EXSEL"                         :          "exsel",
        "KC_STOP"                          :          "stop",

        "KC_LOCKING_CAPS"                  :          "locking_caps_lock",           # Locking Caps Lock
        "KC_LNUM"                          :          "locking_num_lock",
        "KC_LOCKING_NUM"                   :          "locking_num_lock",            # Locking Num Lock
        "KC_LSCR"                          :          "locking_scroll_lock",
        "KC_LOCKING_SCROLL"                :          "locking_scroll_lock",         # Locking Scroll Lock
        "KC_ERAS"                          :          "alternate_erase",
        "KC_ALT_ERASE"                     :          "alternate_erase",             # Alternate Erase
        "KC_CLR"                           :          "clear", 
        "KC_CLEAR"                         :          "clear",                       # Clear
        "KC_NUHS"                          :          "iso#",
        "KC_NONUS_HASH"                    :          "iso_hash",                    # ISO hash (#~)
        "KC_NUBS"                          :          "iso\\",
        "KC_NONUS_BSLASH"                  :          "iso\\",                       # ISO Backslash (\|)
        "KC_ZKHK"                          :          "'`' ",                        # JIS Grave
        "KC_RO"                            :          "int1",          
        "KC_INT1"                          :          "int1",                        # JIS \|
        "KC_KANA"                          :          "int2",
        "KC_INT2"                          :          "int2",                        # JIS Katakana/Hiragana
        "KC_JYEN"                          :          "int3",
        "KC_INT3"                          :          "int3",                        # JIS Y
        "KC_HENK"                          :          "int4",
        "KC_INT4"                          :          "int4",                        # JIS Henkan
        "KC_MHEN"                          :          "int5",
        "KC_INT5"                          :          "int5",                        # JIS Muhenkan
        "KC_INT6"                          :          "int6",
        "KC_INT7"                          :          "int7",
        "KC_INT8"                          :          "int8",
        "KC_INT9"                          :          "int9",
        "KC_HAEN"                          :          "lang1",
        "KC_LANG1"                         :          "lang1",                      # KR Hangul/ENG
        "KC_HANJ"                          :          "lang2",
        "KC_LANG2"                         :          "lang2",                      # KR Hanja
        "KC_LANG3"                         :          "lang3",
        "KC_LANG4"                         :          "lang4",
        "KC_LANG5"                         :          "lang5",
        "KC_LANG6"                         :          "lang6",
        "KC_LANG7"                         :          "lang7",
        "KC_LANG8"                         :          "lang8",
        "KC_LANG9"                         :          "lang9",
     

        # Media Controls
        "KC__MUTE"                         :          "mute",
        "KC_MUTE"                          :          "mute",
        "KC_AUDIO_MUTE"                    :          "mute", #"audio_mute",         # Audio Mute
        "KC_VOLU"                          :          "volu",
        "KC__VOLUP"                        :          "volu",
        "KC_AUDIO_VOL_UP"                  :          "volu", #"audio_vol_up",       # Audio Vol. Up
        "KC_VOLD"                          :          "vold", 
        "KC__VOLDOWN"                      :          "vold",
        "KC_AUDIO_VOL_DOWN"                :          "vold", #"audio_vol_down",     # Audio Vol. Down
        "KC_MNXT"                          :          "mnxt",
        "KC_MEDIA_NEXT_TRACK"              :          "mnxt", #"media_next_track",   # Media Next Track
        "KC_MPRV"                          :          "mprv",
        "KC_MEDIA_PREV_TRACK"              :          "mprv", #"media_prev_track",   # Media Prev Track
        "KC_MFFD"                          :          "mffd",
        "KC_MEDIA_FAST_FORWARD"            :          "mffd",#"media_fast_forward",  # Media Fast Forward
        "KC_MRWD"                          :          "mrwd",
        "KC_MEDIA_REWIND"                  :          "mrwd", #"media_rewind",       # Media Rewind
        "KC_MSTP"                          :          "mstp",
        "KC_MEDIA_STOP"                    :          "mstp", #"media_stop",         # Media Stop
        "KC_MPLY"                          :          "mply",
        "KC_MEDIA_PLAY_PAUSE"              :          "mply", #"media_play_pause",   # Media Play/Pause
        "KC_MSEL"                          :          "msel",
        "KC_MEDIA_SELECT"                  :          "msel", #"media_select",       # Media Select
        "KC_EJCT"                          :          "mjct",
        "KC_MEDIA_EJECT"                   :          "mjct", #"media_eject",        # Media Eject

        # WWW
        "KC_MAIL"                          :          "mail",                        # Mail
        "KC_CALC"                          :          "calc",
        "KC_CALCULATOR"                    :          "calc",                        # Calculator
        "KC_MYCM"                          :          "comp",
        "KC_MY_COMPUTER"                   :          "my_computer",                 # My Computer
        "KC_WSCH"                          :          "www_search",
        "KC_WWW_SEARCH"                    :          "www_search",                  # WWW Search
        "KC_WHOM"                          :          "www_home", 
        "KC_WWW_HOME"                      :          "www_home",                    # WWW Home
        "KC_WBAK"                          :          "www_back", 
        "KC_WWW_BACK"                      :          "www_back",                    # WWW Back
        "KC_WFWD"                          :          "www_forward",
        "KC_WWW_FORWARD"                   :          "www_forward",                 # WWW Forward
        "KC_WSTP"                          :          "www_stop",
        "KC_WWW_STOP"                      :          "www_stop",                    # WWW Stop
        "KC_WREF"                          :          "www_refresh",
        "KC_WWW_REFRESH"                   :          "www_refresh",                 # WWW Refresh
        "KC_WFAV"                          :          "www_favourites",
        "KC_WWW_FAVORITES"                 :          "www_favourites",              # WWW Favourites
        
        # Mousekey
        "KC_MS_U"                          :          "ms_u",
        "KC_MS_UP"                         :          "ms_u", #"mouse_up",           # Mouse Up
        "KC_MS_D"                          :          "ms_d",
        "KC_MS_DOWN"                       :          "ms_d", #"mouse_down",         # Mouse Down
        "KC_MS_L"                          :          "ms_l", 
        "KC_MS_LEFT"                       :          "ms_l", #"mouse_left",         # Mouse Left
        "KC_MS_R"                          :          "ms_r", 
        "KC_MS_RIGHT"                      :          "ms_r", #"mouse_right",        # Mouse Right
        "KC_BTN1"                          :          "btn1",
        "KC_MS_BTN1"                       :          "btn1", #"mouse_btn1",         # MOUSE1
        "KC_BTN2"                          :          "btn2", 
        "KC_MS_BTN2"                       :          "btn2", #"mouse_btn2",         # MOUSE2
        "KC_BTN3"                          :          "btn3",
        "KC_MS_BTN3"                       :          "btn3", #"mouse_btn3",         # MOUSE3
        "KC_BTN4"                          :          "btn4",
        "KC_MS_BTN4"                       :          "btn4", #"mouse_btn4",         # MOUSE4
        "KC_BTN5"                          :          "btn5",
        "KC_MS_BTN5"                       :          "btn5", #"mouse_btn5",         # MOUSE5
        "KC_WH_U"                          :          "wh_u",
        "KC_MS_WH_UP"                      :          "wh_u", #"mouse_wh_up",        # Mouse Wheel Up
        "KC_WH_D"                          :          "wh_d",
        "KC_MS_WH_DOWN"                    :          "wh_d", #"mouse_wh_down",      # Mouse Wheel Down
        "KC_WH_L"                          :          "wh_l", 
        "KC_MS_WH_LEFT"                    :          "wh_l", #"mouse_wh_left",      # Mouse Wheel Left
        "KC_WH_R"                          :          "wh_r", 
        "KC_MS_WH_RIGHT"                   :          "wh_r", #"mouse_wh_right",     # Mouse Wheel Right

        # System
        "KC_PWR"                           :          "system_power",
        "KC_POWER"                         :          "system_power",
        "KC_SYSTEM_POWER"                  :          "system_power",                # Power
        "KC_SLEP"                          :          "system_sleep",
        "KC_SYSTEM_SLEEP"                  :          "system_sleep",                # Sleep
        "KC_WAKE"                          :          "system_wake",
        "KC_SYSTEM_WAKE"                   :          "system_wake",                 # Wake

        # QMK Modifiers
        "KC_HYPR"                          :          "csag-none",                   # Hyper
        "KC_MEH"                           :          "csa-none",                    # Ctrl+Shift+Alt
    }                           
                              
    # QMK -> Keyplus Layer Functions
    keyp_layer_func = {

        "MO("                              :          " L",
        "TG("                              :          "tog_L",
        "TT("                              :          " L",                          # Feature not fully implemented in K+
        "OSL("                             :          "s_L",
        "TO("                              :          "set_L",
        "DF("                              :          "set_L",                       # Feature not fully implemented in K+

    }                      
    # QMK -> Keyplus Modifier functions
    keyp_mods = {
        # Mod Keys
        "LCTL("                            :          "C",
        "LSFT("                            :          "S",
        "S("                               :          "S",
        "LALT("                            :          "A",
        "LGUI("                            :          "G",
        "LCMD("                            :          "G",
        "LWIN("                            :          "G",
        "RCTL("                            :          "rC",
        "RSFT("                            :          "rS",
        "RALT("                            :          "rA",
        "RGUI("                            :          "rG",
        "RWIN("                            :          "rG",
        "RCMD("                            :          "rG",
        # Multi Mod Keys
        "SGUI("                            :          "SG",
        "SCMD("                            :          "SG",
        "SWIN("                            :          "SG",
        "LCA("                             :          "CA",
        "ALTG("                            :          "rCrA",
        "LCAG("                            :          "CAG",
        "MEH("                             :          "CSA",
        "HYPR("                            :          "CSAG",

        "OSM(MOD_LSFT)"                    :          "s_lsft",
        "OSM(MOD_LCTL)"                    :          "s_lctrl",
        "OSM(MOD_LALT)"                    :          "s_lalt",
        "OSM(MOD_LGUI)"                    :          "s_lgui",
        "OSM(MOD_RCTL)"                    :          "s_rctrl",
        "OSM(MOD_RSFT)"                    :          "s_rsft",
        "OSM(MOD_RALT)"                    :          "s_ralt",
        "OSM(MOD_RGUI)"                    :          "s_rgui",
        "OSM(KC_LSFT)"                     :          "s_lsft",
        "OSM(KC_LSHIFT)"                   :          "s_lsft",
        "OSM(KC_LCTL)"                     :          "s_lctrl",
        "OSM(KC_LCTRL)"                    :          "s_lctrl",
        "OSM(KC_LALT)"                     :          "s_lalt",
        "OSM(KC_LGUI)"                     :          "s_lgui",
        "OSM(KC_LWIN)"                     :          "s_lgui",
        "OSM(KC_LCMD)"                     :          "s_lgui",
        "OSM(KC_RSFT)"                     :          "s_rsft",
        "OSM(KC_RSHIFT)"                   :          "s_rsft",
        "OSM(KC_RCTL)"                     :          "s_rctrl",
        "OSM(KC_RCTRL)"                    :          "s_rctrl",
        "OSM(KC_RALT)"                     :          "s_ralt",
        "OSM(KC_RGUI)"                     :          "s_rgui",
        "OSM(KC_RWIN)"                     :          "s_rgui",
        "OSM(KC_RCMD)"                     :          "s_rgui", 
    }

    keyp_tap_layer = {
        "LT("                              :          "L",
        "LM("                              :          "L",
    }

    keyp_tap_mod = {
        "LCTL_T("                          :          "C",
        "CTL_T("                           :          "C",
        "RCTL_T("                          :          "rC",
        "LSFT_T("                          :          "S",
        "SFT_T("                           :          "S",
        "RSFT_T("                          :          "rS",
        "LALT_T("                          :          "A",
        "ALT_T("                           :          "A",
        "RALT_T("                          :          "rA",
        "ALGR_T"                           :          "rA",
        "LGUI_T("                          :          "G",
        "LCMD_T("                          :          "G",
        "GUI_T("                           :          "G",
        "RGUI_T("                          :          "rG",
        "RCMD_T("                          :          "rG",
        "RWIN_T("                          :          "rG",
        "LCA_T("                           :          "CA",
        "C_S_T("                           :          "CS",
        "MEH_T("                           :          "CSA",
        "LCAG_T("                          :          "CAG",
        "RCAG_T("                          :          "rCrArG",
        "ALL_T("                           :          "CSAG",
        "SCMD_T("                          :          "SG",
    }

    # Legacy QMK functions
    qmk_legacy_func = ["KC_FN", "FN", "FUNC(", "F("]
    keyp_actions = { 
        "ACTION_LAYER_MOMENTARY("          :          " L", 
        "ACTION_LAYER_TOGGLE("             :          "tog_L",
        "ACTION_LAYER_SET("                :          "set_L",
        "ACTION_LAYER_TAP_TOGGLE("         :          "s_L", 
        "ACTION_LAYER_TAP_KEY("            :          "L",
        "ACTION_MODS_KEY("                 :          "",

        # Explicitly defined
        "ACTION_FUNCTION(SHIFT_ESC)"       :          "gesc",
        "ACTION_FUNCTION(ESC_GRV)"         :          "gesc",
        "ACTION_FUNCTION(LFK_ESC_TILDE)"   :          "gesc",
        "ACTION_FUNCTION(ESCAPE)"          :          "gesc",
    }

    qmk_legacy_mod = {
        "MOD_LSFT"                         :          "S",
        "MOD_LCTL"                         :          "C",
        "MOD_LALT"                         :          "A",
        "MOD_LGUI"                         :          "G",
        "MOD_RCTL"                         :          "rC",
        "MOD_RSFT"                         :          "rS",
        "MOD_RALT"                         :          "rA",
        "MOD_RGUI"                         :          "rG",
    }

    # QMK Keycodes currently not supported
    keyp_missing = {
        # Setting Mouse Acceleration
        "KC_ACL0", "KC_MS_ACCEL0", "KC_ACL1", "KC_MS_ACCEL1", "KC_ACL2", "KC_MS_ACCEL2",
        # Thermal Printer
        "PRINT_ON", "PRINT_OFF",
        # Arr Gee Bee
        "RGB_TOG", "RGB_VAI", "RGB_VAD", "RGB_SAI", "RGB_MOD", "RGB_HUD", "RGB_SAD", "RGB_HUI",
        # Backlight
        "BL_STEP",
        # QMK Modifiers
        "LCTL(", "LALT(", "LGUI(", "LCMD(", "LWIN(", "RCTL(", "RSFT(", "RALT(", 
        "RGUI(", "RCMD(", "RWIN(", "KC_HYPR", "KC_MEH", "HYPR(", "MEH(", "LCAG(", 
        "ALTG(", "SGUI(", "SCMD(", "SWIN(", "LCA(", "LCTL_T(", "CTL_T(", "RCTL_T(",
        "LSFT_T(", "RSFT_T(", "LALT_T(", "ALT_T(", "RALT_T(", "ALGR_T(", "LGUI_T(",
        "LCMD_T(", "RWIN_T(", "GUI_T(", "RGUI_T(", "RCMD_T(", "RWIN_T(", "C_S_T(",
        "MEH_T(", "LCAG_T(" , "RCAG_T(", "ALL_T(", "SCMD_T(", "SWIN_T(", "LCA_T(",
    }

    # KBfirmware json compatability list
    kbf_kc = [
        "KC_1", "KC_2", "KC_3", "KC_4", "KC_5", "KC_6", "KC_7",
        "KC_8", "KC_9", "KC_0",
        "KC_A", "KC_B", "KC_C", "KC_D", "KC_E", "KC_F", "KC_G",
        "KC_H", "KC_I", "KC_J", "KC_K", "KC_L", "KC_M", "KC_N",
        "KC_O", "KC_P", "KC_Q", "KC_R", "KC_S", "KC_T", "KC_U",
        "KC_V", "KC_W", "KC_X", "KC_Y", "KC_Z",
        "KC_NUHS", "KC_NUBS", "KC_MINS", "KC_EQL", "KC_LBRC", 
        "KC_RBRC", "KC_BSLS", "KC_SCLN", "KC_QUOT", "KC_GRV", 
        "KC_COMM", "KC_DOT",  "KC_SLSH", 
        "KC_ENT", "KC_ESC", "KC_BSPC", "KC_TAB", "KC_SPC", 
        "KC_CAPS", "KC_APP",
        "KC_LCTL", "KC_LSFT", "KC_LALT", "KC_LGUI", "KC_RCTL",
        "KC_RSFT", "KC_RALT", "KC_RGUI", "KC_TRNS", "KC_NO",
        "RESET",
        "KC_EXLM", "KC_AT", "KC_HASH", "KC_DLR", "KC_PERC",
        "KC_CIRC", "KC_AMPR", "KC_ASTR", "KC_LPRN", "KC_RPRN",
        "KC_UNDS", "KC_PLUS", "KC_LCBR", "KC_RCBR", "KC_PIPE",
        "KC_COLN", "KC_DQUO", "KC_TILD", "KC_LABK", "KC_RABK",
        "KC_QUES",
        "KC_F1", "KC_F2", "KC_F3", "KC_F4", "KC_F5", "KC_F6",
        "KC_F7", "KC_F8", "KC_F9", "KC_F10", "KC_F11", "KC_F12",
        "KC_F13", "KC_F14", "KC_F15", "KC_F16", "KC_F17",
        "KC_F18", "KC_F19", "KC_F20", "KC_F21", "KC_F22",
        "KC_F23", "KC_F24",
        "KC_PSCR", "KC_SLCK", "KC_PAUS",
        "KC_INS", "KC_DEL", "KC_HOME", "KC_END", "KC_PGUP", 
        "KC_PGDN", "KC_LEFT", "KC_DOWN", "KC_UP", "KC_RGHT",
        "KC_PWR", "KC_SLEP", "KC_WAKE", "KC_MUTE", "KC_VOLU",
        "KC_VOLD", "KC_MPLY", "KC_MSTP", "KC_MPRV", "KC_MNXT",
        "KC_RO", "KC_KANA", "KC_JYEN", "KC_HENK", "KC_MHEN",
        "KC_LOCKING_CAPS", "KC_LOCKING_NUM", "KC_LOCKING_SCROLL",
        "KC_APP", "KC_CALC", "KC_MYCM", "KC_WSCH", "KC_WHOM",
        "KC_WBAK", "KC_WFWD", "KC_WSTP", "KC_WREF", "KC_WFAV"
        "KC_MSEL",
        "KC_NLCK", "KC_PSLS", "KC_PAST", "KC_PMNS", "KC_PPLS",
        "KC_PDOT", "KC_PEQL", "KC_PENT", "KC_PCMM",
        "KC_P1", "KC_P2", "KC_P3", "KC_P4", "KC_P5", "KC_P6",
        "KC_P7", "KC_P8", "KC_P9", "KC_P0",
        "BL_TOGG", "BL_DEC", "BL_INC", "BL_STEP",
        "RGB_TOG", "RGB_MOD", "RGB_HUI", "RGB_HUD", "RGB_SAI",
        "RGB_SAD",  "RGB_VAI", "RGB_VAD",
        "KC_MS_U", "KC_MS_D", "KC_MS_L", "KC_MS_R", 
        "KC_BTN1", "KC_BTN2", "KC_BTN3", "KC_BTN4", "KC_BTN5",
        "KC_WH_U", "KC_WH_D", "KC_WH_L", "KC_WH_R", 
        "KC_ACL0", "KC_ACL1", "KC_ACL2",
    ]

    kbf_func = [

        "LCTL(", "LSFT(", "LALT(", "LGUI(", "RTL(", "RSFT(",
        "RALT(", "RGUI(", "HYPR(", "MEH(", "LCAG(", "ALTG(", 
        "LT(", "TO(", "MO(", "DF(", "TG(", "OSL(", "OSM(", 
        "MT(", "CTL_T(", "SFT_T(", "ALT_T(", "GUI_T(", 
        "C_S_T(", "MEH_T(", "LCAG_T(", "ALL_T(", "M("
    ]

    kbf_transcode = {

        "S(":"LSFT(", "RCMD(":"RGUI(", "RWIN(":"RGUI(", "LCTL_T(":"CTL_T(", "RCTL_T(":"CTL_T(", "LSFT_T(":"SFT_T(",
        "RSFT_T(":"SFT_T(", "LALT_T(":"ALT_T(", "RALT_T(":"ALT_T(", "LGUI_T(":"GUI_T(", "LCMD_T(":"GUI_T(",
        "LWIN_T(":"GUI_T(", "RGUI_T(":"GUI_T(", "RCMD_T(":"GUI_T(", "RWIN_T(":"GUI_T(", "RCAG_T(":"LCAG_T(",

        "TT(":"MO(", "KC_ENTER":"KC_ENT", "KC_ESCAPE":"KC_ESC", "KC_BSCAPE":"KC_BSPC", "KC_SPACE":"KC_SPC", "KC_MINUS":"KC_MINS",
        "KC_LBRACKET":"KC_LBRC", "KC_RBRACKET":"KC_RBRC", "KC_BSLASH":"KC_BSLS", "KC_NONUS_HASH":"KC_NUHS", "KC_NONUS_BSLASH":"KC_NUBS",
        "KC_INT1":"KC_RO", "KC_INT2":"KC_KANA", "KC_INT3":"KC_JYEN", "KC_INT4":"KC_HENK",  "KC_INT5":"KC_MHEN", "KC_SCOLON":"KC_SCLN",
        "KC_QUOTE":"KC_QUOT", "KC_GRAVE":"KC_GRV", "KC_COMMA":"KC_COMM", "KC_SLASH":"KC_SLSH", "KC_CAPSLOCK":"KC_CAPS", "KC_LCTRL":"KC_LCTL",
        "KC_LSHIFT":"KC_LSFT", "KC_LCMD":"KC_LGUI", "KC_LWIN":"KC_LGUI", "KC_RCTRL":"KC_RCTL", "KC_RSHIFT":"KC_RSFT", "KC_RCMD":"KC_RGUI", 
        "KC_RWIN":"KC_RGUI", "KC_LCAP":"KC_LOCKING_CAPS", "KC_LNUM":"KC_LOCKING_NUM", "KC_LSCR":"KC_LOCKING_SCROLL", "KC_PSCREEN":"KC_PSCR", 
        "KC_SCROLLLOCK":"KC_SLCK", "KC_PAUSE":"KC_PAUS", "KC_INSERT":"KC_INS", "KC_DELETE":"KC_DEL", "KC_DELT":"KC_DEL", "KC_PGDOWN":"KC_PGDN", 
        "KC_RIGHT":"KC_RGHT", 

        "KC_APPLICATION":"KC_APP", "KC_SYSTEM_POWER":"KC_PWR", "KC_SYSTEM_SLEEP":"KC_SLEP", "KC_SYSTEM_WAKE":"KC_WAKE", "KC_CALCULATOR":"KC_CALC", 
        "KC_MY_COMPUTER":"KC_MYCM", "KC_WWW_SEARCH":"KC_WSCH", "KC_WWW_HOME":"KC_WHOM", "KC_WWW_BACK":"KC_WBAK", "KC_WWW_FORWARD":"KC_WFWD", 
        "KC_WWW_STOP":"KC_WSTP", "KC_WWW_REFRESH":"KC_WREF", "KC_WWW_FAVORITES":"KC_WFAV", "KC_AUDIO_MUTE":"KC_MUTE", "KC_AUDIO_VOL_UP":"KC_VOLU", 
        "KC_AUDIO_VOL_DOWN":"KC_VOLD", "KC_MEDIA_NEXT_TRACK":"KC_MNXT", "KC_MEDIA_PREV_TRACK":"KC_MPRV", "KC_MEDIA_STOP":"KC_MSTP", 
        "KC_MEDIA_PLAY_PAUSE":"KC_MPLY", "KC_MEDIA_SELECT":"KC_MSEL", "KC_NUMLOCK":"KC_NLCK", "KC_KP_SLASH":"KC_PSLS", "KC_KP_ASTERISK":"KC_PAST", 
        "KC_KP_MINUS":"KC_PMNS", "KC_KP_PLUS":"KC_PPLS", "KC_KP_ENTER":"KC_PENT", "KC_KP_1":"KC_P1", "KC_KP_2":"KC_P2", "KC_KP_3":"KC_P3", 
        "KC_KP_4":"KC_P4", "KC_KP_5":"KC_P5", "KC_KP_6":"KC_P6", "KC_KP_7":"KC_P7", "KC_KP_8":"KC_P8", "KC_KP_9":"KC_P9", "KC_KP_0":"KC_P0", 
        "KC_KP_DOT":"KC_PDOT", "KC_KP_EQUAL":"KC_PEQL", "KC_KP_COMMA":"KC_PCMM", "KC_TRANSPARENT":"KC_TRNS", "_______":"KC_TRNS", "KC_MS_UP":"KC_MS_U", 
        "KC_MS_DOWN":"KC_MS_D", "KC_MS_LEFT":"KC_MS_L", "KC_MS_RIGHT":"KC_MS_R", "KC_MS_BTN1":"KC_BTN1", "KC_MS_BTN2":"KC_BTN2", "KC_MS_BTN3":"KC_BTN3", 
        "KC_MS_BTN4":"KC_BTN4", "KC_MS_BTN5":"KC_BTN5", "KC_MS_WH_UP":"KC_WH_U", "KC_MS_WH_DOWN":"KC_WH_D", "KC_MS_WH_LEFT":"KC_WH_L", 
        "KC_MS_WH_RIGHT":"KC_WH_R", "KC_MS_ACCEL0":"KC_ACL0", "KC_MS_ACCEL1":"KC_ACL1", "KC_MS_ACCEL2":"KC_ACL2", "RGB_MODE_FORWARD":"RGB_MOD", 
        "KC_TILDE":"KC_TILD", "KC_EXCLAIM":"KC_EXLM", "KC_DOLLAR":"KC_DLR", "KC_PERCENT":"KC_PERC", "KC_CIRCUMFLEX":"KC_CIRC", "KC_AMPERSAND":"KC_AMPR", 
        "KC_ASTERISK":"KC_ASTR", "KC_LEFT_PAREN":"KC_LPRN", "KC_RIGHT_PAREN":"KC_RPRN", "KC_UNDERSCORE":"KC_UNDS", "KC_LEFT_CURLY_BRACE":"KC_LCBR", 
        "KC_RIGHT_CURLY_BRACE":"KC_RCBR", "KC_COLON":"KC_COLN", "KC_DOUBLE_QUOTE":"KC_DQUO",  "KC_DQT":"KC_DQUO", "KC_LEFT_ANGLE_BRACKET":"KC_LABK", 
        "KC_LT":"KC_LABK", "KC_RIGHT_ANGLE_BRACKET":"KC_RABK", "KC_QUESTION":"KC_QUES"
    }

    keyplus_yaml_template = string.Template('''
# Generated by Q2K Keymap parser by 2Cas (c) 2018
# https://github.com/2Cas/Q2K
# This file is released into the public domain as per the CC0 Public Domain
# Dedication (http://creativecommons.org/publicdomain/zero/1.0/)
---
$ERRORS

report_mode : auto_nkro # options: auto_nkro, 6kro, nkro

devices :
  $KB_NAME:
    id: 0
    layout: $LAYOUT_NAME
    layout_offset: 0
    scan_mode:
      mode: $DIODES # options:  col_row, row_col, pins, none
      rows: $ROWS
      cols: $COLS
      # Maps how keys are physically wired, to how they appear visually
      matrix_map: [
        $MATRIX_MAP
      ]
      # Debounce settings
      debounce:
         debounce_time_press: 5
         debounce_time_release: 5
         trigger_time_press: 1
         trigger_time_release: 1
         parasitic_discharge_delay_idle: 10.0
         parasitic_discharge_delay_debouncing: 10.0

$KEYCODES
layouts:
  $LAYOUT_NAME:
    default_layer: 0
    layers: [
$LAYOUT    ]
''')

    keyplus_yaml_keycode_template = string.Template('''
  $KEYCODE:
    keycode: hold
    delay: 200
    tap_key: $TAP
    hold_key: $HOLD
''')
