import wcag_contrast_ratio, re, sys
import tkinter as tk
from tkinter import messagebox as tkmsb
from enum import Enum


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


class CLI:
    class CLITypes(Enum):
        FUNCTION = 1
        ARGUMENT = 2

    @staticmethod
    def help_text(ca_map):
        pass

    @staticmethod
    def CLI_handler(args, ca_map, sc_name, exit_on_error, pop_args_in_use) -> tuple:
        # Use `FUNCTION.args`

        oargs_stack = {}
        args_stack = {}
        function_stack = {}
        prev_function = None
        prev_function_arg_start = 0

        FUNCTION = CLI.CLITypes.FUNCTION
        ARGUMENT = CLI.CLITypes.ARGUMENT

        for ind, oarg in enumerate(args):
            ind -= 1
            ok = oarg in ca_map
            arg = oarg

            if not ok:
                for a in ca_map.keys():
                    if a in oarg:
                        ok = True
                        arg = a
                        break

            if not ok:
                CLI.help_text(ca_map)
                show_bl_err(
                    sc_name,
                    f'Invalid Argument `{arg}`'
                )
                sys.exit(f'Invalid Argument `{arg}`')

            if ca_map[arg]['type'] == ARGUMENT:
                arg_data = ca_map[arg]
                if arg_data['tied_to_function']['b']:
                    if prev_function not in arg_data['tied_to_function']['functions']:
                        show_bl_err(
                            sc_name,
                            f"[FATAL] Argument `{arg}` can only be used in succession to one of the following functions:\n\t* " + "\n\t* ".join(
                                function for function in arg_data['tied_to_function']['functions']
                            )
                        )

                        if exit_on_error:
                            sys.exit("inv_arg")
                        else:
                            return None

                else:
                    prev_function_arg_start = ind

                try:
                    if isinstance(arg_data['separator'], str):
                        if arg_data['separator'] not in oarg or len(oarg.split(arg_data['separator'])) == 1:
                            show_bl_err(
                                sc_name,
                                f"[FATAL] Argument `{arg}` must have key and value separated with a `{arg_data['separator']}` (no spaces allowed)\n\n" +\
                                f"Syntax: {arg}=<data>"
                            )

                            if exit_on_error:
                                sys.exit("inv_arg")
                            else:
                                return None

                        c_arg = "".join(i for i in oarg.split(arg_data['separator'])[1::])
                        n_arg = oarg.split(arg_data['separator'])[0]

                    else:
                        c_arg = arg
                        n_arg = ''

                    args_stack[ind] = arg_data['data_type'](c_arg)
                    oargs_stack[ind] = n_arg

                except Exception as E:
                    show_bl_err(
                        sc_name,
                        f"[FATAL] Argument `{arg}` expected data with type `{arg_data['data_type']}` - {E}"
                    )

                    if exit_on_error:
                        sys.exit("inv_arg")
                    else:
                        return None

                ind += 1

                if isinstance(prev_function, str) and ca_map[arg]['tied_to_function']['b']:
                    if ind == prev_function_arg_start + ca_map[prev_function]['num_args']:

                        function_args = {}

                        f_args_s_ind = ind - ca_map[prev_function]['num_args']
                        f_args_e_ind = ind

                        for index in range(f_args_s_ind, f_args_e_ind):
                            function_args[oargs_stack[index]] = args_stack[index]

                        if pop_args_in_use:
                            for index in range(f_args_s_ind, f_args_e_ind):
                                del args_stack[index]
                                del oargs_stack[index]

                        function_stack[len(function_stack)] = {
                            'call': prev_function,
                            'function': ca_map[prev_function]['path'],
                            'args': function_args
                        }

                        del function_args

                        if ca_map[prev_function]['request_special_call_index'] != -1 and len(function_stack) >= 1:
                            nindex = ca_map[prev_function]['request_special_call_index']
                            cindex = len(function_stack) - 1

                            if cindex != nindex:
                                nd = {}

                                for i in range(nindex):
                                    if i == nindex:  # Just in case
                                        continue

                                    nd[i] = function_stack[i]

                                nd[nindex] = function_stack[cindex]

                                for i in range(nindex, cindex):
                                    nd[i + 1] = function_stack[i]

                                function_stack = nd

                                del nd

                            del nindex, cindex

                        prev_function = None

            elif ca_map[arg]['type'] == FUNCTION:
                if prev_function is not None:
                    function_stack[len(function_stack)] = {
                        'call': prev_function,
                        'function': ca_map[prev_function]['path'],
                        'args': {}
                    }
                    prev_function = None

                if ca_map[arg]['num_args'] <= 0 or ind == len(args) - 2:
                    function_stack[len(function_stack)] = {
                        'call': arg,
                        'function': ca_map[arg]['path'],
                        'args': {}
                    }
                    prev_function = None

                else:
                    prev_function = arg

                prev_function_arg_start = ind + 1

            else:
                show_bl_err(
                    sc_name,
                    f"[FATAL] Invalid Command/Argument Mapping Data; failed to parse arguments\n\nFailed to parse argument `{arg}`"
                )

                if exit_on_error:
                    sys.exit("inv_ca_map")
                else:
                    return None

        for function in function_stack.values():
            try:
                assert len(function["args"]) == ca_map[function['call']]['num_args'], \
                    f"'{function['call']}': expected {ca_map[function['call']]['num_args']} args, got {len(function['args'])}"

                if ca_map[function['call']]['num_args'] > 0:
                    for arg_name in ca_map[function['call']]['args']:
                        assert arg_name in function['args'], \
                            f"Invalid argument name '{arg_name}' for '{function['call']}'; expected the following:\n\t* %s" % \
                            '\n\t* '.join(_ for _ in ca_map[function['call']]['args'])

            except Exception as E:
                show_bl_err(
                    sc_name,
                    f"Invalid Parameter(s):\n{E}"
                )

                if exit_on_error:
                    sys.exit("inv_arg")
                else:
                    return None

        return args_stack, function_stack
