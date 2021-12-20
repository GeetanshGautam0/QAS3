import threading, qa_log_cleaner as log_cleaner, tkinter as tk
from qa_af_module_AFIOObject import IOObjectModule, IOOInterfaceModule
from qa_af_module_AFJSON import JSONModule
import qa_exceptions, os, qa_conf, qa_protected_conf, json, traceback
from qa_af_module_AFIO import FileIOModule
from qa_af_module_AFData import DataModule
import qa_af_module_AFData
from datetime import timedelta
from tkinter import messagebox
from typing import *


self_data = qa_af_module_AFData.self_data

for_log = "%Z(%z)::%w %d %m %y - %H:%M:%S::%f (%j) [%c]"
for_log_name = "%Z%z%w %d %m %y %H %M %S %f %j %c"


class _Loggers:
    class PerformanceLogger(threading.Thread):
        def __init__(
                self,
                log_instance: IOObjectModule,
                open_logs_dir: str,
                script_id: str,
                date: str
        ):
            super().__init__()
            self.thread = threading.Thread
            self.thread.__init__(self)

            self.tcf_IOInstance: IOObjectModule = log_instance
            self.log_IOInstance = None
            self.tcf_file = None
            self.log_file = None
            self.json = None

            self.script_name: str = '<Name=Unknown>'
            self.script_id: str = script_id
            self.date: str = date

            self.open_logs_dir: str = open_logs_dir

            self.update_instance()

            self.start()

        def update_instance(self):

            self.tcf_IOInstance: IOObjectModule
            self.log_IOInstance: IOObjectModule
            self.tcf_file: IOOInterfaceModule
            self.log_file: IOOInterfaceModule
            self.json: JSONModule

            self.tcf_file = IOOInterfaceModule(self.tcf_IOInstance.uid)
            self.tcf_IOInstance = self.tcf_file.instance
            self.json = JSONModule(self.tcf_file.uid)
            log_file_name = self.json.load_file()[self.open_logs_dir][self.date][self.script_id]['filename']
            self.log_IOInstance = IOObjectModule(
                filename=log_file_name,
                owr_exs_err_par_owr_meth=True,
                lines_mode=False,
                re_type=str,
                isFile=True
            )
            self.log_file = IOOInterfaceModule(self.log_IOInstance.uid)
            self.script_name = self.json.load_file()[self.open_logs_dir][self.date][self.script_id]['script_name']

            del log_file_name

        def log(self, level_logging: str, *data: List[any], empty_line: bool = False):

            self.update_instance()

            if not self.log_file.isFile:
                raise qa_exceptions.FileIOException("LOGGER.THREADED_LOGGER", "Attribute 'isFile' is set to 'False.'")

            if not os.path.exists(self.log_file.filename):
                raise FileNotFoundError(self.log_file.filename)

            global for_log

            if empty_line:
                data_to_log = "\n"
            else:
                time = DataModule.Functions.time().strftime(for_log)
                data_to_log = f"[{level_logging}] {self.script_name}@{time}: %s" % "\n\t".join(
                    str(i) for i in data).strip()

            data_to_log += "\n"

            FileIOModule(self.log_file.uid).save(data_to_log, append=True, strip_data=False)

        def change_log_file_kwargs(self, **kwargs):
            self.log_IOInstance.edit_flag(**kwargs)
            self.update_instance()

        def __del__(self):
            self.thread.join(self, 0)

    class ReliableLogger:
        def __init__(
                self,
                log_instance: IOObjectModule,
                open_logs_dir: str,
                script_id: str,
                date: str
        ):
            self.tcf_IOInstance: IOObjectModule = log_instance
            self.log_IOInstance = None
            self.tcf_file = None
            self.log_file = None
            self.json = None

            self.script_name: str = '<Name=Unknown>'
            self.script_id: str = script_id
            self.date: str = date

            self.open_logs_dir: str = open_logs_dir

            self.update_instance()

        def update_instance(self):
            self.tcf_file = IOOInterfaceModule(self.tcf_IOInstance.uid)
            self.tcf_IOInstance = self.tcf_file.instance
            self.json = JSONModule(self.tcf_file.uid)
            log_file_name = self.json.load_file()[self.open_logs_dir][self.date][self.script_id]['filename']
            self.log_IOInstance = IOObjectModule(
                filename=log_file_name,
                owr_exs_err_par_owr_meth=True,
                lines_mode=False,
                re_type=str,
                isFile=True
            )
            self.log_file = IOOInterfaceModule(self.log_IOInstance.uid)
            self.script_name = self.json.load_file()[self.open_logs_dir][self.date][self.script_id]['script_name']

            del log_file_name

        def log(self, logging_level, *data, e=None, empty_line=False):
            self.update_instance()
            if not self.log_file.isFile:
                raise qa_exceptions.FileIOException(
                    "LOGGER.REL_LOGGER",
                    "Attribute 'isFile' is set to 'False.'"
                )

            log_directory = self.log_file.filename
            log_directory = "\\".join(i for i in log_directory.split("\\")[:-1])

            if not os.path.exists(log_directory):
                os.makedirs(log_directory)

            if not os.path.exists(self.log_file.filename):
                with open(self.log_file.filename, 'w') as file:
                    file.close()

            global for_log

            if empty_line:
                data_to_log = "\n"
            else:
                time = DataModule.Functions.time().strftime(for_log)
                data_to_log = f"[{logging_level}] {self.script_name}@{time}: %s" % "\n\t".join(
                    str(i) for i in data).strip()

                if e is not None:
                    data_to_log += f" \n\t>>Reported Exception:\n\t\"{str(e)}\""

            data_to_log += "\n"

            FileIOModule(self.log_file.uid).secure_save(data_to_log, append=True, strip_data=False)

        def change_log_file_kwargs(self, **kwargs):
            self.log_IOInstance.edit_flag(**kwargs)
            self.update_instance()

        def __del__(self):
            pass


