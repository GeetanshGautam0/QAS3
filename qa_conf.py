import json, appdirs, random


class ConfigFile:
    name = "qa_conf.json"
    raw = {}

    @staticmethod
    def reload_raw():
        with open(ConfigFile.name, 'r') as confFile:
            ConfigFile.raw = json.loads(confFile.read())
            confFile.close()


ConfigFile.reload_raw()


class Application:
    app_name = "Quizzing Application 3"
    app_author = "Coding Made Fun"
    version_str = ConfigFile.raw['app_data']['build']['version_id']
    AppDataLoc = appdirs.user_data_dir(appname=app_name, appauthor=app_author, version=version_str, roaming=False)
    RoamingAppDataLoc = appdirs.user_data_dir(appname=app_name, appauthor=app_author, version=version_str, roaming=True)
    in_beta = True
    uid_seed = {
        'admin_tools': random.random(),
        'quizzing_tool': random.random(),
        'recovery_util': random.random(),
        'theming_util': random.random(),
    }


class Encryption:
    key = b"eAxD42i8pmgu8ocHwYNZnn27tj9MIDuuUZ2t-TwJDmE="

    file = {
        'qaQuiz':       b"pFeOoK28eCvrCUrQd9XilUFEMPagUKXwkcD7GMqKDMI=",
        'qaEnc':        b"wpmvp-EMJbBta7BDYhH1cKHVWeue0k93XrizQdYG2t8=",
        'qaLog':        b"7FubkLxSSHAbk7-7uSojdsDDSKBsOHkUqGZmKs49g28=",
        'qaFile':       b"SG6BBQdMsYNk9cllqQEpqRzJKACev8OAYtjX2fYvagI=",
        'qaScore':      b"eAU71fQ61n0wAiDhV5W6L0_JTk-RWxQ6d-WgqUEJ0k4=",
        'qaExport':     b"QsZe516byVY8Siv-nFyWRisw3O-Cl05yndFmW41pSIE=",
        'cmfbackup':    b"-ngoLsvLprDiEdkSzO2lEGUaSSd0PHRI_Svpe33exBo="
    }


class AppContainer:
    general_title = ConfigFile.raw.get('container_data')['general']['title']

    class Prompts:
        def_ws = (500, 450)

    class Splash:
        geo = [600, 225]

    class Apps:
        admin_tools = {
            'main': {
                'ws': (1000, 900)
            },
            'question_entry': {
                'ws': (840, 800)
            }
        }


class Exceptions:
    error_var_codes = {
        'AFDATA.Data.check_encoding::lst':                'D.D:Chk>>ENCO-VAR:LST[opt. inp <aut_g>, 0]',
        'AFDATA.Data.check_encoding::lst>>gen>>encoding': 'D.D:Chk>>ENCO-VAR:lst>>gen>>ENCODING[0]',
        'AFDATA.Data.check_encoding::_data':               'D.D:Chk>>ENCO-VAR:_data[inp, 0][t]',
        'AFDATA.Data.check_encoding::_data[1]':            'D.D.Chk>>ENCO-VAR:_data[inp, 1][l]',

        'AFDATA.Data.recursive_list_conversion::_data[0]': 'D.D.RecConv>>LIST:_data[inp, 0][t]',
        'AFDATA.Data.recursive_list_conversion::_data[1]': 'D.D.RecConv>>LIST:_data[inp, 0][l]',

        'AFDATA.Data.recursive_dict_conversion::_data[0]': 'D.D.RecConv>>DICT:_data[inp, 0][t]',
        'AFDATA.Data.recursive_dict_conversion::_data[1]': 'D.D.RecConv>>DICT:_data[inp, 0][l]',

        'AFDATA.Functions.flags::flag[name_error]':       'D.F.Flags>>DICT::NAME_ERROR[user_inp[KWARG], -1][uk]',

        'ENC.DEC[RE,INP::F]::!INST[-0]':                'E.DEC>>[RE_INP::F]>>-0>>!INIT_INST:NoneType::[-0][init]',
        'ENC.GLOBAL[G]::!ENC[-1]':                      'E.GLB>>[G]>>-1>>!INIT_PRP:!FIOInst.ENCRYPT:FALSE[-1][f]',
        'ENC.GLOBAL[G]::!FER[-0]':                      'E.GLB>>[G]>>-0>>!FER:ENC.fernet>>NOT_INIT[-0][fernet!i]',
        'ENC.GLOBAL[INP]::TP-RAW!:BYTES':               'E.GLB>>INP>>+0>>!TP_RAW!=BYTES;;;FATAL[script_inp, 1++]',
        'ENC.ENC[RE,INP::F]::!INST[-0]':                'E.ENC>>[RE_INP::F]>>-0>>!INIT_INST:NoneType::[-0][init]',
        'ENC.UPD.INV_FER':                              'E.UPD\'R>>FERNET>>FAILED_TO_INIT_FERNET;;;FATAL[0-----]',

        'J_G_ST_D::AFDATA[UINP-1][dict=>?]{merge_error}': 'J.GSTD>>script_inp[0-]>>TYPE>>VAR::[description]<<Exp:[DICT{any}]>>RS:![DICT{any}][-1]',
        'J_G_ST_D::AFDATA[UINP-1][TPE:?]{merge_error}':   'J.GSTD>>script_inp[1-]>>TYPE>>VAR::[description]<<Exp:[accepted]<<REC:?[-2]',
        'J_G_ST_D::AFDATA[UINP-1][##]{merge_error}':      'J.GSTD>>script_inp[2-]>>TYPE>>VAR::[description]<<Exp:[numerical]<<REC:![#][2-]',
        'J_G_ST_D::AFDATA[UINP-1][()]{merge_error}':      'J.GSTD>>script_inp[32-]>>TYPE>>VAR::[description]<<Exp:[mul]<<REC:![{}][2-]',

        'SC::U_PREF;;FUNC::S_T_MPref::VAR::MODE[user_inp[0]]': 'U_PREF>>S_T_MPREF[1]>>NAME::MODE>>TYPE::TUPLE<<Exp:[user_inp[0]>>[~-1]',
        'SC::U_PREF;;FUNC::G_T_MPref::VAR::DEF[user_inp[0]]':  'U_PREF>>G_T_MPREF[1]>>NAME::DEFAULT>>TYPE::TUPLE<<Exp:[user_inp[0]>>[~-2]'
    }


