import tkinter as tk
from tkinter import ttk, messagebox
import threading, sys, os, shutil, traceback
from dataclasses import dataclass
from enum import Enum
from typing import *

import qa_std, qa_exceptions, qa_lookups, qa_log_cleaner, qa_theme, qa_diagnostics, qa_conf, qa_protected_conf, \
    qa_prompts, qa_nv_flags_system, standards_qa_question
from qa_af_master import AFLog, AFData, AFIOObject, AFIOObjectInterface, AFJSON, AFFileIO, AFEncryption, LoggerModule


#########################################
#           GLOBAL VARIABLES            #
#########################################


_script_name = "QuestionMasterFrom"
_file_name = "apps_question_master_form.py"
_self_logger = AFLog(_script_name, AFData.Functions.generate_uid(21420.69))
_app_title = f"Question Master Form {qa_conf.ConfigFile.raw['app_data']['build']['frame_vid']}"


#########################################
#          DATA + ENUM CLASSES          #
#########################################
@dataclass
class Info:
    data: str
    state: qa_std.InfoState


@dataclass
class Theme:
    background: str
    foreground: str
    accent: str
    highlight: str
    padX: int
    padY: int
    border_size: int
    border_color: str
    error_color: str
    warning_color: str
    okay_color: str


class Modes(Enum):
    View = 1
    Edit = 2
    Add = 3


@dataclass
class Mode:
    mode: Modes
    args: list


#########################################
#          MAIN UI DECLARATION          #
#########################################


