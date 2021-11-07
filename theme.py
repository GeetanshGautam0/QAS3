from appfunctions import *
import conf, os, user_pref, re, diagnostics, std

TMODE: str = None
TFILE: str = None

_theme_file = AFIOObject(filename=conf.ConfigFile.raw['theme']['theme_file'], isFile=True,
                         owr_exs_err_par_owr_meth=True)
_theme_data: dict = {None: None}


def _convert_path(path) -> str:
    p = [conf.Application.AppDataLoc, *protected_conf.Configuration.Files.pref_file_loc]
    p_fn = conf.ConfigFile.raw['theme']['custom_config_file']

    theme_file = path.replace("$curr", TFILE)
    theme_file = theme_file.replace("$installed",
                                    os.path.join(
                                        '$appdata',
                                        conf.ConfigFile.raw['theme']['user_can_install_themes']['dir']
                                    )) if conf.ConfigFile.raw['theme']['user_can_install_themes']['in_appdata'] else \
        conf.ConfigFile.raw['theme']['user_can_install_themes']['dir']
    theme_file = theme_file.replace("$appdata", conf.Application.AppDataLoc)
    theme_file = theme_file.replace("$user_pref", os.path.join(*p, p_fn))
    theme_file = theme_file.replace("\\", "/")
    return theme_file


def find_preference(s_at_def=False) -> tuple:
    global TMODE, TFILE
    default = (
        conf.ConfigFile.raw['theme']['theme_file'],
        '__CGET__::$information\\$default_mode'
    )

    if s_at_def:
        TFILE, TMODE = default
        tok = TMODE.split("::")
        loc = "/".join(_ for _ in tok[1::]).strip('/')
        r = user_pref._Basic.IO.load_json(TFILE)
        exs, data = std.data_at_dict_path(loc, r)
        assert exs, '[THEME>>FIND_PREF>>S_AT_DEF[ROUTE]>>!EXS] [?]'
        TMODE = data

    else:
        pref = user_pref.Get.Theme.theme_pref(default)
        TMODE = pref['mode']
        TFILE = pref['file']

    if not os.path.exists(TFILE) and not s_at_def:
        # Rev to default
        revert_to_default()

    pas, ch_f, _1, _2, _3 = check_theme(TFILE.split('\\')[-1], user_pref._Basic.IO.load_json(TFILE), re_comp_data=True)
    if not pas:
        chfs = diagnostics.FormatResultsStr.failures(ch_f)

        if TFILE == default[0]:
            std.show_bl_err(
                "CMF Theme Handler",
                "[CRITICAL] Default theme file has invalid theme data:\n\n%s" % chfs
            )

            sys.exit(-1)

        else:
            std.show_bl_err(
                "CMF Theme Handler",
                "Invalid theme set as preferred theme; resetting to default:\n\n%s" % chfs
            )
            user_pref.Set.Theme.theme_pref(default)
            return find_preference()

    return tuple([TMODE, TFILE])


def reload_default(n_fp: bool = False) -> None:
    global _theme_data, _theme_file
    if not n_fp:
        find_preference()
    _theme_data = AFJSON(_theme_file.uid).load_file()
    if not check_theme('default', _theme_data):
        std.show_bl_err("CMF Theme Handler", "Invalid default theme file.")

    return


def load_theme_file(filename='__USER_PREF__', mode: str = all) -> dict:
    global TMODE, TFILE

    assert type(TFILE) is str, "Failed to load theme file."
    filename = _convert_path(filename)

    if filename == '__USER_PREF__':
        default = (
            conf.ConfigFile.raw['theme']['theme_file'],
            '__CGET__::$information\\$default_mode'
        )
        pref = user_pref.Get.Theme.theme_pref(default)
        TMODE = pref['mode']
        TFILE = pref['file']

        if not os.path.exists(TFILE):
            # Rev to default
            set_preference(-1, -1)

        r = user_pref._Basic.IO.load_json(TFILE)
        if not check_theme(TFILE.split('\\')[-1], r):
            std.show_bl_err("CMF Theme Handler", "Invalid __USER_PREF__ theme file.")

        return r if mode is all else r[TMODE if mode == '__USER_PREF__' else mode]

    else:
        assert os.path.exists(filename), "Theme file provided does not exist."
        r = user_pref._Basic.IO.load_json(filename)

        if not check_theme(filename, r):
            std.show_bl_err("CMF Theme Handler", "Invalid theme file.")

        return r if mode is all else r[mode]


