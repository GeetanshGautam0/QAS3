import conf, splash_screen
import tkinter as tk

boot_steps = {
    1: "Importing modules",
    2: "Loading Variables",
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
    if not conf.Control.doNotUseSplash:
        splash_screen.set_smooth_progress(splObj, index, boot_steps)


_set_boot_progress(1)

from tkinter import ttk
from tkinter import messagebox as tkmsb
from tkinter import filedialog as tkfldl
import threading, shutil, traceback, json, time, random, subprocess, sys, os, exceptions
import exceptions, prompts, pdf_gen, log_cleaner
from appfunctions import *
import online_version_check as ovcc


_set_boot_progress(2)

app_title = f"Administrator Tools {conf.ConfigFile.raw['app_data']['build']['frame_vid']}"

_set_boot_progress(3)

_set_boot_progress(4)

_set_boot_progress(5)

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
                    "The version of this app has the following notes associated with it:\n\n" + "\n\n\t *".join(j for j in version_notes[i]),
                    accent_key=_m[i],
                    degree="%s%s" % (i[0].upper(), i[1::].lower()),
                     use_tk=False
                )

        splash_screen.show(splObj)

splash_screen.set_smooth_progress(splObj, -1, boot_steps)

