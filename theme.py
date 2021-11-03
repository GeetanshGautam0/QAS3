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


def find_preference() -> tuple:
    global TMODE, TFILE
    default = (
        conf.ConfigFile.raw['theme']['theme_file'],
        '__CGET__::$information\\$default_mode'
    )
    pref = user_pref.Get.Theme.theme_pref(default)
    TMODE = pref['mode']
    TFILE = pref['file']

    if not os.path.exists(TFILE):
        # Rev to default
        revert_to_default()

    check_theme(TFILE.split('\\')[-1], user_pref._Basic.IO.load_json(TFILE))
    return tuple([TMODE, TFILE])


def reload_default(n_fp: bool = False) -> None:
    global _theme_data, _theme_file
    if not n_fp:
        find_preference()
    _theme_data = AFJSON(_theme_file.uid).load_file()
    check_theme('default', _theme_data)
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
        check_theme(TFILE.split('\\')[-1], r)

        return r if mode is all else r[TMODE if mode == '__USER_PREF__' else mode]

    else:
        assert os.path.exists(filename), "Theme file provided does not exist."
        r = user_pref._Basic.IO.load_json(filename)

        check_theme(filename, r)

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


def check_theme(name: str, data, *args) -> None:
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
    print("\n\n\n'%s':\n" % name, diagnostics.FormatResultsStr.format_theme_analysis_report(*res[1::]), sep="")
    assert res[0], "%s:\n" % name + diagnostics.FormatResultsStr.failures(res[1])


reload_default()


class Editor:
    @staticmethod
    def create_new_theme(mapping: dict, author: str, name: str, default_val: str, themes: dict,
                         global_data: dict) -> dict:
        """
        **Editor.create_new_theme**

        Will automatically generate the data required for a new theme.

        :param mapping:     mapping information (dict [{name: str}: {code: str}])
        :param author:      theme author (str)
        :param name:        theme master name (str)
        :param default_val: default <code> value
        :param themes:      themes available (dict[{code: str}: {theme_data: dict}])
        :param global_data: global data (dict)
        :return:            compiled theme data ({dict})
        """

        assert isinstance(mapping, dict), "Invalid theme mapping data: expected a python dictionary {<Name>: <Code>}"
        assert isinstance(author, str), "Invalid theme author data: expected type <String>"
        assert isinstance(name, str), "Invalid theme name: expected type <String>"
        assert isinstance(default_val, str), "Invalid default <Code>: expected type <String>"
        assert isinstance(themes,
                          dict), "Invalid theme(s): expected python dictionary {<Mapped_Code>: <Theme_Data [dict]>}"
        assert isinstance(global_data, str), "Invalid global data: expected python dictionary"

        assert len(author.strip()) > 0, "Invalid theme author data: insufficient data"
        assert len(name.strip()), "Invalid theme name: insufficient data"
        assert len(default_val.strip()) > 0, "Invalid default <Code>: insufficient data"
        assert len(global_data.strip()) > 0, "Invalid global data: insufficient data"

        theme_req = {
            'bg': ['HEX_COLOR', str],
            'fg': ['HEX_COLOR', 'fg', str],
            'ok': ['HEX_COLOR', 'fg', str],
            'error': ['HEX_COLOR', 'fg', str],
            'warning': ['HEX_COLOR', 'fg', str],
            'gray': ['HEX_COLOR', 'fg', str],
            'accent': ['HEX_COLOR', 'fg', str],

            'font/font_face': [str],
            'font/title_size': [int],
            'font/sttl_size': [int],
            'font/big_para_size': [int],
            'font/main_size': [int],

            'border/width': [int],
            'border/color': ['HEX_COLOR', str],
        }

        L = {
            'theme':
                {
                    'root': 9,
                    'root/font': 5,
                    'root/border': 2
                },
            'global':
                {
                    'root/$global': 1,
                    'root/$global/padding': 2,
                    'root/$information': 4,
                    'root/$information/$avail_modes': len(themes),
                }
        }

        # Pass the following args
        # Theme, data, check_req
        checks_map = {
            'HEX_COLOR': [
                lambda *arguments: type(arguments[1]) is str,
                lambda *arguments: len("".join(_ for _ in re.findall(r"[0-9a-fA-F]", arguments[1]))) in [3, 6]
            ],
            'fg': [
                lambda *arguments: std.check_hex_contrast(arguments[0]['bg'], arguments[1])[0]
            ],
            'T_CODE_C': [
                lambda *arguments: type(arguments[1]) is str,
                lambda *arguments: arguments[1][0] == '$',
                lambda *arguments: int(arguments[1][1::]) or True
            ]
        }

        for theme_code, theme in themes.items():
            assert isinstance(theme_code, str), "Invalid theme code '%s'" % theme_code
            assert theme_code[0] == '$', "Invalid theme code '%s'; must start with '$' and then contain an integer"
            try:
                int(theme_code[1::])
            except:
                assert False, "Invalid theme code '%s'; must start with '$' and then contain an integer"
            assert isinstance(theme, dict), "Invalid theme data; theme data must be a python dictionary"
            assert len(theme) == L['theme']['root'], "Invalid theme data: missing theme data."

            for data in L['theme']:
                pass
            # TODO: Come here

        compiled_theme_dict = {
            "$information": {
                '$author': author.strip(),
                '$name': name.strip(),
                '$avail_modes': mapping,
                '$default_mode': default_val.strip()
            },
            "$global": global_data
        }

        global_req = {
            'root/$global/padding/x': [int],
            'root/$global/padding/y': [int],
            'root/$information/$default_mode': ['T_CODE_C']
        }

        req_dicts = {
            'root': [
                '$global',
                '$information',
                '$information/$avail_modes',
                '$global/padding'
            ],
            '<<theme>>': [
                'font',
                'border'
            ],
        }

        for root, ps in req_dicts.items():
            if root == '<<theme>>':
                continue

            for p, dicts in ps:
                path = '%s/%s' % (root, p)
                # Two birds one stone
                ex, d = std.data_at_dict_path(path, compiled_theme_dict)
                assert ex, "Failed to compile theme data [EXS-1]: %s" % path
                assert len(ex) == L['global'][path], "Failed to compile theme data [LENGTH]: %s" % path

        for path, reqs in global_req.items():
            ex, d = std.data_at_dict_path(path, compiled_theme_dict)
            assert ex, "Failed to compile theme data [EXS-2]: %s" % path
            for req in reqs:
                if isinstance(req, tuple) or isinstance(req, list):
                    command = req[0]
                    # args = (*req[1::], )
                else:
                    command = req
                    # args = ()

                if isinstance(req, type):
                    assert isinstance(d, req), "Failed to compile theme data [G-C-Reqs-TP-1]: %s" % path
                    continue

                checks = checks_map[command]
                for check in checks:
                    assert check({None: None}, d, req), "Failed to compile theme data [G-C-Reqs-%s-1]: %s" % (command, path)

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
        assert os.path.exists(theme_file), "File does not exist; create file using 'Editor.create_new_theme'"

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
