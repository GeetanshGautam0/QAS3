import json, urllib3, qa_conf as conf, qa_splash_screen as splash_screen
from tkinter import messagebox as tkmsb
import tkinter as tk

_bg = tk.Tk()
_bg.withdraw()
_bg.title("Quizzing Application - Version Checker")

url = conf.URL.version_check
http = urllib3.PoolManager(
    timeout=urllib3.Timeout(connect=1.0, read=1.5),
    retries=False
)


class Check:
    @staticmethod
    def latest():
        global url, http

        curr = conf.ConfigFile.raw['app_data']['build']['version_id']

        try:
            REQ = http.request('GET', url)
        except:
            return "%s::%s" % (
                curr,
                conf.ConfigFile.raw['app_data']['build']['build_id']
            )

        _data = REQ.data
        _r = json.loads(_data)
        _key = _r['map'][curr[0]]
        _vers = _r[_key]['latest']
        _build = _r[_key]['build']

        return "%s::%s" % (_vers, _build)

    @staticmethod
    def check(splash: tk.Toplevel = None):
        global url, http

        curr = conf.ConfigFile.raw['app_data']['build']['version_id']

        try:
            REQ = http.request('GET', url)
        except:
            return True

        _data = REQ.data
        _r = json.loads(_data)
        _key = _r['map'][curr[0]]
        _vers = _r[_key]['latest']

        appro = _r[_key]['versions']
        if curr not in appro:
            if isinstance(splash, tk.Toplevel):
                splash_screen.hide(splash)

            tkmsb.showerror(
                "Version Checker",
                "Failed to check version information - code 1."
            )

            if isinstance(splash, tk.Toplevel):
                splash_screen.show(splash)

        _v_div_curr = (*curr.split("."), )
        _v_div_lats = (*_vers.split("."), )

        for ind, value in enumerate(_v_div_curr):
            if _v_div_lats[ind] > value:

                if isinstance(splash, tk.Toplevel):
                    splash_screen.hide(splash)

                tkmsb.showinfo(
                    "Version Checker",
                    "A new version of the application is available; download is available at geetanshgautam.wixsite.com/home."
                )

                if isinstance(splash, tk.Toplevel):
                    splash_screen.show(splash)

                return False

            elif _v_div_lats[ind] < value:
                if isinstance(splash, tk.Toplevel):
                    splash_screen.hide(splash)

                tkmsb.showerror(
                    "Version Checker",
                    "Failed to check version information."
                )

                if isinstance(splash, tk.Toplevel):
                    splash_screen.show(splash)

                return True

        if _r[_r['map']['v']]['any_avail'] and curr[0] != 'v':
            if isinstance(splash, tk.Toplevel):
                splash_screen.hide(splash)

            tkmsb.showinfo(
                "Version Checker",
                "The build that you have installed is not a stable build; consider installing a stable build."
            )

            if isinstance(splash, tk.Toplevel):
                splash_screen.show(splash)

        return True

    @staticmethod
    def find_comments():
        global url, http

        try:
            REQ = http.request('GET', url)
        except:
            return None

        curr = conf.ConfigFile.raw['app_data']['build']['version_id']

        _data = REQ.data
        _r = json.loads(_data)
        _notes = _r['notes'][_r['map'][curr[0]]].get(curr)

        return _notes
