import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as tkmsb
import threading, os, sys, theme, conf, questions, prompts, colors

import lookups
from appfunctions import *


class UI(threading.Thread):
    def __init__(self):
        super().__init__()
        self.thread = threading.Thread
        self.thread.__init__(self)

        theme.reload_default()
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
        self.xsb = ttk.Scrollbar(self.root, orient=tk.HORIZONTAL)

        self.cont_q = tk.LabelFrame(self.frame)
        self.cont_a = tk.LabelFrame(self.frame)
        self.question_entry = tk.Text(self.cont_q)
        self.questionLbl = tk.Label(self.cont_q, text="Enter Question")
        self.answer_entry = tk.Text(self.cont_a)
        self.answerLbl = tk.Label(self.cont_a, text="Enter Correct Answer")

        self.selContainer = tk.LabelFrame(self.root)
        self.mcSel = tk.Button(self.selContainer, text="Multiple Choice", command=self.mc_click)
        self.tfSel = tk.Button(self.selContainer, text="True/False", command=self.tf_click)
        self.sel_case_sens = tk.Button(self.selContainer, text="Case Sensitive Response", command=self.cs_response_click)

        self.set_cont = tk.LabelFrame(self.root)
        self.submitButton = tk.Button(self.set_cont, text="Add Question", command=self.add)
        self.clearButton = tk.Button(self.set_cont, text="Delete All Questions", command=self.delAll)
        self.helpButton = tk.Button(self.root, text="Click here to view instructions", command=self.help)

        self.sep = ttk.Separator(self.frame)

        self.ss = (self.root.winfo_screenwidth(), self.root.winfo_screenheight())
        self.ws = conf.AppContainer.Apps.admin_tools['question_entry']['ws']
        self.wp = [
            int(self.ss[0] / 2 - self.ws[0] / 2),
            int(self.ss[1] / 2 - self.ws[1] / 2)
        ]

        # Theme data sets
        self.theme_label = []
        self.theme_label_font = {}
        self.theme_button = []
        self.theme_accent = []
        self.theme_invis_cont = []

        self.mc = False
        self.tf = False
        self.cs = False

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
        # The actual control

        ttl = tk.Label(self.root, text="Add Question", wraplength=self.ws[0]-10)
        ttl.pack(fill=tk.BOTH, expand=False, padx=5, pady=5)

        self.theme_label.append(ttl)
        self.theme_accent.append(ttl)
        self.theme_label_font[ttl] = (
            self.theme.get('font').get('font_face'),
            32
        )

        self.helpButton.config(wraplength=self.ws[0]-10)
        self.helpButton.pack(fill=tk.BOTH, expand=False, padx=10, pady=(0, 5))
        self.theme_button.append(self.helpButton)
        self.theme_label_font[self.helpButton] = (
            self.theme.get('font').get('font_face'),
            16
        )

        self.sep.pack(fill=tk.X, expand=True, padx=5)

        self.theme_invis_cont.extend(
            [self.cont_a, self.cont_q, self.set_cont, self.selContainer]
        )
        self.cont_q.pack(fill=tk.X, expand=False)
        self.cont_a.pack(fill=tk.BOTH, expand=False)
        self.questionLbl.config(anchor=tk.SW)
        self.theme_label.append(self.questionLbl)
        self.theme_accent.append(('bg', self.theme.get('bg'), self.questionLbl))

        self.questionLbl.pack(fill=tk.X, expand=True, padx=5, pady=(5, 0))
        self.question_entry.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))

        self.answerLbl.config(anchor=tk.SW)
        self.theme_label.append(self.answerLbl)
        self.theme_accent.append(('bg', self.theme.get('bg'), self.answerLbl))

        self.answerLbl.pack(fill=tk.X, expand=True, padx=5, pady=(5, 0))
        self.answer_entry.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))

        self.mcSel.pack(fill=tk.BOTH, expand=True, pady=(0, 5), padx=(0, 5), side=tk.LEFT)
        self.tfSel.pack(fill=tk.BOTH, expand=True, pady=(0, 5), padx=(5, 0), side=tk.LEFT)
        self.sel_case_sens.pack(fill=tk.BOTH, expand=True, pady=(0, 5), padx=(5, 0), side=tk.RIGHT)
        self.theme_button.extend([
            self.mcSel, self.tfSel, self.sel_case_sens
        ])
        self.theme_label_font[self.mcSel] = (
            self.theme.get('font').get('font_face'),
            14
        )
        self.theme_label_font[self.tfSel] = (
            self.theme.get('font').get('font_face'),
            14
        )
        self.theme_label_font[self.sel_case_sens] = (
            self.theme.get('font').get('font_face'),
            14
        )

        self.set_cont.pack(fill=tk.BOTH, expand=False, side=tk.BOTTOM)
        self.selContainer.pack(fill=tk.BOTH, expand=False, side=tk.BOTTOM, padx=10)

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

        # The basic back
        self.xsb.pack(fill=tk.X, expand=False, side=tk.BOTTOM)
        self.canv.pack(fill=tk.BOTH, expand=1, side=tk.LEFT)
        self.vsb.pack(fill=tk.Y, expand=False, side=tk.RIGHT)
        # self.frame.pack(fill=tk.BOTH, expand=True)

        # ttk :: SB conf. (After widget placement)
        self.vsb.configure(command=self.canv.yview)
        self.xsb.configure(command=self.canv.xview)

        self.canv.configure(
            yscrollcommand=self.vsb.set,
            xscrollcommand=self.xsb.set,
        )

        self.canv.create_window(
            (0, 0),
            window=self.frame,
            anchor="nw",
            tags="self.frame"
        )

        # Final Things
        self.update()

        # Event Handlers
        self.frame.bind("<Configure>", self.onFrameConfig)
        # self.frame.bind_all("<MouseWheel>", self._on_mousewheel)

        self.canv.yview_scroll(1, "units")
        self.canv.xview_scroll(1, "units")
        self.root.update()
        self.canv.update()
        self.vsb.update()
        self.xsb.update()

        self.canv.yview_scroll(-1, "units")
        self.canv.xview_scroll(-1, "units")
        self.root.update()
        self.canv.update()
        self.vsb.update()
        self.xsb.update()

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
        theme.reload_default()
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
            fg=self.theme.get('fg'),
            insertbackground=self.theme['accent'],
        )

        self.answer_entry.config(
            bg=self.theme.get('bg'),
            fg=self.theme.get('fg'),
            insertbackground=self.theme['accent'],
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
                    activeforeground=colors.Functions.calculate_more_contrast(self.theme['bg'], self.theme['fg'], self.theme['accent']),
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

        for i in self.theme_invis_cont:
            try:
                i.config(
                    fg=self.theme['bg'],
                    bg=self.theme['bg'],
                    bd='0',
                )

            except:
                print('sfhsdhfkshdkhfsk', i)

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
            selectforeground=colors.Functions.calculate_more_contrast(self.theme['bg'], self.theme['fg'], self.theme['accent']),
            wrap=tk.WORD,
            font=(
                self.theme.get('font').get('font_face'),
                11
            ),
            insertbackground=self.theme.get('accent')
        )

        self.answer_entry.config(
            selectbackground=self.theme.get('accent'),
            selectforeground=colors.Functions.calculate_more_contrast(self.theme['bg'], self.theme['fg'], self.theme['accent']),
            wrap=tk.WORD,
            font=(
                self.theme.get('font').get('font_face'),
                11
            ),
            insertbackground=self.theme.get('accent')
        )

    def update(self):
        self.update_theme()

    def help(self):
        pdf = conf.Files.help['question_entry']
        os.startfile(f"\"{pdf}\"")

    def reformat_buttons(self):
        self.mcSel.config(
            bg=self.theme.get('accent' if self.mc else 'bg'),
            fg=colors.Functions.calculate_more_contrast(self.theme['bg'], self.theme['fg'], self.theme['accent']) if self.mc else self.theme.get('fg'),
            text=(
                    self.mcSel.cget('text').replace('\u2713', '').strip() + (' \u2713' if self.mc else '')
            )
        )

        self.tfSel.config(
            bg=self.theme.get('accent' if self.tf else 'bg'),
            fg=colors.Functions.calculate_more_contrast(self.theme['bg'], self.theme['fg'], self.theme['accent']) if self.tf else self.theme.get('fg'),
            text=(
                    self.tfSel.cget('text').replace('\u2713', '').strip() + (' \u2713' if self.tf else '')
            )
        )

        self.sel_case_sens.config(
            bg=self.theme.get('accent' if self.cs else 'bg'),
            fg=colors.Functions.calculate_more_contrast(self.theme['bg'], self.theme['fg'],
                                                        self.theme['accent']) if self.cs else self.theme.get('fg'),
            text=(
                    self.sel_case_sens.cget('text').replace('\u2713', '').strip() + (' \u2713' if self.cs else '')
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

    def cs_response_click(self):
        self.cs ^= True
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

        AFFileIO(file.uid).save('{}', append=False)

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
        self.cs &= not(self.mc or self.tf)   # You can't have a case sensitive option for 'tf' and 'mc' modes

        if not(len(q) and len(a)):
            prompts.TextPrompts.ErrorPrompt.Handled(
                "Error: Please enter a question and an answer.\n\nIf you wish to cancel, you can close the ui by clicking the 'X' button on the top of the ui.",
                use_tk=False
            )

            return

        _ok = _check_question(
            (mc_code if self.mc else tf_code if self.tf else nm_code) + " " + q,
            a
        )

        if not _ok[0]:
            prompts.TextPrompts.ErrorPrompt.Handled(_ok[1], degree='Error', accent_key='warning')
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

        file = AFIOObject(
            filename=filename,
            isFile=True,
            # encrypt=conf.Files.files[extension]['encrypt'],
            encrypt=False,
            encoding=conf.Files.files[extension]['encoding'],
            owr_exs_err_par_owr_meth=True
        )

        try:
            og = AFJSON(file.uid).load_file()
        except json.JSONDecodeError as E:
            og = {}
        except Exception as E:
            raise E.__class__(traceback.format_exc())

        n = {
            # f'{len(og) + 1}': {
            f"{AFDATA.Functions.generate_uid(1418972)}": {
                'data': data,
                'q_type': mc_code if self.mc else tf_code if self.tf else nm_code,
                'flags': {
                    'a_formatting_cs': self.cs
                }
            }
        }

        for fl in ('a_formatting_cs', ):
            assert fl in lookups.Table.Q.formatting_flags, f'Outdated formatting flag "{fl}" used'

        sdata = json.dumps({**og, **n}, indent=4)

        if not os.path.exists(conf.Application.AppDataLoc):
            os.makedirs(conf.Application.AppDataLoc)

        if conf.Files.files[extension]['encrypt']:
            print(conf.Encryption.file[extension])
            file.edit_flag(enc_key=conf.Encryption.file[extension])

        AFFileIO(file.uid).secure_save(
            sdata,
            append=False
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

        tkmsb.showinfo("QAS", "Added question successfully\nYou may add a new question now, or close this window.")

        # self.close()
        # Reset UI for another question
        self.reset()

    def reset(self):
        self.mc = False
        self.tf = False
        self.cs = False
        self.reformat_buttons()
        self.question_entry.delete('1.0', 'end-1c')
        self.answer_entry.delete('1.0', 'end-1c')
        self.helpButton.config(state=tk.NORMAL)
        self.submitButton.config(state=tk.NORMAL)
        self.clearButton.config(state=tk.NORMAL)
        self.update_theme()

    def __del__(self):
        self.thread.join(self, 0)


def _check_question(question, answer) -> list:
    try:
        def token_type(_token, tok_ls, _is_word=True) -> bool:
            # return not((False if (Type == 'word') else True) ^ (token in tok_ls))
            return not ((not _is_word) ^ (_token in tok_ls))

        q_tokens, a_tokens, output = (*question.split(),), (*answer.split(),), ()

        assert len(conf.FileCodes.question_codes) == 3, "Update _check_question function (viewing form)"

        mc_q_tok = conf.FileCodes.question_codes['mc']['question']
        mc_a_tok = conf.FileCodes.question_codes['mc']['option']
        tf_q_tok = conf.FileCodes.question_codes['tf']
        nm_q_tok = conf.FileCodes.question_codes['normal']

        tokens_list = (mc_q_tok, tf_q_tok, nm_q_tok, mc_a_tok, *list(conf.FileCodes.question_separators.items()))

        assert q_tokens[0] in (mc_q_tok, tf_q_tok, nm_q_tok), "Question must start with question type data."
        assert not((q_tokens[0] == mc_q_tok) ^ (mc_a_tok in q_tokens)), "Question must contain options."

        if q_tokens[0] == tf_q_tok:
            assert ('t' in answer.lower()) ^ ('f' in answer.lower()), "Answer to a true/false question can only be one of the aforementioned options, not both."

        elif q_tokens[0] == mc_q_tok:
            mc_a_stack = ()
            # Find the options' indexes
            for index, token in enumerate(q_tokens):
                if token_type(token, tokens_list, False):
                    if token == mc_a_tok:
                        mc_a_stack = (*mc_a_stack, index)

            assert len(mc_a_stack) >= 2, "You must add at least two options to a multiple choice question."

            option_handles = ()
            for index in mc_a_stack:
                assert len(q_tokens) >= (index + 1), "Unable to extract option data from the question; please define the question properly. (1)"

                handle = q_tokens[index + 1]
                assert handle[0] == '[' and handle[-1] == ']', "Unable to extract option data from the question; please define the question properly. (2)"

                handle = handle.lstrip('[').rstrip(']')
                assert len(handle) > 0, "Please ensure that you've defined all options properly."

                option_handles = (*option_handles, handle.strip())

            assert answer.lower().strip() in option_handles, "The answer provided has not been referenced in the question."

        elif q_tokens[0] == nm_q_tok:
            pass

        else:
            raise Exception

        return [True, ""]

    except Exception as E:
        return [False, E.__str__(), ]


if __name__ == "__main__":
    UI()
