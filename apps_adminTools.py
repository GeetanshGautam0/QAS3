from typing import Dict, Union, Callable

import qa_conf, qa_splash_screen
import tkinter as tk

_boot_steps = {
    1: "Importing modules\nIf app gets stuck, try pressing 'Enter'\nPress [Alt] + [F4] to exit.",
    2: "Loading Globals\nIf app gets stuck, try pressing 'Enter'\nPress [Alt] + [F4] to exit.",
    3: "Loading Functions\nIf app gets stuck, try pressing 'Enter'\nPress [Alt] + [F4] to exit.",
    4: "Loading Configuration\nIf app gets stuck, try pressing 'Enter'\nPress [Alt] + [F4] to exit.",
    5: "Running Boot Checks\nIf app gets stuck, try pressing 'Enter'\nPress [Alt] + [F4] to exit.",
    6: "Fetching Version Information\nIf app gets stuck, try pressing 'Enter'\nPress [Alt] + [F4] to exit."
}

_bg_frame = tk.Tk()
_bg_frame.withdraw()
_bg_frame.title("QA Administrator Tools - Background Frame")
splRoot = None

if not qa_conf.Control.doNotUseSplash:
    splRoot = tk.Toplevel()
    splObj = qa_splash_screen.Splash(splRoot)
    splObj.setTitle("Administrator Tools")


def _set_boot_progress(index):
    if not qa_conf.Control.doNotUseSplash:
        qa_splash_screen.set_smooth_progress(splObj, index, _boot_steps)


_set_boot_progress(1)

if isinstance(splRoot, tk.Toplevel):
    splRoot.attributes('-topmost', False)

from tkinter import ttk, Button
from tkinter import filedialog as tkfldl
from tkinter import messagebox as tkmsb
import threading, shutil, traceback, json, time, random, subprocess, sys, os, qa_exceptions
import qa_exceptions, qa_prompts, qa_pdf_gen, qa_log_cleaner, qa_nv_flags_system, qa_diagnostics, qa_theme
from qa_appfunctions import AFLog, AFDATA, AFIOObject, AFIOObjectInterface, AFJSON, AFFileIO, AFEncryption
import qa_online_version_check as ovcc
from time import sleep

if isinstance(splRoot, tk.Toplevel):
    splRoot.attributes('-topmost', True)

_set_boot_progress(2)

app_title = f"Administrator Tools {qa_conf.ConfigFile.raw['app_data']['build']['frame_vid']}"
_logger = AFLog(
    'qa_apps-admin_tools--core',
    AFDATA.Functions.generate_uid(qa_conf.Application.uid_seed['admin_tools'])
)


