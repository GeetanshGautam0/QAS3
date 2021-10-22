import conf, os, json, importlib
import exceptions

with open("low.json", 'r') as file:
    _l_json = json.loads(file.read())
    file.close()

protected_confFile: str = _l_json['pcm_file']
protected_conf = importlib.import_module(protected_confFile)


class _Basic:
    class IO:
        @staticmethod
        def check_file() -> bool:
            filename = os.path.join(*_Data.Global.p, _Data.Global.p_fn)
            directory = os.path.join(*_Data.Global.p)
            if not os.path.exists(filename):
                if not os.path.exists(directory):
                    os.makedirs(directory)

                with open(filename, 'w') as pref_file:
                    pref_file.write(json.dumps({}, indent=4))
                    pref_file.close()

            else:
                try:
                    pref_file = open(filename, 'r')
                    json.loads(pref_file.read())
                    pref_file.close()

                    return True

                except Exception as E:
                    print(E)
                    with open(filename, 'w') as pref_file:
                        pref_file.write(json.dumps({}, indent=4))
                        pref_file.close()

            return False

        @staticmethod
        def load_file() -> dict:
            if not _Basic.IO.check_file():
                return {}

            directory = os.path.join(*_Data.Global.p)
            filename = os.path.join(directory, _Data.Global.p_fn)

            with open(filename, 'r') as pref_file:
                ret = json.loads(pref_file.read())
                pref_file.close()

            return ret

        @staticmethod
        def set(value, root, key):
            _Basic.IO.check_file()
            _r = _Basic.IO.load_file()
            f1 = True

            if root in _r:
                if type(_r[root]) is dict:
                    f1 = False

            if f1:
                if root not in _r:
                    _r[root] = {}

            _r[root][key] = value

            _s = json.dumps(_r, indent=4)

            with open(os.path.join(*_Data.Global.p, _Data.Global.p_fn), 'w') as pref_file:
                pref_file.write(_s)
                pref_file.close()

        @staticmethod
        def get(root, key, default):
            _Basic.IO.check_file()
            _r = _Basic.IO.load_file()

            f_s1 = True

            if root in _r:
                ret = _r[root].get(key)
                if ret is not None:
                    f_s1 = False

            if f_s1:
                ret = default
                _Basic.IO.set(default, root, key)

            return ret


class _Data:
    class Theme:
        root = "theme"
        mode_pref_key = "mode"
        mode_pref_accepted = ('l', 'd')

    class Global:
        p = [conf.Application.AppDataLoc, *protected_conf.Configuration.Files.pref_file_loc]
        p_fn = protected_conf.Configuration.Files.pref_file_name


class Set:
    class Theme:
        @staticmethod
        def mode_pref(mode):
            if type(mode) is not str:
                raise exceptions.ParameterException(
                    "SCRIPT::U_PREF ;; FUNCTION::SET_THEME_MODE_PREF",
                    "MODE",
                    "STR[accp. >> in %s]" % str(_Data.Theme.mode_pref_accepted),
                    type(mode).__str__().upper(),
                    True,
                    "SC::U_PREF;;FUNC::S_T_MPref::VAR::MODE[user_inp[0]]"
                )

            elif mode not in _Data.Theme.mode_pref_accepted:
                raise exceptions.ParameterException(
                    "SCRIPT::U_PREF ;; FUNCTION::SET_THEME_MODE_PREF",
                    "MODE",
                    "STR[accp. >> in %s]" % str(_Data.Theme.mode_pref_accepted),
                    mode.strip().upper(),
                    True,
                    "SC::U_PREF;;FUNC::S_T_MPref::VAR::MODE[user_inp[0]]"
                )

            _Basic.IO.set(mode, _Data.Theme.root, _Data.Theme.mode_pref_key)


class Get:
    class Theme:
        @staticmethod
        def mode_pref(default):
            if type(default) is not str:
                raise exceptions.ParameterException(
                    "SCRIPT::U_PREF ;; FUNCTION::GET_THEME_MODE_PREF",
                    "DEFAULT",
                    "STR[accp. >> in %s]" % str(_Data.Theme.mode_pref_accepted),
                    type(default).__str__().upper(),
                    True,
                    "SC::U_PREF;;FUNC::G_T_MPref::VAR::DEF[user_inp[0]]"
                )

            elif default not in _Data.Theme.mode_pref_accepted:
                raise exceptions.ParameterException(
                    "SCRIPT::U_PREF ;; FUNCTION::GET_THEME_MODE_PREF",
                    "MODE",
                    "STR[accp. >> in %s]" % str(_Data.Theme.mode_pref_accepted),
                    default.strip().upper(),
                    True,
                    "SC::U_PREF;;FUNC::G_T_MPref::VAR::DEF[user_inp[0]]"
                )

            ret = _Basic.IO.get(_Data.Theme.root, _Data.Theme.mode_pref_key, default)

            return ret
