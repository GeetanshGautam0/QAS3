import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as tkmsb
import threading, os, sys, theme, conf, questions, prompts, colors
from appfunctions import *


class UI(threading.Thread):
    def __init__(self):
        super().__init__()
        self.thread = threading.Thread
        self.thread.__init__(self)

        theme.reload_theme()
        # theme.find_preference()
        self.theme = theme.Theme.UserPref.m(theme.TMODE)

        self.root = tk.Toplevel()

        self.vsb_style = ttk.Style()
        self.vsb_style.theme_use('default')

        self.sep_style = ttk.Style()
        self.sep_style.theme_use('default')

        self.canv = tk.Canvas(self.root)
        self.frame = tk.Frame(self.root)
        self.vsb = ttk.Scrollbar(self.root)

        self.question_entry = tk.Text(self.frame)
        self.questionLbl = tk.Label(self.frame, text="Enter Question")
        self.answer_entry = tk.Text(self.frame)
        self.answerLbl = tk.Label(self.frame, text="Enter Correct Answer")

        self.selContainer = tk.LabelFrame(self.frame, bd='0', bg=self.theme.get('bg'))
        self.mcSel = tk.Button(self.selContainer, text="Multiple Choice", command=self.mc_click)
        self.tfSel = tk.Button(self.selContainer, text="True/False", command=self.tf_click)
        self.submitButton = tk.Button(self.frame, text="Add Question", command=self.add)

        self.clearButton = tk.Button(self.frame, text="Delete All Questions", command=self.delAll)
        self.helpButton = tk.Button(self.frame, text="Click here to\n view instructions", command=self.help)

        self.sep = ttk.Separator(self.frame)

        self.ss = (self.root.winfo_screenwidth(), self.root.winfo_screenheight())
        self.ws = conf.AppContainer.Apps.admin_tools['question_entry']['ws']
        self.wp = [
            int(self.ss[0] / 2 - self.ws[0] / 2),
            int(self.ss[1] / 2 - self.ws[1] / 2)
        ]

        # Theme data sets
        self.theme_label: list = []
        self.theme_label_font: dict = {}
        self.theme_button: list = []
        self.theme_accent: list = []

        self.mc = False
        self.tf = False

        self.start()
        self.root.attributes('-topmost', 1)
        self.root.attributes('-topmost', 0)
        self.root.mainloop()

    def run(self):
        # Root configuration
        self.root.geometry(f"{self.ws[0]}x{self.ws[1]}+{self.wp[0]}+{self.wp[1]}")
        self.root.resizable(False, True)
        self.root.minsize(self.ws[0], int(self.ws[1] / 2))
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.title("Quizzing Application - Add Question")
        self.root.iconbitmap(conf.Files.app_icons['admin_tools']['ico'])

        # Widget configuration + placement
        # The basic back
        self.canv.pack(fill=tk.BOTH, expand=1, side=tk.LEFT)
        self.vsb.pack(fill=tk.Y, expand=False, side=tk.RIGHT)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # The actual control

        ttl = tk.Label(self.frame, text="Add Question")
        ttl.pack(fill=tk.BOTH, expand=False, padx=5, pady=5)

        self.theme_label.append(ttl)
        self.theme_accent.append(ttl)
        self.theme_label_font[ttl] = (
            self.theme.get('font').get('font_face'),
            32
        )

        self.helpButton.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 5))
        self.theme_button.append(self.helpButton)
        self.theme_label_font[self.helpButton] = (
            self.theme.get('font').get('font_face'),
            16
        )

        self.sep.pack(fill=tk.X, expand=True, padx=5)

        self.questionLbl.config(anchor=tk.SW)
        self.theme_label.append(self.questionLbl)
        self.theme_accent.append(('bg', self.theme.get('bg'), self.questionLbl))

        self.questionLbl.pack(fill=tk.X, expand=True, padx=10, pady=(5, 0))
        self.question_entry.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 5))

        self.answerLbl.config(anchor=tk.SW)
        self.theme_label.append(self.answerLbl)
        self.theme_accent.append(('bg', self.theme.get('bg'), self.answerLbl))

        self.answerLbl.pack(fill=tk.X, expand=True, padx=10)
        self.answer_entry.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 5))

        self.selContainer.pack(fill=tk.BOTH, expand=True, padx=10)
        self.mcSel.pack(fill=tk.BOTH, expand=True, pady=(0, 5), padx=(0, 5), side=tk.LEFT)
        self.tfSel.pack(fill=tk.BOTH, expand=True, pady=(0, 5), padx=(5, 0), side=tk.RIGHT)
        self.theme_button.append(self.mcSel)
        self.theme_button.append(self.tfSel)
        self.theme_label_font[self.mcSel] = (
            self.theme.get('font').get('font_face'),
            14
        )
        self.theme_label_font[self.tfSel] = (
            self.theme.get('font').get('font_face'),
            14
        )

        self.submitButton.pack(
            fill=tk.BOTH,
            expand=True,
            padx=(10, 5),
            pady=(0, 5),
            side=tk.LEFT
        )
        self.theme_button.append(self.submitButton)
        self.theme_label_font[self.submitButton] = (
            self.theme.get('font').get('font_face'),
            14
        )

        self.clearButton.pack(
            fill=tk.BOTH,
            expand=True,
            padx=(10, 5),
            pady=(0, 5),
            side=tk.RIGHT
        )
        self.theme_label_font[self.clearButton] = (
            self.theme.get('font').get('font_face'),
            14
        )

        # ttk :: SB conf. (After widget placement)
        self.vsb.configure(command=self.canv.yview)

        self.canv.configure(
            yscrollcommand=self.vsb.set
        )

        self.canv.create_window(
            (0, 0),
            window=self.frame,
            anchor="nw",
            tags="self.frame"
        )

        # self.frame.config(
        #     width=(self.ws[0] - self.vsb.winfo_width())
        # )

        # Final Things
        self.update()

        # Event Handlers
        self.frame.bind("<Configure>", self.onFrameConfig)
        # self.frame.bind_all("<MouseWheel>", self._on_mousewheel)

        self.canv.yview_scroll(1, "units")
        self.root.update()
        self.canv.update()
        self.vsb.update()

        self.canv.yview_scroll(-1, "units")
        self.root.update()
        self.canv.update()
        self.vsb.update()

    def _on_mousewheel(self, event):
        """
        Straight out of stackoverflow
        Article: https://stackoverflow.com/questions/17355902/tkinter-binding-mousewheel-to-scrollbar
        Change
        : added "int" around the first arg
        """
        # self.canv.yview_scroll(int(-1 * (event.delta / 120)), "units")
        pass

    def onFrameConfig(self, event):  # for scbar
        self.canv.configure(
            scrollregion=self.canv.bbox("all")
        )

    def close(self):
        if __name__ == "__main__":
            sys.exit("WM_DELETE_WINDOW")
        else:
            self.root.after(0, self.root.destroy)
            return

    def update_theme(self):
        # Pre
        theme.reload_theme()
        self.theme = theme.Theme.UserPref.m(theme.TMODE)

        # TTK
        self.vsb_style.configure(
            "TScrollbar",
            background=self.theme.get('bg'),
            arrowcolor=self.theme.get('fg'),
            bordercolor=self.theme.get('bg'),
            troughcolor=self.theme.get('bg')
        )

        self.vsb_style.map(
            "TScrollbar",
            background=[
                ("active", self.theme.get('accent')), ('disabled', self.theme.get('bg'))
            ]
        )

        self.sep_style.configure(
            "TSeparator",
            background=self.theme.get('fg')
        )

        # TK
        self.root.config(
            bg=self.theme.get('bg')
        )

        self.canv.config(
            bg=self.theme.get('bg')
        )

        self.frame.config(
            bg=self.theme.get('bg')
        )

        self.question_entry.config(
            bg=self.theme.get('bg'),
            fg=self.theme.get('fg')
        )

        self.answer_entry.config(
            bg=self.theme.get('bg'),
            fg=self.theme.get('fg')
        )

        # self.theme_label: list = []
        # self.theme_label_font: dict = {}
        # self.theme_button: list = []
        # theme_accent: list = []

        for i in self.theme_label:
            try:
                i.config(
                    bg=self.theme.get('bg'),
                    fg=self.theme.get('fg')
                )

            except:
                print('sdfsjhfhsdf', i)

        for i in self.theme_label_font:
            try:
                i.config(
                    font=self.theme_label_font.get(i)
                )

            except:
                print('sdfsasdjhfhsdf', i)

        for i in self.theme_button:
            try:
                i.config(
                    bg=self.theme.get('bg'),
                    fg=self.theme.get('fg'),
                    activebackground=self.theme.get('accent'),
                    activeforeground=colors.Functions.calculate_nearer(self.theme['bg'], self.theme['fg'], self.theme['accent']),
                    bd=0
                )

            except:
                print('sdfsassdfdjhfhsdf', i)

        for i in self.theme_accent:
            try:
                if type(i) is tuple or type(i) is list:

                    if i[0] == 'bg':
                        i[-1].config(
                            bg=self.theme.get('accent'),
                            fg=i[1]
                        )

                else:
                    i.config(
                        fg=self.theme.get('accent')
                    )

            except:
                print('sdfsjhsdffhsdf', i)

        # Exceptions
        self.clearButton.config(
            bg="red",
            fg="white",
            activebackground="white",
            activeforeground="red",
            bd=0
        )

        self.question_entry.config(
            selectbackground=self.theme.get('accent'),
            selectforeground=colors.Functions.calculate_nearer(self.theme['bg'], self.theme['fg'], self.theme['accent']),
            wrap=tk.WORD,
            font=(
                self.theme.get('font').get('font_face'),
                11
            )
        )

        self.answer_entry.config(
            selectbackground=self.theme.get('accent'),
            selectforeground=colors.Functions.calculate_nearer(self.theme['bg'], self.theme['fg'], self.theme['accent']),
            wrap=tk.WORD,
            font=(
                self.theme.get('font').get('font_face'),
                11
            )
        )

    def update(self):
        self.update_theme()

    def help(self):
        pdf = conf.Files.help['question_entry']
        os.startfile(f"\"{pdf}\"")

    def reformat_buttons(self):
        self.mcSel.config(
            bg=self.theme.get('accent' if self.mc else 'bg'),
            fg=colors.Functions.calculate_nearer(self.theme['bg'], self.theme['fg'], self.theme['accent']) if self.mc else self.theme.get('fg'),
            text=(
                    self.mcSel.cget('text').replace('\u2713', '').strip() + (' \u2713' if self.mc else '')
            )
        )

        self.tfSel.config(
            bg=self.theme.get('accent' if self.tf else 'bg'),
            fg=colors.Functions.calculate_nearer(self.theme['bg'], self.theme['fg'], self.theme['accent']) if self.tf else self.theme.get('fg'),
            text=(
                    self.tfSel.cget('text').replace('\u2713', '').strip() + (' \u2713' if self.tf else '')
            )
        )

    def mc_click(self):
        self.mc = not self.mc
        self.tf = False if self.mc else self.tf

        self.reformat_buttons()

    def tf_click(self):
        self.tf = not self.tf
        self.mc = False if self.tf else self.mc

        self.reformat_buttons()

    def delAll(self):
        confirm = tkmsb.askyesno(
            "Delete All Questions",
            "Are you sure you want to delete all questions? This process cannot be undone."
        )
        if not confirm: return

        filename = os.path.join(
            conf.Application.AppDataLoc,
            conf.Files.questions_and_answers['filename']
        )

        extension = filename.split('.')[-1]

        if not os.path.exists(conf.Application.AppDataLoc):
            os.makedirs(conf.Application.AppDataLoc)

        file = AFIOObject(
            filename=filename,
            isFile=True,
            encrypt=conf.Files.files[extension]['encrypt'],
            encoding=conf.Files.files[extension]['encoding'],
            owr_exs_err_par_owr_meth=True
        )

        if conf.Files.files[extension]['encrypt']:
            file.edit_flag(enc_key=conf.Encryption.file[extension])

        AFFileIO(file.uid).save('', append=False)

        prompts.TextPrompts.BasicTextPrompt(
            "Successfully deleted all questions.",
            degree="Deleted Questions",
            accent_key="ok"
        )

    def add(self):

        mc_code = conf.FileCodes.question_codes['mc']['question']
        tf_code = conf.FileCodes.question_codes['tf']
        nm_code = conf.FileCodes.question_codes['normal']

        q = self.question_entry.get("1.0", "end-1c").strip()
        a = self.answer_entry.get("1.0", "end-1c").strip()

        if not(len(q) and len(a)):
            prompts.TextPrompts.ErrorPrompt.Handled(
                "Error: Please enter a question and an answer.\n\nIf you wish to cancel, you can close the ui by clicking the 'X' button on the top of the ui.",
                use_tk=False
            )

            return

        data = questions.Conversions.convertToQuestionStr(
            ((mc_code if self.mc else tf_code if self.tf else nm_code) + " " + q),
            a
        )

        filename = os.path.join(
            conf.Application.AppDataLoc,
            conf.Files.questions_and_answers['filename']
        )

        extension = filename.split('.')[-1]

        if not os.path.exists(conf.Application.AppDataLoc):
            os.makedirs(conf.Application.AppDataLoc)

        file = AFIOObject(
            filename=filename,
            isFile=True,
            encrypt=conf.Files.files[extension]['encrypt'],
            encoding=conf.Files.files[extension]['encoding'],
            owr_exs_err_par_owr_meth=True
        )

        if conf.Files.files[extension]['encrypt']:
            print(conf.Encryption.file[extension])
            file.edit_flag(enc_key=conf.Encryption.file[extension])

        AFFileIO(file.uid).secure_save(
            data,
            append=True
        )

        self.submitButton.config(
            state=tk.DISABLED,
            disabledforeground=self.theme['gray']
        )

        self.clearButton.config(
            state=tk.DISABLED,
            background=self.theme.get('bg'),
            disabledforeground=self.theme['gray']
        )

        self.helpButton.config(
            state=tk.DISABLED,
            background=self.theme.get('bg'),
            disabledforeground=self.theme['gray']
        )

        tkmsb.showinfo("QAS", "Added question successfully")

        self.close()

    def __del__(self):
        self.thread.join(self, 0)


if __name__ == "__main__":
    UI()
