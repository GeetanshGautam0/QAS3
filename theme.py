from appfunctions import *
# import prconf as _prconf
from appfunctions import *
import conf, os,  user_pref

_prconf = protected_conf

TMODE = None

_theme_file = AFIOObject(filename=conf.ConfigFile.raw['theme']['theme_file'], isFile=True, owr_exs_err_par_owr_meth=True)
_theme_data: dict = {None: None}


def find_preference() -> str:
    global TMODE
    default = conf.ConfigFile.raw['theme']['default_mode'].strip()[0].lower()
    TMODE = user_pref.Get.Theme.mode_pref(default)
    return TMODE

def reload_theme() -> None:
    global _theme_data, _theme_file
    find_preference()
    _theme_data = AFJSON(_theme_file.uid).load_file()

def set_preference(mode) -> None:
    TMODE = user_pref.Set.Theme.mode_pref(mode)

reload_theme()


class Theme:
    class Default:
        @staticmethod
        def m(mode):
            global _theme_data

            reload_theme()

            _t = {
                **_theme_data[mode],
                **_theme_data
            }

            del _t['dark']
            del _t['light']

            return _t

        @staticmethod
        def dark_mode():
            return Theme.Default.m('dark')

        @staticmethod
        def light_mode():
            return Theme.Default.m('light')

    class UserPref:
        @staticmethod
        def m(mode):
            global _theme_file

            reload_theme()

            if not conf.ConfigFile.raw['theme']['user_can_config']:
                raise Exception

            filename = os.path.join(
                conf.Application.AppDataLoc,
                *protected_conf.Configuration.Files.pref_file_loc,
                conf.ConfigFile.raw['theme']['custom_config_file']
            )

            if not os.path.exists(filename):
                # Create, Copy Default, Paste to New
                directory = os.path.join(
                    conf.Application.AppDataLoc,
                    *protected_conf.Configuration.Files.pref_file_loc
                )

                if not os.path.exists(directory):
                    os.makedirs(directory)

                with open(_theme_file.filename, 'r') as original:
                    with open(filename, 'w') as new:
                        new.write(original.read())
                        new.close()
                    original.close()

                return Theme.Default.m(mode)

            file = AFIOObject(filename=filename, isFile=True, encrypt=False, owr_exs_err_par_owr_meth=True)
            raw  = AFJSON(file.uid).load_file()

            _t = {
                **raw[mode],
                **raw
            }

            del _t['dark']
            del _t['light']

            return _t

        @staticmethod
        def dark_mode():
            return Theme.UserPref.m('dark') if conf.ConfigFile.raw['theme']['user_can_config'] else Theme.Default.dark_mode()

        @staticmethod
        def light_mode():
            return Theme.UserPref.m('light') if conf.ConfigFile.raw['theme']['user_can_config'] else Theme.Default.light_mode()

    @staticmethod
    def SetCustomTheme(theme):
        global _theme_data, _theme_file

        if not conf.ConfigFile.raw['theme']['user_can_config']:
            raise Exception

        reload_theme()

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

            # _r = {**_theme_data, **_t}  # Will not work for nested dicts; use rctd function.
            _r = rec_combine_theme_dict(_theme_data, _t)
        else:
            _r = {**_theme_data}

        # Saving
        filename = os.path.join(
            conf.Application.AppDataLoc,
            *protected_conf.Configuration.Files.pref_file_loc,
            conf.ConfigFile.raw['theme']['custom_config_file']
        )

        if not os.path.exists(filename):
            # Create
            directory = os.path.join(
                conf.Application.AppDataLoc,
                *protected_conf.Configuration.Files.pref_file_loc
            )

            if not os.path.exists(directory):
                os.makedirs(directory)

            # with open(_theme_file.filename, 'r') as original:
            #     with open(filename, 'w') as new:
            #         new.write(original.read())
            #         new.close()
            #     original.close()

        with open(filename, 'w') as UserPrefThemeFile:
            UserPrefThemeFile.write(json.dumps(_r, indent=4))
            UserPrefThemeFile.close()

    @staticmethod
    def SetUserPref(mode):
        user_pref.Set.Theme.mode_pref(mode)
