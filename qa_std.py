import wcag_contrast_ratio, re
import tkinter as tk
from tkinter import messagebox as tkmsb


def float_map(value: float, input_min: float, input_max: float, output_min: float, output_max: float) -> float:
    """
    **FLOAT_MAP**

    Takes in float 'value' between points 'input_min' and 'input_max' and scales it to fit into the output range (output_min >> output_max)

    :param value: Actual Value
    :param input_min: Input range (min)
    :param input_max: Input range (max)
    :param output_min: Output range (min)
    :param output_max: Output range (max)
    :return: mapped float
    """

    leftSpan = input_max - input_min
    rightSpan = output_max - output_min
    valueScaled = float(value - input_min) / float(leftSpan)
    return output_min + (valueScaled * rightSpan)


def check_hex_contrast(bg, fg, adj=0) -> tuple:
    """
    **CHECK_HEX_CONTRAST**

    Takes in colors 1 and 2 ('bg' and 'fg') and decides whether if there is enough contrast.

    :param bg: Color 1 (HEX)
    :param fg: Color 2 (HEX)
    :return: Tuple (Passes WCAG AA?, Passes WCAG AAA?, (BG, FG))
    """

    contrast = ()

    def map_rgb(color_rgb: tuple) -> tuple:
        assert len(color_rgb) == 3
        o_tuple = ()

        for col in color_rgb:
            o_tuple = (*o_tuple, float_map(col, 0.00, 255.00, 0.00, 1.00))

        return o_tuple

    def hex_to_rgb(Hex: str) -> tuple:
        return tuple(int("".join(i for i in re.findall(r"\w", Hex))[j:j + 2], 16) for j in (0, 2, 4))

    back = hex_to_rgb(bg)
    front = hex_to_rgb(fg)
    adjusted_contrast_ratio = wcag_contrast_ratio.rgb(map_rgb(back), map_rgb(front)) + adj

    AA_res = wcag_contrast_ratio.passes_AA(adjusted_contrast_ratio)
    AAA_res = wcag_contrast_ratio.passes_AAA(adjusted_contrast_ratio)

    return AA_res, AAA_res, (bg, fg)


def data_at_dict_path(path: str, dictionary: dict) -> tuple:
    """
    **DATA_AT_DICT_PATH**

    Takes in dictionary 'dictionary' and finds data at path 'path'

    :param path: Path in dict (entries separated by '/' or '\\')
    :param dictionary: Data dictionary
    :return: Tuple (found?, data)
    """

    assert isinstance(path, str), "Invalid path input"
    assert isinstance(dictionary, dict), "Invalid dict input"

    path = path.replace('/', '\\')
    path_tokens = (*path.split('\\'), )

    found = True
    data = {**dictionary}

    for index, token in enumerate(path_tokens):
        if token == "root" and index == 0:
            continue

        found = token in data
        data = data.get(token)
        if index != len(path_tokens) - 1:
            if type(data) is not dict:
                found = False

        if not found:
            break

    return found, data


def show_bl_err(title, message):
    assert isinstance(title, str)
    assert isinstance(message, str)

    bgf = tk.Tk()
    bgf.withdraw()
    bgf.title("%s - Error messagebox handler" % title)

    tkmsb.showerror(title, message)

    bgf.title("%s - Error messagebox handler - closed" % title)
    bgf.withdraw()


def split_filename_direc(file_path: str) -> tuple:
    assert isinstance(file_path, str), "Invalid file path provided."
    _ = file_path.replace("\\", '/').split('/')
    return "\\".join(i for i in _[:-1:]), _[-1]


