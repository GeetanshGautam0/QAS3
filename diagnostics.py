import os, conf, theme, json, re
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
            data_type = {
                '$information': {
                    'information': 'Contains information about the theme',
                    'type': dict,
                    'required': TRUE,  # False = recommended, but not required.
                    'children': {
                        '$name': {
                            'information': 'Name of the theme',
                            'type': str,
                            'required': TRUE,
                            'children': {},
                            'default': "Unknown"
                        },
                        '$author': {
                            'information': 'Name of the author of the theme',
                            'type': str,
                            'required': FALSE,
                            'children': {},
                            "default": "Unknown"
                        },
                        '$avail_modes': {
                            'information': 'Describes the modes available in the theme ("d" or "l")',
                            'type': list,
                            'required': TRUE,
                            'children': {},
                            "default": ['l']
                        }
                    }
                },
                "dark": {
                    "information": "Dark mode colors",
                    "type": dict,
                    'required': CONDITIONAL,
                    'conditions': ['len[d, l] > 0'],
                    'children': {
                        "name": {
                            "information": "Name of the mode",
                            "type": str,
                            'required': TRUE,
                            'children': {},
                            "default": "Dark Mode"
                        },
                        'bg': {
                            "information": "Background color",
                            "type": str,
                            'required': TRUE,
                            'children': {},
                            "default": "#202020",
                            'conditions': ['HEX_COLOR']
                        },
                        'fg': {
                            "information": "Foreground color",
                            "type": str,
                            'required': TRUE,
                            'children': {},
                            "default": "#ffffff",
                            'conditions': ['HEX_COLOR']
                        },
                        'ok': {
                            "information": "Color for success prompts",
                            "type": str,
                            'required': TRUE,
                            'children': {},
                            "default": "#8bb174",
                            'conditions': ['HEX_COLOR']
                        },
                        'warning': {
                            "information": "Color for warning prompts",
                            "type": str,
                            'required': TRUE,
                            'children': {},
                            "default": "#ffb30f",
                            'conditions': ['HEX_COLOR']
                        },
                        'error': {
                            "information": "Color for warning prompts",
                            "type": str,
                            'required': TRUE,
                            'children': {},
                            "default": "#db504a",
                            'conditions': ['HEX_COLOR']
                        }
                    }
                },
                "light": {
                    "information": "Light mode colors",
                    "type": dict,
                    'required': CONDITIONAL,
                    'conditions': ['len[d, l] > 0'],
                    'children': {
                        "name": {
                            "information": "Name of the mode",
                            "type": str,
                            'required': TRUE,
                            'children': {},
                            "default": "Light  Mode"
                        },
                        'bg': {
                            "information": "Background color",
                            "type": str,
                            'required': TRUE,
                            'children': {},
                            "default": "#ffffff",
                            'conditions': ['HEX_COLOR']
                        },
                        'fg': {
                            "information": "Foreground color",
                            "type": str,
                            'required': TRUE,
                            'children': {},
                            "default": "#000000",
                            'conditions': ['HEX_COLOR']
                        },
                        'ok': {
                            "information": "Color for success prompts",
                            "type": str,
                            'required': TRUE,
                            'children': {},
                            "default": "#8bb174",
                            'conditions': ['HEX_COLOR']
                        },
                        'warning': {
                            "information": "Color for warning prompts",
                            "type": str,
                            'required': TRUE,
                            'children': {},
                            "default": "#ffb30f",
                            'conditions': ['HEX_COLOR']
                        },
                        'error': {
                            "information": "Color for warning prompts",
                            "type": str,
                            'required': TRUE,
                            'children': {},
                            "default": "#db504a",
                            'conditions': ['HEX_COLOR']
                        }
                    }
                },
                'gray': {
                    "information": "Gray",
                    "type": str,
                    'required': TRUE,
                    'children': {},
                    "default": "#5c5c5c",
                    'conditions': ['HEX_COLOR']
                },
                'accent': {
                    "information": "The accent color of the application",
                    "type": str,
                    'required': TRUE,
                    'children': {},
                    "default": "#008888",
                    'conditions': ['HEX_COLOR']
                },
                'padding': {
                    "information": "Padding information",
                    "type": dict,
                    'required': TRUE,
                    'children': {
                        'x': {
                            "information": "Padding in the x-axis",
                            "type": int,
                            'required': TRUE,
                            'children': {},
                            "default": 20
                        },
                        'y': {
                            "information": "Padding in the y-axis",
                            "type": int,
                            'required': TRUE,
                            'children': {},
                            'default': 10
                        }
                    }
                },
                'font': {
                    "information": "Font information",
                    "type": dict,
                    'required': TRUE,
                    'children': {
                        'font_face': {
                            "information": "The font used in the applications",
                            "type": str,
                            'required': TRUE,
                            'children': {},
                            'default': 'Montserrat'
                        },
                        'title_size': {
                            "information": "The largest font size used in the application",
                            "type": int,
                            'required': TRUE,
                            'children': {},
                            'default': 28
                        },
                        'sttl_size': {
                            "information": "The second largest size used in the application",
                            "type": int,
                            'required': TRUE,
                            'children': {},
                            'default': 15
                        },
                        'big_para_size': {
                            "information": "The third largest size used in the application",
                            "type": int,
                            'required': TRUE,
                            'children': {},
                            'default': 13
                        },
                        'main_size': {
                            "information": "The smallest size used in the application (most common)",
                            "type": int,
                            'required': TRUE,
                            'default': 10,
                            'children': {}
                        }
                    }
                },
                'border': {
                    "information": "Border information",
                    "type": dict,
                    'required': TRUE,
                    'children': {
                        "width": {
                            "information": "Size of the border",
                            "type": int,
                            'required': TRUE,
                            'children': {},
                            'default': 0
                        },
                        "color": {
                            "information": "Color of the border",
                            "type": str,
                            'required': TRUE,
                            'children': {},
                            'default': '#ffffff'
                        }
                    }
                }
            }

            conditional_checks = {
                "HEX_COLOR": [
                    lambda color: len("".join(_ for _ in re.findall(r"[0-9a-fA-F]", color))) in [3, 6]
                ]
            }

        @staticmethod
        def check_defaults() -> tuple:
            failed = passed = violations = ()
            for item in os.listdir(conf.ConfigFile.raw['theme']['theme_root']):
                item = os.path.join(
                    conf.ConfigFile.raw['theme']['theme_root'],
                    item
                )

                if os.path.isdir(item):
                    for file in os.listdir(item):
                        print(item)

                        file = os.path.join(
                            item,
                            file
                        )

                        if os.path.isfile(file):
                            if file.split('.')[-1] in ['png', 'json']:
                                if file.split('.')[-1] == 'json':
                                    with open(os.path.abspath(file), 'r') as jfile:
                                        r = jfile.read()
                                        jfile.close()
                                    try:
                                        r = json.loads(r)
                                        res = _check_theme_file(r, file.split("\\")[-1])
                                        failed = (*failed, *res['failed'])
                                        passed = (*passed, *res['passed'])
                                        violations = (*violations, *res['violations'])

                                    except:
                                        failed = (*failed, "FAILURE: Failed to load theme file %s" % os.path.abspath(file))

                            else:
                                violations = (
                                    *violations,
                                    "VIOLATION: Found non-png, non-json item in 2nd level dir in theme_root directory (%s)" % os.path.abspath(
                                        file
                                    )
                                )
                        else:
                            violations = (
                                *violations,
                                "VIOLATION: Found non-file item in 2nd level dir in theme_root directory (%s)" % os.path.abspath(
                                    file
                                )
                            )
                else:
                    violations = (*violations, 'VIOLATION: Non-dir item found in theme_root directory (%s)' % item)

            output = (passed, failed, violations)
            return output

        @staticmethod
        def check_user_pref():
            pass


