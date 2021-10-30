import os, conf, json, re, protected_conf, wcag_contrast_ratio, traceback, colors, std

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
            output = (not (len(output) > 0), output, passed, req)
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

            req = (*r['all']['list'],)
            output, passed = _run_file_exs_check(req)
            output = (not (len(output) > 0), output, passed, req)
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
                output = (not (len(output) > 0), output, passed, req)
                return output


class DataDiagnostics:
    class Theme:
        @staticmethod
        class _FileData:
            hc = "HEX_COLOR"
            tp = ("TYPE",)

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
                    lambda *args: type(args[0]) is str,
                    lambda *args: len("".join(_ for _ in re.findall(r"[0-9a-fA-F]", args[0]))) in [3, 6]
                ],
                "TYPE": [
                    lambda *args: type(args[0]) is args[-1]
                ]
            }

        @staticmethod
        def check_defaults() -> tuple:
            """
            :return: Tuple (all good? (bool), failed (tuple), passed (tuple), violations (tuple))
            """
            direc = conf.ConfigFile.raw['theme']['theme_root'].replace("\\", "/")
            return _check_directory(direc)

        @staticmethod
        def check_user_pref() -> tuple:
            """
            :return: Tuple (all good? (bool), failed (tuple), passed (tuple), violations (tuple), contrast results)
            """

            ucit = conf.ConfigFile.raw['theme']['user_can_install_themes']
            assert ucit['root'], "Application doesn't support feature"

            direc = os.path.join(
                conf.Application.AppDataLoc if ucit['in_appdata'] else '.\\',
                ucit['dir']
            ).replace("\\", "/")

            return _check_directory(direc)

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


# STRUCT: Functions \/ ;; Classes /\


def _check_directory(direc) -> tuple:
    """
    :return: Tuple (all good? (bool), failed (tuple), passed (tuple), violations (tuple), conrast results)
    """

    vio = passed = failed = contrast = ()

    if not os.path.exists(direc):
        o = (True, (), ("no themes installed",), ())
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
                    with open(file_abs, 'r') as file_inst:
                        r = file_inst.read()
                        file_inst.close()

                    raw_json = json.loads(r)

                except:
                    failed = (*failed, "Failed to read file '%s/%s'" % (folder, file))
                    continue

                try:
                    r = _check_theme(raw_json)
                except:
                    print(traceback.format_exc())
                    failed = (*failed, "Failed to check theme data in '%s/%s'" % (folder, file))
                    continue

                passed = (*passed, *r['p'])
                failed = (*failed, *r['f'])
                vio = (*vio, *r['v'])
                contrast = (*contrast, *r['c'])

        else:
            vio = (*vio, "VIOLATION: Non-directory item found in 1st level direc ('%s')" % str(folder))

    return len(failed) == 0, failed, passed, vio, contrast


