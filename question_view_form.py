import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as tkmsb

import lookups
from appfunctions import *
import threading, sys, os, conf, theme, exceptions, questions, random


class UI(threading.Thread):
    def __init__(self):
        super().__init__()
        self.thread = threading.Thread
        self.thread.__init__(self)

        self.root = tk.Toplevel()

        self.ws = (self.root.winfo_screenwidth(), self.root.winfo_screenheight())
        self.ws = (self.ws[0], self.ws[1])
        self.wp = (0, 0)

        self.vsb_style = ttk.Style()
        self.vsb_style.theme_use('default')

        self.sepStyle = ttk.Style()
        self.sepStyle.theme_use('default')

        self.vsb = ttk.Scrollbar(
            self.root,
            orient=tk.VERTICAL
        )

        self.xsb = ttk.Scrollbar(
            self.root,
            orient=tk.HORIZONTAL
        )

        self.canv = tk.Canvas(self.root)
        self.frame = tk.Frame(self.canv)

        self.loadingLbl = tk.Label(self.frame, text="Loading questions; please wait.")

        theme.reload_default()
        self.theme = theme.Theme.UserPref.m(theme.TMODE)

        self.update_lbl: list = []
        self.update_accent_foreground: list = []
        self.update_text_font: dict = {}
        self.rec_questions = {}
        self.question_index_map = {}
        self.id_assign = {}

        self.start()
        self.root.mainloop()

    def close(self):
        if not __name__ == "__main__":
            self.root.after(0, self.root.destroy)
            return

        else:
            sys.exit('WM_DELETE_WINDOW')

    def run(self):
        # Root config
        self.root.state('zoomed')  # Maximize the window
        self.root.iconbitmap(conf.Files.app_icons['admin_tools']['ico'])
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.title(f"Quizzing Application: Recorded Questions")
        self.root.minsize(500, 100)

        # Place the widgets
        self.xsb.pack(fill=tk.X, expand=False, side=tk.BOTTOM)
        self.canv.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        self.vsb.pack(fill=tk.Y, expand=False, side=tk.RIGHT)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.loadingLbl.config(text="Loading questions; please wait.")
        self.loadingLbl.pack(fill=tk.X, expand=False, padx=10, pady=10)
        self.update_lbl.append(self.loadingLbl)
        self.update_accent_foreground.append(self.loadingLbl)
        self.update_text_font[self.loadingLbl] = (
            self.theme.get('font').get('font_face'),
            18
        )

        self.rec_questions = _loadQuestions(no_q_type=True)

        self.loadingLbl.config(text="Inserting questions into UI...")

        for i in self.rec_questions:
            try:
                _format = _format_question(
                    i.strip(), self.rec_questions[i]['a'], *self.rec_questions[i]['f']
                )
            except Exception as E:
                print(traceback.format_exc())
                _format = ("Error", E.__str__(), "System Message - Error", "")
            tempQuestionNumberLbl = tk.Label(
                self.frame,
                text=f"Question #{_dict_getIndex(self.rec_questions, i, 1, True)}:",
                anchor=tk.W,
                justify=tk.LEFT,
                wraplength=int((int(self.ws[0] - self.ws[0] * 0.02)))
            )

            tempQuestionNumberLbl.pack(fill=tk.BOTH, expand=False, padx=10, pady=(15, 2.5))

            self.update_lbl.append(tempQuestionNumberLbl)
            self.update_text_font[tempQuestionNumberLbl] = (
                self.theme.get('font')['font_face'], self.theme['font']['big_para_size']
            )
            self.update_accent_foreground.append(tempQuestionNumberLbl)

            tempQuestionLbl = tk.Label(
                self.frame,
                text=_format[0],
                anchor=tk.W,
                justify=tk.LEFT,
                wraplength=int((int(self.ws[0] - self.ws[0] * 0.02)))
            )

            tempQuestionLbl.pack(fill=tk.BOTH, expand=False, padx=10, pady=0)

            self.update_lbl.append(tempQuestionLbl)
            self.update_text_font[tempQuestionLbl] = (
                self.theme.get('font').get('font_face'), self.theme['font']['big_para_size']
            )
            self.update_accent_foreground.append(tempQuestionLbl)

            tempAnswerLbl = tk.Label(
                self.frame,
                text=f"Answer: '{_format[1]}'",
                anchor=tk.W,
                justify=tk.LEFT,
                wraplength=int((int(self.ws[0] - self.ws[0] * 0.08)))
            )

            tempAnswerLbl.pack(fill=tk.BOTH, expand=False, padx=10, pady=5)

            tempTypeLbl = tk.Label(
                self.frame,
                text="Question Type: %s" % _format[2],
                anchor=tk.W,
                justify=tk.LEFT,
                wraplength=int((int(self.ws[0] - self.ws[0] * 0.02)))
            )

            tempTypeLbl.pack(fill=tk.BOTH, expand=False, padx=10, pady=5)
            self.update_lbl.append(tempTypeLbl)
            self.update_text_font[tempTypeLbl] = (self.theme.get('font')['font_face'], self.theme['font']['main_size'])

            if len(_format[3]) > 0:
                tempCommentsLbl = tk.Label(
                    self.frame,
                    text=_format[3],
                    anchor=tk.W,
                    justify=tk.LEFT,
                    wraplength=int((int(self.ws[0] - self.ws[0] * 0.02)))
                )

                tempCommentsLbl.pack(fill=tk.BOTH, expand=False, padx=10, pady=5)
                self.update_lbl.append(tempCommentsLbl)
                self.update_text_font[tempCommentsLbl] = (
                    self.theme.get('font')['font_face'], self.theme['font']['main_size']
                )

            remButton = tk.Button(
                self.frame,
                text="Remove Question",
                fg=self.theme.get('error'),
                bg=self.theme.get('bg'),
                activebackground=self.theme.get('error'),
                activeforeground=self.theme.get('bg'),
                bd=0,
                anchor=tk.SW
            )
            remButton.pack(
                fill=tk.BOTH,
                expand=False,
                padx=10,
                pady=(0, 10)
            )

            self.question_index_map[self.rec_questions[i]['i']] = i
            self.config_rm_button(remButton, self.rec_questions[i]['i'])

            self.update_lbl.append(tempAnswerLbl)
            self.update_text_font[tempAnswerLbl] = (
            self.theme.get('font')['font_face'], self.theme['font']['main_size'])

            self.update_text_font[remButton] = (self.theme.get('font')['font_face'], self.theme['font']['main_size'])

        self.loadingLbl.config(text="Completed loading process...")
        self.loadingLbl.pack_forget()

        # ttk :: SB conf. (After widget placement)
        self.vsb.configure(command=self.canv.yview)
        self.xsb.configure(command=self.canv.xview)

        self.canv.configure(
            yscrollcommand=self.vsb.set,
            xscrollcommand=self.xsb.set
        )

        self.canv.create_window(
            (0, 0),
            window=self.frame,
            anchor="nw",
            tags="self.frame"
        )

        # Event Handlers
        self.frame.bind("<Configure>", self.onFrameConfig)
        self.frame.bind_all("<MouseWheel>", self._on_mousewheel)
        # Final things
        self.update()

    def config_rm_button(self, tkButton, index):
        qId = (random.randint(0, 9999999999999999) + random.random()) * random.randint(1, 99)

        counter = 0
        while qId in self.id_assign:
            counter += 1
            qId = (random.randint(0, 9999999999999999) + random.random()) * random.randint(1, 99)
            if counter > 10000000:
                break

        self.id_assign[qId] = index.strip()

        tkButton.config(
            command=lambda: self.rm_q(qId)
        )

    def _on_mousewheel(self, event):
        """
        Straight out of stackoverflow
        Article: https://stackoverflow.com/questions/17355902/tkinter-binding-mousewheel-to-scrollbar
        Change
        : added "int" around the first arg
        """
        self.canv.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def onFrameConfig(self, event):  # for scbar
        self.canv.configure(
            scrollregion=self.canv.bbox("all")
        )

        self.ws = [
            self.root.winfo_width(),
            self.root.winfo_height()
        ]

    def rm_q(self, ID) -> None:
        ind = self.id_assign[ID]
        question = self.question_index_map[ind]

        confirmation = tkmsb.askyesno(
            "Confirm Removal",
            "Are you sure you want to remove the following question:\n\n'{}'".format(question.strip())
        )
        if not confirmation:
            return

        filename = os.path.join(conf.Application.AppDataLoc, conf.Files.questions_and_answers['filename'])
        extension = filename.split('.')[-1]

        file = AFIOObject(
            filename=filename,
            isFile=True,
            encrypt=conf.Files.files[extension]['encrypt'],
            owr_exs_err_par_owr_meth=True
        )

        if conf.Files.files[extension]['encrypt']:
            file.edit_flag(enc_key=conf.Encryption.file[extension])

        try:
            l = AFJSON(file.uid).load_file()
        except:
            print(2, traceback.format_exc())
            return

        del self.rec_questions[question]
        del l[ind]

        # Save
        AFFileIO(file.uid).secure_save(
            json.dumps(l, indent=4),
            append=False
        )

        # Reset UI
        children = self.frame.winfo_children()
        for i in children:
            i.pack_forget()

        self.run()

    def update_theme(self):
        theme.reload_default()
        self.theme = theme.Theme.UserPref.m(theme.TMODE)

        self.root.config(
            bg=self.theme.get('bg')
        )

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

        # ttk::style configure TSeparator -background color
        self.sepStyle.configure(
            "TSeparator",
            background=self.theme.get('bg')
        )

        self.canv.config(
            bg=self.theme.get('bg'),
            bd=0
        )

        self.frame.config(
            bg=self.theme.get('bg')
        )

        for i in self.update_lbl:
            i.config(
                bg=self.theme.get('bg'),
                fg=self.theme.get('fg')
            )

        for i in self.update_accent_foreground:
            i.config(
                fg=self.theme.get('accent')
            )

        for i in self.update_text_font:
            i.config(
                font=self.update_text_font[i]
            )

    def update(self):
        self.update_theme()


