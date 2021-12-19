import threading, qa_log_cleaner as log_cleaner, tkinter as tk
from qa_af_module_AFIOObject import IOObjectModule, IOOInterfaceModule
from qa_af_module_AFJSON import JSONModule
import qa_exceptions, os, qa_conf, qa_protected_conf, json, traceback
from qa_af_module_AFIO import FileIOModule
from qa_af_module_AFData import DataModule
import qa_af_module_AFData
from datetime import timedelta
from tkinter import messagebox


self_data = qa_af_module_AFData.self_data

for_log = "%Z(%z)::%w %d %m %y - %H:%M:%S::%f (%j) [%c]"
for_log_name = "%Z%z%w %d %m %y %H %M %S %f %j %c"


class _Loggers:
    class PerformanceLogger(threading.Thread):
        def __init__(self, log_instance, open_logs_dir, sid, sdate):
            super().__init__()
            self.thread = threading.Thread
            self.thread.__init__(self)

            self.O_IOInstance = log_instance
            self.L_IOInstance = None
            self.o_file = None
            self.log_file = None
            self.open_logs_dir = open_logs_dir
            self.j = None
            self.sid = sid
            self.sdate = sdate
            self.scname = None
            self.update_instance()

            self.start()

        def update_instance(self):
            self.o_file = IOOInterfaceModule(self.O_IOInstance.uid)
            self.O_IOInstance = self.o_file.instance
            self.j = JSONModule(self.o_file.uid)
            log_file_name = self.j.load_file()[self.open_logs_dir][self.sdate][self.sid]['filename']
            self.L_IOInstance = IOObjectModule(
                filename=log_file_name,
                owr_exs_err_par_owr_meth=True,
                lines_mode=False,
                re_type=str,
                isFile=True
            )
            self.log_file = IOOInterfaceModule(self.L_IOInstance.uid)
            self.scname = self.j.load_file()[self.open_logs_dir][self.sdate][self.sid]['script_name']

        def log(self, lvl, *data, empty_line: bool = False):

            self.update_instance()

            if not self.log_file.isFile:
                raise qa_exceptions.FileIOException("LOGGER.THREADED_LOGGER", "Attribute 'isFile' is set to 'False.'")

            if not os.path.exists(self.log_file.filename):
                raise FileNotFoundError(self.log_file.filename)

            global for_log

            if empty_line:
                d2l = "\n"
            else:
                time = DataModule.Functions.time().strftime(for_log)
                d2l = f"[{lvl}] " + self.scname + "@" + time + ": " + "\n\t".join(str(i) for i in data).strip()

            d2l += "\n"

            FileIOModule(self.log_file.uid).save(d2l, append=True, strip_data=False)

        def change_log_file_kwargs(self, **kwargs):
            self.L_IOInstance.edit_flag(**kwargs)
            self.update_instance()

        def __del__(self):
            self.thread.join(self, 0)

    class ReliableLogger:
        def __init__(self, log_instance, open_logs_dir, sid, sdate):
            self.O_IOInstance = log_instance
            self.L_IOInstance = None
            self.o_file = None
            self.log_file = None
            self.open_logs_dir = open_logs_dir
            self.j = None
            self.sid = sid
            self.sdate = sdate
            self.scname = None
            self.update_instance()

        def update_instance(self):
            self.o_file = IOOInterfaceModule(self.O_IOInstance.uid)
            self.O_IOInstance = self.o_file.instance
            self.j = JSONModule(self.o_file.uid)
            log_file_name = self.j.load_file()[self.open_logs_dir][self.sdate][self.sid]['filename']
            self.L_IOInstance = IOObjectModule(
                filename=log_file_name,
                owr_exs_err_par_owr_meth=True,
                lines_mode=False,
                re_type=str,
                isFile=True
            )
            self.log_file = IOOInterfaceModule(self.L_IOInstance.uid)
            self.scname = self.j.load_file()[self.open_logs_dir][self.sdate][self.sid]['script_name']

        def log(self, lvl, *data, e=None, empty_line=False):
            self.update_instance()
            if not self.log_file.isFile:
                raise qa_exceptions.FileIOException("LOGGER.REL_LOGGER", "Attribute 'isFile' is set to 'False.'")

            l_dir = self.log_file.filename
            l_dir = "\\".join(i for i in l_dir.split("\\")[:-1])

            if not os.path.exists(l_dir):
                os.makedirs(l_dir)

            if not os.path.exists(self.log_file.filename):
                with open(self.log_file.filename, 'w') as file:
                    file.close()

            global for_log

            if empty_line:
                d2l = "\n"
            else:
                time = DataModule.Functions.time().strftime(for_log)
                d2l = f"[{lvl}] " + self.scname + "@" + time + ": " + "\n\t".join(str(i) for i in data).strip()
                if e is not None:
                    d2l += " \n\t>>EXCEP_REPORT::" + str(e)

            d2l += "\n"

            FileIOModule(self.log_file.uid).secure_save(d2l, append=True, strip_data=False)

        def change_log_file_kwargs(self, **kwargs):
            self.L_IOInstance.edit_flag(**kwargs)
            self.update_instance()

        def __del__(self):
            pass


