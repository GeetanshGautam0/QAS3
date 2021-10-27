import diagnostics
from appfunctions import *
import conf, os,  user_pref

TMODE = TFILE = None

_theme_file = AFIOObject(filename=conf.ConfigFile.raw['theme']['theme_file'], isFile=True, owr_exs_err_par_owr_meth=True)
_theme_data: dict = {None: None}


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
    filename = filename.replace("$appdata", conf.Application.AppDataLoc)
    filename = filename.replace("$curr", TFILE)
    filename = filename.replace("\\", "/")

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
    file_name = file_name.replace("$appdata", conf.Application.AppDataLoc)
    file_name = file_name.replace("$curr", TFILE)
    file_name = file_name.replace("\\", "/")

    if mode == -1:
        reload_default(True)
        mode = _theme_data['$information']['$default_mode']

    user_pref.Set.Theme.theme_pref((file_name, mode,))

    return


def check_theme(name: str, data, *args) -> None:
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
    # assert len(data['$information']['$map']) == len(data['$information']['$avail_modes']), "Invalid theme file (%s)" % name


reload_default()


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

    @staticmethod
    def SetCustomTheme(theme_file, theme):
        if not conf.ConfigFile.raw['theme']['user_can_config']:
            raise Exception

        reload_default()
        global TFILE, _theme_data, _theme_file

        assert type(TFILE) is str, "Failed to load theme file name."

        theme_file = theme_file.replace("$appdata", conf.Application.AppDataLoc)
        theme_file = theme_file.replace("$curr", TFILE)
        theme_file = theme_file.replace("\\", "/")

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
        filename = theme_file

        if not os.path.exists(filename):
            # Create
            directory = "\\".join(i for i in filename.split('\\')[:-1:])

            if not os.path.exists(directory):
                os.makedirs(directory)

        with open(filename, 'w') as UserPrefThemeFile:
            UserPrefThemeFile.write(json.dumps(_r, indent=4))
            UserPrefThemeFile.close()

    @staticmethod
    def SetUserPref(theme_file, mode):
        find_preference()
        global TFILE

        assert type(TFILE) is str, "Failed to load theme file name."

        theme_file = theme_file.replace("$appdata", conf.Application.AppDataLoc)
        theme_file = theme_file.replace("$curr", TFILE)
        theme_file = theme_file.replace("\\", "/")

        assert os.path.exists(theme_file), "File does not exist."
        f = open(theme_file, 'r')
        r = f.read()
        f.close()
        r = json.loads(r)  # If this fails, it will cause an error anyway; don't catch.

        assert diagnostics.DataDiagnostics.Theme.check_file(theme_file, mode=mode), "Invalid theme file."

        user_pref.Set.Theme.theme_pref((theme_file, mode, ))

        find_preference()
