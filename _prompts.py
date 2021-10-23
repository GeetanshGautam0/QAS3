from _appfunctions import *
import conf, re, theme, os, sys, shutil, random, json, colors
import tkinter as tk
from tkinter import ttk as ttk
from shared_memory_dict import SharedMemoryDict
from threading import Thread
from tkinter import messagebox as tkmsb


TMODE = theme.TMODE 
prconf = protected_conf

if prconf.dsb_mod_run_stdnalone and __name__ == "__main__":
    sys.exit("cannot run module standalone.")

v = "!~0010.00101.-3"

if v != pr_conf.r_prompts_version_id:
    raise Exception("Failed to init _prompts.py; invalid script version.")

with open("low.json", 'r') as file:
    _l_json = json.loads(file.read())
    file.close()


def _update_sc_bar(bar, canvas, root):
    canvas.yview_scroll(1, "units")
    root.update()
    canvas.update()
    bar.update()

    canvas.yview_scroll(-1, "units")
    root.update()
    canvas.update()
    bar.update()


class _Basic:
    class OnStart:
        @staticmethod
        def init():
            global TMODE
            TMODE = theme.find_preference()


class SMem:
    def __init__(self):
        self.r1 = random.randint(100, 999)
        self.r2 = random.randint(100, 999)
        self.r3 = random.randint(100, 999)
        self.r4 = random.randint(100, 999)
        self.r5 = int(random.randint(10000, 99999) * (random.random() * (10 ** 3)))

    def get(self):
        _addr = "%s%s%s%s" % (self.r4, self.r3, self.r1, self.r2)
        _k = str(self.r5)

        _s = SharedMemoryDict(name=_addr, size=SMem._pro_000_s_mem_addr_0_size())
        return _s.get(_k)

    @staticmethod
    def _pro_000_s_mem_addr_0_size():
        return 2048