def revert_to_default() -> None:
    # reload_default()  # Will happen automatically in 'set_preference'
    set_preference(-1, -1, True)
    find_preference()


def set_preference(file_name, mode, r_n_fp=False) -> None:
    global _theme_file, _theme_data, TFILE

    if file_name == -1:
        file_name = _theme_file.filename

    assert type(TFILE) is str, "Failed to load theme file."
    file_name = _convert_path(file_name)

    if mode == -1:
        reload_default(True)
        mode = _theme_data['$information']['$default_mode']

    user_pref.Set.Theme.theme_pref((file_name, mode,))

    return


def check_theme(name: str, data, *args, re_comp_data: bool = False):
    try:
        assert type(name) is str, "Invalid input [script]"

        for i in [
            '$information',
            # ['$information', ('$name', '$default_mode', '$avail_modes', '$map', '$author)],
            ['$information', ('$name', '$default_mode', '$avail_modes')],
            '$global',
            *args
        ]:
            if type(i) is list:
                for j in i[1]: assert j in data[i[0]], "Invalid theme file (%s)" % name
            else:
                assert i in data, "Invalid theme file (%s)" % name

        res = diagnostics.DataDiagnostics.Theme.check_data(data)
        return res if re_comp_data else res[0]
    except Exception as E:
        return False, (E.__str__(), ), (), (), ()


reload_default()