class LoggerModule:  # AFLog-USER_ACCESS-interface:auto
    def __init__(self, script_name: str, script_init_identifier: str):
        """
        **CRITICAL: DO NOT OVERWRITE VARIABLES LOGGING VARIABLES; DOING SO WILL ACTIVATE LOGGER_REQ_CLEAR; ALL PREVIOUS LOGS WILL BE MARKED AS 'CLOSED' WHENEVER THIS CLASS IS NEXT INITIALIZED.**

        :param script_name: Script name (str)
        :param script_init_identifier: UID (str)
        """

        self.TCF_LOC: str = os.path.join(qa_conf.Application.AppDataLoc, *qa_protected_conf.Application.Logging.TCF_AD_TREE)
        self.TCF_NAME: str = os.path.join(self.TCF_LOC, qa_protected_conf.Application.Logging.TCF_NAME)
        self.TCF_I: IOOInterfaceModule = object
        self.TCF_OVR_FL_VAL: int = qa_protected_conf.Application.Logging.env['usage']['TCF']['TCF_OVR_FL_VAL']
        self._o: IOObjectModule = object

        self.script_name = script_name
        self.script_identifier_code = script_init_identifier

        self.date = ""
        self.min_date = None
        self.max_date = None

        self.date = None
        self.min_date = None
        self.max_date = None

        self.j = None
        self.open_logs_dir = "open_logs"

        if log_cleaner.BootCheck.clear_logs():
            log_cleaner.Actions.clear_logs(self.TCF_NAME, self.open_logs_dir)

        self.refresh()

        # Run this after the statement prior as that can cause the TCF file to reset.
        self.add_log_name()
        self.performance_logger = _Loggers.PerformanceLogger(self._o, self.open_logs_dir, script_init_identifier,
                                                             self.date)
        self.reliable_logger = _Loggers.ReliableLogger(self._o, self.open_logs_dir, script_init_identifier, self.date)

    def refresh(self):
        global self_data

        ndate = DataModule.Functions.time()
        ndate_f = ndate.strftime("%w %d %m %Y")

        if ndate_f != self.date:
            self.date = ndate

            self.min_date = self.date - timedelta(days=1)
            self.max_date = self.date + timedelta(days=1)

            self.date = ndate_f
            self.min_date = self.min_date.strftime("%w %d %m %Y")
            self.max_date = self.max_date.strftime("%w %d %m %Y")

        if not os.path.exists(self.TCF_LOC):
            os.makedirs(self.TCF_LOC)

        f_1 = False

        if not os.path.exists(self.TCF_NAME):
            f_1 = True
            with open(self.TCF_NAME, 'x') as TCF_FILE:
                TCF_FILE.close()

        uid_inst_files = (*set(self_data.uid_instance_map[file][-1] for file in self_data.uid_instance_map),)

        if self._o is object or self.TCF_NAME not in uid_inst_files:
            self._o = IOObjectModule(
                filename=self.TCF_NAME,
                encrypt=False,
                isFile=True,
                encoding=str,
                lines_mode=False,
                re_type=str,
                owr_exs_err_par_owr_meth=True
            )

        self.TCF_I = IOOInterfaceModule(self._o.uid)
        self._o = self.TCF_I.instance
        self.j = JSONModule(self._o.uid)

        if not f_1:
            try:
                if 'header' not in self.j.load_file():
                    f_1 = True
            except:
                f_1 = True

        if f_1:
            self.j.set_data("header", qa_protected_conf.Application.Logging.TCF_HEADER,
                            append=False,
                            a2k=False
                            )

            self.j.set_data(self.open_logs_dir, {"header": -1},
                            append=True,
                            a2k=False
                            )

        if 'header' not in self.j.get_data(self.open_logs_dir):
            self.j.set_data(self.open_logs_dir, {"header": -1},
                            append=True,
                            a2k=False
                            )

    def ovr_handler(self):
        r = self.j.load_file()
        with open(self._o.filename, 'r') as file:
            f = file.readlines()

        if len(f) > self.TCF_OVR_FL_VAL:
            n = {**r, 'closed_files': {}}
            FileIOModule(self._o.uid).secure_save(json.dumps(n, indent=4))

    def find_script_logger(self, exsc=False):
        self.refresh()
        r = self.j.load_file()
        for date in self.find_dates_in_use():
            if date in r[self.open_logs_dir]:
                if date == "header":
                    continue

                if self.script_identifier_code in r[self.open_logs_dir][date]:
                    return True if exsc else r[self.open_logs_dir][date][self.script_identifier_code]

        return False if exsc else None

    def find_sci(self):
        self.refresh()
        r = self.j.load_file()
        if self.open_logs_dir not in r:
            return {}

        output = {}

        for date, scis in r[self.open_logs_dir].items():
            for sci in scis:
                output = {**output, sci: date}

        return output

    def find_dates_in_use(self):
        self.refresh()
        r = self.j.load_file()
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
        r = self.j.load_file()
        o = {}

        for date, scis in r[self.open_logs_dir].items():
            for sci, data in scis.items():
                if ((not data['is_open']) if closed else data['is_open']):
                    if date in o:
                        o[date] = (*o[date], sci)
                    else:
                        o[date] = (sci,)

        return o

    def add_log_name(self):
        global for_log_name, for_log

        if self.find_script_logger(True):
            return 1

        self.refresh()

        r = self.j.load_file()

        with open(self._o.filename) as jfile:
            a = jfile.readlines()
            jfile.close()

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
            r = self.j.load_file()

        elif len(a) > qa_protected_conf.Application.Logging.min_crit_point and len(r['closed_files']) != 0:
            messagebox.showwarning(qa_conf.Application.app_name,
                              "File 'LCF File.json' is approaching a critical point that can cause lag (>%s lines.) Attempting to clear some older application description." % str(
                                  qa_protected_conf.Application.Logging.min_crit_point
                              ))
            o1 = {"header": r['header'], self.open_logs_dir: {**r[self.open_logs_dir]}, "closed_files": {}}
            s1 = json.dumps(o1, indent=4)
            FileIOModule(self._o.uid).secure_save(s1, append=False)
            r = self.j.load_file()

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
        self.refresh()
        r = self.j.load_file()
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
        :return: None
        """

        self.refresh()
        if print_d:
            print(f'[{lvl}]\n\t', '\n\t'.join(i for i in data))

        try:
            self.performance_logger.log(lvl, *data, empty_line=empty_line)
        except Exception as E:
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
