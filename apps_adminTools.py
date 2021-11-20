import qa_conf, qa_splash_screen
import tkinter as tk

import qa_theme

_boot_steps = {
    1: "Importing modules",
    2: "Loading Globals",
    3: "Loading Functions",
    4: "Loading Configuration",
    5: "Running Boot Checks",
    6: "Fetching Version Information"
}

_bg_frame = tk.Tk()
_bg_frame.withdraw()
_bg_frame.title("QA Administrator Tools - Background Frame")

if not qa_conf.Control.doNotUseSplash:
    splRoot = tk.Toplevel()
    splObj = qa_splash_screen.Splash(splRoot)
    splObj.setTitle("Administrator Tools")
else:
    splObj = None


def _set_boot_progress(index):
    if not qa_conf.Control.doNotUseSplash:
        qa_splash_screen.set_smooth_progress(splObj, index, _boot_steps)


_set_boot_progress(1)

from tkinter import ttk
from tkinter import messagebox as tkmsb
from tkinter import filedialog as tkfldl
import threading, shutil, traceback, json, time, random, subprocess, sys, os, qa_exceptions
import qa_exceptions, qa_prompts, qa_pdf_gen, qa_log_cleaner, qa_nv_flags_system, qa_diagnostics
from qa_appfunctions import *
import qa_online_version_check as ovcc


_set_boot_progress(2)

app_title = f"Administrator Tools {qa_conf.ConfigFile.raw['app_data']['build']['frame_vid']}"
_logger = AFLog(
    'qa_apps-admin_tools--core',
    AFDATA.Functions.generate_uid(conf.Application.uid_seed['admin_tools'])
)


