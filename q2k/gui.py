import q2k.core as core
import os
import platform
import sys
import threading
import traceback

from tkinter import filedialog, Tk, E, W, LEFT, CENTER, INSERT, NORMAL, ttk, Menu, Text, scrolledtext, messagebox, Button, Entry, StringVar, LabelFrame, Label, Frame
from tkinter.ttk import Combobox

import yaml

class ConsoleText(Text):
    """A Tkinter Text widget that provides a scrolling display of console
    stderr and stdout."""

    class IORedirector(object):
        """A general class for redirecting I/O to this Text gcwidget."""
        def __init__(self,text_area):
            self.text_area = text_area

    class StdoutRedirector(IORedirector):
        """A class for redirecting stdout to this Text widget."""
        def write(self,str):
            self.text_area.write(str,False)

    class StderrRedirector(IORedirector):
        """A class for redirecting stderr to this Text widget."""
        def write(self,str):
            self.text_area.write(str,True)

    def __init__(self, master=None, cnf={}, **kw):
        self.__debug = False
        """See the __init__ for Tkinter.Text for most of this stuff."""

        Text.__init__(self, master, cnf, **kw)

        self.started = False
        self.write_lock = threading.Lock()

        self.tag_configure('STDOUT',background='black',foreground='white')
        self.tag_configure('STDERR',background='black',foreground='red')

        self.config(state=NORMAL)
        self.bind('<Key>',lambda e: 'break') #ignore all key presses

    def start(self):

        if self.started:
            return

        self.started = True

        
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr

        stdout_redirector    = ConsoleText.StdoutRedirector(self)
        stderr_redirector    = ConsoleText.StderrRedirector(self)
        if not self.__debug:
            sys.stdout       = stdout_redirector
            sys.stderr       = stderr_redirector

    def stop(self):

        if not self.started:
            return

        self.started = False
        if not self.__debug:
            sys.stdout = self.original_stdout
            sys.stderr = self.original_stderr

    def write(self,val,is_stderr=False):

        self.write_lock.acquire()

        self.insert('end',val,'STDERR' if is_stderr else 'STDOUT')
        self.see('end')

        self.write_lock.release()