class Editor:
    @staticmethod
    def create_new_theme_file(
        mapping: dict,
        author: str,
        name: str,
        default_val: str,
        themes: dict,
        global_data: dict,
        filename: str,
        **kwargs
    ):
        try:
            file_path = _convert_path(filename)
            o_f1 = isinstance(kwargs.get('over_write_file'), bool)
            o_f1 &= (kwargs.get('over_write_file') if o_f1 else False)
            assert not os.path.exists(file_path) or o_f1, "File '%s' already exists; use 'OVERWRITE_THEME_FILE' mode to edit this file." % file_path

            file_d, file_n = std.split_filename_direc(file_path)
            assert file_n.split('.')[-1] == 'json', "Theme files must be .json files."

            n_theme = json.dumps(Editor._create_new_theme(
                mapping=mapping, author=author, name=name, default_val=default_val,
                themes=themes, global_data=global_data
            ), indent=4)

            if not os.path.exists(file_d):
                os.makedirs(file_d)

            with open(file_path, 'w') as new_file:
                new_file.write(n_theme)
                new_file.close()

        except PermissionError as PE:
            raise PermissionError("Failed to create new theme file; lack permissions: %s" % PE.__str__())

        except Exception as E:
            raise Exception("Failed to create new theme file: %s" % E.__str__())

        else:
            return True

    @staticmethod
    def overwrite_theme_file(
        mapping: dict,
        author: str,
        name: str,
        default_val: str,
        themes: dict,
        global_data: dict,
        filename: str
    ):
        try:
            Editor.create_new_theme_file(
                mapping, author, name, default_val, themes, global_data, filename, over_write_file=True
            )

        except PermissionError as PE:
            raise PermissionError("Failed to create new theme file; lack permissions: %s" % PE.__str__())

        except Exception as E:
            raise Exception("Failed to create new theme file: %s" % E.__str__())

        else:
            return True

    @staticmethod
    def _create_new_theme(mapping: dict, author: str, name: str, default_val: str, themes: dict,
                          global_data: dict) -> dict:
        """
        **Editor._create_new_theme**

        Will automatically generate the data required for a new theme.

        :param mapping:     mapping information (dict [{name: str}: {code: str}])
        :param author:      theme author (str)
        :param name:        theme master name (str)
        :param default_val: default <code> value
        :param themes:      themes available (dict[{code: str}: {theme_data: dict}])
        :param global_data: global data (dict)
        :return:            compiled theme data ({dict})
        """

        function_name = 'theme.py/Editor/<private>/create_new_theme'

        try:
            inp_pass, inp_fail, _s = std.check_inp(
                (
                    [mapping, dict, 'Mapping_Data (mapping)'],
                    [author, str, 'Author_Name (author)'],
                    [name, str, 'Theme_Name (name)'],
                    [default_val, str, 'Default_Theme_Code (default_val)'],
                    [themes, dict, 'Themes (themes)'],
                    [global_data, dict, 'Global_Theme_Data (global_data)']
                ),
                function_name
            )

            try:
                int(default_val[1::])
            except:
                inp_fail = (*inp_fail, "Invalid theme default <Code>; must follow same standard as <Theme_Code>")

            inp_pass &= (len(inp_fail) == 0)

            assert inp_pass, "%s: Invalid input(s):\n\t* %s" % (function_name, "\n\t* ".join(_ for _ in inp_fail))

            theme_req = {
                'bg': ['HEX_COLOR', str],
                'fg': ['HEX_COLOR', 'contrast', str],
                'ok': ['HEX_COLOR', 'contrast', str],
                'error': ['HEX_COLOR', 'contrast', str],
                'warning': ['HEX_COLOR', 'contrast', str],
                'gray': ['HEX_COLOR', 'contrast', str],
                'accent': ['HEX_COLOR', 'contrast', str],

                'font/font_face': [str],
                'font/title_size': [int, 'FONT_MIN_SIZE_5'],
                'font/sttl_size': [int, 'FONT_MIN_SIZE_5'],
                'font/big_para_size': [int, 'FONT_MIN_SIZE_5'],
                'font/main_size': [int, 'FONT_MIN_SIZE_5'],

                'border/width': [int],
                'border/color': ['HEX_COLOR', str],
            }

            req_dicts = {
                'root': (
                    '$global',
                    '$information',
                    '$information/$avail_modes',
                    '$global/padding',
                ),
                '<<theme>>': (
                    'font',
                    'border',
                ),
            }

            L = {
                'global':
                    {
                        'root': len(themes) + 2,
                        'root/$global': 1,
                        'root/$global/padding': 2,
                        'root/$information': 4,
                        'root/$information/$avail_modes': len(themes),
                    },
                'theme':
                    {
                        'root': 9,
                        'root/font': 5,
                        'root/border': 2
                    },
            }

            assert len(themes) > 0, \
                "Insufficient theme data"

            temp_ctd = {
                "$information": {
                    '$author': author.strip(),
                    '$name': name.strip(),
                    '$avail_modes': mapping,
                    '$default_mode': default_val.strip()
                },
                "$global": global_data,
                **themes
            }

            for tctd_code, tctd_data in temp_ctd.items():
                d_g = tctd_code in ['$information', '$global']
                d_u = 'global' if d_g else 'theme'

                for asset_code, asset_length in L[d_u].items():
                    exs, data = std.data_at_dict_path(asset_code, temp_ctd if d_g else tctd_data)

                    assert exs, "Missing data '%s/%s' (<%s>)" % ('' if d_g else tctd_code, asset_code, d_u.upper())
                    assert len(data) == asset_length, "Invalid data length for '%s/%s' (<%s>) expected <%s>, got <%s>." % \
                                                      ('' if d_g else tctd_code, asset_code, d_u.upper(), str(asset_length), str(len(data)))

            assert default_val in themes, \
                "Invalid <Default_Value>; '%s' code not found in the themes provided." % default_val

            checks_map = {
                'HEX_COLOR': [
                    lambda *arguments: type(arguments[1]) is str,
                    lambda *arguments: len("".join(_ for _ in re.findall(r"[0-9a-fA-F]", arguments[1]))) in [3, 6]
                ],
                'contrast': [
                    lambda *arguments: std.check_hex_contrast(arguments[0]['bg'], arguments[1])[0]
                ],
                'T_CODE_C': [
                    lambda *arguments: type(arguments[1]) is str,
                    lambda *arguments: arguments[1][0] == '$',
                    lambda *arguments: int(arguments[1][1::]) or True
                ],
                'FONT_MIN_SIZE_5': [
                    lambda *arguments: type(arguments[1]) is int,
                    lambda *arguments: arguments[1] >= 5
                ]
            }

            for theme_code, theme in themes.items():
                assert isinstance(theme_code, str), "Invalid theme code '%s'" % set(theme_code)
                assert theme_code[0] == '$', "Invalid theme code '%s'; must start with '$' and then contain an integer"
                try:
                    int(theme_code[1::])
                except:
                    assert False, "Invalid theme code '%s'; must start with '$' and then contain an integer"
                assert isinstance(theme, dict), "Invalid theme data for '%s'; theme data must be a python dictionary" % theme_code
                assert len(theme) == L['theme']['root'], "Invalid theme data: missing/extra theme data."

                for dic in req_dicts['<<theme>>']:
                    assert dic in theme, "Invalid theme; missing '%s/%s' data." % (theme_code, dic)

                failed = ()
                for asset_code, asset_checks in theme_req.items():
                    exs, asset_data = std.data_at_dict_path(asset_code, theme)
                    if not exs:
                        failed = (
                            *failed,
                            "Invalid theme; data for '%s/%s' not found." % (theme_code, asset_code)
                        )
                        continue

                    for check in asset_checks:
                        if isinstance(check, type):
                            if not isinstance(asset_data, check):
                                failed = (*failed,
                                          "Invalid theme data for '%s/%s' (expected %s)" % (
                                              theme_code, asset_code, str(check)
                                          ))

                        else:
                            assert type(check) is str, "SCRIPT ERROR: INVALID CHECK CODE '%s' [1]" % check
                            assert check in checks_map, "SCRIPT ERROR: INVALID CHECK CODE '%s' [2]" % check

                            for check_function in checks_map[check]:
                                if isinstance(check_function, tuple) or isinstance(check_function, list):
                                    command = check_function[0]
                                else:
                                    command = check_function
                                try:
                                    if not command(
                                        theme,
                                        asset_data,
                                        check_function
                                    ):
                                        failed = (*failed, "FAILED: Failed test '%s' on '%s/%s'." % (
                                            check, theme_code, asset_code
                                        ))
                                except Exception as E:
                                    failed = (*failed, "FAILED: Failed to conduct test '%s' on '%s/%s' :: %s" % (
                                        check, theme_code, asset_code, E.__str__()
                                    ))

                assert len(failed) == 0, "Failed one one or more tests:\n\t* %s" % "\n\t* ".join(_ for _ in set(failed)).strip()

            compiled_theme_dict = {
                "$information": {
                    '$author': author.strip(),
                    '$name': name.strip(),
                    '$avail_modes': mapping,
                    '$default_mode': default_val.strip()
                },
                **themes,
                "$global": global_data
            }

            global_req = {
                'root/$global/padding/x': [int],
                'root/$global/padding/y': [int],
                'root/$information/$default_mode': ['T_CODE_C']
            }

            for root, ps in req_dicts.items():
                if root == '<<theme>>':
                    continue

                for p in ps:
                    path = '%s/%s' % (root, p)
                    # Two birds one stone
                    ex, d = std.data_at_dict_path(path, compiled_theme_dict)
                    assert ex, "Failed to compile theme data [EXS-1]: %s" % path
                    assert len(d) == L['global'][path], "Failed to compile theme data [LENGTH]: %s" % path

            for path, reqs in global_req.items():
                ex, d = std.data_at_dict_path(path, compiled_theme_dict)
                assert ex, "Failed to compile theme data [EXS-2] (The following data does not exist): %s" % path
                for req in reqs:
                    if isinstance(req, tuple) or isinstance(req, list):
                        command = req[0]
                        # args = (*req[1::], )
                    else:
                        command = req
                        # args = ()

                    if isinstance(req, type):
                        assert isinstance(d, req), "Failed to compile theme data [G-C-Reqs-TP-1] (Invalid type; expected %s, got %s): %s" % (req, type(d), path)
                        continue

                    checks = checks_map[command]
                    for check in checks:
                        assert check({None: None}, d, req), "Failed to compile theme data [G-C-Reqs-%s-1] (%s): %s" % (command, command, path)

            final_check = check_theme('COMPILED_CUSTOM_THEME_DATA', compiled_theme_dict, re_comp_data=True)

            assert final_check[0], diagnostics.FormatResultsStr.failures(final_check[1])

        except Exception as E:
            print(traceback.format_exc())
            raise E.__class__('Failed to generate theme data due to the following errors:\n\n================ ERRORS ================\n' + E.__str__())

        else:
            return compiled_theme_dict


