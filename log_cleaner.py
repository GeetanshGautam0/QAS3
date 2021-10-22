import os, conf, json, nv_flags_system, importlib

with open("low.json", 'r') as file:
    _l_json = json.loads(file.read())
    file.close()

_prConfFile: str = _l_json['pcm_file']
protected_conf = importlib.import_module(_prConfFile)

_p = nv_flags_system.FlagsLookup.logging['log_cleaner']['request clear']


class BootCheck:
    @staticmethod
    def clear_logs() -> bool:
        global _p
        return nv_flags_system.FlagsIO.check(_p)


class Actions:
    @staticmethod
    def set_logger_req_clear() -> None:
        global _p
        if not BootCheck.clear_logs():
            nv_flags_system.FlagsIO.create(_p)

    @staticmethod
    def clear_logs(n, open_logs_dir) -> None:
        global _p

        if os.path.exists(n):
            jfile = open(n, 'r')
            r = json.loads(jfile.read())
            jfile.close()

            o = {**r, '-1': -1}
            del o['-1']

            c = {}

            for k in r[open_logs_dir].keys():
                if k != "header":
                    date = k  # Date
                    for sci, data in r[open_logs_dir][date].items():
                        # if description['is_open']:
                        if date not in c:
                            c[date] = (sci,)
                        else:
                            c[date] = (*c[date], sci,)

            if 'closed_files' not in o:
                o['closed_files'] = {}

            for date, scis in c.items():
                for sci in scis:
                    if date not in o['closed_files']:
                        o['closed_files'][date] = {}

                    o['closed_files'][date][sci] = {**r[open_logs_dir][date][sci]}
                    del o[open_logs_dir][date][sci]
                    del o['closed_files'][date][sci]['is_open']
                    if "NOTICE1" in o['closed_files'][date][sci]:
                        del o['closed_files'][date][sci]['NOTICE1']

            o = {"header": {**o['header']}, open_logs_dir: [], "closed_files": {**o['closed_files']}}
            s = json.dumps(o, indent=4)

            with open(n, 'w') as jfile:
                jfile.write(s)
                jfile.close()

        if BootCheck.clear_logs():
            nv_flags_system.FlagsIO.delete(_p)

    @staticmethod
    def del_closed_logs() -> None:
        def write_def(n) -> None:
            # LTCF = LoggingTemporaryConfigurationFile
            with open(n, 'w') as LTCF:
                LTCF.write(json.dumps({
                    'header': protected_conf.Application.Logging.TCF_HEADER,
                    'open_logs': {},
                    'closed_files': {}
                }, indent=4))
                LTCF.close()

        def rec_remove(start, open) -> None:
            for _item in os.listdir(start):
                item = os.path.join(start, _item)

                if os.path.isfile(item):
                    if item not in open:
                        os.remove(item)
                        print('LC:Actions:del_closed_logs:rec_remove: removed file', _item)

                    else:
                        print('LC:Actions:del_closed_logs:rec_remove: kept file', _item)

                elif os.path.isdir(item):
                    rec_remove(item, open)

                else:
                    raise Exception("Failed to remove closed logs :: err:1")

        tcf_n = os.path.join(
            conf.Application.AppDataLoc,
            *protected_conf.Application.Logging.TCF_AD_TREE,
            protected_conf.Application.Logging.TCF_NAME
        )

        if not os.path.exists(tcf_n):
            print('LoggingTemporaryConfigurationFile not found; creating')
            tcf_l = os.path.join(
                    conf.Application.AppDataLoc,
                    *protected_conf.Application.Logging.TCF_AD_TREE
                )
            if not os.path.exists(tcf_l):
                os.makedirs(tcf_l)

            write_def(tcf_n)

            return

        with open(tcf_n, 'r') as LoggingTemporaryConfigurationFile:
            _r = json.loads(LoggingTemporaryConfigurationFile.read())
            LoggingTemporaryConfigurationFile.close()

        if 'open_logs' in _r:
            open_logs = ()
            for date, date_data in _r['open_logs'].items():
                if date != "header":
                    for key, data in date_data.items():
                        open_logs = (*open_logs, data['filename'])

            rec_remove(os.path.join(conf.Application.AppDataLoc, "Logs"), open_logs)

        else:
            write_def(tcf_n)
