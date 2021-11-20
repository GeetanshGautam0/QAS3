import qa_conf, qa_splash_screen
import tkinter as tk

_boot_steps = {
    1: "Importing modules",
    2: "Loading Globals",
    3: "Loading Functions",
    4: "Loading Configuration",
    5: "Running Boot Checks",
    6: "Fetching Version Information"
}

_bg_frame = tk.Tk()
_bg_frame.deiconify()
_bg_frame.withdraw()
_bg_frame.title("QA Administrator Tools - Background Frame")

if not conf.Control.doNotUseSplash:
    splRoot = tk.Toplevel()
    splObj = splash_screen.Splash(splRoot)
    splObj.setTitle("Administrator Tools")
else:
    splObj = None


def _set_boot_progress(index):
    if not qa_conf.Control.doNotUseSplash:
        splash_screen.set_smooth_progress(splObj, index, _boot_steps)


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


class AdminToolsUI(threading.Thread):
    def __init__(self):
        super().__init__()
        self.thread = threading.Thread
        self.thread.__init__(self)

        # Roots
        self.root_bg = tk.Tk()
        self.root_bg.withdraw()
        self.root_bg.title(f"QA_AdminToolsUI{qa_conf.ConfigFile.raw['app_data']['build']['frame_vid']}_backgroundFrame")
        self.root = tk.Toplevel()
        self.root.withdraw()

        # Theming Updates
        self.theme = _load_data('theme')

        # Screens
        self.master_screen = tk.Frame(self.root)
        self.selector_panel = tk.Frame(self.root)
        self.screen_1 = tk.Frame(self.master_screen)
        self.screen_2 = tk.Frame(self.master_screen)
        self.screen_3 = tk.Frame(self.master_screen)
        self.screen_4 = tk.Frame(self.master_screen)
        self.screen_5 = tk.Frame(self.master_screen)

        # Selector Panel
        self.selector_panel_screen_1 = tk.Button(self.selector_panel, command=lambda: self.select_screen(1))
        self.selector_panel_screen_2 = tk.Button(self.selector_panel, command=lambda: self.select_screen(2))
        self.selector_panel_screen_3 = tk.Button(self.selector_panel, command=lambda: self.select_screen(3))
        self.selector_panel_screen_4 = tk.Button(self.selector_panel, command=lambda: self.select_screen(4))
        self.selector_panel_screen_5 = tk.Button(self.selector_panel, command=lambda: self.select_screen(5))

        self.selector_panel_mapper = {
            1: self.screen_1,
            2: self.screen_2,
            3: self.screen_3,
            4: self.screen_4,
            5: self.screen_5,
        }

        self.screen_info_mapper = {
            1: {
                'title': 'Configuration'
            },
            2: {
                'title': 'Question Database Editor'
            },
            3: {
                'title': 'Scores File IO'
            },
            4: {
                'title': 'General File IO'
            },
            5: {
                'title': 'Miscellaneous Items'
            },
        }

        # Screen 1 elements [Configuration Screen]
        # Screen 2 elements [Question Editing Screen]
        # Screen 3 elements [Scores IO Screen]
        # Screen 4 elements [File IO Screen]
        # Screen 5 elements [Misc. Items Screen]

        # Calls
        self.start()
        self.root.deiconify()
        self.root.mainloop()

    def run(self):
        pass

    def select_screen(self, index):
        assert index in self.selector_panel_mapper, f"Invalid index '{index}'"

    def __del__(self):
        self.thread.join(self, 0)


_set_boot_progress(3)


def _load_data(data_key) -> any:
    data_key_mapper = {
        'theme': [
            lambda: 2
        ]
    }


_set_boot_progress(4)

# Any loading logic goes here

_set_boot_progress(5)

# Check loaded data here

_set_boot_progress(6)

ovcc.Check.check(splObj)
version_notes = ovcc.Check.find_comments()
if version_notes is not None:
    if len(version_notes) > 0:

        splash_screen.hide(splObj)

        _m = {
            'error': 'error',
            'warning': 'warning',
            'info': 'accent'
        }
        for i in ['error', 'warning', 'info']:  # In this order
            if i in version_notes:
                prompts.TextPrompts.BasicTextPrompt(
                    "The version of this app has the following notes associated with it:\n\n" + "\n\n\t *".join(
                        j for j in version_notes[i]),
                    accent_key=_m[i],
                    degree="%s%s" % (i[0].upper(), i[1::].lower()),
                    use_tk=False
                )

        splash_screen.show(splObj)

splash_screen.set_smooth_progress(splObj, -1, _boot_steps)
