import qa_conf as conf, os, json, qa_protected_conf as protected_conf, qa_exceptions as exceptions, \
    qa_std as std


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
                if type(ret) is type(default):
                    f_s1 = False

            if f_s1:
                ret = default
                _Basic.IO.set(default, root, key)

            return ret

        @staticmethod
        def load_json(file_name):
            assert os.path.exists(file_name), "Invalid file provided (0)"
            with open(file_name) as file:
                r = file.read()
                file.close()
            try:
                o = json.loads(r)
            except:
                o = {}

            return o


class _Data:
    class Theme:
        root = "theme"
        theme_pref_key = "file/mode"

    class Global:
        p = [conf.Application.AppDataLoc, *protected_conf.Configuration.Files.pref_file_loc]
        p_fn = protected_conf.Configuration.Files.pref_file_name


class Set:
    class Theme:
        @staticmethod
        def theme_pref(data: tuple) -> None:
            if type(data) not in (tuple, list, ):
                raise exceptions.ParameterException(
                    "SCRIPT::U_PREF ;; FUNCTION::SET_THEME_MODE_PREF",
                    "MODE",
                    "TUPLE[STR, STR]",
                    type(data).__str__().upper(),
                    True,
                    "SC::U_PREF;;FUNC::S_T_MPref::VAR::MODE[user_inp[0]]"
                )

            def_file, dict_loc = data

            if "__CGET__" in dict_loc:
                tok = dict_loc.split("::")
                assert len(tok) == 2, "Failed to `__CGET__` default data; insufficient arguments."

                loc = "/".join(_ for _ in tok[1::]).strip('/')
                r = _Basic.IO.load_json(def_file)
                exs, d_found = std.data_at_dict_path(loc, r)
                assert exs, "Failed to `__CGET__` default data; invalid dict path."

                def_loc = d_found

            else:
                def_loc = dict_loc

            _Basic.IO.set((def_file, def_loc), _Data.Theme.root, _Data.Theme.theme_pref_key)

            return None


class Get:
    class Theme:
        @staticmethod
        def theme_pref(default: tuple):
            if type(default) not in (tuple, list, ):
                raise exceptions.ParameterException(
                    "SCRIPT::U_PREF ;; FUNCTION::GET_THEME_MODE_PREF",
                    "DEFAULT",
                    "TUPLE[STR, STR]",
                    type(default).__str__().upper(),
                    True,
                    "SC::U_PREF;;FUNC::G_T_MPref::VAR::DEF[user_inp[0]]"
                )

            def_file, dict_loc = default

            if "__CGET__" in dict_loc:
                tok = dict_loc.split("::")
                assert len(tok) == 2, "Failed to `__CGET__` default data; insufficient arguments."

                loc = "/".join(_ for _ in tok[1::]).strip('/')
                r = _Basic.IO.load_json(def_file)
                exs, data = std.data_at_dict_path(loc, r)
                assert exs, "Failed to `__CGET__` default data; invalid dict path."

                def_loc = data

            else:
                def_loc = dict_loc

            try:
                _fi, mode = _Basic.IO.get(
                    _Data.Theme.root,
                    _Data.Theme.theme_pref_key,
                    [def_file, def_loc]
                )

            except:
                _Basic.IO.set((def_file, def_loc), _Data.Theme.root, _Data.Theme.theme_pref_key)
                _fi, mode = default

            return {
                'file': _fi,
                'mode': mode
            }
