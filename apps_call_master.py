import qa_std, sys, traceback
from tkinter import messagebox


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
        except Exception as E:
            print(E, traceback.format_exc(), sep="\n\n")

            messagebox.showerror(
                f"{_script_name} - Crash Report",
                traceback.format_exc()
            )


class StartupHandlers:
    @staticmethod
    def CLIHandler(script_name, *args):
        del script_name

        global _file_name, _script_name
        arguments = list(args)
        del args

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

        for call in new_function_stack:
            call()


if __name__ == "__main__":
    try:
        StartupHandlers.CLIHandler(*sys.argv)
    except Exception as E:
        print(traceback.format_exc())
        sys.exit(str(E))