class AdminToolsUI(threading.Thread):
    def __init__(self):
        super().__init__()
        self.thread = threading.Thread
        self.thread.__init__(self)

        # Root
        self.root = tk.Toplevel()
        self.root.withdraw()

        # IU Params
        def_ws = (*qa_conf.AppContainer.Apps.admin_tools['main']['ws'], )
        self.max_ws = (self.root.winfo_screenwidth(), self.root.winfo_screenheight())
        self.ws = (
            def_ws[0] if def_ws[0] <= self.max_ws[0] else self.max_ws[0],
            def_ws[1] if def_ws[1] <= self.max_ws[0] else self.max_ws[1]
        )
        del def_ws
        self.sp = (
            self.max_ws[0] // 2 - self.ws[0] // 2,
            self.max_ws[1] // 2 - self.ws[1] // 2,
        )

        # Theming Updates
        self.theme = {}
        self.theme_font_mapping = {}
        self.reload_data()
        self.theme_update_req = {
            'lbl': [],
            'btn': [],
            'lbl_frame': [],
            'font': {},
            'invis_container': [],
            'frame': [],
            'accent_fg': [],
            'accent_bg': [],
            'wraplength': []
        }

        # Global UI Elements
        self.error_label = tk.Label(self.root)
        self.theme_update_req['lbl'].append(self.error_label)
        self.theme_update_req['font'][self.error_label] = ('<face>', '<normal>')
        self.title_lbl = tk.Label(self.root, text='Administrator Tools')
        self.theme_update_req['lbl'].append(self.title_lbl)
        self.theme_update_req['accent_fg'].append(self.title_lbl)
        self.theme_update_req['font'][self.title_lbl] = ('<face>', '<title>')
        self.sep = ttk.Separator(self.root, orient=tk.HORIZONTAL)
        self.sep2 = ttk.Separator(self.root, orient=tk.VERTICAL)
        self.sep_style = ttk.Style()
        self.sep_style.theme_use('alt')

        # Screens
        self.master_screen = tk.Frame(self.root)
        self.selector_panel = tk.Frame(self.root)
        self.screen_1 = tk.Frame(self.master_screen)
        self.screen_2 = tk.Frame(self.master_screen)
        self.screen_3 = tk.Frame(self.master_screen)
        self.screen_4 = tk.Frame(self.master_screen)
        self.screen_5 = tk.Frame(self.master_screen)

        self.theme_update_req['frame'].extend([
            self.root,
            self.master_screen,
            self.selector_panel,
            self.screen_1,
            self.screen_2,
            self.screen_3,
            self.screen_4,
            self.screen_5
        ])

        self.current_screen_index = 1

        # Selector Panel
        self.selector_panel_screen_1 = tk.Button(self.selector_panel, command=lambda: self.select_screen(1))
        self.selector_panel_screen_2 = tk.Button(self.selector_panel, command=lambda: self.select_screen(2))
        self.selector_panel_screen_3 = tk.Button(self.selector_panel, command=lambda: self.select_screen(3))
        self.selector_panel_screen_4 = tk.Button(self.selector_panel, command=lambda: self.select_screen(4))
        self.selector_panel_screen_5 = tk.Button(self.selector_panel, command=lambda: self.select_screen(5))

        self.theme_update_req['btn'].extend([
            self.selector_panel_screen_1,
            self.selector_panel_screen_2,
            self.selector_panel_screen_3,
            self.selector_panel_screen_4,
            self.selector_panel_screen_5,
        ])

        self.selector_panel_mapper = {
            1: self.screen_1_packer,
            2: self.screen_2_packer,
            3: self.screen_3_packer,
            4: self.screen_4_packer,
            5: self.screen_5_packer,
        }

        self.screen_info_mapper = {
            1: {
                'title': 'Configuration',
                'button': self.selector_panel_screen_1,
            },
            2: {
                'title': 'Question Database Editor',
                'button': self.selector_panel_screen_2,
            },
            3: {
                'title': 'Scores File IO',
                'button': self.selector_panel_screen_3,
            },
            4: {
                'title': 'General File IO',
                'button': self.selector_panel_screen_4,
            },
            5: {
                'title': 'Miscellaneous Items',
                'button': self.selector_panel_screen_5,
            },
        }

        # Screen 1 elements [Configuration Screen]
        # Screen 1 containers
        self.configuration_allow_custom_config_container = tk.LabelFrame(self.screen_1)
        self.config_acc_description_lbl = tk.Label(self.configuration_allow_custom_config_container)
        self.config_acc_action_btn = tk.Button(self.configuration_allow_custom_config_container, command=self.toggle_config_acc)
        self.configuration_question_dist_config_container = tk.LabelFrame(self.screen_1)
        self.configuration_question_divF_container = tk.LabelFrame(self.configuration_question_dist_config_container)
        self.configuration_deductions_config_container = tk.LabelFrame(self.screen_1)
        self.configuration_deductions_amnt_container = tk.LabelFrame(self.configuration_deductions_config_container)
        self.theme_update_req['lbl_frame'].extend([
            self.configuration_allow_custom_config_container,
            self.configuration_question_dist_config_container,
            self.configuration_question_divF_container,
            self.configuration_deductions_config_container,
            self.configuration_deductions_amnt_container
        ])

        self.theme_update_req['lbl'].extend([
            self.config_acc_description_lbl,
        ])

        for elem in (self.config_acc_description_lbl, self.config_acc_action_btn):
            self.theme_update_req['font'][elem] = ('<face>', '<normal>')

        self.theme_update_req['btn'].extend([
            self.config_acc_action_btn,
        ])

        # Screen 2 elements [Question Editing Screen]
        # Screen 3 elements [Scores IO Screen]
        # Screen 4 elements [File IO Screen]
        # Screen 5 elements [Misc. Items Screen]

        # Calls
        self.start()
        self.root.deiconify()
        self.root.mainloop()

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.close_window)
        self.root.title(f"Quizzing Application {qa_conf.ConfigFile.raw['app_data']['build']['frame_vid']} - Admin Tools")
        self.root.geometry("%sx%s+%s+%s" % (*self.ws, *self.sp))
        self.root.iconbitmap(qa_conf.Files.app_icons['admin_tools']['ico'])

        self.title_lbl.pack(
            fill=tk.X,
            expand=False,
            padx=self.theme['padding']['x'],
            pady=(self.theme['padding']['y'], 0),
        )
        self.sep.pack(fill=tk.X, expand=False, padx=self.theme['padding']['x'], pady=self.theme['padding']['y'])
        self.error_label.pack(
            fill=tk.X,
            expand=False,
            side=tk.BOTTOM,
            padx=self.theme['padding']['x'],
            pady=(self.theme['padding']['y'], 0),
        )
        # Add the button panel (+ items)
        self.selector_panel.pack(fill=tk.BOTH, expand=False, side=tk.LEFT)
        for ind, but in enumerate(
                (self.selector_panel_screen_1,
                 self.selector_panel_screen_2,
                 self.selector_panel_screen_3,
                 self.selector_panel_screen_4,
                 self.selector_panel_screen_5)
        ):
            self.theme_update_req['font'][but] = ('<face>', '<large>')
            but.config(text=self.screen_info_mapper[ind+1]['title'])
            but.pack(fill=tk.BOTH, expand=False, side=tk.TOP)

        self.sep2.pack(fill=tk.Y, expand=False, side=tk.LEFT)

        # Add the master screen
        self.master_screen.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT)

        self.select_screen(-1)
        self.update_theme()

    def close_window(self, code=0):
        sys.exit(code)

    def reload_data(self):
        self.theme = _load_data('theme')
        self.theme_font_mapping = {
            '<normal>': self.theme['font']['main_size'],
            '<medium>': self.theme['font']['big_para_size'],
            '<large>': self.theme['font']['sttl_size'],
            '<title>': self.theme['font']['title_size'],
            '<face>': self.theme['font']['font_face']
        }

    def update_theme(self) -> None:
        global _logger

        self.reload_data()

        command_map = {
            'bg_norm': lambda _elem: _elem.config(bg=self.theme['bg']),
            'fg_norm': lambda _elem: _elem.config(fg=self.theme['fg']),
            'bg_accent': lambda _elem: _elem.config(bg=self.theme['accent'], fg=self.theme['bg']),
            'fg_accent': lambda _elem: _elem.config(bg=self.theme['bg'], fg=self.theme['accent']),
            'active_state': lambda _elem: _elem.config(activebackground=self.theme['accent'], activeforeground=self.theme['bg']),
            'borderless': lambda _elem: _elem.config(bd='0'),
            'wraplength': lambda _elem: _elem.config(wraplength=(self.root.winfo_width() - self.selector_panel.winfo_width() - self.theme['padding']['x'] * 2)),
            'invisible': lambda _elem: _elem.config(bg=self.theme['bg'], fg=self.theme['fg'])
        }

        for name, elem_list_and_commands in {
            'Label': ((*self.theme_update_req['lbl'], ), ('bg_norm', 'fg_norm')),
            'Button': ((*self.theme_update_req['btn'], ), ('bg_norm', 'fg_norm', 'active_state', 'borderless')),
            'LabelFrame': ((*self.theme_update_req['lbl_frame'], ), ('bg_norm', 'fg_accent')),
            'Frame': ((*self.theme_update_req['frame'], ), ('bg_norm', )),
            '<set_wraplength>': ((*self.theme_update_req['wraplength'],), ('wraplength', )),
            'InvisibleContainer': ((*self.theme_update_req['invis_container'],), ('invisible', )),
            'AccentFG': ((*self.theme_update_req['accent_fg'],), ('fg_accent', )),
            'AccentBG': ((*self.theme_update_req['accent_bg'],), ('bg_accent', )),
        }.items():
            ls, commands = elem_list_and_commands
            for element in ls:
                for command_request in commands:
                    try:
                        command_map[command_request](element)
                    except Exception as E:
                        _logger.log(
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
                font_data = (*n_font_data, )
                del n_font_data
                element.config(font=font_data)

            except Exception as E:
                _logger.log(
                    f'Failed to apply command "font" to "{element}" :: {E} :: {traceback.format_exc()}',
                    print_d=True
                )

        # Exceptions
        self.error_label.config(fg=self.theme['error'])
        but = self.screen_info_mapper[self.current_screen_index]['button']
        but.config(
            bg=self.theme['accent'],
            fg=self.theme['bg'],
            activebackground=self.theme['bg'],
            activeforeground=self.theme['fg'],
        )

        # TTK
        self.sep_style.configure('Horizontal.TSepartor', background=self.theme['accent'])
        self.sep_style.configure('Vertical.TSepartor', background=self.theme['accent'])

        # Calls
        # Return
        return

    def show_error(self, error: str):
        self.error_label.config(text=error)

    def select_screen(self, index):
        assert index in (*self.selector_panel_mapper, -1), f"Invalid index '{index}'"
        if index != -1:
            self.current_screen_index = index
        self.selector_panel_mapper[self.current_screen_index]()
        self.update_theme()

    def screen_1_packer(self):
        # Reset
        self.reset_screen(1, self.screen_1)

        # Vars
        padX = self.theme['padding']['x']
        padY = self.theme['padding']['y']

        # Set
        for frame, text in {
            self.configuration_allow_custom_config_container: 'Allow Custom Configuration',
            self.configuration_question_dist_config_container: 'Distribution Settings',
            self.configuration_deductions_config_container: 'Point Deduction Settings',
        }.items():
            frame.config(text=text)
            frame.pack(fill=tk.BOTH, expand=True, padx=padX, pady=padY)

        # Each Frame
        self.config_acc_description_lbl.config(text="Test [Lbl]")
        self.config_acc_action_btn.config(text="Test [Button]")

        self.config_acc_description_lbl.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=padX, pady=padY)
        self.config_acc_action_btn.pack(fill=tk.X, expand=False, side=tk.RIGHT, ipadx=padX, padx=padX, pady=padY, ipady=padY)

    def screen_2_packer(self):
        # Reset
        self.reset_screen(2, self.screen_2)

    def screen_3_packer(self):
        # Reset
        self.reset_screen(3, self.screen_3)

    def screen_4_packer(self):
        # Reset
        self.reset_screen(4, self.screen_4)

    def screen_5_packer(self):
        # Reset
        self.reset_screen(5, self.screen_5)

    def reset_screen(self, index: int, screen: tk.Frame):
        self.current_screen_index = index
        self.screen_clear_master()
        screen.pack(fill=tk.BOTH, expand=True)
        try:
            for item in screen.winfo_children():
                try:
                    item.pack_forget()
                except:
                    pass
        except:
            pass

    def screen_clear_master(self):
        for i in (self.screen_1, self.screen_2, self.screen_3, self.screen_4, self.screen_5):
            try: i.pack_forget()
            except: pass

    def toggle_config_acc(self):
        pass

    def __del__(self):
        self.thread.join(self, 0)