def _run_file_exs_check(req: tuple):
    output = passed = ()
    for item in req:
        if os.path.exists(item):
            passed = (*passed, item)
        else:
            output = (*output, item)

    output = (output, passed)
    return output


def _deduce_theme_data_result(raw, req, cond_checks, file_path, key_dir='root') -> dict:
    output = {
        'failed': (),
        'passed': (),
        'violations': ()
    }

    key_directory = file_path.replace("\\", "//") + "/" + key_dir

    for key, requirement in req.items():
        if key not in raw and requirement['required'] == TRUE:
            output['failed'] = (
                *output['failed'],
                "FAILURE: Key '%s' does not exist in theme file (%s/%s)." % (key, key_directory, key)
            )

        else:
            output['passed'] = (*output['passed'],
                                "PASSED: Found key '%s/%s' in theme file." % (key_directory, key))

            if 'conditions' in requirement:
                for condition in requirement['conditions']:
                    if condition != "len[d, l] > 0":
                        result = True
                        for check in cond_checks[condition]:
                            result = result and check(raw[key])

                        if result:
                            output['passed'] = (
                                *output['passed'],
                                "PASSED: key '%s/%s' passed condition '%s'" % (key_directory, key, condition)
                            )
                        else:
                            output['failed'] = (
                                *output['failed'],
                                "FAILURE: key '%s/%s' failed condition '%s'" % (key_directory, key, condition)
                            )

                    else:
                        if 'light' in raw or 'dark' in raw:
                            output['passed'] = (
                                *output['passed'],
                                "PASSED: key '%s/%s' passed condition '%s'" % (key_directory, key, condition)
                            )

            if type(raw[key]) is requirement['type']:
                output['passed'] = (
                    *output['passed'],
                    "PASSED: key '%s/%s' is type '%s'" % (key_directory, key, str(requirement['type']))
                )

            else:
                output['failed'] = (
                    *output['failed'],
                    "FAILURE: key '%s/%s' is type '%s', but expected type '%s'" % (key_directory, key, str(type(raw[key])), str(requirement['type']))
                )

            for _ in requirement['children']:
                res = _deduce_theme_data_result(raw[key], req[key]['children'], cond_checks, "", key_directory + "/" + key)
                output['failed'] = (*output['failed'], *res['failed'])
                output['passed'] = (*output['passed'], *res['passed'])
                output['violations'] = (*output['violations'], *res['violations'])

    for key, items in output.items():
        output[key] = (*set(items), )

    return output


def _check_theme_file(raw, file_path) -> dict:
    try:

        req = DataDiagnostics.Theme._FileData.data_type
        cond_checks = DataDiagnostics.Theme._FileData.conditional_checks

        result = _deduce_theme_data_result(raw, req, cond_checks, file_path)
        output = result

        return output

    except Exception as E:
        print(traceback.format_exc())

        return {
            'failed': (
                'FAILURE: Failed to check file: %s.' % E.__str__(),
            ),
            'passed': (),
            'violations': ()
        }