class TextPrompts:
    class BasicTextPrompt:
        def __init__(self, data, use_tk=False, button_text="Okay", degree='Notice',
                     title=conf.AppContainer.general_title, accent_key='accent', contrast_key=-1):
            global TMODE
            TMODE = theme.TMODE

            # self.thread = Thread
            # self.thread.__init__(self)

            if use_tk:
                self.root = tk.Tk()
            else:
                self.root = tk.Toplevel()

            self.root.withdraw()

            self.title_lbl = tk.Label(self.root)
            self.data = data
            self.data_canvas = tk.Canvas(self.root)
            self.data_section = tk.Frame(self.data_canvas)
            self.data_label = tk.Label(self.data_section)
            self.data_section_v_scbar = ttk.Scrollbar(self.root)
            self.degree = degree
            self.button_text = button_text
            self.title = title
            self.ok_button = tk.Button(self.root)
            self.accent_key = accent_key
            self.contrast_key = contrast_key

            def_ws = conf.AppContainer.Prompts.def_ws
            self.ss = (self.root.winfo_screenwidth(), self.root.winfo_screenheight())
            self.ws = (
                def_ws[0] if def_ws[0] <= self.ss[0] else self.ss[0],
                def_ws[1] if def_ws[1] <= self.ss[1] else self.ss[1]
            )
            self.wp = (
                self.ss[0] // 2 - self.ws[0] // 2,
                self.ss[1] // 2 - self.ws[1] // 2
            )

            self.theme = {}
            self.theme_mode = TMODE

            # self.start()
            self.run()
            self.root.deiconify()
            self.root.wm_attributes('-topmost', 1)
            self.root.mainloop()

        def __on_window_close__(self):
            self.ok_button.config(state=tk.DISABLED)
            self.root.title("CMF - BasicTextPrompt - Closed - Waiting for main app to close")
            # self.root.after(0, self.root.destroy)
            self.root.withdraw()
            self.root.quit()
            # self.thread.join(self, 0)

        def __okay(self):
            self.__on_window_close__()

        def run(self):
            _Basic.OnStart.init()

            if self.theme_mode == 'd':
                self.theme = theme.Theme.UserPref.dark_mode()
            else:
                self.theme = theme.Theme.UserPref.light_mode()

            if self.contrast_key == -1:
                # Calculated
                _m = {
                    self.theme['fg']: 'fg',
                    self.theme['bg']: 'bg'
                }

                _res = colors.Functions.calculate_nearer(*_m.keys(), self.theme[self.accent_key])
                self.contrast_key = _m[_res]

            self.root.geometry(
                "%sx%s+%s+%s" % (self.ws[0], self.ws[1], self.wp[0], self.wp[1])
            )
            self.root.title(self.title)
            self.root.protocol("WM_DELETE_WINDOW", self.__on_window_close__)
            self.root.config(
                bg=self.theme['bg']
            )
            self.root.lift()

            ttktheme = 'alt'

            # Data Label
            self.data_label.config(
                text=self.data,
                wraplength=self.ws[0] - 3.5 * self.theme['padding']['x'],
                fg=self.theme['fg'],
                bg=self.theme['bg'],
                font=(self.theme['font']['font_face'], self.theme['font']['main_size']),
                anchor=tk.W,
                justify=tk.LEFT
            )
            self.data_label.pack(
                fill=tk.BOTH,
                expand=True
            )

            # Title Label
            self.title_lbl.config(
                text=self.degree,
                wraplength=self.ws[0] - 2 * self.theme['padding']['x'],
                fg=self.theme[self.accent_key],
                bg=self.theme['bg'],
                font=(self.theme['font']['font_face'], self.theme['font']['title_size'])
            )

            self.title_lbl.pack(
                fill=tk.BOTH,
                expand=False,
                padx=self.theme['padding']['x'],
                pady=self.theme['padding']['y'] * 1.5
            )

            # OK Button
            self.ok_button.config(
                text=self.button_text,
                fg=self.theme[self.contrast_key],
                bg=self.theme[self.accent_key],
                activebackground=self.theme[self.contrast_key],
                activeforeground=self.theme[self.accent_key],
                command=self.__okay,
                font=(self.theme['font']['font_face'], self.theme['font']['big_para_size']),
                bd=0
            )

            self.ok_button.pack(
                fill=tk.BOTH,
                expand=False,
                padx=self.theme['padding']['x'],
                pady=self.theme['padding']['y'],
                ipadx=self.theme['padding']['x'] // 2,
                ipady=self.theme['padding']['y'] // 2,
                side=tk.BOTTOM
            )

            # SCBar + Data Section
            self.data_canvas.config(
                bg=self.theme['bg'],
                bd='0',
                highlightthickness=0
            )

            self.data_section_v_scbar.pack(
                fill=tk.Y,
                expand=False,
                padx=(self.theme['padding']['x'], 0),
                pady=self.theme['padding']['y'],
                side=tk.LEFT
            )

            self.data_canvas.pack(
                fill=tk.BOTH,
                expand=True,
                padx=(0, self.theme['padding']['x']),
                pady=self.theme['padding']['y'],
                side=tk.RIGHT
            )

            self.data_section.config(bd=0)

            # SCBar Conifg

            sStyle = ttk.Style()
            sStyle.theme_use(ttktheme)

            # The absolute legend that created the following code for MyTScrollbar.trough
            # can be found at:
            # https://stackoverflow.com/questions/28375591/changing-the-appearance-of-a-scrollbar-in-tkinter-using-ttk-styles
            if 'My.Scrollbar.trough' not in sStyle.element_names():
                sStyle.element_create("My.Scrollbar.trough", "from", ttktheme)

            sStyle.layout("My.TScrollbar",
                          [('My.Scrollbar.trough', {'children':
                              [
                                  ('Vertical.Scrollbar.uparrow', {'side': 'top', 'sticky': ''}),
                                  ('Vertical.Scrollbar.downarrow', {'side': 'bottom', 'sticky': ''}),
                                  ('Vertical.Scrollbar.thumb', {'unit': '1', 'children':
                                      [('Vertical.Scrollbar.grip', {'sticky': ''})], 'sticky': 'nswe'})],
                              'sticky': 'ns'})
                           ])
            sStyle.configure("My.TScrollbar", *sStyle.configure("TScrollbar"))
            sStyle.configure("My.TScrollbar", troughcolor=self.theme['bg'])

            sStyle.configure(
                'My.TScrollbar',
                background=self.theme['bg'],
                arrowcolor=self.theme[self.accent_key]
            )
            sStyle.map(
                "My.TScrollbar",
                background=[
                    ("active", self.theme[self.accent_key]), ('disabled', self.theme['bg'])
                ],
                foreground=[
                    ("active", self.theme[self.accent_key]), ('disabled', self.theme['bg'])
                ],
                arrowcolor=[
                    ('disabled', self.theme['bg'])
                ]
            )

            self.data_section_v_scbar.configure(command=self.data_canvas.yview, style='My.TScrollbar')

            self.data_canvas.configure(
                yscrollcommand=self.data_section_v_scbar.set
            )

            self.data_canvas.create_window(
                (0, 0),
                window=self.data_section,
                anchor="nw",
                tags="self.frame"
            )

            # Event Handlers
            self.data_section.bind("<Configure>", self.__onFrameConfig)
            self.data_section.bind_all("<MouseWheel>", self.__on_mousewheel)

            _update_sc_bar(self.data_section_v_scbar, self.data_canvas, self.root)

        def __onFrameConfig(self, *args):
            self.data_canvas.configure(
                scrollregion=self.data_canvas.bbox("all")
            )

        def __on_mousewheel(self, event):
            """
            Straight out of stackoverflow
            Article: https://stackoverflow.com/questions/17355902/tkinter-binding-mousewheel-to-scrollbar
            Change
            : added "int" around the first arg
            """
            self.data_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def __del__(self):
            # self.thread.join(self, 0)
            pass

    class ErrorPrompt:

        class _ErrRoot:
            def __init__(self, data, use_tk=False, button_text="Okay", degree='ERROR',
                         title=conf.AppContainer.general_title + " - Error", accent_key='error', contrast_key=-1,
                         fatal=False):
                global TMODE
                TMODE = theme.TMODE

                if use_tk:
                    self.root = tk.Tk()
                else:
                    self.root = tk.Toplevel()
                self.root.withdraw()
                self.title_lbl = tk.Label(self.root)
                self.data = data
                self.data_canvas = tk.Canvas(self.root)
                self.data_section = tk.Frame(self.data_canvas)
                self.data_label = tk.Label(self.data_section)
                self.data_section_v_scbar = ttk.Scrollbar(self.root)
                self.degree = degree
                self.button_text = button_text
                self.title = title
                self.ok_button = tk.Button(self.root)
                self.accent_key = accent_key
                self.contrast_key = contrast_key

                def_ws = conf.AppContainer.Prompts.def_ws
                self.ss = (self.root.winfo_screenwidth(), self.root.winfo_screenheight())
                self.ws = (
                    def_ws[0] if def_ws[0] <= self.ss[0] else self.ss[0],
                    def_ws[1] if def_ws[1] <= self.ss[1] else self.ss[1]
                )
                self.wp = (
                    self.ss[0] // 2 - self.ws[0] // 2,
                    self.ss[1] // 2 - self.ws[1] // 2
                )

                self.theme = {}
                self.theme_mode = TMODE

                self.fatal = fatal

                self.run()
                self.root.deiconify()
                self.root.wm_attributes('-topmost', 1)
                self.root.mainloop()

            def __on_window_close__(self):
                if self.fatal:
                    sys.exit(1)

                else:
                    self.ok_button.config(state=tk.DISABLED)
                    self.root.title("CMF - BasicTextPrompt - Closed - Waiting for main app to close")
                    self.root.withdraw()
                    self.root.quit()

            def run(self):
                _Basic.OnStart.init()

                if self.theme_mode == 'd':
                    self.theme = theme.Theme.UserPref.dark_mode()
                else:
                    self.theme = theme.Theme.UserPref.light_mode()

                if self.contrast_key == -1:
                    _m = {
                        self.theme['fg']: 'fg',
                        self.theme['bg']: 'bg'
                    }

                    _res = colors.Functions.calculate_nearer(*_m.keys(), self.theme[self.accent_key])
                    self.contrast_key = _m[_res]

                self.root.geometry(
                    "%sx%s+%s+%s" % (self.ws[0], self.ws[1], self.wp[0], self.wp[1])
                )
                self.root.title(self.title)
                self.root.protocol("WM_DELETE_WINDOW", self.__on_window_close__)
                self.root.config(
                    bg=self.theme['bg']
                )
                self.root.lift()

                ttktheme = 'alt'

                # Data Label
                self.data_label.config(
                    text=self.data,
                    wraplength=self.ws[0] - 3.5 * self.theme['padding']['x'],
                    fg=self.theme['fg'],
                    bg=self.theme['bg'],
                    font=(self.theme['font']['font_face'], self.theme['font']['main_size'])
                )
                self.data_label.pack(
                    fill=tk.BOTH,
                    expand=True
                )

                # Title Label
                self.title_lbl.config(
                    text=self.degree,
                    wraplength=self.ws[0] - 2 * self.theme['padding']['x'],
                    fg=self.theme[self.accent_key],
                    bg=self.theme['bg'],
                    font=(self.theme['font']['font_face'], self.theme['font']['title_size'])
                )

                self.title_lbl.pack(
                    fill=tk.BOTH,
                    expand=False,
                    padx=self.theme['padding']['x'],
                    pady=self.theme['padding']['y'] * 1.5
                )

                # OK Button
                self.ok_button.config(
                    text=self.button_text,
                    fg=self.theme[self.contrast_key],
                    bg=self.theme[self.accent_key],
                    activebackground=self.theme[self.contrast_key],
                    activeforeground=self.theme[self.accent_key],
                    command=self.__okay,
                    font=(self.theme['font']['font_face'], self.theme['font']['big_para_size']),
                    bd=0
                )

                self.ok_button.pack(
                    fill=tk.BOTH,
                    expand=False,
                    padx=self.theme['padding']['x'],
                    pady=self.theme['padding']['y'],
                    ipadx=self.theme['padding']['x'] // 2,
                    ipady=self.theme['padding']['y'] // 2,
                    side=tk.BOTTOM
                )

                # SCBar + Data Section
                self.data_canvas.config(
                    bg=self.theme['bg'],
                    bd='0',
                    highlightthickness=0
                )

                self.data_section_v_scbar.pack(
                    fill=tk.Y,
                    expand=False,
                    padx=(self.theme['padding']['x'], 0),
                    pady=self.theme['padding']['y'],
                    side=tk.LEFT
                )

                self.data_canvas.pack(
                    fill=tk.BOTH,
                    expand=True,
                    padx=(0, self.theme['padding']['x']),
                    pady=self.theme['padding']['y'],
                    side=tk.RIGHT
                )

                self.data_section.config(bd=0)

                # SCBar Conifg

                sStyle = ttk.Style()
                sStyle.theme_use(ttktheme)

                # The absolute legend that created the following code for MyTScrollbar.trough
                # can be found at:
                # https://stackoverflow.com/questions/28375591/changing-the-appearance-of-a-scrollbar-in-tkinter-using-ttk-styles
                if 'My.Scrollbar.trough' not in sStyle.element_names():
                    sStyle.element_create("My.Scrollbar.trough", "from", ttktheme)

                sStyle.layout("My.TScrollbar",
                              [('My.Scrollbar.trough', {'children':
                                  [
                                      ('Vertical.Scrollbar.uparrow', {'side': 'top', 'sticky': ''}),
                                      ('Vertical.Scrollbar.downarrow', {'side': 'bottom', 'sticky': ''}),
                                      ('Vertical.Scrollbar.thumb', {'unit': '1', 'children':
                                          [('Vertical.Scrollbar.grip', {'sticky': ''})], 'sticky': 'nswe'})],
                                  'sticky': 'ns'})
                               ])
                sStyle.configure("My.TScrollbar", *sStyle.configure("TScrollbar"))
                sStyle.configure("My.TScrollbar", troughcolor=self.theme['bg'])

                sStyle.configure(
                    'My.TScrollbar',
                    background=self.theme['bg'],
                    arrowcolor=self.theme[self.accent_key]
                )
                sStyle.map(
                    "My.TScrollbar",
                    background=[
                        ("active", self.theme[self.accent_key]), ('disabled', self.theme['bg'])
                    ],
                    foreground=[
                        ("active", self.theme[self.accent_key]), ('disabled', self.theme['bg'])
                    ],
                    arrowcolor=[
                        ('disabled', self.theme['bg'])
                    ]
                )

                self.data_section_v_scbar.configure(command=self.data_canvas.yview, style='My.TScrollbar')

                self.data_canvas.configure(
                    yscrollcommand=self.data_section_v_scbar.set
                )

                self.data_canvas.create_window(
                    (0, 0),
                    window=self.data_section,
                    anchor="nw",
                    tags="self.frame"
                )

                # Event Handlers
                self.data_section.bind("<Configure>", self.__onFrameConfig)
                self.data_section.bind_all("<MouseWheel>", self.__on_mousewheel)

                _update_sc_bar(self.data_section_v_scbar, self.data_canvas, self.root)

            def __onFrameConfig(self, *args):
                self.data_canvas.configure(
                    scrollregion=self.data_canvas.bbox("all")
                )

            def __on_mousewheel(self, event):
                """
                Straight out of stackoverflow
                Article: https://stackoverflow.com/questions/17355902/tkinter-binding-mousewheel-to-scrollbar
                Change
                : added "int" around the first arg
                """
                self.data_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

            def __okay(self):
                self.__on_window_close__()

            def __del__(self):
                pass

        @staticmethod
        def Handled(*args, **kwargs):
            TextPrompts.ErrorPrompt._ErrRoot(*args, **kwargs)

        @staticmethod
        def Fatal(*args, **kwargs):
            try:
                cont_ttl = conf.AppContainer.general_title + " - Fatal Error"
                ttl = "Fatal Error"
                btn_txt = "Exit"

                kwargs['button_text'] = btn_txt
                kwargs['degree'] = ttl
                kwargs['title'] = cont_ttl
                kwargs['fatal'] = True

                TextPrompts.ErrorPrompt._ErrRoot(*args, **kwargs)
            except:
                tkmsb.showerror("Quizzing Application - Fatal Error", "The application has encountered a fatal error; terminating.")
                sys.exit(-1)