class QuestionMasterFormUI(threading.Thread):
    def __init__(self, mode: Mode, *args, **kwargs):
        # Threading Initialization
        super().__init__()
        self.thread = threading.Thread
        self.thread.__init__(self)

        # Master Control Vars
        # MAIN FRAME
        self.root = tk.Tk() if '-tk' in args else tk.Toplevel()

        # UI INITIALIZATION LEVEL
        self.init_level = 0
        # Determines UI initialization state
        #       - 0: No UI initialization complete
        #       - 1: UI packed, but not themed
        #       - 2: UI themed, but not updated
        #       - 3: UI initialization complete

        # WINDOW GEOMETRY
        def_ws = (*qa_conf.AppContainer.Apps.admin_tools['question_master']['ws'],)  # Default
        max_ws = (self.root.winfo_screenwidth(), self.root.winfo_screenheight())  # Maximum (SS)
        self.ws = (
            def_ws[0] if def_ws[0] <= max_ws[0] else max_ws[0],
            def_ws[1] if def_ws[1] <= max_ws[0] else max_ws[1]
        )  # Init. Window Size [x, y]
        self.sp = (
            max_ws[0] // 2 - self.ws[0] // 2,
            max_ws[1] // 2 - self.ws[1] // 2,
        )  # Init. Window Position [x, y]

        del def_ws, max_ws  # No longer needed

        # Master Data Vars
        self.args, self.kwargs, self.init_mode = args, kwargs, mode

        # Theming
        self.theme_dict = {}
        self.theme: Theme = Theme('white', 'black', 'blue', 'white', 20, 10, 0, 'white', 'red', 'yellow', 'green')
        self.theme_font_mapping = {}
        self.refresh_theme_data()  # Installs theme data
        self.theme_update_req = {
            'lbl': [],
            'btn': [],
            'lbl_frame': [],
            'font': {},
            'invisible_container': [],
            'frame': [],
            'accent_fg': [],
            'accent_bg': [],
            'wrap_length': [],
            'borderless': [],
            'custom_color': {},
            'custom_wrap_length': {},
            'custom_command': {}
        }
        self.master_ttk_style = ttk.Style()
        self.master_ttk_style.theme_use('alt')

        # Frames
        self.shell_1_c = tk.Canvas(self.root)  # Viewing
        self.shell_2_c = tk.Canvas(self.root)  # Adding, Editing
        self.shell_1 = tk.Frame(self.shell_1_c)
        self.shell_2 = tk.Frame(self.shell_2_c)

        self.shell_status = {
            self.shell_1_c: {
                'init': False
            },
            self.shell_2_c: {
                'init': False
            }
        }

        # Frame Controllers
        self.shell_mode_index: Modes = self.init_mode.mode
        self.shell_c_mapper = {
            Modes.View: self.shell_1_c,
            Modes.Add: self.shell_2_c,
            Modes.Edit: self.shell_2_c,
        }

        self.question_id: str = ""

        # Frame Theming Requests
        self.theme_update_req['frame'].extend([
            self.root, self.shell_1, self.shell_2
        ])

        # Root-level elements
        self.info_label = tk.Label(self.root)
        self.theme_update_req['lbl'].append(self.info_label)
        self.theme_update_req['font'][self.info_label] = ('<face>', '<normal>')

        # Scrollbars Variables
        self.shell_1_vsb = ttk.Scrollbar(self.root, orient=tk.VERTICAL)
        self.shell_1_xsb = ttk.Scrollbar(self.root, orient=tk.HORIZONTAL)
        self.shell_2_vsb = ttk.Scrollbar(self.root, orient=tk.VERTICAL)
        self.shell_2_xsb = ttk.Scrollbar(self.root, orient=tk.HORIZONTAL)

        # Initializing Calls
        self.start()  # Calls 'run' via self.thread
        self.root.mainloop()  # UI mainloop init

    def on_window_close(self):
        if __name__ == "__main__":
            sys.exit(0)
        else:
            try:
                self.root.after(0, self.root.destroy)
                self.thread.join(self, 0)
            except Exception as E:
                print(E)

    def run(self):
        global _app_title
        self.root.geometry(f"{self.ws[0]}x{self.ws[1]}+{self.sp[0]}+{self.sp[1]}")
        self.root.title(_app_title)
        self.root.protocol('WM_DELETE_WINDOW', self.on_window_close)

        self.info_label.pack(fill=tk.X, expand=False, padx=self.theme.padX, pady=self.theme.padY, side=tk.BOTTOM)

        self.init_level = 1
        self.update_theme()
        self.init_level = 2
        self.update_elements()

    def show_info(self, info: Info):
        self.info_label.config(
            fg=self.theme_dict[
                'error' if info.state == qa_std.InfoState.ERROR else
                'warning' if info.state == qa_std.InfoState.WARNING else
                'ok' if info.state == qa_std.InfoState.OK else
                'accent' if info.state == qa_std.InfoState.INFO else 'fg'
            ],
            text=info.data
        )

    def refresh_theme_data(self):
        self.theme_dict = _load_data('theme')
        self.theme = Theme(
            self.theme_dict['bg'],
            self.theme_dict['fg'],
            self.theme_dict['accent'],
            self.theme_dict['bg'],
            self.theme_dict['padding']['x'],
            self.theme_dict['padding']['y'],
            self.theme_dict['border']['width'],
            self.theme_dict['border']['color'],
            self.theme_dict['error'],
            self.theme_dict['warning'],
            self.theme_dict['ok']
        )
        self.theme_font_mapping = {
            '<normal>': self.theme_dict['font']['main_size'],
            '<medium>': self.theme_dict['font']['big_para_size'],
            '<large>': self.theme_dict['font']['sttl_size'],
            '<title>': self.theme_dict['font']['title_size'],
            '<face>': self.theme_dict['font']['font_face'],
            '<alt_face>': self.theme_dict['font']['alt_font_face']
        }

    def update_theme(self):
        global _self_logger

        self.refresh_theme_data()

        command_map = {
            'bg_norm': lambda _elem: _elem.config(
                bg=self.theme_dict['bg']
            ),
            'fg_norm': lambda _elem: _elem.config(
                fg=self.theme_dict['fg']
            ),
            'bg_accent': lambda _elem: _elem.config(
                bg=self.theme_dict['accent'], fg=self.theme_dict['bg']
            ),
            'fg_accent': lambda _elem: _elem.config(
                bg=self.theme_dict['bg'], fg=self.theme_dict['accent']
            ),
            'active_state': lambda _elem: _elem.config(
                activebackground=self.theme_dict['accent'], activeforeground=self.theme_dict['bg']
            ),
            'borderless': lambda _elem: _elem.config(
                bd='0'
            ),
            'wrap_length': lambda _elem: _elem.config(
                wraplength=(self.ws[0] - self.theme_dict['padding']['x'] * 2)
            ),
            'invisible': lambda _elem: _elem.config(
                bg=self.theme_dict['bg'], fg=self.theme_dict['fg'], bd='0'
            ),
            'button': lambda _elem: _elem.config(
                bd='1', highlightcolor=self.theme_dict['accent'], relief=tk.GROOVE
            ),
        }

        for name, (ls, commands) in {
            'Label': ((*self.theme_update_req['lbl'],), ('bg_norm', 'fg_norm')),
            'Button': ((*self.theme_update_req['btn'],), ('bg_norm', 'fg_norm', 'active_state', 'button')),
            'LabelFrame': ((*self.theme_update_req['lbl_frame'],), ('bg_norm', 'fg_accent')),
            'Frame': ((*self.theme_update_req['frame'],), ('bg_norm',)),
            '<set_wrap_length>': ((*self.theme_update_req['wrap_length'],), ('wrap_length',)),
            'InvisibleContainer': ((*self.theme_update_req['invisible_container'],), ('invisible',)),
            'AccentFG': ((*self.theme_update_req['accent_fg'],), ('fg_accent',)),
            'AccentBG': ((*self.theme_update_req['accent_bg'],), ('bg_accent',)),
            '<set_borderless>': ((*self.theme_update_req['borderless'],), ('borderless',))
        }.items():
            for element in ls:
                for command_request in commands:
                    try:
                        command_map[command_request](element)
                    except Exception as E:
                        _self_logger.log(
                            'ERROR',
                            f'Failed to apply command "{command_request}" to "{element}" ({name}) :: {E} :: {traceback.format_exc()}',
                            print_d=True
                        )

        for element, font_data in self.theme_update_req['font'].items():
            try:
                n_font_data = []
                for d in font_data:
                    if d in self.theme_font_mapping:
                        n_font_data.append(self.theme_font_mapping[d])
                    else:
                        n_font_data.append(d)
                font_data = (*n_font_data,)
                del n_font_data
                element.config(font=font_data)

            except Exception as E:
                _self_logger.log(
                    'ERROR',
                    f'Failed to apply command "font" to "{element}" :: {E} :: {traceback.format_exc()}',
                    print_d=True
                )

        for element, bf in self.theme_update_req['custom_color'].items():
            try:
                bg, fg = bf
                element.config(bg=self.theme_dict[bg], fg=self.theme_dict[fg])

            except Exception as E:
                _self_logger.log(
                    'ERROR',
                    f'Failed to apply command "font" to "{element}" :: {E} :: {traceback.format_exc()}',
                    print_d=True
                )

        del command_map

        for uid, (cc, args) in self.theme_update_req['custom_command'].items():
            try:
                c_args = []
                for lookup_F, arg_N in args:
                    if lookup_F:
                        c_args.append(self.theme_dict[arg_N])
                    else:
                        c_args.append(arg_N)

                cc(*c_args)

                del c_args

            except Exception as E:
                print(E)
                _self_logger.log(
                    'ERROR',
                    f'Failed to run the attached command ({cc}) :: {E} :: {traceback.format_exc()}',
                    print_d=True
                )

        for elem, wrap_length in self.theme_update_req['custom_wrap_length'].items():
            try:
                elem.config(wraplength=wrap_length)
            except Exception as E:
                print(E)
                _self_logger.log(
                    'ERROR',
                    f'Failed to apply wrap_length \'{wrap_length}\' :: {E} :: {traceback.format_exc()}',
                    print_d=True
                )

        # TTK
        # Scrollbars [H, V]
        for i in ('Horizontal', 'Vertical'):
            self.master_ttk_style.configure(
                f'TScrollbar.{i}',
                background=self.theme_dict['bg'],
                arrowcolor=self.theme_dict['fg'],
                bordercolor=self.theme_dict['bg'],
                troughcolor=self.theme_dict['bg']
            )

            self.master_ttk_style.map(
                f'TScrollbar.{i}',
                background=[
                    ("active", self.theme_dict['accent']), ('disabled', self.theme_dict['bg'])
                ]
            )

        # Exceptions
        return

    def get_children(self, container, recursive_search: bool = True, *exp) -> tuple:
        o0 = []

        for element in container.winfo_children():
            if element in exp:
                continue

            if element.winfo_children and recursive_search:
                o0.extend(self.get_children(element, *exp))

            else:
                o0.append(element)

        return *set(o0),

    def frame_configure(self, *args):
        if self.shell_status[self.shell_c_mapper[self.shell_mode_index]]['init']:
            return

        print(f'configuring {self.shell_c_mapper[self.shell_mode_index]}')

        m = {
            Modes.Add: [self.shell_2_c, self.shell_2, 'self.shell_2', self.shell_2_vsb, self.shell_2_xsb],
            Modes.Edit: [self.shell_2_c, self.shell_2, 'self.shell_2', self.shell_2_vsb, self.shell_2_xsb],
            Modes.View: [self.shell_1_c, self.shell_1, 'self.shell_1', self.shell_1_vsb, self.shell_1_xsb],
        }

        # WARNING: Need to import `typing` to annotate the following as shown:
        m: Dict[Modes, List[tk.Canvas, tk.Frame, ttk.Scrollbar, ttk.Scrollbar]]

        shell, frame, frame_str, vsb, xsb = m[self.shell_mode_index]

        vsb.configure(command=shell.yview)
        xsb.configure(command=shell.xview)

        shell.configure(
            xscrollcommand=xsb.set,
            yscrollcommand=vsb.set,
        )

        shell.create_window(
            (0, 0),
            window=frame,
            anchor='nw',
            tags=frame_str
        )

        del m, shell, vsb, xsb, frame, frame_str

    def update_elements(self):
        m = {
            Modes.Add: [self.shell_2_c, self.shell_2_vsb, self.shell_2_xsb, self.shell_2_packer],
            Modes.Edit: [self.shell_2_c, self.shell_2_vsb, self.shell_2_xsb, self.shell_2_packer],
            Modes.View: [self.shell_1_c, self.shell_1_vsb, self.shell_1_xsb, self.shell_1_packer],
        }

        # WARNING: Need to import `typing` to annotate the following as shown:
        m: Dict[Modes, List[tk.Canvas, ttk.Scrollbar, ttk.Scrollbar, Callable]]

        c2r = self.get_children(self.root, False, self.info_label)
        for child in c2r:
            try:
                child.pack_forget()
            except:
                pass

        shell, vsb, xsb, packer = m[self.shell_mode_index]

        xsb.pack(fill=tk.X, expand=False, side=tk.BOTTOM)
        vsb.pack(fill=tk.Y, expand=False, side=tk.RIGHT)
        shell.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        self.frame_configure()
        packer()

        del m, shell, vsb, xsb, c2r, packer

    def shell_1_packer(self):
        # Temporary, of course
        lbl = tk.Label(self.shell_1, text="Shell 1")
        lbl.pack(fill=tk.BOTH, expand=True)

    def shell_2_packer(self):
        # Temporary, of course
        lbl = tk.Label(self.shell_2, text="Shell 2")
        lbl.pack(fill=tk.BOTH, expand=True)

    def __del__(self):
        self.thread.join(self, 0)


