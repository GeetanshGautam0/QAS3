import qa_conf

v = "0.1aba-7"
insider_build = True
dsb_mod_run_stdnalone = (not conf.Application.in_beta) if insider_build else True


class Configuration:

    class Files:
        pref_file_loc = ['.appdata', '.user']
        pref_file_name = "pref.json"


class Application:

    class Logging:
        TCF_AD_TREE = ['.appdata', '.logging', '.tcf']
        TCF_NAME = "TCF File.json"

        env = {
            "usage": {
                "TCF": {
                    "TCF_OVR_FL_VAL": 4096
                }
            }
        }

        TCF_HEADER = {
                "Application": "Coding Made Fun - %s" % conf.Application.app_name,
                "App Version": conf.Application.version_str,
                "Purpose": "Storing [temporary] information about log files; DO NOT DELETE.",
                "Importance": "Extreme; logging may malfunction if this file is modified.",
                "Notice": "This file will never get larger than %s lines; all old description will be deleted automatically." % str(
                    env['usage']['TCF']['TCF_OVR_FL_VAL'])
            }

        extention = ".cmf_log"
        critical_point = 2048
        min_crit_point = 1024