def _check_theme(theme_data) -> dict:
    passed = failed = contrast = ()

    assert "$information" in theme_data, "Invalid theme data; fatal"
    assert "$avail_modes" in theme_data['$information'], "Invalid theme data; fatal"
    assert "$global" in theme_data, "Invalid theme data; fatal"

    try:
        for name, theme_id in theme_data['$information']['$avail_modes'].items():
            if not theme_id in theme_data:
                failed = (*failed, "FAILED: Invalid theme mode mapping data.")
            else:
                passed = (*passed, "PASSED: Theme mode '%s' found in map and data sections." % theme_id)

    except:
        print(traceback.format_exc())
        failed = (*failed, "FAILED: Failed to check mapping; fatal")

    try:
        a: dict = {**theme_data}
        del a['$global']
        del a['$information']

        if len(a) != len(theme_data['$information']['$avail_modes']):  # Pass
            failed = (*failed, "FAILED: Invalid theme file data (pot. mapping error [author-caused]).")

        for theme_code, theme_name_data in a.items():
            name = theme_data['$information']['$avail_modes']
            assert isinstance(theme_code, str), "Invalid theme mapping data. (%s)" % str(theme_code)
            assert theme_code in (*name.values(), ), "Invalid theme mapping data. (%s)" % theme_code
            assert theme_code[0] == "$", "Invalid theme mapping data; expected '$' character in front of theme decleration. (%s)" % theme_code

            try:
                name = (*name.keys(),)[(*name.values(),).index(theme_code)]
            except:
                failed = (*failed, "FAILED: Invalid theme mapping data (%s)." % theme_code)

            assert 'bg' in theme_name_data and 'fg' in theme_name_data, "Invalid theme data (%s.)" % theme_code

            ts1 = True
            for color in [theme_name_data['fg'], theme_name_data['bg']]:
                for test in DataDiagnostics.Theme._FileData.conditional_checks['HEX_COLOR']:
                    ts1 = ts1 and test(color)
                    if not ts1:
                        break
                if not ts1:
                    break

            assert ts1, "Invalid theme data; colors 'bg', 'fg' don't pass tests for HEX_COLOR"

            def map_rgb(color_rgb: tuple) -> tuple:
                assert len(color_rgb) == 3

                o_min_val = 0.0
                o_max_val = 1.0
                i_min_val = o_min_val
                i_max_val = 255.0 - (i_min_val - o_max_val)

                comp_ratio = o_max_val / i_max_val
                o_tuple = ()

                for col in color_rgb:
                    o_tuple = (*o_tuple, std.float_map(col, 0.00, 255.00, 0.00, 1.00))

                return o_tuple

            base = 'bg'
            for check_with in ['fg', 'accent', 'error', 'warning', 'ok']:
                back = colors.Convert.HexToRGB(theme_name_data['bg'])
                front = colors.Convert.HexToRGB(theme_name_data['fg'])

                AA_res = wcag_contrast_ratio.passes_AA(wcag_contrast_ratio.rgb(map_rgb(back), map_rgb(front)))
                AAA_res = wcag_contrast_ratio.passes_AAA(wcag_contrast_ratio.rgb(map_rgb(back), map_rgb(front)))

                contrast = (
                    *contrast,
                    "Contrast between '%s' and '%s': passes AA (required): %s, passes AAA (recommended): %s" %
                    (base, check_with, str(AA_res), str(AAA_res))
                )

                assert AA_res, "Insufficient contrast in theme."

    except AssertionError as E:
        failed = (*failed, "FAILED: Failed to conduct contrast check between foreground and background colors. :: %s" % E)

    except Exception as E:
        failed = (
            *failed,
            "FAILED: Failed to test theme data (POTENTIALLY SCRIPT ERROR) :: %s" % E
        )

    else:
        passed = (*passed, "PASSED: Passed contrast checks and theme mapping data checks.")

    gf1 = (len(failed) == 0)

    if gf1:
        check_tbl = {
            "root": {
                "$information": {
                    "$name": "",
                    "$avail_modes": {},
                    "$default_mode": ""
                },
                "any_mode": {
                    "bg": "",
                    "fg": "",
                    "ok": "",
                    "warning": "",
                    "error": "",
                    "gray": "",
                    "accent": "",
                    "font": {
                        "font_face": "",
                        "title_size": 0,
                        "sttl_size": 0,
                        "big_para_size": 0,
                        "main_size": 0
                    },
                    "border": {
                        "width": 0,
                        "color": ""
                    }
                },
                "$global": {
                    "padding": {
                        "x": 0,
                        "y": 0
                    }
                }
            }
        }

        def rec_check(data: dict, ch_tbl, lvl) -> tuple:
            assert type(data) is dict, "Failed to check theme file - invalid theme data provided (1)"
            in_vio = in_passed = in_failed = ()

            if len(data) < 0:
                return (), (), ()

            base = {**data}
            ch_base = {**ch_tbl}

            for level in lvl.split("/"):
                if level[0] == '$':
                    if level[1::].isdigit():
                        level = 'any_mode'

                assert level in ch_base, "Invalid dictionary key location."
                if type(ch_base[level]) is dict:
                    ch_base = ch_base[level]

            for key, value in ch_base.items():
                if key == 'any_mode':
                    continue

                if key in base:
                    in_passed = (*in_passed, "PASSED: Key '%s/%s' does exist." % (lvl, key))

                    if type(value) is type(base[key]) and None not in (value, base[key]):
                        in_passed = (*in_passed,
                                     "PASSED: Key '%s/%s' has the correct type of data (validity not checked.)" % (
                                         lvl, key))

                    else:
                        in_failed = (*in_failed,
                                     "FAILED: Key '%s/%s' does not have the correct type of data; expected: %s, got: %s." % (
                                         lvl, key, type(value), type(base[key])))
                else:
                    in_failed = (*in_failed, "FAILED: Key '%s/%s' does not exist." % (lvl, key))

            # The mode 'precise' checks
            checks = DataDiagnostics.Theme._FileData.conditional_checks
            checks_tbl = DataDiagnostics.Theme._FileData.cond_checks_tbl

            for key, value in data.items():
                if type(value) is dict:
                    f, p, v = rec_check(value, ch_tbl, "/".join(i for i in [lvl, key]).strip("/"))
                    in_failed = (*in_failed, *f)
                    in_passed = (*in_passed, *p)
                    in_vio = (*in_vio, *v)
                    continue

                if key in checks_tbl:
                    for check_todo in checks_tbl[key]:
                        if type(check_todo) is tuple:
                            args = check_todo[1::]
                            check_todo = check_todo[0]
                        else:
                            args = ()

                        for check in checks[check_todo]:
                            try:

                                res = check(value, check_todo, *args)
                                if res:
                                    in_passed = (
                                        *in_passed,
                                        "PASSED: Passed test '%s/%s' on data." % (lvl, str(checks_tbl[key])))
                                else:
                                    in_failed = (
                                        *in_failed,
                                        "FAILED: Failed test condition '%s/%s'" % (lvl, str(checks_tbl[key])))

                            except Exception as E:
                                print(E, traceback.format_exc(), sep="\n\n")
                                in_failed = (
                                    *in_failed,
                                    "FAILED: Failed to conduct test '%s/%s' on data" % (lvl, str(checks_tbl[key]))
                                )

            return (*set(in_failed),), (*set(in_passed),), (*set(in_vio),)

        failed, passed, vio = rec_check(theme_data, check_tbl, 'root')

    else:
        vio = ()

    vio = (*set(vio),)
    passed = (*set(passed),)
    failed = (*set(failed),)
    contrast = (*set(contrast), )

    return {
        'p': passed,
        'f': failed,
        'v': vio,
        'c': contrast
    }


def _format_theme_analysis_report(f, p, v, c):
    f = ("Total failures: %s" % (str(len(f))), *f)
    p = ("Total passed tests: %s" % (str(len(p))), *p)
    v = ("Total violations: %s" % (str(len(v))), *v)
    c = ("# Contrast checks ran: %s" % str(len(c)), *c)

    b = "Ran multiple tests on theme file; the following are the results:"
    b += "\n\n-------- FAILURES --------\n"
    b += "\n* ".join(fail for fail in f)
    b += "\n\n-------- PASSED --------\n"
    b += "\n* ".join(pas for pas in p)
    b += "\n\n-------- VIOLATIONS --------\n"
    b += "\n* ".join(vio for vio in v)
    b += "\n\n-------- CONTRASTS --------\n"
    b += "\n* ".join(con for con in c)

    return b


def _run_file_exs_check(req: tuple):
    output = passed = ()
    for item in req:
        if os.path.exists(item):
            passed = (*passed, item)
        else:
            output = (*output, item)

    output = (output, passed)
    return output