def _format_question(question, answer, *flags) -> tuple:
    q_tokens, a_tokens, output = (*question.split(),), (*answer.split(),), ()
    a_raw = ""

    assert len(conf.FileCodes.question_codes) == 3, "Update _format_question function (viewing form)"

    mc_q_tok = conf.FileCodes.question_codes['mc']['question']
    mc_a_tok = conf.FileCodes.question_codes['mc']['option']
    tf_q_tok = conf.FileCodes.question_codes['tf']
    nm_q_tok = conf.FileCodes.question_codes['normal']

    tokens_list = (mc_q_tok, tf_q_tok, nm_q_tok, mc_a_tok, *list(conf.FileCodes.question_separators.keys()))

    if 'system_msg' not in flags:
        assert q_tokens[0] in (mc_q_tok, tf_q_tok, nm_q_tok), "Question must start with question type data."
        assert not ((q_tokens[0] == mc_q_tok) ^ (mc_a_tok in q_tokens)), "Question must contain options."

    token_type = lambda _token, tok_ls, _is_word=True: not ((not _is_word) ^ (_token in tok_ls))

    for token in a_tokens:
        if token_type(token, tokens_list):
            a_raw = " ".join(_ for _ in [a_raw, token])
    a_raw = a_raw.strip()

    if q_tokens[0] == tf_q_tok:
        assert ('t' in a_raw.lower()) ^ (
                    'f' in a_raw.lower()), "Answer to a true/false question can only be one of the aforementioned options, not both."

        if 't' in a_raw:
            compiled_answer = 'True'
        else:
            compiled_answer = 'False'

        q_raw = " ".join(_ for _ in q_tokens)

    elif q_tokens[0] == mc_q_tok:
        mc_a_stack = ()
        # Find the options' indexes
        for index, token in enumerate(q_tokens):
            if token_type(token, tokens_list, False):
                if token == mc_a_tok:
                    mc_a_stack = (*mc_a_stack, index)

        # Compile them into a string
        pre = q_tokens[:mc_a_stack[0]]
        options = ()
        for s_index, index in enumerate(mc_a_stack):
            if index < mc_a_stack[-1]:
                options = (*options, " ".join(i for i in q_tokens[index:mc_a_stack[s_index + 1]]))
            else:
                options = (*options, " ".join(i for i in q_tokens[index::]))

        # Find the options
        option_handles = ()
        for index in mc_a_stack:
            assert len(q_tokens) >= (index + 1), "Question not defined properly. (1)"

            handle = q_tokens[index + 1]
            assert handle[0] == '[' and handle[-1] == ']', "Question not defied properly. (2)"

            handle = handle.lstrip('[').rstrip(']')
            assert len(handle) > 0, "Question not defined properly. (3)"

            option_handles = (*option_handles, handle.strip())

        assert answer.lower().strip() in option_handles, "Question not defined properly. (4)"

        # Compile the previous tuples into strings
        pre_compiled = " ".join(_ for _ in pre).strip()
        options_compiled = "\n\t".join(_ for _ in options)
        q_raw = pre_compiled + "\n\t" + options_compiled

        compiled_answer = a_raw.strip()

    elif q_tokens[0] == nm_q_tok:
        compiled_answer = a_raw.strip()
        q_raw = " ".join(_ for _ in q_tokens)

    else:
        if 'system_msg' not in flags:
            raise Exception
        else:
            q_raw = question.strip()
            compiled_answer = answer.strip()

    question_compiled = ""
    q_raw = q_raw.replace(
        '\n', "<<<<NEWLINE%%&@(#&$(*@#($&>>>>"
    ).replace(
        '\t', "<<<<TABBED%%&@(#&$(*@#($&>>>>"
    )
    for token in q_raw.split():
        if token_type(token, tokens_list):
            question_compiled = " ".join(_ for _ in [question_compiled, token])

    question_compiled = question_compiled.replace(
        "<<<<NEWLINE%%&@(#&$(*@#($&>>>>", "\n"
    ).replace(
        "<<<<TABBED%%&@(#&$(*@#($&>>>>", "\t"
    )
    question_compiled = question_compiled.strip()
    compiled_answer = compiled_answer.strip()

    for token in tokens_list:
        assert type(token) is str, "%s token is not str" % str(token)
        question_compiled = question_compiled.replace(token, "")
        compiled_answer = compiled_answer.replace(token, "")

    q_type = {
        mc_q_tok: 'Multiple Choice',
        tf_q_tok: 'True/False',
        nm_q_tok: 'Normal (Written)'
    }.get(q_tokens[0]) if 'system_msg' not in flags else 'SYSTEM MESSAGE'
    if len(flags) > 0:
        fls_str = "\n\t\u2022 ".join(
            lookups.Table.Q.formatting_flags[i] for i in flags if i in lookups.Table.Q.formatting_flags
        )
        fls_str = f"The following are the flags linked with this question:\n\t\u2022 {fls_str}"
    else:
        fls_str = ""

    output = (question_compiled, compiled_answer, q_type, fls_str)

    del question_compiled, compiled_answer, q_type, fls_str, q_raw, a_raw, q_tokens, token_type, a_tokens, tokens_list

    return output


