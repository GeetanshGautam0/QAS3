import os, conf, json, re, protected_conf
import traceback

FALSE = 0
TRUE = 1
CONDITIONAL = 2


class FileDiagnostics:

    class Critical:
        @staticmethod
        def required_files() -> tuple:
            """
            **Required Files**

            * Default theme file
            * low.json
            * conf.json
            * scripts.json

            :return: Tuple (All passed (bool), Failed (tuple), Passed (tuple), Tests ran (tuple))
            """

            req = (conf.Files.theme['default']['filename'], '.\\low.json', '.\\conf.json')

            output, passed = _run_file_exs_check(req)
            output = (not(len(output) > 0), output, passed, req)
            return output

        @staticmethod
        def required_scripts() -> tuple:
            """
            **Required Files**

            * Scripts from 'scripts.json'

            :return: Tuple (All passed (bool), Failed (tuple), Passed (tuple), Tests ran (tuple))
            """
            f = open("scripts.json", 'r')
            r = f.read()
            f.close()
            r = json.loads(r)

            req = (*r['all']['list'], )
            output, passed = _run_file_exs_check(req)
            output = (not(len(output) > 0), output, passed, req)
            return output

    class Recommendations:
        class Installation:
            @staticmethod
            def recommended_files() -> tuple:
                """
                **Recommendations**

                * src/icons (all)
                * src/sfx (all)
                * aid (all)
                :return: Tuple (All passed (bool), Failed (tuple), Passed (tuple), Tests ran (tuple))
                """

                req = ()

                for data_set, values in {
                    1: ({**conf.Files.app_icons, **conf.Files.files}, ['png', 'ico']),
                    2: ({**conf.Files.sfx}, ['file'])
                }.values():
                    pass
                    for _, v in data_set.items():
                        req = (*req, *(v[value] for value in values))

                req = (*req, *list(conf.Files.help.values()))
                output, passed = _run_file_exs_check(req)
                output = (not(len(output) > 0), output, passed, req)
                return output


class DataDiagnostics:
    class Theme:
        @staticmethod
        class _FileData:
            hc = "HEX_COLOR"
            tp = ("TYPE", )

            cond_checks_tbl = {
                "bg": [hc],
                "fg": [hc],
                "accent": [hc],
                "error": [hc],
                "ok": [hc],
                "warning": [hc],
                "gray": [hc],

                "font_face": [(*tp, str)],
                "title_size": [(*tp, int)],
                "sttl_size": [(*tp, int)],
                "big_para_size": [(*tp, int)],
                "main_size": [(*tp, int)],

                "width": [(*tp, int)],
                "color": [hc],

                "x": [(*tp, int)],
                "y": [(*tp, int)],
            }

            conditional_checks = {
                "HEX_COLOR": [
                    lambda *args: type(*args[0]) is str,
                    lambda *args: len("".join(_ for _ in re.findall(r"[0-9a-fA-F]", args[0]))) in [3, 6]
                ],
                "TYPE": [
                    lambda *args: type(args[0]) is args[1][1]
                ]
            }

        @staticmethod
        def check_defaults() -> tuple:
            """
            :return: Tuple (all good? (bool), failed (tuple), passed (tuple), violations (tuple))
            """
            pass

        @staticmethod
        def check_user_pref() -> tuple:
            """
            :return: Tuple (all good? (bool), failed (tuple), passed (tuple), violations (tuple))
            """

            ucit = conf.ConfigFile.raw['theme']['user_can_install_themes']

            vio = passed = failed = ()

            assert ucit['root'], "Application doesn't support feature"

            direc = os.path.join(
                conf.Application.AppDataLoc if ucit['in_appdata'] else '.\\',
                ucit['dir']
            ).replace("\\", "/")

            if not os.path.exists(direc):
                o = (True, (), ("no themes installed", ), ())
                os.makedirs(direc)
                return o

            for folder in os.listdir(direc):
                folder_abs = os.path.join(direc, folder)

                assert os.path.exists(folder_abs), "Path compilation logic error"

                if os.path.isdir(folder_abs):
                    ls = os.listdir(folder_abs)
                    assert len(ls) >= 0, "Invalid ls data"

                    if len(ls) == 0:
                        o = (True, (), ("no themes installed",), ())
                        return o

                    for file in ls:
                        file_abs = os.path.join(folder_abs, file).replace("\\", "/")

                        assert os.path.exists(folder_abs), "Path compilation logic error (lvl2)"

                        if file.split(".")[-1] != 'json':
                            vio = (*vio, "VIOLATION: Non-json file found in 2nd level direc ('%s/%s')" % (
                                folder, file
                            ))

                            continue

                        if file.split('.')[0] != folder:
                            vio = (*vio, "VIOLATION: File does not share the same name as directory (%s/%s)" % (
                                folder, file
                            ))

                        try:
                            with open(file_abs, 'r') as file:
                                r = file.read()
                                file.close()

                            raw_json = json.loads(r)

                        except:
                            failed = (*failed, "Failed to read file '%s/%s'" % (folder, file))
                            continue

                        try:
                            check_theme(raw_json)
                        except:
                            failed = (*failed, "Failed to check theme data in '%s/%s'" % (folder, file))
                            continue

                else:
                    vio = (*vio, "VIOLATION: Non-directory item found in 1st level direc ('%s')" % str(folder))

        @staticmethod
        def check_custom() -> tuple:
            """
            :return: Tuple (all good? (bool), failed (tuple), passed (tuple), violations (tuple))
            """

            p = [conf.Application.AppDataLoc, *protected_conf.Configuration.Files.pref_file_loc]
            p_fn = conf.ConfigFile.raw['theme']['custom_config_file']

            pass

        @staticmethod
        def check_file(file_path, mode=any) -> bool:
            pass


def check_theme(theme_data) -> dict:
    vio = passed = failed = ()
    ch_tbl = {
        "$information": {
            "$name": {},
            "$avail_modes": {},
            "$default_mode": {}
        },
        "./$avail_modes/any": {
            "bg": {},
            "fg": {},
            "ok": {},
            "warning": {},
            "error": {},
            "gray": {},
            "accent": {},
            "font": {
                "font_face": {},
                "title_size": {},
                "sttl_size": {},
                "big_para_size": {},
                "main_size": {}
            },
            "border": {
                "width": {},
                "color": {}
            }
        },
        "$global": {
            "padding": {
                "x": {},
                "y": {}
            }
        }
    }

    def rec_check(data, ch_tbl, lvl="./") -> tuple:
        in_vio = in_passed = in_failed = ()

        # The mode 'precise' checks
        checks = DataDiagnostics.Theme._FileData.conditional_checks
        checks_tbl = DataDiagnostics.Theme._FileData.cond_checks_tbl

        for key, value in data.items():
            if type(value is dict):
                in_failed, in_passed, in_vio = rec_check(value, ch_tbl)
                continue

            if key in checks_tbl:
                for check in checks[checks_tbl[key]]:
                    try:
                        res = check(value, checks_tbl[key])
                        if res:
                            in_passed = (*in_passed, "PASSED: Passed test '%s' on data." % str(checks_tbl[key]))
                    except Exception as E:
                        print(E, traceback.format_exc(), sep="\n\n")
                        in_failed = (*in_failed, "FAILED: Failed to conduct test '%s' on data" % str(checks_tbl[key]))

    failed, passed, vio = rec_check(theme_data, )

    vio = (*set(vio), )
    passed = (*set(passed), )
    failed = (*set(failed), )

    return {
        'p': passed,
        'f': failed,
        'v': vio
    }
