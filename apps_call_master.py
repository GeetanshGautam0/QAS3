import qa_std, sys, traceback, qa_conf, os, hashlib
from tkinter import messagebox
from datetime import datetime


_file_name = "apps_call_master.py"
_script_name = "Master Application Handler"


class _Starters:
    @staticmethod
    def ShellApplication(path: str):
        paths = {
            'at': _Starters.AdminToolsStarter
        }

        assert path in paths, "Invalid script path"

        paths[path]()

    @staticmethod
    def AdminToolsStarter():
        global _script_name

        print(f'Running Admin Tools Shell from {_script_name}')

        try:
            import apps_adminTools as AdminTools
            AdminTools.AdminToolsUI()

        except Exception as e:
            _crash_handler(
                "AdminToolsShell",
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
        new_function_stack = []

        shell_map = {
            '-AdminToolsShell': 'at'
        }

        for index, (_0, function, supplied_args) in function_stack.items():
            function = function_stack[index][function]
            supplied_args = function_stack[index][supplied_args]

            for key, value in supplied_args.items():
                if value in shell_map:
                    supplied_args[key] = shell_map[value]

            new_function_stack.append(
                lambda: function(*supplied_args.values())
            )

            del _0

        print(
            "Initial Arguments:\n\t* %s" % "\n\t* ".join(a for a in args),
            "Parsed Arguments, Function Stack:\n\t* %s" % "\n\t* ".join(str(a) for a in (
                *[v['call'] for v in function_stack.values()],
                *arg_stack.values(),
                *named_args_stack.values(),
                *og_args_stack.values()
            )), sep="\n"
        )

        del args

        for call in new_function_stack:
            call()


def _crash_handler(
        name,
        exception,
        traceback_str
):
    global _script_name

    time = datetime.now().strftime("%d %m %y - %H %M %S")

    output_str = f"""Quizzing Application {qa_conf.ConfigFile.raw['app_data']['build']['frame_vid']}
{qa_conf.Application.cr}

========================================
Crash Log

Time of crash: {time}
Reason for crash: {exception}
Code: 0x{hashlib.md5(f"{exception}{traceback_str}".encode()).hexdigest()}

Technical Information:
{traceback_str}
"""
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

    messagebox.showerror(
        f"{_script_name} - Crash Report",
        output_str
    )

    return


if __name__ == "__main__":
    try:
        StartupHandlers.CLIHandler(*sys.argv)
    except Exception as E:
        print(traceback.format_exc())
        sys.exit(str(E))