def _loadQuestions(__r=True, no_q_type: bool = False) -> dict:
    output: dict = {}
    def_o = {
        "No questions found": {
            'a': "No answers found",
            'f': ['system_msg'],
            'i': ''
        }
    }
    if not no_q_type:
        def_o['No questions found']['t'] = 'sys'

    path = os.path.join(conf.Application.AppDataLoc, conf.Files.questions_and_answers['filename'])

    if not os.path.exists(path):
        return def_o if __r else {}

    extension = path.split('.')[-1]

    file = AFIOObject(
        filename=path,
        isFile=True,
        encrypt=conf.Files.files[extension]['encrypt'],
        owr_exs_err_par_owr_meth=True
    )

    if conf.Files.files[extension]['encrypt']:
        file.edit_flag(enc_key=conf.Encryption.file[extension])

    try:
        _raw = AFJSON(file.uid).load_file()
    except:
        return def_o if __r else {}

    if len(_raw) <= 0:
        return def_o if __r else {}

    for index, qad in _raw.items():
        flags = [k for k, v in qad['flags'].items() if v]
        if not no_q_type:
            q_type = qad['q_type']
        else:
            q_type = {}

        f = questions.Conversions.raw_to_dict(qad['data'])
        ql, al = (*f.items(), )[0]

        output[ql] = {
            'a': al,
            'f': flags,
            'i': index
        }

        if not no_q_type:
            output[ql]['t'] = q_type

        del ql, al, flags, q_type, f

    del _raw, file, extension, path

    return output


def _dict_getIndex(dictionary: dict, key: str, add: int = 0, changeToStr: bool = False):
    ind = None
    ls: list = [i.strip() for i in dictionary.keys()]

    for i in dictionary:
        try:
            if i.strip() == key.strip():
                ind = ls.index(i)
                break

        except:
            pass

    if ind is not None:
        ind += add

    elif changeToStr:
        ind = " << Unknown Index >> "

    return ind


if __name__ == "__main__":
    UI()
