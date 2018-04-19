import q2k.core
import sys
import yaml
from tkinter import filedialog
from tkinter import Tk, E, W, LEFT, INSERT, ttk, Menu, Text, scrolledtext, messagebox, Button, Entry, StringVar, LabelFrame, Label, Frame
from tkinter.ttk import Combobox

import sys

class Window():

    def __init__(self):
        self.q2k_app = q2k.core.application('keyplus', is_gui=True)
        self.dirs = self.q2k_app.dirs
        self.q2k_gui()


    def q2k_gui(self):
        window = Tk()
        #window.option_add('*Dialog.msg.font', 'Helvetica 12')
        window.resizable(width=False, height=False)
        window.option_add('*font', 'Arial -12')
        window.title("Q2K Keymap Utility")
        window.geometry('380x280')

        menu = Menu(window)
        new_item = Menu(menu, tearoff=0)
        #new_item.add_command(label='Settings')
        #menu.add_cascade(label='File', menu=new_item)
        menu.add_command(label='About',command=self.show_about)
        window.config(menu=menu)

        tab_control = ttk.Notebook(window)

        tab1 = ttk.Frame(tab_control)
        #tab2 = ttk.Frame(tab_control)
        tab_control.add(tab1, text='Keyplus')
        #tab_control.add(tab2, text='KBfirmware')

        # Keyplus
        keyplus_lbl = Label(tab1, text= 'Convert to Keyplus YAML')
        keyplus_lbl.grid(column=0, row=0)

        top_frame = LabelFrame(tab1, text='', bd=0, padx=15, pady=2)
        top_frame.grid(sticky=W+E)

        qmk_lbl = Label(top_frame, text='QMK Firmware Directory:')
        qmk_lbl.grid(column=0, row=0, sticky=W)

        self.qmk_dir = StringVar()
        self.qmk_dir.set(self.dirs['QMK dir'])
        qmk_dir = self.qmk_dir
        qmkdir_entry = Entry(top_frame, textvariable=qmk_dir, width=44)
        qmkdir_entry.grid(column=0, row=1, sticky=W+E)
        btn = Button(top_frame, text="..", command=lambda:self.find_directory(qmk_dir))
        btn.grid(column=1, row=1)

        keyplus_lbl = Label(top_frame, text='Output Directory:')
        keyplus_lbl.grid(column=0, row=2, sticky=W)

        self.keyplus_dir = StringVar()
        self.keyplus_dir.set(self.dirs['Keyplus YAML output'])
        keyplus_dir = self.keyplus_dir
        keyplus_dir_entry = Entry(top_frame, textvariable=keyplus_dir, width=44)
        keyplus_dir_entry.grid(column=0, row=3, sticky=W+E)
        btn = Button(top_frame, text="..", command=lambda:self.find_directory(keyplus_dir))
        btn.grid(column=1, row=3)

        kb_opts = LabelFrame(tab1, text='', bd=0, padx=15, pady=5, height=50)
        kb_opts.grid(sticky=E+W)

        kb_list = self.q2k_app.keyboard_list()
        kb_list.sort()

        self.template = Combobox(kb_opts, width=22, state='readonly')
        self.keymap = Combobox(kb_opts, width=22, state='readonly')
        self.rev = Combobox(kb_opts, width=22, state='readonly')
        self.rev.bind('<<ComboboxSelected>>', self.event_rev_selected)
        self.kb = Combobox(kb_opts, width=22,  values = kb_list, state='readonly')
        self.kb.bind('<<ComboboxSelected>>', self.event_kb_selected)
       
        kb_lbl = Label(kb_opts, text='Keyboard:')
        rev_lbl = Label(kb_opts, text='Rev:')
        keymap_lbl = Label(kb_opts, text='Keymap:')
        template_lbl = Label(kb_opts, text='Template:')

        kb_lbl.grid(sticky='w',column=0, row=0)
        rev_lbl.grid(sticky='w',column=1, row=0)
        keymap_lbl.grid(sticky='w',column=0, row=2)
        template_lbl.grid(sticky='w',column=1, row=2)
        self.kb.grid(column=0,row=1)
        self.rev.grid(column=1,row=1)
        self.keymap.grid(column=0,row=3)
        self.template.grid(column=1,row=3)

        kb_opts2 = LabelFrame(tab1, text='', bd=0, padx=15, pady=5, height=50, width=100)
        kb_opts2.grid(sticky=E+W)

        btn = Button(kb_opts2, text='Generate Keyboard List', command=lambda:self.btn_generate_lists())
        btn.grid(row=0, column=0)
        btn = Button(kb_opts2, text='Reset', command=lambda:self.btn_reset())
        btn.grid(padx = 5, row=0, column=1)
        btn = Button(kb_opts2, text='Convert', command=lambda:self.btn_execute())
        btn.grid(row=0, column=2)

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

        tab_control.pack(expand=1, fill='both')

        window.mainloop()

    def find_directory(self, string):
        folder_selected = filedialog.askdirectory()
        string.set(folder_selected+'/')

    def show_about(self):
        messagebox.showinfo('About', 'Q2K Keymap Utility\nv 1.0.0a1')

    def btn_generate_lists(self):

        self.dirs['QMK dir'] = self.qmk_dir.get()
        self.dirs['Keyplus YAML output'] = self.keyplus_dir.get()

        with open(q2k.core.defaults.src+'pref.yaml', 'w') as f:
            f.write('# Q2K Folder Locations\n')
            yaml.dump(self.dirs, f, default_flow_style = False)

        self.q2k_app.refresh_dir()
        self.q2k_app.refresh_cache()
        kb_list = self.q2k_app.keyboard_list()
        kb_list.sort()
        self.kb['values'] = kb_list
        self.kb.set('')
        self.rev.set('')
        self.keymap.set('')
        self.template.set('')

    def btn_reset(self):
        self.q2k_app.reset_dir_defaults()
        self.q2k_app.clear_cache()
        self.qmk_dir.set(q2k.core.defaults.qmk)
        self.keyplus_dir.set(q2k.core.defaults.keyp)
        self.kb.set('')
        self.rev.set('')
        self.keymap.set('')
        self.template.set('')

    def btn_execute(self):
        kb_n = self.kb.get()
        rev_n = self.rev.get()
        km_n = self.keymap.get()
        temp_n = self.template.get()

        self.q2k_app.set_kb(keyboard=kb_n, rev=rev_n, keymap=km_n, template=temp_n)
        self.q2k_app.execute()

    def event_rev_selected(self, event):

        keymap_list = self.q2k_app.keymap_list(self.kb.get(), self.rev.get())
        template_list = self.q2k_app.template_list(self.kb.get(), self.rev.get())
        if keymap_list:
            keymap_list.sort()

        self.keymap['values'] = keymap_list
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
        keymap_list = self.q2k_app.keymap_list(self.kb.get())
        template_list = self.q2k_app.template_list(self.kb.get())
        if keymap_list:
            keymap_list.sort()

        self.rev['values']= rev_list
        self.keymap['values'] = keymap_list
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