_set_boot_progress(3)


def _load_data(data_key) -> any:
    data_key_mapper = {
        'theme': lambda: qa_theme.Theme.UserPref.pref()
    }

    assert data_key in data_key_mapper, f"Invalid data_key '{data_key}'"

    return data_key_mapper[data_key]()


_set_boot_progress(4)

# Any loading logic goes here

_set_boot_progress(5)

# Check loaded data here

_set_boot_progress(6)

ovcc.Check.check(splObj)
version_notes = ovcc.Check.find_comments()
if version_notes is not None:
    if len(version_notes) > 0:

        qa_splash_screen.hide(splObj)

        _m = {
            'error': 'error',
            'warning': 'warning',
            'info': 'accent'
        }
        for i in ['error', 'warning', 'info']:  # In this order
            if i in version_notes:
                qa_prompts.TextPrompts.BasicTextPrompt(
                    "The version of this app has the following notes associated with it:\n\n" + "\n\n\t *".join(
                        j for j in version_notes[i]),
                    accent_key=_m[i],
                    degree="%s%s" % (i[0].upper(), i[1::].lower()),
                    use_tk=False
                )

        qa_splash_screen.show(splObj)

qa_splash_screen.set_smooth_progress(splObj, -1, _boot_steps)

AdminToolsUI()