class AdminToolsUI(threading.Thread):
    def __init__(self):
        super().__init__()
        self.thread = threading.Thread
        self.thread.__init__(self)

        # TL Logic Vars
        self.init = False

        # Root
        self.root = tk.Toplevel()
        self.root.withdraw()

        # IU Params
        def_ws = (*qa_conf.AppContainer.Apps.admin_tools['main']['ws'],)
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
            'wraplength': [],
            'borderless': [],
            'custom_color': {},
            'wraplength_no_sel_panel': [],
            'custom_command': {}
        }

        # Screens
        self.main_screen = tk.Frame(self.root)
        self.master_screen = tk.Frame(self.main_screen)
        self.selector_panel = tk.Frame(self.main_screen)
        self.prompts_screen = tk.Frame(self.root)
        self.screen_0 = tk.Frame(self.master_screen)
        self.screen_1 = tk.Frame(self.master_screen)
        self.screen_2 = tk.Frame(self.master_screen)
        self.screen_3 = tk.Frame(self.master_screen)
        self.screen_4 = tk.Frame(self.master_screen)
        self.screen_5 = tk.Frame(self.master_screen)

        self.theme_update_req['frame'].extend(
            [
                self.root,
                self.main_screen,
                self.prompts_screen,
                self.master_screen,
                self.selector_panel,
                self.screen_0,
                self.screen_1,
                self.screen_2,
                self.screen_3,
                self.screen_4,
                self.screen_5
            ]
        )

        self.master_screen_index = 1

        self.master_screen_map = {
            1: self.main_screen,
            2: self.prompts_screen
        }

        # Global UI Elements
        self.error_label = tk.Label(self.root)
        self.theme_update_req['lbl'].append(self.error_label)
        self.theme_update_req['font'][self.error_label] = ('<face>', '<normal>')

        self.sep2 = ttk.Separator(self.main_screen, orient=tk.VERTICAL)
        self.sep_style = ttk.Style()
        self.sep_style.theme_use('alt')

        # Selector Panel
        self.selector_panel_app_name = tk.Label(self.selector_panel, text="Administrator\nTools")
        self.selector_panel_screen_0 = tk.Button(self.selector_panel, command=lambda: self.select_screen(0))
        self.selector_panel_screen_1 = tk.Button(self.selector_panel, command=lambda: self.select_screen(1))
        self.selector_panel_screen_2 = tk.Button(self.selector_panel, command=lambda: self.select_screen(2))
        self.selector_panel_screen_3 = tk.Button(self.selector_panel, command=lambda: self.select_screen(3))
        self.selector_panel_screen_4 = tk.Button(self.selector_panel, command=lambda: self.select_screen(4))
        self.selector_panel_screen_5 = tk.Button(self.selector_panel, command=lambda: self.select_screen(5))

        self.current_screen_index = 0

        self.theme_update_req['btn'].extend(
            [
                self.selector_panel_screen_0,
                self.selector_panel_screen_1,
                self.selector_panel_screen_2,
                self.selector_panel_screen_3,
                self.selector_panel_screen_4,
                self.selector_panel_screen_5,
            ]
        )

        self.theme_update_req['lbl'].extend([
            self.selector_panel_app_name
        ])
        self.theme_update_req['font'][self.selector_panel_app_name] = ("<face>", "<large>")
        self.theme_update_req['accent_fg'].append(self.selector_panel_app_name)

        self.selector_panel_mapper = {
            0: self.screen_0_packer,
            1: self.screen_1_packer,
            2: self.screen_2_packer,
            3: self.screen_3_packer,
            4: self.screen_4_packer,
            5: self.screen_5_packer,
        }

        self.theme_update_req['borderless'].extend(
            [
                self.selector_panel_screen_0,
                self.selector_panel_screen_1,
                self.selector_panel_screen_2,
                self.selector_panel_screen_3,
                self.selector_panel_screen_4,
                self.selector_panel_screen_5,
            ]
        )

        self.screen_info_mapper = {
            0: {
                'title': 'Information',
                'app_name': 'Administrator Tools',
                'description': """
Welcome to Administrator Tools, using this application, you can:
    (i) Modify the quiz configuration,
    (ii) Modify question databases,
    (iii) View scores, and modify them as well,
    (iv) Export quiz files,
    (v) Select an installed theme,
    And more!
    
    Change tabs on the left side to get started.
    Help files have been added wherever necessary.
                """,
                "button": self.selector_panel_screen_0
            },
            1: {
                'title': 'Configuration',
                'button': self.selector_panel_screen_1,
                'info1': """Should the quiz taker be allowed to configure the quiz themselves?""",
                'info2': """Should the quiz taker be presented with all questions, or only a sample of the question database?""",
                'cmd_1_r': False,
                'cmd_1_c': self.screen_1_aft_packer,
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

        self.screen_data = {
            0: {},
            1: {},
            2: {},
            3: {},
            4: {},
            5: {},
            '<<prompts>>': {
                'master_prompt_ask_custom': {
                    'theme': {}
                }
            }
        }

        c_raw = _load_configuration()
        c_key_data_file = AFIOObject(
            filename=qa_conf.Files.conf_std_file,
            isFile=True,
            encrypt=False
        )
        c_key_data = AFJSON(c_key_data_file.uid).load_file()['keys']
        c_key_data_file.delete_instance()
        del c_key_data_file

        for k, v in c_key_data.items():
            self.screen_data[1][k] = c_raw[v]

        self.screen_data[1]['saved_data'] = {**self.screen_data[1]}

        del c_key_data

        # Screen 0 elements [Intro]
        self.intro_title_lbl = tk.Label(self.screen_0, text=self.screen_info_mapper[0]['app_name'])
        self.intro_desc_lbl = tk.Label(self.screen_0, text=self.screen_info_mapper[0]['description'])
        self.intro_cr_lbl = tk.Label(self.screen_0, text=qa_conf.Application.cr)

        # Screen 0 Theming Requests
        self.theme_update_req['lbl'].extend(
            [
                self.intro_title_lbl,
                self.intro_desc_lbl,
                self.intro_cr_lbl
            ]
        )
        self.theme_update_req['font'][self.intro_desc_lbl] = ('<face>', '<medium>')
        self.theme_update_req['wraplength'].append(self.intro_desc_lbl)
        self.theme_update_req['font'][self.intro_title_lbl] = ('<face>', '<title>')
        self.theme_update_req['accent_fg'].append(self.intro_title_lbl)
        self.theme_update_req['font'][self.intro_cr_lbl] = ('<alt_face>', '<normal>')
        self.theme_update_req['accent_fg'].append(self.intro_cr_lbl)

        # Screen 1 elements [Configuration Screen]
        # Screen 1 containers
        self.configuration_allow_custom_config_container = tk.LabelFrame(self.screen_1)
        self.configuration_question_dist_config_container = tk.LabelFrame(self.screen_1)
        self.configuration_question_divF_container = tk.LabelFrame(self.configuration_question_dist_config_container)
        self.configuration_deductions_config_container = tk.LabelFrame(self.screen_1)
        self.configuration_deductions_amnt_container = tk.LabelFrame(self.configuration_deductions_config_container)

        # Screen 1 Elements
        self.config_acc_description_lbl = tk.Label(self.configuration_allow_custom_config_container)
        self.config_acc_action_btn = tk.Button(
            self.configuration_allow_custom_config_container,
            command=self.toggle_config_acc
        )
        self.config_save_btn = tk.Button(self.screen_1, text="Save Configuration", command=self.save_config)
        self.config_qs_pa_rnd_description_lbl = tk.Label(self.configuration_question_dist_config_container)
        self.config_qa_pa_rnd_selector_btn = tk.Button(self.configuration_question_dist_config_container, command=self.toggle_config_pa)

        # Screen 1 Theming Requests
        self.theme_update_req['lbl'].extend(
            [
                self.config_acc_description_lbl,
                self.config_qs_pa_rnd_description_lbl
            ]
        )
        for elem in (
                self.configuration_allow_custom_config_container,
                self.configuration_question_dist_config_container,
                self.configuration_question_divF_container,
                self.configuration_deductions_config_container,
                self.configuration_deductions_amnt_container,
                self.config_acc_description_lbl,
                self.config_acc_action_btn,
                self.config_qs_pa_rnd_description_lbl,
                self.config_qa_pa_rnd_selector_btn
        ):
            self.theme_update_req['font'][elem] = ('<face>', '<normal>')
        self.theme_update_req['btn'].extend(
            [
                self.config_acc_action_btn,
                self.config_save_btn,
                self.config_qa_pa_rnd_selector_btn
            ]
        )
        self.theme_update_req['borderless'].extend(
            [
                self.config_save_btn
            ]
        )
        self.theme_update_req['lbl_frame'].extend(
            [
                self.configuration_allow_custom_config_container,
                self.configuration_question_dist_config_container,
                self.configuration_question_divF_container,
                self.configuration_deductions_config_container,
                self.configuration_deductions_amnt_container
            ]
        )
        self.theme_update_req['font'][self.config_save_btn] = ("<face>", "<medium>")

        # Screen 2 elements [Question Editing Screen]
        # Screen 3 elements [Scores IO Screen]
        # Screen 4 elements [File IO Screen]
        # Screen 5 elements [Misc. Items Screen]

        # Calls
        self.start()
        self.init = True
        self.root.deiconify()
        self.root.mainloop()

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.close_window)
        self.root.title(
            f"Quizzing Application {qa_conf.ConfigFile.raw['app_data']['build']['frame_vid']} - Admin Tools"
        )
        self.root.geometry("%sx%s+%s+%s" % (*self.ws, *self.sp))
        self.root.iconbitmap(qa_conf.Files.app_icons['admin_tools']['ico'])

        self.error_label.pack(
            fill=tk.X,
            expand=False,
            side=tk.BOTTOM,
            padx=self.theme['padding']['x'],
            pady=(self.theme['padding']['y'], 0),
        )
        # Add the button panel (+ items)
        self.selector_panel.pack(fill=tk.BOTH, expand=False, side=tk.LEFT)
        self.selector_panel_app_name.pack(
            fill=tk.X,
            expand=False,
            padx=self.theme['padding']['x'],
            pady=self.theme['padding']['y'],
        )
        for ind, but in enumerate(
                (self.selector_panel_screen_0,
                 self.selector_panel_screen_1,
                 self.selector_panel_screen_2,
                 self.selector_panel_screen_3,
                 self.selector_panel_screen_4,
                 self.selector_panel_screen_5)
        ):
            self.theme_update_req['font'][but] = ('<face>', '<large>')
            but.config(text=self.screen_info_mapper[ind]['title'])
            but.pack(fill=tk.BOTH, expand=False, side=tk.TOP)

        self.sep2.pack(fill=tk.Y, expand=False, side=tk.LEFT)

        # Add the master screen
        self.master_screen.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT)
        self.select_screen(-1)
        self.update_ui()

        # Make visible
        self.master_screen_packer()

        self.root.bind('<Configure>', self.onFrameConfig)

    def close_window(self, code=0):
        self.show_error('')

        if self.master_screen_index == 2:
            self.show_error("Please answer the prompt above before exiting.")
            return

        config_us = {**self.screen_data[1]}
        del config_us['saved_data']
        for key in list(config_us.keys()):
            if key not in self.screen_data[1]['saved_data']:
                config_us.pop(key)

        if config_us != self.screen_data[1]['saved_data']:
            self.master_screen_index = 2
            self.master_screen_packer()
            self.master_prompt_ask_custom(
                'Unsaved Configuration',
                'You have made some changes to your configuration; do you want to save the new config. data before exiting?',
                ('Yes, Save New Data', lambda: self.save_config(True)),
                ('No, Do NOT Save New Data', lambda: g_exit(code)),
                ('Do not close application', self.go_back_to_main_screen),
                ttl_col_key='warning'
            )

        else:
            g_exit(code)

    def reload_data(self):
        self.show_error('')

        self.theme = _load_data('theme')
        self.theme_font_mapping = {
            '<normal>': self.theme['font']['main_size'],
            '<medium>': self.theme['font']['big_para_size'],
            '<large>': self.theme['font']['sttl_size'],
            '<title>': self.theme['font']['title_size'],
            '<face>': self.theme['font']['font_face'],
            '<alt_face>': self.theme['font']['alt_font_face']
        }

    def update_ui(self):
        self.show_error('')

        self.update_theme()
        self.update_buttons_theme()

    def update_theme(self, upd_buttons: bool = False):
        global _logger

        self.reload_data()

        command_map = {
            'bg_norm': lambda _elem: _elem.config(bg=self.theme['bg']),
            'fg_norm': lambda _elem: _elem.config(fg=self.theme['fg']),
            'bg_accent': lambda _elem: _elem.config(bg=self.theme['accent'], fg=self.theme['bg']),
            'fg_accent': lambda _elem: _elem.config(bg=self.theme['bg'], fg=self.theme['accent']),
            'active_state': lambda _elem: _elem.config(
                activebackground=self.theme['accent'], activeforeground=self.theme['bg']
            ),
            'borderless': lambda _elem: _elem.config(bd='0'),
            'wraplength': lambda _elem: _elem.config(
                wraplength=(self.ws[0] - self.selector_panel.winfo_width() - self.theme['padding']['x'] * 2)
            ),
            'invisible': lambda _elem: _elem.config(bg=self.theme['bg'], fg=self.theme['fg'], bd='0'),
            'button': lambda _elem: _elem.config(bd='1', highlightcolor=self.theme['accent'], relief=tk.GROOVE),
            'wraplength_no_sel_panel': lambda _elem: _elem.config(
                wraplength=(self.ws[0] - self.theme['padding']['x'] * 2)
            ),
        }

        for name, elem_list_and_commands in {
            'Label': ((*self.theme_update_req['lbl'],), ('bg_norm', 'fg_norm')),
            'Button': ((*self.theme_update_req['btn'],), ('bg_norm', 'fg_norm', 'active_state', 'button')),
            'LabelFrame': ((*self.theme_update_req['lbl_frame'],), ('bg_norm', 'fg_accent')),
            'Frame': ((*self.theme_update_req['frame'],), ('bg_norm',)),
            '<set_wraplength>': ((*self.theme_update_req['wraplength'],), ('wraplength',)),
            'InvisibleContainer': ((*self.theme_update_req['invis_container'],), ('invisible',)),
            'AccentFG': ((*self.theme_update_req['accent_fg'],), ('fg_accent',)),
            'AccentBG': ((*self.theme_update_req['accent_bg'],), ('bg_accent',)),
            '<set_wraplength_no_sel_panel>': (
                    (*self.theme_update_req['wraplength_no_sel_panel'],), ('wraplength_no_sel_panel',)),
            '<set_borderless>': ((*self.theme_update_req['borderless'],), ('borderless',))
        }.items():
            ls, commands = elem_list_and_commands
            for element in ls:
                for command_request in commands:
                    try:
                        command_map[command_request](element)
                    except Exception as E:
                        _logger.log(
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
                _logger.log(
                    'ERROR',
                    f'Failed to apply command "font" to "{element}" :: {E} :: {traceback.format_exc()}',
                    print_d=True
                )

        for element, bf in self.theme_update_req['custom_color'].items():
            try:
                bg, fg = bf
                element.config(bg=self.theme[bg], fg=self.theme[fg])

            except Exception as E:
                _logger.log(
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
                        c_args.append(self.theme[arg_N])
                    else:
                        c_args.append(arg_N)

                cc(*c_args)

                del c_args

            except Exception as E:
                print(E)
                _logger.log(
                    'ERROR',
                    f'Failed to run the attached command ({cc}) :: {E} :: {traceback.format_exc()}',
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

        self.config_save_btn.config(
            fg=self.theme['bg'],
            bg=self.theme['accent'],
            activeforeground=self.theme['accent'],
            activebackground=self.theme['bg'],
        )

        # TTK
        self.sep_style.configure('Horizontal.TSepartor', background=self.theme['accent'])
        self.sep_style.configure('Vertical.TSepartor', background=self.theme['accent'])

        # Calls
        if upd_buttons:
            self.update_buttons_theme()

        return

    def update_buttons_theme(self):
        self.toggle_config_acc(False)
        self.toggle_config_pa(False)

    def show_error(self, error: str):
        if not self.init:
            return

        self.error_label.config(text=error)

    def select_screen(self, index):
        assert index in (*self.selector_panel_mapper, -1), f"Invalid index '{index}'"
        if index != -1:
            self.current_screen_index = index

        self.clear_master_screen()
        self.selector_panel_mapper[self.current_screen_index]()
        self.update_ui()

    def master_screen_packer(self):
        try:
            for sc in list(self.master_screen_map.values()):
                try:
                    sc.pack_forget()
                except:
                    pass
        except:
            pass

        sc = self.master_screen_map[self.master_screen_index]
        sc.pack(fill=tk.BOTH, expand=True, pady=(self.theme['padding']['y'] * 2, 0))

    def screen_0_packer(self):
        # Reset
        self.reset_screen(0, self.screen_0)

        # Vars
        padX = self.theme['padding']['x']
        padY = self.theme['padding']['y']

        # Set
        self.intro_title_lbl.pack(fill=tk.X, expand=False, padx=padX, pady=(padY * 2, padY))
        self.intro_desc_lbl.pack(fill=tk.X, expand=False, padx=padX, pady=padY)
        self.intro_desc_lbl.config(justify=tk.LEFT)
        self.intro_cr_lbl.pack(fill=tk.BOTH, expand=False, padx=padX, pady=padY, side=tk.BOTTOM)
        self.intro_cr_lbl.config(anchor=tk.E, justify=tk.RIGHT)

        del padX, padY

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
            frame.pack(fill=tk.BOTH, expand=False, padx=padX, pady=padY)

        # Each Frame
        self.config_acc_action_btn.pack(fill=tk.X, expand=False, side=tk.RIGHT, ipadx=padX, padx=padX, pady=padY, ipady=padY)
        self.config_acc_description_lbl.config(
            text=self.screen_info_mapper[1]['info1'],
            wraplength=self.ws[
                           0] - self.selector_panel.winfo_width() - padX * 8 - self.config_acc_action_btn.winfo_width(),
            justify=tk.LEFT
        )
        self.config_acc_description_lbl.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=padX, pady=padY)

        self.config_qa_pa_rnd_selector_btn.config(text="Part")
        self.config_qa_pa_rnd_selector_btn.pack(fill=tk.X, expand=False, side=tk.RIGHT, ipadx=padX, padx=padX, pady=padY, ipady=padY)
        self.config_qs_pa_rnd_description_lbl.config(
            text=self.screen_info_mapper[1]['info2'],
            wraplength=self.ws[
                           0] - self.selector_panel.winfo_width() - padX * 8 - self.config_qa_pa_rnd_selector_btn.winfo_width(),
            justify=tk.LEFT
        )
        self.config_qs_pa_rnd_description_lbl.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=padX, pady=padY)

        # Save Button
        self.config_save_btn.pack(fill=tk.X, expand=False, padx=padX, pady=padY, ipadx=padX, ipady=padY, side=tk.BOTTOM)

        if not self.screen_info_mapper[1]['cmd_1_r']:
            self.screen_info_mapper[1]['cmd_1_r'] ^= True
            self.screen_info_mapper[1]['cmd_1_c']()

        del padX, padY

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
        self.show_error("")
        self.current_screen_index = index
        self.clear_master_screen()
        screen.pack(fill=tk.BOTH, expand=True)
        try:
            for item in screen.winfo_children():
                try:
                    item.pack_forget()
                except:
                    pass
        except:
            pass

    def clear_master_screen(self):
        for i in {
            self.screen_0, self.screen_1, self.screen_2, self.screen_3, self.screen_4, self.screen_5,
            *c(self.screen_0), *c(self.screen_1), *c(self.screen_2), *c(self.screen_3), *c(self.screen_4),
            *c(self.screen_5)
        }:
            try:
                i.pack_forget()
            except Exception as E:
                _logger.log(
                    'ERROR',
                    f"Failed to `pack_forget` `{i}` :: `{E}` - `{traceback.format_exc()}`",
                    print_d=True
                )

    def toggle_config_acc(self, change_state: bool = True):
        if change_state:
            self.screen_data[1]['config_acc'] ^= 1

        self.config_acc_action_btn.config(
            text='Enabled' if self.screen_data[1]['config_acc'] else 'Disabled'
        )

        self.config_acc_action_btn.config(
            bg=self.theme['accent' if self.screen_data[1]['config_acc'] else 'bg'],
            fg=self.theme['bg' if self.screen_data[1]['config_acc'] else 'fg'],
            highlightbackground=self.theme['accent'],
            bd='1'
        )

        self.config_acc_action_btn.update()

    def toggle_config_pa(self, change_state: bool = True):
        if change_state:
            m = {'p': 1, 'a': 0}
            self.screen_data[1]['qs_dist_pa'] ^= 1

        self.config_qa_pa_rnd_selector_btn.config(
            text='Part' if self.screen_data[1]['qs_dist_pa'] else 'All'
        )

        self.config_qa_pa_rnd_selector_btn.config(
            bg=self.theme['accent' if self.screen_data[1]['qs_dist_pa'] else 'bg'],
            fg=self.theme['bg' if self.screen_data[1]['qs_dist_pa'] else 'fg'],
            highlightbackground=self.theme['accent'],
            bd='1'
        )

    def save_config(self, close_after: bool = False):
        pus_config = {**self.screen_data[1]}
        s_d = pus_config['saved_data']
        for i in list(pus_config.keys()):
            if i not in s_d:
                del pus_config[i]

        if s_d == pus_config:
            self.show_error("No changes were made to the configuration.")
            return

        c_key_data_file = AFIOObject(
            filename=qa_conf.Files.conf_std_file,
            isFile=True,
            encrypt=False
        )
        c_key_data = AFJSON(c_key_data_file.uid).load_file()['keys']
        c_key_data_file.delete_instance()

        translated_pus_config = {}
        for k, v in c_key_data.items():
            translated_pus_config[v] = pus_config[k]

        res, reas = _save_configuration(translated_pus_config)

        if res:
            self.screen_data[1]['saved_data'] = pus_config

        del c_key_data

        if not res:
            self.master_screen_index = 2
            self.clear_prompts_screen()
            self.master_screen_packer()
            self.master_prompt_ask_custom(
                "Failed to Save Configuration",
                f"Reason: {reas}",
                ("Go Back", self.go_back_to_main_screen),
                ttl_col_key='error'
            )

        else:
            self.master_screen_index = 2
            self.clear_prompts_screen()
            self.master_screen_packer()
            self.master_prompt_ask_custom(
                "Saved Configuration Successfully",
                "Successfully saved configuration data to your custom configuration file.",
                ("Ok" if not close_after else "Exit",
                 self.go_back_to_main_screen if not close_after else lambda: g_exit(0)),
                ttl_col_key='ok'
            )

    def go_back_to_main_screen(self):
        self.clear_prompts_screen()
        self.clear_master_screen()
        self.master_screen_index = 1
        self.master_screen_packer()
        self.select_screen(-1)
        self.show_error('')

    def clear_prompts_screen(self):
        global _logger
        cl = c(self.prompts_screen)
        for child in cl:
            try:
                if child in self.theme_update_req['custom_command']:
                    del self.theme_update_req['custom_command'][child]
                child.pack_forget()
            except Exception as E:
                _logger.log(
                    'ERROR', f"Failed to `pack_forget` `{child}` :: `{E}` - {traceback.format_exc()}",
                    print_d=True
                )

    def master_prompt_ask_custom(self, title, description, *buttons, ttl_col_key: str = 'accent', btn_follow_ttl_col: bool = True):
        self.clear_prompts_screen()

        padX = self.theme['padding']['x']
        padY = self.theme['padding']['y']

        title_lbl = tk.Label(self.prompts_screen, text=title)
        description_lbl = tk.Label(self.prompts_screen, text=description)
        temp_ic_f_ic = tk.LabelFrame(self.prompts_screen)
        temp_ic = tk.LabelFrame(temp_ic_f_ic)

        description_lbl.config(justify=tk.LEFT)

        title_lbl.pack(fill=tk.BOTH, expand=False, padx=padX, pady=padY)
        description_lbl.pack(fill=tk.BOTH, expand=False, padx=padX, pady=padY)
        temp_ic.pack(fill=tk.BOTH, expand=False, padx=padX, pady=padY, side=tk.BOTTOM)
        temp_ic_f_ic.pack(fill=tk.BOTH, expand=True, padx=padX, pady=padY, side=tk.BOTTOM)

        for ind, (txt, com) in enumerate(buttons):
            temp_button = tk.Button(temp_ic, text=txt, command=com)
            temp_button.pack(fill=tk.X, expand=True, padx=padX, pady=padY, ipadx=padX / 2, ipady=padY / 2, side=tk.LEFT)

            self.theme_update_req['font'][temp_button] = ('<face>', '<medium>')
            self.theme_update_req['btn'].append(temp_button)
            self.theme_update_req['borderless'].append(temp_button)

            if btn_follow_ttl_col and ttl_col_key != 'accent':
                u = AFDATA.Functions.generate_uid()
                self.theme_update_req['custom_command'][u] = (
                    _UI_mpt_custom_button,
                    (
                        (False, temp_button),
                        (True, 'bg'),
                        (True, ttl_col_key)
                    )
                )

        self.theme_update_req['lbl'].extend([title_lbl, description_lbl])
        self.theme_update_req['custom_color'][title_lbl] = ('bg', ttl_col_key)
        self.theme_update_req['wraplength_no_sel_panel'].append(description_lbl)
        self.theme_update_req['font'][title_lbl] = ('<face>', '<title>')
        self.theme_update_req['font'][description_lbl] = ('<face>', '<normal>')
        self.theme_update_req['invis_container'].extend([temp_ic, temp_ic_f_ic])

        del padX, padY

        self.update_theme()

    def onFrameConfig(self, *event):
        self.screen_info_mapper[1]['cmd_1_r'] = False
        self.screen_info_mapper[1]['cmd_1_c']()
        self.ws = (self.root.winfo_width(), self.root.winfo_height())

    def screen_1_aft_packer(self):
        padX = self.theme['padding']['x']
        self.config_qs_pa_rnd_description_lbl.config(
            wraplength=(self.ws[0] - self.selector_panel.winfo_width() - padX * 8 - self.config_qa_pa_rnd_selector_btn.winfo_width()),
            justify=tk.LEFT
        )

        self.config_acc_description_lbl.config(
            wraplength= \
                self.ws[0] - self.selector_panel.winfo_width() - padX * 8 - \
                self.config_acc_action_btn.winfo_width(),
            justify=tk.LEFT
        )

        del padX

    def __del__(self):
        self.thread.join(self, 0)


_set_boot_progress(3)


def _UI_mpt_custom_button(button: tk.Button, background: str, accent: str) -> None:
    button.config(
        activeforeground=background,
        activebackground=accent,
        bg=background,
        fg=accent,
    )


def _load_data(data_key) -> any:
    data_key_mapper = {
        'theme': lambda: qa_theme.Theme.UserPref.pref()
    }

    assert data_key in data_key_mapper, f"Invalid data_key '{data_key}'"

    return data_key_mapper[data_key]()


def g_exit(code):
    global _logger
    _logger.log('EXIT INFO', f'Exiting with code: {code}')
    del _logger

    sys.exit(code)


def c(p):
    global _logger

    cl = set()
    for item in p.winfo_children():
        try:
            if len(item.winfo_children()) > 1:
                cl = {*cl, *c(item)}
            else:
                cl.add(item)
        except Exception as E:
            _logger.log(
                'ERROR',
                traceback.format_exc(), E,
                print_d=True
            )
    return cl


_set_boot_progress(4)


def _load_configuration() -> dict:
    global apptitle

    r = {}
    d = os.path.join(
        qa_conf.Files.qs_parent_dir['dst'],
        qa_conf.Files.configuration['filename']
    )
    s = os.path.abspath(
        os.path.join(
            qa_conf.Files.qs_parent_dir['src'],
            qa_conf.Files.configuration['filename']
        )
    )

    def load_file(p: str) -> dict:
        with open(p, 'r') as f:
            r = json.loads(f.read())
            f.close()
        return r

    d_dir = qa_conf.Files.qs_parent_dir['dst']

    if not os.path.exists(d_dir):
        os.makedirs(d_dir)

    del d_dir

    if not os.path.exists(d):
        if not os.path.exists(s):
            print(s)
            qa_splash_screen.hide(splObj)
            tkmsb.showerror(
                app_title,
                "[CRITICAL ERROR] Failed to find 'src:configuration.qaFile'"
            )
            g_exit(1)

        else:
            shutil.copy(s, d)

            qa_splash_screen.hide(splObj)
            tkmsb.showinfo(
                app_title,
                "Created 'dst:configuration.qaFile'"
            )
            qa_splash_screen.show(splObj)

            try:
                r = load_file(d)
                assert qa_diagnostics.Configuration.general(r)

            except:
                qa_splash_screen.hide(splObj)
                tkmsb.showerror(
                    app_title,
                    f"[CRITICAL ERROR] Invalid 'src:configuration.qaFile' file.\n\nTechnical:\n{traceback.format_exc()}"
                )
                g_exit(1)
    else:
        try:
            r = load_file(d)
            pa, c = qa_diagnostics.Configuration.general(r)
            try:
                assert pa
            except:
                raise Exception(c)

        except:
            try:
                os.remove(d)
            except FileNotFoundError:
                pass

            try:
                shutil.copy(s, d)
                r = load_file(d)
                pa, c = qa_diagnostics.Configuration.general(r)
                try:
                    assert pa
                except:
                    raise Exception(c)

            except:
                qa_splash_screen.hide(splObj)
                tkmsb.showerror(
                    app_title,
                    f"[CRITICAL ERROR] Invalid 'src:configuration.qaFile' file.\n\nTechnical:\n{traceback.format_exc()}"
                )
                qa_splash_screen.show(splObj)
                g_exit(1)

            qa_splash_screen.hide(splObj)
            tkmsb.showwarning(
                app_title,
                "Overwrote (reset) 'dst:configuration.qaFile' [invalid data found]"
            )
            qa_splash_screen.show(splObj)

    return r


def _save_configuration(config_data: dict) -> tuple:
    try:
        p, s = qa_diagnostics.Configuration.general(config_data)
    except Exception as E:
        return False, traceback.format_exc()

    if not p:
        return p, s

    d = os.path.join(
        qa_conf.Files.qs_parent_dir['dst'],
        qa_conf.Files.configuration['filename']
    )
    with open(d, 'w') as config_file:
        config_file.write(json.dumps(config_data, indent=4))
        config_file.close()

    return True, ""


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
                        j for j in version_notes[i]
                    ),
                    accent_key=_m[i],
                    degree="%s%s" % (i[0].upper(), i[1::].lower()),
                    use_tk=False
                )

        qa_splash_screen.show(splObj)

qa_splash_screen.set_smooth_progress(splObj, -1, _boot_steps)
del splRoot

AdminToolsUI()
