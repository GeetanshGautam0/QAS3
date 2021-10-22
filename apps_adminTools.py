import conf, splash_screen
import tkinter as tk

app_title = f"Administrator Tools {conf.ConfigFile.raw['app_data']['build']['frame_vid']}"

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
_bg_frame.title(app_title + " - Background Frame")

if not conf.Control.doNotUseSplash:
    splRoot = tk.Toplevel()
    splObj = splash_screen.Splash(splRoot)
    splObj.setTitle("Administrator Tools")

    splash_screen.set_smooth_progress(splObj, 1, boot_steps)

from tkinter import ttk
from tkinter import messagebox as tkmsb
from tkinter import filedialog as tkfldl
import sys, os, json, online_version_check


splash_screen.set_smooth_progress(splObj, 6, boot_steps)
online_version_check.Check.check(splObj)
splash_screen.set_smooth_progress(splObj, -1, boot_steps)