class InputPrompts:
    class BasicInput:
        def __init__(self, s_mem_addr_inst: SMem, **kwargs):
            global TMODE
            TMODE = theme.TMODE

            # Functional Objects
            # super().__init__()
            # self.thread = Thread
            # self.thread.__init__(self)

            self.smai = s_mem_addr_inst
            self._shared_mem_dict_args = {}
            self._smai_key = ""
            self._create_sm_args()
            fls = {
                "f_title": [conf.AppContainer.general_title + " - Input", True, True],
                "button_text": ["Submit", True, True],
                "description": ["", True, True],
                "title": ["Input", True, True],
                "min_len": [None, int, False, True],
                "regex": [None, str, False, True],
                "strip_inp": [True, True, True],
                "use_tk": [True, True, True],
                "accent_key": ["accent", True, True],
                "contrast_key": [-1, str, False, True]
            }

            self.fls = AFDATA.Functions.flags(fls, kwargs)
            self._smd = SharedMemoryDict(**self._shared_mem_dict_args)

            # UI Objects
            if self.fls['use_tk']:
                self.root = tk.Tk()
            else:
                self.root = tk.Toplevel()

            self.root.withdraw()

            self.description = self.fls['description']
            self.button_text = self.fls['button_text']
            self.title = self.fls['title'],
            self.container_title = self.fls['f_title']

            self.accent_key = self.fls['accent_key']
            self.contrast_key = self.fls['contrast_key']

            self.title_lbl = tk.Label(self.root)
            self.description_canvas = tk.Canvas(self.root)
            self.description_section = tk.Frame(self.description_canvas)
            self.description_label = tk.Label(self.description_section)
            self.description_section_v_scbar = ttk.Scrollbar(self.root)
            self.ok_button = tk.Button(self.root)
            self.entry = ttk.Entry(self.root)
            self.err_lbl = tk.Label(self.root)

            self.theme_mode = TMODE
            self.theme = {}

            def_ws = conf.AppContainer.Prompts.def_ws
            self.ss = (self.root.winfo_screenwidth(), self.root.winfo_screenheight())
            self.ws = [
                def_ws[0] if def_ws[0] <= self.ss[0] else self.ss[0],
                def_ws[1] if def_ws[1] <= self.ss[1] else self.ss[1]
            ]
            if len(self.description.strip()) <= 0:
                self.ws = (self.ws[0], self.ws[1] // 2)
            else:
                self.ws = (*self.ws,)

            self.wp = (
                self.ss[0] // 2 - self.ws[0] // 2,
                self.ss[1] // 2 - self.ws[1] // 2
            )

            # self.start()
            self.run()
            self.root.deiconify()
            self.root.attributes('-topmost', 1)
            self.root.mainloop()

        def __on_window_close__(self):
            self.root.withdraw()
            self.root.quit()

        def __set__(self, data, *args, **kwargs):
            self._smd[self._smai_key] = kwargs['data01']

        def __on_submit__(self):
            _r = self.entry.get()

            if self.fls['strip_inp']:
                _r = _r.strip()

            if self.fls['regex'] is not None:
                _r = re.findall(self.fls['regex'], _r)

            if type(self.fls['min_len']) is int:
                if len(_r) < self.fls['min_len']:
                    self.err_lbl.config(
                        text="Your input must be at least %s characters long." % self.fls['min_len']
                    )

                    return

            self.__set__('', data01=_r)

            self.__on_window_close__()

        def run(self):
            _Basic.OnStart.init()

            if self.theme_mode == 'd':
                self.theme = theme.Theme.UserPref.dark_mode()
            else:
                self.theme = theme.Theme.UserPref.light_mode()

            if self.contrast_key == -1:
                _m = {
                    self.theme['fg']: 'fg',
                    self.theme['bg']: 'bg'
                }

                _res = colors.Functions.calculate_nearer(*_m.keys(), self.theme[self.accent_key])
                self.contrast_key = _m[_res]

            self.root.geometry(
                "%sx%s+%s+%s" % (self.ws[0], self.ws[1], self.wp[0], self.wp[1])
            )
            self.root.title(self.container_title)
            self.root.protocol("WM_DELETE_WINDOW", self.__on_window_close__)
            self.root.config(bg=self.theme['bg'])
            self.root.lift()

            ttktheme = 'alt'

            # Title Label
            self.title_lbl.config(
                text=self.title,
                wraplength=self.ws[0] - 2 * self.theme['padding']['x'],
                fg=self.theme[self.accent_key],
                bg=self.theme['bg'],
                font=(self.theme['font']['font_face'], self.theme['font']['title_size'])
            )

            self.title_lbl.pack(
                fill=tk.BOTH,
                expand=False,
                padx=self.theme['padding']['x'],
                pady=self.theme['padding']['y'] * 1.5
            )

            # Error Label
            self.err_lbl.config(
                text="",
                background=self.theme['bg'],
                foreground=self.theme['error'],
                font=(self.theme['font']['font_face'], self.theme['font']['main_size']),
                wraplength=self.ws[0] - (self.theme['padding']['x'] * 2),
                justify=tk.CENTER
            )

            self.err_lbl.pack(
                fill=tk.X,
                expand=False,
                padx=self.theme['padding']['x'],
                pady=(self.theme['padding']['y'] // 2, self.theme['padding']['y']),
                side=tk.BOTTOM
            )

            # OK Button
            self.ok_button.config(
                text=self.button_text,
                fg=self.theme[self.contrast_key],
                bg=self.theme[self.accent_key],
                activebackground=self.theme[self.contrast_key],
                activeforeground=self.theme[self.accent_key],
                command=self.__on_submit__,
                font=(self.theme['font']['font_face'], self.theme['font']['big_para_size']),
                bd=0
            )

            self.ok_button.pack(
                fill=tk.BOTH,
                expand=False,
                padx=(self.theme['padding']['x']),
                pady=(self.theme['padding']['y'], 0),
                ipadx=self.theme['padding']['x'] // 2,
                ipady=self.theme['padding']['y'] // 2,
                side=tk.BOTTOM
            )

            # Entry
            self.entry.pack(
                fill=tk.X,
                expand=True,
                padx=self.theme['padding']['x'],
                pady=self.theme['padding']['y'],
                ipadx=self.theme['padding']['x'] // 1.7,
                ipady=self.theme['padding']['y'] // 1.7,
                side=tk.BOTTOM
            )

            estyle = ttk.Style()
            estyle.theme_use(ttktheme)
            estyle.configure(
                "TEntry",
                background=self.theme['bg'],
                foreground=self.theme['fg'],
                fieldbackground=self.theme['bg'],
                selectbackground=self.theme[self.accent_key],
                selectforeground=self.theme['fg'],
                bordercolor=self.theme['bg'],
                insertcolor=self.theme[self.accent_key]
            )
            self.entry.configure(
                font=(self.theme['font']['font_face'], self.theme['font']['big_para_size'])
            )

            # Description
            if len(self.description.strip()) > 0:
                # Description Label
                self.description_label.config(
                    text=self.description.strip(),
                    wraplength=self.ws[0] - 3.5 * self.theme['padding']['x'],
                    fg=self.theme['fg'],
                    bg=self.theme['bg'],
                    font=(self.theme['font']['font_face'], self.theme['font']['main_size'])
                )
                self.description_label.pack(
                    fill=tk.BOTH,
                    expand=True
                )

                # SCBar + Data Section
                self.description_canvas.config(
                    bg=self.theme['bg'],
                    bd='0',
                    highlightthickness=0
                )

                self.description_section_v_scbar.pack(
                    fill=tk.Y,
                    expand=False,
                    padx=(self.theme['padding']['x'], 0),
                    pady=self.theme['padding']['y'],
                    side=tk.LEFT
                )

                self.description_canvas.pack(
                    fill=tk.BOTH,
                    expand=True,
                    padx=(self.theme['padding']['x'] // 4, self.theme['padding']['x']),
                    pady=self.theme['padding']['y'],
                    side=tk.RIGHT
                )

                self.description_section.config(bd=0)

                # SCBar Config

                sStyle = ttk.Style()
                sStyle.theme_use(ttktheme)

                # The absolute legend that created the following code for MyTScrollbar.trough
                # can be found at:
                # https://stackoverflow.com/questions/28375591/changing-the-appearance-of-a-scrollbar-in-tkinter-using-ttk-styles

                sStyle.element_create("My.Scrollbar.trough", "from", ttktheme)
                sStyle.layout("My.TScrollbar",
                              [('My.Scrollbar.trough', {'children':
                                  [
                                      ('Vertical.Scrollbar.uparrow', {'side': 'top', 'sticky': ''}),
                                      ('Vertical.Scrollbar.downarrow', {'side': 'bottom', 'sticky': ''}),
                                      ('Vertical.Scrollbar.thumb', {'unit': '1', 'children':
                                          [('Vertical.Scrollbar.grip', {'sticky': ''})], 'sticky': 'nswe'})],
                                  'sticky': 'ns'})
                               ])
                sStyle.configure("My.TScrollbar", *sStyle.configure("TScrollbar"))
                sStyle.configure("My.TScrollbar", troughcolor=self.theme['bg'])

                sStyle.configure(
                    'My.TScrollbar',
                    background=self.theme['bg'],
                    arrowcolor=self.theme[self.accent_key]
                )
                sStyle.map(
                    "My.TScrollbar",
                    background=[
                        ("active", self.theme[self.accent_key]), ('disabled', self.theme['bg'])
                    ],
                    foreground=[
                        ("active", self.theme[self.accent_key]), ('disabled', self.theme['bg'])
                    ],
                    arrowcolor=[
                        ('disabled', self.theme['bg'])
                    ]
                )

                self.description_section_v_scbar.configure(command=self.description_canvas.yview, style='My.TScrollbar')

                self.description_canvas.configure(
                    yscrollcommand=self.description_section_v_scbar.set
                )

                self.description_canvas.create_window(
                    (0, 0),
                    window=self.description_section,
                    anchor="nw",
                    tags="self.frame"
                )

                # Event Handlers
                self.description_section.bind("<Configure>", self.__onFrameConfig)
                self.description_section.bind_all("<MouseWheel>", self.__on_mousewheel)

                _update_sc_bar(self.description_section_v_scbar, self.description_canvas, self.root)

        def __onFrameConfig(self, *args):
            self.description_canvas.configure(
                scrollregion=self.description_canvas.bbox("all")
            )

        def __on_mousewheel(self, event):
            """
            Straight out of stackoverflow
            Article: https://stackoverflow.com/questions/17355902/tkinter-binding-mousewheel-to-scrollbar
            Change
            : added "int" around the first arg
            """
            self.description_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def __del__(self):
            # self.thread.join(self, 0)
            pass

        def _create_sm_args(self):
            _t0 = SMem._pro_000_s_mem_addr_0_size()
            _t0 = {
                'name': '%s%s%s%s',
                'size': _t0,
                'key': '%s'
            }
            _t0['name'] = _t0['name'] % (
                self.smai.r4,
                self.smai.r3,
                self.smai.r1,
                self.smai.r2
            )
            _t0['key'] = _t0['key'] % self.smai.r5
            self._shared_mem_dict_args = {
                'name': _t0['name'],
                'size': _t0['size']
            }
            self._smai_key = _t0['key']
