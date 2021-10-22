import time
from tkinter import *
import tkinter.ttk as ttk
import conf, colors, os
import theme as qa_theme

qa_theme.find_preference()
theme = qa_theme.Theme.UserPref.m(qa_theme.TMODE)


class Splash(Toplevel):
    def __init__(self, master=None):
        global theme

        if conf.Control.doNotUseSplash:
            return

        self.root = master
        self.frame = Frame(self.root)

        self.geo = "%sx%s+%s+%s" % (
            conf.AppContainer.Splash.geo[0],
            conf.AppContainer.Splash.geo[1],
            int(self.root.winfo_screenwidth() / 2 - conf.AppContainer.Splash.geo[0] / 2),
            int(self.root.winfo_screenheight() / 2 - conf.AppContainer.Splash.geo[1] / 2)
        )

        self.titleLbl = Label(self.frame)
        self.imgLbl = Button(self.frame, anchor=NE)
        self.pbar = ttk.Progressbar(self.frame, length=100, mode='determinate', orient=HORIZONTAL)
        self.infoLbl = Label(self.frame, justify=LEFT)

        self.title = "Quizzing Application"
        self.information = "Coding Made Fun"
        self.img = conf.Files.app_icons['quizzing_tool']['ico']

        self.ac_start = theme['fg']
        self.ac_end = theme['accent']
        self.loadGrad = True
        self.grad = [self.ac_start]
        self.complete = False

        self.pbarStyle = ttk.Style()
        self.pbarStyle.theme_use('default')

        self.pbarStyle.configure(
            "Horizontal.TProgressbar",
            foreground=self.ac_start,
            background=self.ac_start,
            troughcolor=theme['bg'],
            borderwidth=0,
            thickness=2
        )

        # UI Config
        self.run()

        # UI Update
        self.root.update()

    def run(self):
        self.root.geometry(self.geo)
        self.root.overrideredirect(True)
        self.root.protocol("WM_DELETE_WINDOW", lambda: destroy(self))
        self.root.wm_attributes('-topmost', 1)
        self.root.iconbitmap(self.img)

        self.frame.pack(fill=BOTH, expand=True)
        self.frame.config(bg=theme['bg'])

        self.titleLbl.config(
            text=self.title,
            bg=theme.get('bg'),
            fg=theme.get('fg'),
            font=(theme.get('font')['font_face'], 36),
            anchor=SW
        )

        self.infoLbl.config(
            text=self.information,
            bg=theme.get('bg'),
            fg=theme.get('fg'),
            font=(theme.get('font')['font_face'], theme.get('font')['main_size']),
            anchor=NW
        )

        self.titleLbl.pack(fill=BOTH, expand=True, padx=5)
        self.pbar.pack(fill=X, expand=1)
        self.infoLbl.pack(fill=X, expand=True, padx=5)

        self.root.update()

    def completeColor(self) -> None:
        global theme
        compTheme = theme
        self.complete = True

        self.pbarStyle.configure(
            "Horizontal.TProgressbar",
            foreground=compTheme.get('ac'),
            background=compTheme.get('ac'),
            troughcolor=theme.get('bg')
        )
        self.titleLbl.config(
            fg=compTheme.get('ac'),
            bg=compTheme.get('bg')
        )
        self.frame.config(
            bg=compTheme.get('bg')
        )
        self.infoLbl.config(
            bg=compTheme.get('bg'),
            fg=compTheme.get('fg')
        )

        self.root.update()

    def changePbar(self, per: float) -> None:
        if self.loadGrad:
            self.grad = colors.Fade.mono(self.ac_start, self.ac_end)
            self.loadGrad = False

        self.pbar['value'] = per

        if not self.complete:
            self.pbarStyle.configure(
                "Horizontal.TProgressbar",
                background=self.grad[int((len(self.grad) - 1) * (per / 100) * 0.8)],
                foreground=self.grad[int((len(self.grad) - 1) * (per / 100) * 0.8)],
                troughcolor=theme.get('bg')
            )
            self.titleLbl.config(fg=self.grad[int((len(self.grad) - 1) * per / 100)])

        self.pbar.configure(
            style="Horizontal.TProgressbar"
        )

        self.root.update()

    def setInfo(self, text) -> None:
        self.information = text.strip()
        self.infoLbl.config(text=self.information)
        self.root.update()

    def setTitle(self, text: str) -> None:
        self.title = text.strip()
        self.titleLbl.config(text=self.title)
        self.root.update()

    def update(self) -> None:
        self.root.update()


def Pass(): pass


def hide(inst: Splash):
    if conf.Control.doNotUseSplash:
        return

    inst.root.overrideredirect(False)
    inst.root.wm_attributes("-topmost", 0)
    inst.root.iconify()
    inst.root.withdraw()
    inst.root.update_ui()
    return


def show(inst: Splash):
    if conf.Control.doNotUseSplash:
        return

    inst.root.overrideredirect(True)
    inst.root.deiconify()
    inst.root.wm_attributes("-topmost", 1)
    inst.root.update_ui()
    return


def destroy(inst: Splash):
    if conf.Control.doNotUseSplash:
        return

    inst.root.after(0, inst.root.destroy)
    return


def set_smooth_progress(inst: Splash, ind, boot_steps, resolution=100):
    if conf.Control.doNotUseSplash:
        return

    total_boot_steps = len(boot_steps)
    inst.setInfo(boot_steps[ind+1])
    index = ind - 1
    prev = ind - 1 if ind > 0 else ind

    colors.clamp(0, index, len(boot_steps) - 1)
    colors.clamp(0, prev, len(boot_steps) - 1)

    for i in range(prev*resolution, ind*resolution):
        for _ in range(20): pass

        inst.changePbar((i/total_boot_steps)/(resolution/100))

    print(prev, index, ind, total_boot_steps)

    if ind >= total_boot_steps - 1:
        inst.completeColor()
        inst.setInfo("Completed Boot Process")

        index = total_boot_steps - 1
        for i in range(index*resolution, total_boot_steps*resolution):
            for _ in range(20): pass
            inst.changePbar((i / total_boot_steps) / (resolution / 100))
        time.sleep(0.5)

        destroy(inst)