class Theme:
    class Default:
        @staticmethod
        def m(mode):
            global _theme_data
            assert mode in _theme_data, "Invalid mode '%s'" % str(mode)

            o = {**_theme_data[mode], **_theme_data['$global']}
            return o

        @staticmethod
        def dark_mode():
            global _theme_data
            return Theme.Default.m(
                _theme_data['$information']['$avail_modes']['Dark Mode']
            )

        @staticmethod
        def light_mode():
            return Theme.Default.m(
                _theme_data['$information']['$avail_modes']['Light Mode']
            )

        @staticmethod
        def default():
            return Theme.Default.m(
                _theme_data['$information']['$default_mode']
            )

    class UserPref:
        @staticmethod
        def m(mode):
            find_preference()
            global TMODE, TFILE

            if not conf.ConfigFile.raw['theme']['user_can_config']:
                raise Exception

            filename: str = TFILE
            assert type(filename) is str, "Invalid TFILE attribute"
            assert os.path.exists(TFILE), "TFILE does not exist; `find_preference()` should not have let this happen."

            file = AFIOObject(filename=filename, isFile=True, encrypt=False, owr_exs_err_par_owr_meth=True)
            raw = AFJSON(file.uid).load_file()

            _t = {
                **raw[mode if mode != '__USER_PREF__' else TMODE],
                **raw['$global']
            }

            return _t

        @staticmethod
        def pref():
            return Theme.UserPref.m('__USER_PREF__')

        @staticmethod
        def get_modes_list() -> list:
            a = list(load_theme_file(mode='$information')['$avail_modes'].keys())
            print(a)
            return a

        @staticmethod
        def get_theme_by_mode(mode) -> dict:
            return Theme.UserPref.m(load_theme_file()['$information']['$avail_modes'][mode])

    # TODO: Fix auto-correction logic + addition logic
    # TODO: Raise errors for erroneous addition requests
    # TODO: Add map-checking logic
    @staticmethod
    def SetCustomTheme(theme_file, theme) -> tuple:
        """
        **Theme.SetCustomTheme**

        :param theme_file: theme filename
        :param theme:      theme data
        :return:           tuple (all good?, failures (str), failures (tuple[str]))
        """

        assert conf.ConfigFile.raw['theme']['user_can_config'], "unsupported feature"

        reload_default()
        global TFILE, _theme_data, _theme_file

        assert type(TFILE) is str, "Failed to load theme file name."

        theme_file = _convert_path(theme_file)
        assert os.path.exists(theme_file), "File does not exist; create file using 'Editor._create_new_theme'"

        # Recursive Functions
        def rec_dict_path(key, value) -> tuple:
            if "\\" in key:
                k = (*key.split("\\"),)

                if len(k) > 1:
                    rdp = rec_dict_path("\\".join(i for i in k[1::]), value)
                    return (k[0], {k[0]: rdp[1]})

                else:
                    return (key, {key: value})

            else:
                return (key, {key: value})

        def rec_combine_theme_dict(og, new) -> dict:
            o = {}
            for item in og:
                if type(og[item]) is dict and item in new:
                    o[item] = rec_combine_theme_dict(og[item], new[item])
                elif item in new:
                    o[item] = new[item]
                else:
                    o[item] = og[item]

            return o

        # Assembler
        if theme not in ('def', -1):
            _t = {}
            for tk, tv in theme.items():
                rdp = rec_dict_path(tk, tv)
                _t[rdp[0]] = rdp[1][rdp[0]]

            # _r = {**_theme_data, **_t}  # Will not work for nested dicts; use RCTD function.
            _r = rec_combine_theme_dict(_theme_data, _t)
        else:
            _r = {**_theme_data}

        # Saving
        filename = theme_file.replace("\\", "/")
        print(filename)

        if not os.path.exists(filename):
            # Create
            directory = "\\".join(i for i in filename.split('/')[:-1:])

            if not os.path.exists(directory):
                os.makedirs(directory)

        res = diagnostics.DataDiagnostics.Theme.check_data(_r)
        if not res[0]:
            fail = diagnostics.FormatResultsStr.failures(res[1])
            return res[0], fail, res[1]

        _r = json.dumps(_r, indent=4)

        with open(filename, 'w') as UserPrefThemeFile:
            UserPrefThemeFile.write(_r)
            UserPrefThemeFile.close()

        return res[0], "No failures", ()

    @staticmethod
    def SetUserPref(theme_file, mode):
        find_preference()
        global TFILE

        assert type(TFILE) is str, "Failed to load theme file name."

        theme_file = _convert_path(theme_file)

        assert os.path.exists(theme_file), "File does not exist."

        f = open(theme_file, 'r')
        r = f.read()
        f.close()
        r = json.loads(r)  # If this fails, it will cause an error anyway; don't catch.

        assert diagnostics.DataDiagnostics.Theme.check_file(theme_file), "Invalid theme file."

        user_pref.Set.Theme.theme_pref((theme_file, mode,))

        find_preference()
