import qa_std, sys, traceback, qa_conf, os, hashlib
from tkinter import messagebox
from datetime import datetime
from qa_af_module_AFData import DataModule


_file_name = "apps_call_master.py"
_script_name = "Master Application Handler"


class _Starters:
    @staticmethod
    def ShellApplication(path: str, *args):
        print(path, args)

        paths = {
            'at': _Starters.AdminToolsStarter,
            'qmf': _Starters.QuestionMasterForm
        }

        assert path in paths, "Invalid script path"
        print(args)
        paths[path](*args)

    @staticmethod
    def AdminToolsStarter(*args):
        global _script_name

        print(f'Running Admin Tools Shell from {_script_name}')

        try:
            import apps_adminTools as AdminTools
            AdminTools.control_debugger = '--debug' in args
            AdminTools.AdminToolsUI()

        except Exception as e:
            _crash_handler(
                "AdminToolsShell",
                e,
                traceback.format_exc()
            )

            sys.exit(-1)

    @staticmethod
    def QuestionMasterForm(*args):
        global _script_name

        assert len(args) > 0, 'Insufficient arguments'

        print(f'Running Question Master Form Shell from {_script_name}')

        try:
            import apps_question_master_form as qmf

            mapper = {
                1: qmf.Modes.View,
                2: qmf.Modes.Edit,
                3: qmf.Modes.Add
            }

            assert args[0] in mapper, "Invalid mode; expected:\n\t* %s" % ("\n\t* ".join("%s: %s" % (k, v) for k, v in mapper.items()))
            m = mapper[args[0]]
            args = [*args]
            args.pop(0)

            if '--debug' in args:
                qmf.control_debugger = True
                args.pop(args.index('--debug'))
            else:
                qmf.control_debugger = False

            mode = qmf.Mode(m, args)

            qmf.QuestionMasterFormUI(mode, *args)

        except Exception as e:
            _crash_handler(
                "QuestionMasterFormShell",
                e,
                traceback.format_exc()
            )

            sys.exit(-1)


class StartupHandlers:
    @staticmethod
    def CLIHandler(_, *args):
        del _

        global _file_name, _script_name
        arguments = list(args)

        assert len(arguments) > 0, "Insufficient Arguments"
        if arguments[0] == _file_name:
            arguments.pop(0)

        assert len(arguments) > 0, "Insufficient Arguments"

        command_map = {
            'ShellApplication': {
                'type': qa_std.CLI.CLITypes.FUNCTION,
                'path': _Starters.ShellApplication,
                'num_args': 1,
                'args': [],
                'request_special_call_index': 0,
            },
            '-AdminToolsShell': {
                'type': qa_std.CLI.CLITypes.ARGUMENT,
                'separator': None,
                'data_type': str,
                'tied_to_function': {
                    'b': True,
                    'functions': ['ShellApplication']
                },
            },
            '-QuestionMasterForm': {
                'type': qa_std.CLI.CLITypes.ARGUMENT,
                'separator': ":",
                'data_type': int,
                'tied_to_function': {
                    'b': True,
                    'functions': ['ShellApplication']
                },
            },
            '--debug': {
                'type': qa_std.CLI.CLITypes.ARGUMENT,
                'separator': None,
                'data_type': str,
                'tied_to_function': {
                    'b': False,
                    'functions': []
                },
            },
            '-tk': {
                'type': qa_std.CLI.CLITypes.ARGUMENT,
                'separator': None,
                'data_type': str,
                'tied_to_function': {
                    'b': False,
                    'functions': []
                },
            },
        }

        cli_trans = qa_std.CLI.CLI_handler(
            arguments,
            command_map,
            _script_name,
            __name__ == "__main__",
            True
        )

        assert isinstance(cli_trans, tuple), "Invalid arguments"

        arg_stack, function_stack, named_args_stack, og_args_stack = cli_trans
        new_function_stack = {}

        shell_map = {
            '-AdminToolsShell': 'at',
            '-QuestionMasterForm': 'qmf'
        }

        for index, (_0, function, supplied_args) in function_stack.items():
            function = function_stack[index][function]
            supplied_args = function_stack[index][supplied_args]

            supplied_named_args = {
                [*supplied_args.values()].index(i):
                [named_args_stack[[*supplied_args.values()].index(i)], i]
                for i in supplied_args.values()
            }

            o_parsed_args = []

            for key, parsed_args in supplied_named_args.items():
                if len(parsed_args) == 0:
                    new_function_stack[function] = ()
                    continue

                assert isinstance(parsed_args, list) or isinstance(parsed_args, tuple) or isinstance(parsed_args, set), \
                    'ScriptError 1'

                parsed_args = [*parsed_args]  # Make mutable
                for item in parsed_args:
                    print(item, item in shell_map)
                    if item in shell_map:
                        parsed_args[parsed_args.index(item)] = shell_map[item]

                for item in [*parsed_args, *named_args_stack.values()]:
                    if (item not in o_parsed_args) and (True if item not in shell_map else (shell_map[item] not in o_parsed_args)):
                        o_parsed_args.append(item)

            new_function_stack[function] = o_parsed_args

            del _0

        print(
            "Initial Arguments:\n\t* %s" % "\n\t* ".join(a for a in args),
            "Parsed Arguments, Function Stack:\n\t* %s" % "\n\t* ".join(str(a) for a in {
                *[v['call'] for v in function_stack.values()],
                *arg_stack.values(),
                *named_args_stack.values(),
                *og_args_stack.values()
            }),
            "Function Calls, Arguments:\n\t* %s" % "\n\t* ".join(
                f"{str(k)}: {str(v)}" for k, v in new_function_stack.items()
            ),
            sep="\n"
        )

        del args

        for call, call_args in new_function_stack.items():
            call(*call_args)


def _crash_handler(
        name,
        exception,
        traceback_str
):
    global _script_name

    time = datetime.now().strftime("%d %m %y - %H %M %S")

    output_str = f"""Quizzing Application {qa_conf.ConfigFile.raw['app_data']['build']['frame_vid']}
{qa_conf.Application.cr}

----------------------
Crash Log (Saved)


Time of crash: {time}
Reason for crash: {exception}

Exception Code: 0x{hashlib.md5(f"{exception}".encode()).hexdigest()}
Traceback Code: 0x{hashlib.md5(f"{traceback_str}".encode()).hexdigest()}
Unique ID: 0x{DataModule.Functions.generate_uid(0.01, function=hashlib.md5)}

----------------------
Technical Information:
{traceback_str}
"""

    try:
        if not os.path.exists(os.path.join(qa_conf.Application.crash_logs_location, name)):
            os.makedirs(os.path.join(qa_conf.Application.crash_logs_location, name))

        with open(
            os.path.join(
                qa_conf.Application.crash_logs_location,
                name,
                f'{time}.cmflog'
            ),
            'w'
        ) as crash_log_file:
            crash_log_file.write(output_str)
            crash_log_file.close()

    except Exception as E:
        output_str += f"\n\nFailed to save log: {E}"

    messagebox.showerror(
        f"{_script_name} - Crash Report",
        output_str
    )

    print(output_str)

    return


if __name__ == "__main__":
    try:
        StartupHandlers.CLIHandler(*sys.argv)
    except Exception as E:
        print(traceback.format_exc())
        sys.exit(str(E))