class Window():

    def __init__(self):
       # =============================================================================================================       
        # init Q2K tkinter GUI
       # =============================================================================================================
        self.init_q2k_gui()  
       # =============================================================================================================
        # Load Core Q2K
       # =============================================================================================================
        self.output.start() # Ensure output from loading q2k gets printed to console
        self.q2k_app = core.Q2KApp('keyplus', is_gui=True)
        self.output.stop() # Stop output printing
       # =============================================================================================================
        # Set dynamic lists and enter main loop
       # =============================================================================================================
        self.set_lists()
        self.window.mainloop()

    def init_q2k_gui(self):
        self.window = Tk()
        self.window.resizable(width=False, height=False)
        self.window.title("Q2K Keymap Utility")
        if platform.system()   == 'Linux':
            self.window.option_add('*font', ('Liberation Sans', '-12'))
            self.window.geometry('490x700')
        if platform.system() == 'Windows':
            self.window.option_add('*font', ('Calibri', '-13'))
            self.window.geometry('496x700')

        menu     = Menu(self.window)
        new_item = Menu(menu, tearoff=0)
        #new_item.add_command(label='Settings')
        #menu.add_cascade(label='File', menu=new_item)
        menu.add_command(label='About',command=self.show_about)
        self.window.config(menu=menu)

       # =============================================================================================================
        # Tabs
       # =============================================================================================================

        tab_control = ttk.Notebook(self.window)
        tab1        = ttk.Frame(tab_control)
        #tab2       = ttk.Frame(tab_control)
        tab_control.add(tab1, text='Keyplus')
        #tab_control.add(tab2, text='KBfirmware')
       # =============================================================================================================
        # KEYPLUS TAB
       # =============================================================================================================
        #   Frame 1 - Combo Boxes
       # =============================================================================================================
        # Label
        keyplus_lbl = Label(tab1, text= 'Convert to Keyplus YAML')
        keyplus_lbl.grid(column=0, row=0, sticky=W+E)
        # Settings
        top_frame = LabelFrame(tab1, text='', bd=0, padx=15, pady=2)
        top_frame.grid(sticky=W+E)

       # =============================================================================================================
        #       QMK Firmware Directory Entry
       # =============================================================================================================
        # Label
        qmk_lbl           = Label(top_frame, text='QMK Firmware Directory')
        # Text Box
        self.qmk_dir      = StringVar()
        qmk_dir_entry      = Entry(top_frame, textvariable=self.qmk_dir)
        # Button
        qmk_dir_btn       = Button(top_frame, text="..", command=lambda:self.set_qmk_directory())

       # =============================================================================================================
        #      Keyplus Output Directory Entry
       # =============================================================================================================
        # Label
        keyplus_lbl       = Label(top_frame, text='Output Directory')
        # Text Box
        self.keyplus_dir  = StringVar()
        keyplus_dir_entry = Entry(top_frame, textvariable=self.keyplus_dir)

        # Button
        keyplus_dir_btn   = Button(top_frame, text="..", command=lambda:self.set_keyplus_directory())

        # Settings / Positioning
        qmk_lbl.grid          (row=0, column=0,   sticky=W)
        keyplus_lbl.grid      (row=2, column=0,   sticky=W)

        qmk_dir_entry.grid     (row=1, column=0, sticky=W+E)
        qmk_dir_btn.grid      (row=1, column=1)
        keyplus_dir_entry.grid(row=3, column=0, sticky=W+E)
        keyplus_dir_btn.grid  (row=3, column=1)

        if platform.system()   == 'Linux':
            qmk_dir_entry['width']     = 59
            qmk_dir_btn['width']       = 2
            keyplus_dir_entry['width'] = 59
            keyplus_dir_btn['width']   = 2
        if platform.system() == 'Windows':
            qmk_dir_entry['width']     = 60
            qmk_dir_btn['width']       = 4
            keyplus_dir_entry['width'] = 60
            keyplus_dir_btn['width']   = 4
       # =============================================================================================================
        #   Frame 2 - Combo Boxes
       # =============================================================================================================
        kb_opts = LabelFrame(tab1, text='', bd=0, padx=15, pady=5, height=50)
        kb_opts.grid(sticky=E+W)
       # =============================================================================================================
        #       Dynamic Combo Boxes
        #          | Keyboard               |  Rev                 |  
        #          | Keymap                 |  Template            | 
       # =============================================================================================================
        # Labels
        kb_lbl       = Label(kb_opts, text='Keyboard')
        rev_lbl      = Label(kb_opts, text='Rev')
        keymap_lbl   = Label(kb_opts, text='Keymap')
        template_lbl = Label(kb_opts, text='Template')

        # Combo Boxes
        self.template = Combobox(kb_opts, state='readonly')
        self.keymap   = Combobox(kb_opts, state='readonly')
        self.rev      = Combobox(kb_opts, state='readonly')
        self.kb       = Combobox(kb_opts, state='readonly')

        if platform.system()   == 'Linux':
            self.template['width'] = 30
            self.keymap['width']   = 30
            self.rev['width']      = 30
            self.kb['width']       = 30

        elif platform.system() == 'Windows':
            self.template['width'] = 30
            self.keymap['width']   = 30
            self.rev['width']      = 30
            self.kb['width']       = 30

        self.rev.bind('<<ComboboxSelected>>', self.event_rev_selected) # Updating list triggers event rev_select
        self.kb.bind( '<<ComboboxSelected>>', self.event_kb_selected)   # Updating list triggers event kb_select

        # Settings / Positioning
        self.kb.grid       (row=1, column=0)
        self.rev.grid      (row=1, column=1)
        self.keymap.grid   (row=3, column=0)
        self.template.grid (row=3, column=1)

        kb_lbl.grid        (row=0, column=0, sticky=W)
        rev_lbl.grid       (row=0, column=1, sticky=W)
        keymap_lbl.grid    (row=2, column=0, sticky=W)
        template_lbl.grid  (row=2, column=1, sticky=W)
       # =============================================================================================================
        # Frame 3 - Buttons 
       # =============================================================================================================
        kb_opts2 = LabelFrame(tab1, text='', bd=0, padx=15, pady=5, height=50, width=100)
        kb_opts2.grid(sticky=E+W)
       # =============================================================================================================
        #     Buttons:  | Convert | Generate Keyboard List | Reset |
       # =============================================================================================================

        convert_btn = Button(kb_opts2, width='10', text='Convert', command=lambda:self.btn_execute())
        gen_btn     = Button(kb_opts2, width='20', text='Generate Keyboard List', command=lambda:self.btn_generate_lists())
        reset_btn   = Button(kb_opts2, width='10', text='Reset', command=lambda:self.btn_reset())

        convert_btn.grid(row=0, column=0, sticky=W+E)
        gen_btn.grid    (row=0, column=1, padx=5, sticky=W+E)
        reset_btn.grid  (row=0, column=2, sticky=W+E)

        if platform.system()   == 'Linux':
            convert_btn['width']     = 16
            gen_btn['width']         = 20
            reset_btn['width']       = 16
        if platform.system() == 'Windows':
            convert_btn['width']     = 20
            gen_btn['width']         = 20
            reset_btn['width']       = 20
       # =============================================================================================================
        # Frame 4 - Output 
       # =============================================================================================================
        console = LabelFrame(tab1, text='', bd=0, padx=15, pady=5, height=50)
        console.grid(sticky=W+E)
       # =============================================================================================================
        #   Console
       # =============================================================================================================
        # Label
        con_lbl = Label(console, text='Console')
        con_lbl.grid(padx=5, row=0, column=0)
        # Text Box
        self.output = ConsoleText(console, bd=0, bg='black', fg='white')
        if platform.system()   == 'Linux':
            self.output['height'] = 35
            self.output['width']  = 75
            self.output['font']   = ('Consolas', '9')
        elif platform.system() == 'Windows':
            self.output['height'] = 27
            self.output['width']  = 65
            self.output['font']   = ('Consolas', '9')

        self.output.grid(padx=5, row=1, column=0, sticky=W+E)

        # KBfirmware
        '''
        lbl2 = Label(tab2, text= 'Convert to KBfirmware JSON')
        lbl2.grid(column=0, row=0)

        frame1_qmk_dir = LabelFrame(tab2, text='  QMK Firmware Dir:  ', bd=0, padx=15, pady=2)
        frame1_qmk_dir.grid(sticky=E+W)

        qmkdir_entry = Entry(frame1_qmk_dir, textvariable=qmkdir, width=32)
        qmkdir_entry.grid(column=0, row=0, sticky=E+W)
        dir_btn = Button(frame1_qmk_dir, text="..", command=lambda:find_directory(qmkdir))
        dir_btn.grid(column=1, row=0)

        frame2_kbf_dir = LabelFrame(tab2, text='  Output Dir:  ', bd=0, padx=15, pady=2)
        frame2_kbf_dir.grid(sticky=E+W)

        kbfdir = StringVar()
        kbfdir_entry = Entry(frame2_kbf_dir, textvariable=kbfdir, width=32)
        kbfdir_entry.grid(column=0, row=0, sticky=E+W)
        dir_btn = Button(frame2_kbf_dir, text="..", command=lambda:find_directory(kbfdir))
        dir_btn.grid(column=1, row=0)
        '''

        #tab_control.pack(expand=1, fill='both')
        tab_control.grid()

    def set_lists(self):
        self.qmk_dir.set(self.q2k_app.dirs['QMK dir'])
        self.keyplus_dir.set(self.q2k_app.dirs['Keyplus YAML output'])

        kb_list = self.q2k_app.keyboard_list()
        kb_list.sort()

        self.kb['values'] = kb_list

    def save_pref(self):
        pref_yaml = os.path.join(core.Defaults.SRC, 'pref.yaml')
        with open(pref_yaml, 'w') as f:
            f.write('# Q2K Folder Locations\n')
            yaml.dump(self.q2k_app.dirs, f, default_flow_style = False)

    def set_qmk_directory(self):
        dir_select = os.path.normpath( filedialog.askdirectory() )
        self.qmk_dir.set(dir_select)
        self.q2k_app.dirs['QMK dir'] = dir_select
        self.save_pref()

    def set_keyplus_directory(self):
        dir_select = os.path.normpath( filedialog.askdirectory() )
        self.keyplus_dir.set(dir_select)
        self.q2k_app.dirs['Keyplus YAML output'] = dir_select
        self.save_pref()

    def show_about(self):
        messagebox.showinfo('About', 'Q2K Keymap Utility\nv '+core.Defaults.VERSION)

    def btn_generate_lists(self):
        self.output.start()

        # Get dirs from StringVars
        self.q2k_app.dirs['QMK dir'] = self.qmk_dir.get()
        self.q2k_app.dirs['Keyplus YAML output'] = self.keyplus_dir.get()
        # Save to pref.yaml
        self.save_pref()
        #self.q2k_app.refresh_dir()
        self.q2k_app.refresh_cache()

        # Get KB list, sort and set combobox to this list.
        kb_list = self.q2k_app.keyboard_list()
        kb_list.sort()
        self.kb['values'] = kb_list

        # Reset other combo boxes
        self.rev['values'] = []
        self.keymap['values'] = []
        self.template['values'] = []

        # Reset comboboxes to blank
        self.kb.set('')
        self.rev.set('')
        self.keymap.set('')
        self.template.set('')

        self.output.stop()

    def btn_reset(self):
        self.output.start()

        # Reset Q2K App to defaults
        self.q2k_app.reset()
        # Set fields to defaults
        self.qmk_dir.set(core.Defaults.QMK)
        self.keyplus_dir.set(core.Defaults.KEYP)
        # Set all combo boxes to blank
        self.kb.set('')
        self.rev.set('')
        self.keymap.set('')
        self.template.set('')

        # Get KB list, sort and set combobox to this list.
        kb_list = self.q2k_app.keyboard_list()
        kb_list.sort()
        self.kb['values'] = kb_list

        # Reset other combo boxes
        self.rev['values'] = []
        self.keymap['values'] = []
        self.template['values'] = []

        # Reset comboboxes to blank
        self.kb.set('')
        self.rev.set('')
        self.keymap.set('')
        self.template.set('')

        self.output.stop()

    def btn_execute(self):
        kb_n   = self.kb.get()
        rev_n  = self.rev.get()
        km_n   = self.keymap.get()
        temp_n = self.template.get()

        try:
            self.output.start()
            self.q2k_app.set_kb(keyboard=kb_n, rev=rev_n, keymap=km_n, template=temp_n)
            self.q2k_app.execute()
            self.output.stop()

        except RuntimeError as e:
            #print(traceback.format_exc(), file=sys.stderr)
            print(str(e), file=sys.stderr)
            self.output.stop()

        except RuntimeWarning as e:
            print(str(e), file=sys.stderr)
            self.output.stop()

    def event_rev_selected(self, event=None):

        keymap_list   = self.q2k_app.keymap_list(self.kb.get(), self.rev.get())
        template_list = self.q2k_app.template_list(self.kb.get(), self.rev.get())
        if keymap_list:
            keymap_list.sort()

        self.keymap['values']   = keymap_list
        self.template['values'] = template_list
        if keymap_list and 'default' in keymap_list:
            self.keymap.set('default')
        else:
            self.keymap.set('')
        if template_list:
            self.template.set(template_list[0])
        else:
            self.template.set('')

    def event_kb_selected(self, event):

        rev_list = self.q2k_app.rev_list(self.kb.get())
        rev_list.sort(reverse=True)

        if rev_list:

            self.rev.set(rev_list[0])
            self.rev['values']= rev_list
            self.event_rev_selected()

        else:

            keymap_list   = self.q2k_app.keymap_list(self.kb.get())
            template_list = self.q2k_app.template_list(self.kb.get())
            if keymap_list:
                keymap_list.sort()

            self.rev['values']      = rev_list
            self.keymap['values']   = keymap_list
            self.template['values'] = template_list


            self.rev.set('')
            if keymap_list and 'default' in keymap_list:
                self.keymap.set('default')
            else:
                self.keymap.set('')
            if template_list:
                self.template.set(template_list[0])
            else:
                self.template.set('')

def main():
    window = Window()