class LoggerModule:  # AFLog-USER_ACCESS-interface:auto
    def __init__(self, script_name: str, script_init_identifier: str):
        """
        **CRITICAL: DO NOT OVERWRITE VARIABLES LOGGING VARIABLES; DOING SO WILL ACTIVATE LOGGER_REQ_CLEAR; ALL PREVIOUS LOGS WILL BE MARKED AS 'CLOSED' WHENEVER THIS CLASS IS NEXT INITIALIZED.**

        **Tip:** When exiting, use `del <logger>`

        :param script_name: Script name (str)
        :param script_init_identifier: UID (str)
        """

        self.tcf_location: str = os.path.join(qa_conf.Application.AppDataLoc, *qa_protected_conf.Application.Logging.TCF_AD_TREE)
        self.tcf_file_path: str = os.path.join(self.tcf_location, qa_protected_conf.Application.Logging.TCF_NAME)
        self.tcf_instance = object
        self.TCF_OVR_FL_VAL: int = qa_protected_conf.Application.Logging.env['usage']['TCF']['TCF_OVR_FL_VAL']
        self._o = object

        self.script_name = script_name
        self.script_identifier_code = script_init_identifier

        self.date = ""
        self.min_date = None
        self.max_date = None

        self.json = None
        self.open_logs_dir = "open_logs"

        if log_cleaner.BootCheck.clear_logs():
            log_cleaner.Actions.clear_logs(self.tcf_file_path, self.open_logs_dir)

        self.refresh()

        self.tcf_instance: IOOInterfaceModule
        self._o: IOObjectModule

        # Run this after the statement prior as that can cause the TCF file to reset.
        self.add_log_name()
        self.performance_logger = _Loggers.PerformanceLogger(
            self._o,
            self.open_logs_dir,
            script_init_identifier,
            self.date
        )
        self.reliable_logger = _Loggers.ReliableLogger(
            self._o,
            self.open_logs_dir,
            script_init_identifier,
            self.date
        )

    def refresh(self):
        global self_data

        self.tcf_instance: IOOInterfaceModule
        self._o: IOObjectModule

        new_date = DataModule.Functions.time()
        new_date_format = new_date.strftime("%w %d %m %Y")

        if new_date_format != self.date:
            self.date = new_date

            self.min_date = self.date - timedelta(days=1)
            self.max_date = self.date + timedelta(days=1)

            self.date = new_date_format
            self.min_date = self.min_date.strftime("%w %d %m %Y")
            self.max_date = self.max_date.strftime("%w %d %m %Y")

        if not os.path.exists(self.tcf_location):
            os.makedirs(self.tcf_location)

        f_1 = False

        if not os.path.exists(self.tcf_file_path):
            f_1 = True
            with open(self.tcf_file_path, 'x') as TCF_FILE:
                TCF_FILE.close()

        uid_inst_files = (*set(self_data.uid_instance_map[file][-1] for file in self_data.uid_instance_map),)

        if self._o is object or self.tcf_file_path not in uid_inst_files:
            self._o = IOObjectModule(
                filename=self.tcf_file_path,
                encrypt=False,
                isFile=True,
                encoding=str,
                lines_mode=False,
                re_type=str,
                owr_exs_err_par_owr_meth=True
            )

        self.tcf_instance = IOOInterfaceModule(self._o.uid)
        self._o = self.tcf_instance.instance
        self.json = JSONModule(self._o.uid)

        if not f_1:
            try:
                if 'header' not in self.json.load_file():
                    f_1 = True
            except Exception as E:
                print(E)
                f_1 = True

        if f_1:
            self.json.set_data("header", qa_protected_conf.Application.Logging.TCF_HEADER,
                               append=False,
                               append_to_key=False
                               )

            self.json.set_data(self.open_logs_dir, {"header": -1},
                               append=True,
                               append_to_key=False
                               )

        if 'header' not in self.json.get_data(self.open_logs_dir):
            self.json.set_data(self.open_logs_dir, {"header": -1},
                               append=True,
                               append_to_key=False
                               )

    def ovr_handler(self):
        self.tcf_instance: IOOInterfaceModule
        self._o: IOObjectModule

        r = self.json.load_file()
        with open(self._o.filename, 'r') as file:
            f = file.readlines()

        if len(f) > self.TCF_OVR_FL_VAL:
            n = {**r, 'closed_files': {}}
            FileIOModule(self._o.uid).secure_save(json.dumps(n, indent=4))

    def find_script_logger(self, return_exists_bool=False):
        self.refresh()
        r = self.json.load_file()
        for date in self.find_dates_in_use():
            if date in r[self.open_logs_dir]:
                if date == "header":
                    continue

                if self.script_identifier_code in r[self.open_logs_dir][date]:
                    return True if return_exists_bool else r[self.open_logs_dir][date][self.script_identifier_code]

        return False if return_exists_bool else None

    def find_sci(self):
        self.refresh()
        r = self.json.load_file()
        if self.open_logs_dir not in r:
            return {}

        output = {}

        for date, script_ids in r[self.open_logs_dir].items():
            for sci in script_ids:
                output = {**output, sci: date}

        return output

    def find_dates_in_use(self):
        self.refresh()
        r = self.json.load_file()
        if self.open_logs_dir in r:
            o = ()

            for date in r[self.open_logs_dir].keys():
                o = (*o, date,)

            o = (*set(o),)
            return o

        else:
            return [self.min_date, self.max_date, self.date]

    def find_in_use_logs(self, closed: bool = True):
        self.refresh()
        r = self.json.load_file()
        o = {}

        for date, script_ids in r[self.open_logs_dir].items():
            for sci, data in script_ids.items():
                if (not data['is_open']) if closed else data['is_open']:
                    if date in o:
                        o[date] = (*o[date], sci)
                    else:
                        o[date] = (sci,)

        return o

    def add_log_name(self):
        self.tcf_instance: IOOInterfaceModule
        self._o: IOObjectModule

        global for_log_name, for_log

        if self.find_script_logger(True):
            return 1

        self.refresh()

        r = self.json.load_file()

        with open(self._o.filename) as json_file:
            a = json_file.readlines()
            json_file.close()

        if len(a) > qa_protected_conf.Application.Logging.critical_point and len(r['closed_files']) != 0:
            a = tk.Tk()
            a.withdraw()
            messagebox.showwarning(qa_conf.Application.app_name,
                                   "File 'LCF File.json' is approaching a critical point that can cause severe lag (>%s lines.) Attempting to clear some older application description." % str(
                                       qa_protected_conf.Application.Logging.critical_point
                                   ))

            op1 = dict(list(r.items())[:len(r) // 2])
            o1 = {"header": r['header'], self.open_logs_dir: op1, "closed_files": {}}
            s2 = json.dumps(o1, indent=4)
            FileIOModule(self._o.uid).secure_save(s2, append=False)
            r = self.json.load_file()

        elif len(a) > qa_protected_conf.Application.Logging.min_crit_point and len(r['closed_files']) != 0:
            messagebox.showwarning(qa_conf.Application.app_name,
                                   "File 'LCF File.json' is approaching a critical point that can cause lag (>%s lines.) Attempting to clear some older application description." % str(
                                       qa_protected_conf.Application.Logging.min_crit_point
                                   ))
            o1 = {"header": r['header'], self.open_logs_dir: {**r[self.open_logs_dir]}, "closed_files": {}}
            s1 = json.dumps(o1, indent=4)
            FileIOModule(self._o.uid).secure_save(s1, append=False)
            r = self.json.load_file()

        if self.open_logs_dir not in r:
            r[self.open_logs_dir] = {}

        if self.date not in r[self.open_logs_dir]:
            r[self.open_logs_dir][self.date] = {}

        r[self.open_logs_dir][self.date][self.script_identifier_code] = {
            'script_name': self.script_name,
            'filename': "%s.%s" % (
                os.path.join(
                    qa_conf.Application.AppDataLoc,
                    "Logs",
                    self.script_name,
                    DataModule.Functions.time().strftime(for_log_name).replace(":", "-")
                ), qa_protected_conf.Application.Logging.extention
            ),
            'time': DataModule.Functions.time().strftime(for_log),
            'is_open': True
        }

        s = json.dumps(r, indent=4)
        FileIOModule(self._o.uid).secure_save(s, append=False)

        self.ovr_handler()

    def mark_finished(self):
        self._o: IOObjectModule

        self.refresh()
        r = self.json.load_file()
        sci = self.find_sci()
        if self.script_identifier_code in sci:
            d = sci[self.script_identifier_code]
            r[d][self.script_identifier_code]['is_open'] = False
            r[d][self.script_identifier_code]['NOTICE1'] = "THIS FILE WAS PRODUCED BY AN INSTANCE OF THE SCRIPT THAT IS STILL RUNNING"

            s = json.dumps(r, indent=4)
            FileIOModule(self._o.uid).secure_save(s, append=False)

    def log(self, lvl, *data, empty_line: bool = False, print_d: bool = False):
        """
        **AFLog.log**
        Will log _data (attempts to do so with 'PerformanceLogger,' if fails, will try to use 'ReliableLogger'

        :param data: _data
        :param empty_line: [bool] add an empty line [[NO DataModule WILL BE LOGGED]] (optional)
        :param print_d: Print data to console (slower)
        :param lvl: Logging level [str]
        :return: None
        """

        self.refresh()
        if print_d:
            print(f'[{lvl}]\n\t', '\n\t'.join(i for i in data))

        try:
            self.performance_logger.log(lvl, *data, empty_line=empty_line)
        except Exception as E:
            print(E)
            try:
                t = traceback.format_exc()
                self.reliable_logger.log(lvl, *data, e=t, empty_line=empty_line)
            except Exception as E:
                print("Failed to log data; E; TB; DATA:", E, traceback.format_exc(), ("\n\t".join(d for d in data)))

    def performance(self, lvl, *data, empty_line: bool = False):
        """
         **AFLog.performance**
         Will use 'PerformanceLogger'

        :param data: _data
        :param empty_line: [bool] add an empty line [[NO DataModule WILL BE LOGGED]] (optional)
        :param lvl: Error level [str]
        :return: None
        """

        self.refresh()

        self.performance_logger.log(lvl, *data, empty_line=empty_line)

    def reliable(self, lvl, *data, e=None, empty_line: bool = False):
        """
         **AFLog.performance**
         Will use 'ReliableLogger'

        :param data: _data
        :param e: exception (optional)
        :param empty_line: [bool] add an empty line [[NO DataModule WILL BE LOGGED]] (optional)
        :param lvl: [str] Logging level
        :return: None
        """

        self.refresh()

        self.reliable_logger.log(lvl, *data, e=e, empty_line=empty_line)

    def change_io_instance(self, **kwargs):
        # self._o.edit_flag(**kwargs)
        self.performance_logger.change_log_file_kwargs(**kwargs)
        self.reliable_logger.change_log_file_kwargs(**kwargs)

    def __del__(self):
        log_cleaner.Actions.set_logger_req_clear()
