import json
import appdirs


class ConfigFile:
    name = "conf.json"
    raw = {}

    @staticmethod
    def reload_raw():
        with open(ConfigFile.name, 'r') as confFile:
            ConfigFile.raw = json.loads(confFile.read())
            confFile.close()


ConfigFile.reload_raw()


class Application:
    app_name = "Application Starter Script"
    app_author = "Coding Made Fun"
    version_str = ConfigFile.raw['app_data']['build']['version_id']
    AppDataLoc = appdirs.user_data_dir(appname=app_name, appauthor=app_author, version=version_str, roaming=False)
    RoamingAppDataLoc = appdirs.user_data_dir(appname=app_name, appauthor=app_author, version=version_str, roaming=True)
    in_beta = True


class Encryption:
    key = b"eAxD42i8pmgu8ocHwYNZnn27tj9MIDuuUZ2t-TwJDmE="


class AppContainer:
    general_title = ConfigFile.raw.get('container_data')['general']['title']

    class Prompts:
        def_ws = (400, 450)


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

        'SC::U_PREF;;FUNC::S_T_MPref::VAR::MODE[user_inp[0]]': 'U_PREF>>S_T_MPREF[1]>>NAME::MODE>>TYPE::STR[accp]<<Exp:[user_inp[0]>>[~-1]',
        'SC::U_PREF;;FUNC::G_T_MPref::VAR::DEF[user_inp[0]]':  'U_PREF>>G_T_MPREF[1]>>NAME::DEFAULT>>TYPE::STR[accp]<<Exp:[user_inp[0]>>[~-2]'
    }