def dict_check_redundant_data_inter_dict(dic: dict, dic2: dict, root_name: str = '<root_directory>') -> tuple:
    p, f, s = check_inp(((dic, dict, 'dic'), (dic2, dict, 'dic2'), (root_name, str, '<REPORTING_REQ::ROOT_DIRECTORY>')), 'qa_std.py/dict_check_redundant_data_inter_dict')
    assert p, s

    def rec_add(d, d2, root='<root_directory>') -> tuple:
        _p, _, _s = check_inp(((d, dict, 'd'), (d2, dict, 'd2'), (root, str, '<REPORTING_REQ::ROOT_DIRECTORY>')), 'qa_std.py/dict_check_redundant_data_inter_dict/rec_add')
        assert p, s

        b = True
        oc = {}
        fnc = set()

        for k, v in d2.items():
            if isinstance(v, dict):
                if k in d:
                    b1, oc1, fnc1 = rec_add(d[k], d2[k], root='%s/%s' % (root, k))
                    b &= b1
                    oc = {**oc, **oc1}
                    fnc = {*fnc, *fnc1}

                continue

            if '%s/%s' % (root, v) not in d.values():
                oc['%s/%s' % (root, v)] = ('%s/%s' % (root, k), )

            else:
                b ^= b
                oc['%s/%s' % (root, v)] = (*oc['%s/%s' % (root, v)], '%s/%s' % (root, k))

        for v in oc:
            if len(oc[v]) > 1:
                fnc.add("'%s' is common between %s" % (v, oc[v]))

        return b, oc, fnc

    c, _, f = rec_add(dic, dic2)

    return not c, f


def dict_check_redundant_data(dic: dict, root_name: str = '<root_directory>') -> tuple:
    p, f, s = check_inp(((dic, dict, 'dic'), (root_name, str, '<REPORTING_REQ::ROOT_DIRECTORY>')), 'qa_std.py/dict_check_redundant_data')
    assert p, s

    def rec_add(d, root='<root_directory>') -> tuple:
        _p, _, _s = check_inp(((d, dict, 'd'), (root, str, '<REPORTING_REQ::ROOT_DIRECTORY>')), 'qa_std.py/dict_check_redundant_data/rec_add')
        assert p, s

        b = True
        oc = {}
        fnc = set()

        for k, v in d.items():
            if isinstance(v, dict):
                b1, oc1, fnc1 = rec_add(d[k], root='%s/%s' % (root, k))
                b &= b1
                oc = {**oc, **oc1}
                fnc = {*fnc, *fnc1}

                continue

            if '%s/%s' % (root, v) not in oc:
                oc['%s/%s' % (root, v)] = ('%s/%s' % (root, k), )

            else:
                b ^= b
                oc['%s/%s' % (root, v)] = (*oc['%s/%s' % (root, v)], '%s/%s' % (root, k))

        for v in oc:
            if len(oc[v]) > 1:
                fnc.add("'%s' is common between %s" % (v, oc[v]))

        return b, oc, fnc

    c, _, f = rec_add(dic, root_name)

    return not c, f


def check_inp(inp_g, function_name, l_check: bool = True) -> tuple:
    failed = ()

    for inp in inp_g:
        if not isinstance(*inp[:2]):
            failed = (*failed,
                      "Invalid input for param <%s>; expected %s, got %s." % (inp[2], inp[1], type(inp[0]))
                      )
            continue

        if l_check:
            if inp[1] in [str, bytes]:
                if not len(inp[0].strip()) > 0:
                    failed = (*failed,
                              "Invalid theme author data: insufficient data (<%s>)" % inp[-1]
                              )
            elif inp[1] in [int, float, complex]:
                pass

            else:
                if not len(inp[0]) > 0:
                    failed = (*failed,
                              "Invalid theme author data: insufficient data (<%s>)" % inp[-1]
                              )

    return len(failed) == 0, failed, ("%s: Invalid input(s):\n\t* %s" % (function_name, "\n\t* ".join(_ for _ in failed) if len(failed) != 0 else ''))


def copy_to_clipboard(text: str, shell: tk.Toplevel, clear_old: bool = True):
    assert isinstance(text, str)
    assert isinstance(shell, tk.Toplevel) or isinstance(shell, tk.Tk)
    assert len(text) <= 100  # Max length = 100
    assert isinstance(clear_old, bool)

    if clear_old:
        shell.clipboard_clear()
    shell.clipboard_append(text)
    shell.update()