class Files:
    configuration = {"filename": "user_config.qaFile"}
    questions_and_answers = {"filename": "qas.qaFile"}
    scores = {"folder_name": ".local_scores"}
    theme = {
        "default": {
            "filename": ConfigFile.raw['theme']['theme_file']
        },
        "userPref": {
            "filename": ConfigFile.raw['theme']['custom_config_file']
        },
        'presets': {
            'folder_name': "\\".join(s for s in ConfigFile.raw['theme']['theme_file'].split('\\')[0::])
        }
    }

    fts = {
        'folder_name': '.fts',
        'files_req': [configuration['filename'], questions_and_answers['filename']]
    }

    app_icons = {
        'theming_util': {
            'ico': '.src\\.icons\\themer.ico',
            'png': '.src\\.icons\\themer.png'
        },
        'recovery_util': {
            'ico': '.src\\.icons\\ftsra.ico',
            'png': '.src\\.icons\\ftsra.png'
        },
        'quizzing_tool': {
            'ico': '.src\\.icons\\quizzing_tool.ico',
            'png': '.src\\.icons\\quizzing_tool.png'
        },
        'admin_tools': {
            'ico': '.src\\.icons\\admin_tools.ico',
            'png': '.src\\.icons\\admin_tools.png'
        },
        'installer': {
            'ico': '.src\\.icons\\setup.ico',
            'png': '.src\\.icons\\setup.png'
        }
    }

    global_enco = 'utf-8'

    files = {
        'cmfbackup': {
            'ico':      '.src\\.icons\\cmfbackup.ico',
            'png':      '.src\\.icons\\cmfbackup.png',
            'encrypt':  True,
            'encoding': global_enco
        },
        'cmflog': {
            'ico': '.src\\.icons\\cmflog.ico',
            'png': '.src\\.icons\\cmflog.png',
            'encrypt': False,
            'encoding': global_enco
        },
        '$favicon': {
            'ico': '.src\\.icons\\favicon.ico',
            'png': '.src\\.icons\\favicon.png',
            'zip': '.src\\.icons\\favicon.zip'
        },
        'qaExport': {
            'ico': '.src\\.icons\\qaExport.ico',
            'png': '.src\\.icons\\qaExport.png',
            'encrypt': True,
            'encoding': global_enco
        },
        'qaEnc': {
            'ico': '.src\\.icons\\qaEnc.ico',
            'png': '.src\\.icons\\qaEnc.png',
            'encrypt': True,
            'encoding': global_enco
        },
        'qaFile': {
            'ico': '.src\\.icons\\qaFile.ico',
            'png': '.src\\.icons\\qaFile.png',
            'encrypt': True,
            'encoding': global_enco
        },
        'qaLog': {
            'ico': '.src\\.icons\\qaLog.ico',
            'png': '.src\\.icons\\qaLog.png',
            'encrypt': False,
            'encoding': global_enco
        },
        'qaQuiz': {
            'ico': '.src\\.icons\\qaQuiz.ico',
            'png': '.src\\.icons\\qaQuiz.png',
            'encrypt': False,
            'encoding': global_enco
        },
        'qaScore': {
            'ico': '.src\\.icons\\qaScore.ico',
            'png': '.src\\.icons\\qaScore.png',
            'encrypt': True,
            'encoding': global_enco
        }
    }

    sfx = {
        'error': {
            'file': '.src\\.sfx\\error.mp3'
        }
    }

    help = {
        'recovery_utilities': '.aid\\recov_util.pdf',
        'question_entry':     '.aid\\admt_q-add_aid.pdf'
    }

    extensions = {
        'export':       'qaExport',
        'quiz_file':    'qaQuiz',
        'score_db':     'qaScore'
    }


class FileCodes:
    file_header = "<<QA::COMPATIBILITY::VERSION :: %s>>" % str(ConfigFile.raw['app_data']['build']['file_compatibility'])

    question_separators = {
        'nl':       '<<%%QA::0&000001%%>>',
        'qas':      '<<%%QA::0&000002%%>>',
        'space':    '<<%%QA::0&000003%%>>'
    }

    question_codes = {
        'normal':       '<<%%QA::QUESTION::TYPE::NM%%>>',
        'mc': {
            'question': '<<%%QA::QUESTION::TYPE::MC%%>>',
            'option':   '[Option]'
        },
        'tf':   '<<%%QA::QUESTION::TYPE::TF%%>>'
    }


class URL:
    bug_report = "https://geetanshgautam.wixsite.com/database/qas-bug-report-form"
    version_check = "https://raw.githubusercontent.com/GeetanshGautam0/cmfvers/master/qas/v3.json"


class Control:
    doNotUseSplash = False