#########################################
#           STARTER HANDLERS            #
#########################################


class StartupHandlers:
    @staticmethod
    def CLIStarter(*args):
        global _file_name, _script_name
        a = [*args]
        if 'python' in a[0].lower():
            del a[0]
        if _file_name in a[0].lower():
            del a[0]

        args_map = {
            '-tk': {
                'type': qa_std.CLI.CLITypes.ARGUMENT,
                'separator': None,
                'data_type': str,
                'tied_to_function': {
                    'b': False,
                    'functions': []
                },
            },
            '-edit': {
                'type': qa_std.CLI.CLITypes.ARGUMENT,
                'separator': '::quid=',
                'data_type': str,
                'tied_to_function': {
                    'b': False,
                    'functions': []
                },
            },
            '-add': {
                'type': qa_std.CLI.CLITypes.ARGUMENT,
                'separator': None,
                'data_type': str,
                'tied_to_function': {
                    'b': False,
                    'functions': []
                },
            },
            '-view': {
                'type': qa_std.CLI.CLITypes.ARGUMENT,
                'separator': None,
                'data_type': str,
                'tied_to_function': {
                    'b': False,
                    'functions': []
                },
            }
        }

        s = qa_std.CLI.CLI_handler(
            [*args], args_map, _script_name, __name__ == "__main__", True
        )

        p0 = False
        args_stack, comp_args_stack, name_args_stack = [], [], []
        og_args_stack, og_comp_args_stack, og_name_args_stack = [], [], []

        if isinstance(s, tuple):
            if len(s) == 4:
                og_args_stack, _, og_name_args_stack, og_comp_args_stack = s
                args_stack = (*og_args_stack.values(), )
                name_args_stack = (*og_name_args_stack.values(), )
                comp_args_stack = (*og_comp_args_stack.values(), )
                p0 = True

        # Find Mode
        # In named_args
        pop_stack = []  # ARGS_STACK, N_ARGS_STACK, O_ARGS_STACK [OG dicts]
        mode = None

        if '-add' in name_args_stack:
            add_ind = name_args_stack.index('-add') - 1
            assert og_name_args_stack[add_ind] == '-add'
            pop_stack.append(add_ind)
            mode = Mode(Modes.Add, [])

        if '-view' in name_args_stack:
            add_ind = name_args_stack.index('-view') - 1
            assert og_name_args_stack[add_ind] == '-view'
            pop_stack.append(add_ind)
            mode = Mode(Modes.View, [])

        if '-edit' in name_args_stack:
            add_ind = name_args_stack.index('-edit') - 1
            assert og_name_args_stack[add_ind] == '-edit'
            pop_stack.append(add_ind)
            mode = Mode(Modes.Edit, og_args_stack[add_ind])

        assert len(pop_stack) == 1 and mode is not None, f'Expected 1 mode, got {len(pop_stack)}'

        del og_args_stack[pop_stack[0]]
        del og_name_args_stack[pop_stack[0]]
        del og_comp_args_stack[pop_stack[0]]

        args_stack = (*og_args_stack.values(),)
        name_args_stack = (*og_name_args_stack.values(),)
        comp_args_stack = (*og_comp_args_stack.values(),)

        if not p0:
            if __name__ == "__main__":
                sys.exit('invalid arguments')
            else:
                return -1

        del p0, args_map, a, args, pop_stack, s

        QuestionMasterFormUI(mode, *args_stack)

        del name_args_stack, args_stack, comp_args_stack, og_name_args_stack, og_args_stack, \
            og_comp_args_stack, mode


#########################################
#              FUNCTIONS                #
#########################################


def _load_data(data_key) -> any:
    data_key_mapper = {
        'theme': lambda: qa_theme.Theme.UserPref.pref()
    }

    assert data_key in data_key_mapper, f"Invalid data_key '{data_key}'"

    return data_key_mapper[data_key]()


#########################################
#             STARTER CODE              #
#########################################

if __name__ == "__main__":
    if len(sys.argv) > 1:
        StartupHandlers.CLIStarter(*sys.argv[1::])
    else:
        QuestionMasterFormUI(Mode(
            Modes.View, []
        ))
