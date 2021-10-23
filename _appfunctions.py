import conf, pr_conf
import os, sys, json, threading, random, exceptions, traceback, datetime, importlib, log_cleaner
from datetime import datetime
from datetime import timedelta
import tkinter as tk
from tkinter import messagebox as tkmsb
from cryptography.fernet import Fernet
import cryptography


# Globals
_SELF_LOG = None

for_log = "%Z(%z)::%w %d %m %y - %H:%M:%S::%f (%j) [%c]"
# for_log_name = "%Z%z%w %d%m%y%H%M%S%f%j%c"
for_log_name = "%Z%z%w %d %m %y %H %M %S %f %j %c"

version_id = "!~0010.00101.-8"

with open("low.json", 'r') as file:
    _l_json = json.loads(file.read())
    file.close()

_prConfFile: str = _l_json['pcm_file']
protected_conf = importlib.import_module(_prConfFile)

if pr_conf.pro_conf_version_id != protected_conf.v:
    raise SystemError("Invalid pr_conf version description (discr.)")
elif pr_conf.r_appf_version_id != version_id:
    raise SystemError("Invalid appfunctions script") 


class AFDATA:
    class Data:
        defaults = {
            'container_title': conf.AppContainer.general_title,
            'encoding': 'utf-8',
            'enc_key': conf.Encryption.key,
            'class': {
                'AFIOObject': {}
            }
        }

        prompts = {
            'ync': {
                'D_AFI_OWR_EXS:FALSE_EXS:TRUE': """Undefined behaviour encountered:
AFDATA.AFI.OWR_EXS=FALSE && EXS=TRUE

Do you wish to 'OWR_UID' [yes] or cancel the operation [no]?
"""
            }
        }

        blacklists = {
            'encoding': [['=', 'utf-32'], ['*', 'utf-16']]
        }

        encoding_lookup = ['utf-8', ]

    class ScriptData:
        def __init__(self):
            self.class_name = "ScriptData"
            function_name = "ScDATA_INIT"
            self.uid_instance_map = {}
            self.data = {
                'class': {
                    'AFIOObject': {}
                }
            }
            self.instances = []
            self.apploc = conf.Application.AppDataLoc

        def add_file_instance(self, filename: str, uid: str, instance: object, _owr_exs: bool = True) -> None:
            function_name = "ScDATA_AD_F_INST"
            if _owr_exs or uid not in self.uid_instance_map:
                self.uid_instance_map[uid] = [instance, filename]
                self.instances.append(instance)

            elif uid in self.uid_instance_map:
                r = tk.Tk()
                r.withdraw()
                confirmation = tkmsb.askyesno(
                    AFDATA.Data.defaults['container_title'],
                    AFDATA.Data.prompts['ync']['D_AFI_OWR_EXS:FALSE_EXS:TRUE']
                )
                r.after(0, r.destroy)

                if confirmation:
                    self.uid_instance_map[uid] = [instance, filename]
                    self.instances.append(instance)

            self.instances = list(set(self.instances))  # Rids the list of duplicates    
            return None

        def add_non_file_instance(self, uid: str, instance: object, _owr_exs: bool = True) -> None:
            function_name = "ScDATA_AD_N_F_INST"
            if _owr_exs or uid not in self.uid_instance_map:
                self.uid_instance_map[uid] = [instance, None]
                self.instances.append(instance)

            elif uid in self.uid_instance_map:
                r = tk.Tk()
                r.withdraw()
                confirmation = tkmsb.askyesnocancel(
                    AFDATA.Data.defaults['container_title'],
                    AFDATA.Data.prompts['ync']['D_AFI_OWR_EXS:FALSE_EXS:TRUE']
                )
                r.after(0, r.destroy)

                if confirmation:
                    self.uid_instance_map[uid] = [instance, None]
                    self.instances.append(instance)

            self.instances = list(set(self.instances))  # Rids the list of duplicates
            return None

        def check_instance_exs(self, instance: object) -> bool:
            function_name = "ScDATA_C_INST_EXS"
            return instance in self.instances

        def check_uid_exs(self, uid: str) -> bool:
            function_name = "ScDATA_C_UID_EXS"
            return uid in self.uid_instance_map

        def check_file_exs(self, filename) -> list:
            function_name = "ScDATA_C_FILENAME_EXS"
            if filename is None: return [False, None]

            f = {file[-1]: uid for uid, file in self.uid_instance_map.items()}

            if filename not in f:
                return [False, None]
            else:
                return [True, f[filename]]

        def del_instance(self, uid: str) -> None:
            function_name = "ScDATA_DAN_DEL_INST"
            _ins = self.uid_instance_map[uid]
            del self.uid_instance_map[uid]
            try:
                self.instances.pop(self.instances.index(_ins))
            except:
                pass
            return None

        def get_uid_from_filename(self, filename: str) -> str:
            function_name = "ScDATA_G_UID_F_FILENAME"
            return {file[-1]: uid for uid, file in self.uid_instance_map.items()}.get(filename)

        def get_instance_from_uid(self, uid: str) -> object:
            function_name = "ScDATA_G_INST_F_UID"
            return self.uid_instance_map[uid][0]  # Will cause error if uid doesn't exist (intentional.)

        def get_filename_from_uid(self, uid: str) -> str:
            function_name = "G_FILENAME_F_UID"
            return self.uid_instance_map[uid][-1]

    class Functions:
        @staticmethod
        def time():
            function_name = "FUNC_TIME"
            return datetime.now()

        @staticmethod
        def generate_uid(seed=0.00) -> str:
            function_name = "FUNC_GEN_UID"
            I = str(random.randint(100000000000000, 999999999999999)) + "." + \
                str(random.random() * (random.random() * 10 ** 5)) + \
                "." + str(random.random() * random.randint(0, 9)) + ":" + \
                str(random.random() * seed)
            _time = datetime.now().strftime("%d:%m:%Y:%H:%M:%S:%f::%z::%j---%X")
            _rs = ["~~", "1~", "`@", "3~@", "#@~", "$%@~"]
            return _time + I + _rs[random.randint(0, len(_rs) - 1)]

        @staticmethod
        def flags(template_dict: dict, user_in_dict: dict) -> dict:
            """
            :param template_dict: Template
            :param user_in_dict: User Input
            :return: dict

            template format:
            [<default _data [any]>, type <optional; needed if next bool is False [type]>, <same type [bool]>, <type sensitive [bool]>]
            """

            global _SELF_LOG

            function_name = "FUNC_KWARG_INPUT_HANDLER"
            template = template_dict
            user_in = user_in_dict

            for flag in user_in:
                if flag not in template:
                    E = exceptions.ParameterException(
                        function_name,
                        'USER_IN_DICT[DICT]',
                        'FUNC_DESC_TYPE[ANY--ANY]: NAME_ERROR',
                        str(flag),
                        True,
                        'AFDATA.Functions.flags::flag[name_error]'
                    )

                    # try:
                    #     if _SELF_LOG is not None:
                    #         _SELF_LOG.log(function_name + ": " + E.__str__())
                    # except:
                    #     pass

                    raise E

            # _output = template
            _output: dict = {}
            for k, v in template.items():

                if k in user_in:
                    if v[-1]:
                        if v[-2]:
                            if type(v[0]) is type(user_in[k]):
                                _output[k] = user_in[k]
                            else:
                                _output[k] = v[0]

                        else:
                            if type(user_in[k]) is v[-3]:
                                _output[k] = user_in[k]
                            else:
                                _output[k] = v[0]
                    else:
                        _output[k] = user_in[k]

                else:
                    _output[k] = v[0] if type(v) in [list, tuple, set] else v

            # try:
            #     if _SELF_LOG is not None:
            #         _SELF_LOG.log(function_name + ": " + "td, ud, _o: ", template, user_in, _output)
            # except:
            #     pass

            return _output

        @staticmethod
        def check_blacklist(user_in: any, template: list, default: any) -> any:
            function_name = "FUNC_C_BLCKLST"
            global _SELF_LOG

            ok = True
            for item in template:
                if not ok: break
                check = item[0]
                bl = item[-1]

                if check == "type":
                    if type(bl) is not type(user_in): ok = False

                elif check == "!!":
                    if user_in not in bl: ok = False

                elif check == "=" or type(bl) is not str or type(default) is not str:
                    if bl == user_in: ok = False

                elif check == "*":
                    if bl.lower() in user_in.lower(): ok = False

                else:
                    ok = False

            try:
                #  _SELF_LOG is not None:
                #   SELF_LOG.log(function_name + ": " + "ok, ui, def: ", ok, user_in, default)
                pass
            except:
                pass

            if ok:
                return user_in
            else:
                return default

        @staticmethod
        def check_encoding(data: bytes, use_default: bool, lst=('utf-8',)):
            function_name = "FUN_C_ENCO_NAME"
            global _SELF_LOG

            if use_default:
                lst = (*AFDATA.Data.encoding_lookup,)

            if len(lst) < 0:
                E = exceptions.ParameterException(
                    function_name,
                    'lst',
                    'LIST[LEN>0]',
                    'LIST[LEN<=0]',
                    True,
                    'AFDATA.Data.check_encoding::lst'
                )

                try:
                    if _SELF_LOG is not None:
                        _SELF_LOG.log(function_name + ": " + E.__str__())
                except:
                    pass

                raise E

            elif type(data) is not bytes:
                E = exceptions.ParameterException(
                    function_name,
                    '_data',
                    'BYTES[LEN>0]',
                    str(type(data)).upper(),
                    True,
                    'AFDATA.Data.check_encoding::_data'
                )

                try:
                    if _SELF_LOG is not None:
                        _SELF_LOG.log(function_name + ": " + E.__str__())
                except:
                    pass

                raise E

            elif len(data) <= 0:
                E = exceptions.ParameterException(
                    function_name,
                    '_data',
                    'BYTES[LEN>0]',
                    'BYTES[LEN<=0]',
                    True,
                    'AFDATA.Data.check_encoding::_data[1]'
                )

                try:
                    if _SELF_LOG is not None:
                        _SELF_LOG.log(function_name + ": " + E.__str__())
                except:
                    pass

                raise E

            for encoding in lst:
                if type(encoding) is str and encoding not in (enco[-1] for enco in AFDATA.Data.blacklists['encoding']):
                    try:
                        f = data.decode(encoding)
                    except:
                        # print('encoding \'{}\' did not work.'.format(encoding))
                        pass
                    else:
                        return encoding

                else:
                    E = exceptions.ParameterException(
                        function_name,
                        'lst >>> gen >>> ENCODING',
                        'STR[ENCO, !in_D.D.BLKLST.ENCO(s)]',
                        'STR[in_D.D.BLKLST.ENCO(s)] || !STR (\'{}\')'.format(encoding),
                        True,
                        'AFDATA.Data.check_encoding::lst>>gen>>encoding'
                    )

                    try:
                        if _SELF_LOG is not None:
                            _SELF_LOG.log(function_name + ": " + E.__str__())
                    except:
                        pass

                    raise E

                return -1

        @staticmethod
        def recursive_list_conversion(_data, sep: str = "\n", kv_sep: str = " ") -> str:
            function_name = "FUNC_REC_CONV_F_LST"
            global _SELF_LOG

            # Error Conditions (type, length)
            if type(_data) not in [list, tuple, set]:
                E = exceptions.ParameterException(
                    function_name,
                    '_data',
                    'LIST||TUPLE[ANY, LEN>0]',
                    str(type(_data)).upper(),
                    True,
                    'AFDATA.Data.recursive_list_conversion::_data[0]'
                )

                try:
                    if _SELF_LOG is not None:
                        _SELF_LOG.log(function_name + ": " + E.__str__())
                except:
                    pass

                raise E

            _data = (*_data,)

            if len(_data) <= 0:
                E = exceptions.ParameterException(
                    function_name,
                    '_data',
                    'LIST||TUPLE[ANY, LEN>0]',
                    'LIST||TUPLE[LEN<=0]',
                    True,
                    'AFDATA.Data.recursive_list_conversion::_data[1]'
                )

                try:
                    if _SELF_LOG is not None:
                        _SELF_LOG.log(function_name + ": " + E.__str__())
                except:
                    pass

                raise E

            _output_comp = []

            for item in _data:
                if type(item) in [list, tuple, set]:
                    _output_comp.append(AFDATA.Functions.recursive_list_conversion(item, sep, kv_sep))
                elif type(item) is str:
                    _output_comp.append(item.strip())
                elif type(item) is bytes:
                    _output_comp.append(item.decode(AFDATA.Functions.check_encoding(item, True)).strip())
                elif type(item) is dict:
                    _output_comp.append(AFDATA.Functions.recursive_dict_conversion(item, sep, kv_sep))
                elif type(item) in [int, float]:
                    _output_comp.append(str(item))

            _sample = _output_comp[0]

            if type(_sample) is bytes and type(sep) is str:
                sep2use = sep.encode(AFDATA.Functions.check_encoding(_sample, True))

            elif type(_sample) is str and type(sep) is bytes:
                sep2use = sep.decode(AFDATA.Functions.check_encoding(sep, True))

            else:
                sep2use = sep

            return sep2use.join(_line for _line in _output_comp)

        @staticmethod
        def recursive_dict_conversion(data, kv_sep: str = " ", sep: str = "\n") -> str:  # AFDATA.Data.RDConv
            function_name = "FUNC_REC_CON_F_DICT"
            global _SELF_LOG

            # Error conditions
            if type(data) is not dict:
                E = exceptions.ParameterException(
                    function_name,
                    '_data',
                    'DICT[ANY, LEN::ANY]',
                    str(type(data)).upper(),
                    True,
                    'AFDATA.Data.recursive_dict_conversion::_data[0]'
                )

                try:
                    if _SELF_LOG is not None:
                        _SELF_LOG.log(function_name + ": " + E.__str__())
                except:
                    pass

                raise E

            if len(data) <= 0:
                return ""

            output_comp = []

            for key, value in data.items():
                v = k = None

                # Key
                if type(key) in [list, tuple, set]:
                    k = AFDATA.Functions.recursive_list_conversion(key, sep, kv_sep)
                elif type(key) is dict:
                    k = AFDATA.Functions.recursive_dict_conversion(key, sep, kv_sep)
                elif type(key) is str:
                    k = key.strip()
                elif type(key) is bytes:
                    k = key.decode(AFDATA.Functions.check_encoding(key, True)).strip()
                elif type(key) in [int, float]:
                    k = str(key)

                # Value
                if type(value) in [list, tuple, set]:
                    v = AFDATA.Functions.recursive_list_conversion(value, sep, kv_sep)
                elif type(value) is dict:
                    v = AFDATA.Functions.recursive_dict_conversion(value, sep, kv_sep)
                elif type(value) is str:
                    v = value.strip()
                elif type(value) is bytes:
                    v = value.decode(AFDATA.Functions.check_encoding(value, True)).strip()
                elif type(value) in [int, float]:
                    v = str(value)

                output_comp.append(f"%s%s%s" % (k, kv_sep, v))

            output: str = sep.join(new for new in output_comp)
            return output


SELF_DATA = AFDATA.ScriptData()
SELF_DATA.data['class']['AFIOObject']['flags_template'] = {
    'isFile': [False, True, True],
    'encoding': [AFDATA.Data.defaults['encoding'], True, True],
    'encrypt': [False, True, True],
    'filename': [None, str, False, True],
    'enc_key': [AFDATA.Data.defaults['enc_key'], True, True],
    're_type': [bytes, True, True],
    'lines_mode': [False, True, True]
}


class AFIOObject:
    def __init__(self, owr_exs_err_par_owr_meth: bool = False, *args, **kwargs):
        """
        **O_IOInstance:**
            * Will create an instance for any object/file you want
            * Allows seamless usage of all functions within the 'raw_appfunctions.py' script
            * Access 'UID' by getting the 'id' attribute from this instancedatetime A combination of a date and a time. Attributes: ()

        **Supported KWARGS**
            1. 'isFile':
                - type: boolean
                - default: false

            2. 'encoding':
                - type: str
                - default: 'AFDATA.Data.defaults.encoding'

            3. 'encrypt':
                - type: boolean
                - default: false

            4. 'filename':
                - type: str
                - default: None

            5. 'enc_key':
                - type: bytes
                - default: AFDATA.Data.defaults.enc_key
                - comments: This attribute controls the RSA encryption key that is used by all functions relating to the 'encrypt' flag.

            6. 're_type':
                - type: type [accepts bytes, str]
                - default: bytes
                - comments: 'Read Type:' Bytes / String

            7. 'lines_mode':
                - type: bool
                - default: false
                - comments: use 'read_lines' when reading (writing is automatic.)
        """
        global SELF_DATA, _SELF_LOG
        self.flags_loaded = False
        self.flags_template = SELF_DATA.data['class']['AFIOObject']['flags_template']
        self.flags = {}
        self._protected_flags = {}
        self.valid_instance = True
        self._read_only = False
        self.fernet = None
        self._load_flags(kwargs)

        if self.flags['isFile']:
            if type(self.flags['filename']) is not str and 'DE_ENC_METH' not in args:
                E = TypeError(
                    "Expected type 'str' for flag 'filename;' got type %s" % str(type(self.flags['filename'])))

                try:
                    if _SELF_LOG is not None:
                        _SELF_LOG.log("AFIOObject::root: " + E.__str__())
                except:
                    pass

                raise E

            self.filename = self.flags['filename']

        else:
            self.filename = None

        sel_uid = False

        if SELF_DATA.check_file_exs(self.filename)[0] and 'DE_ENC_METH' not in args:
            if not owr_exs_err_par_owr_meth and 'DE_ENC_METH':
                E = exceptions.FileInstanceEXSException(self.filename)

                try:
                    if _SELF_LOG is not None:
                        _SELF_LOG.log("AFIOObject::root: " + E.__str__())
                except:
                    pass

                raise E

            template = SELF_DATA.uid_instance_map[SELF_DATA.get_uid_from_filename(self.filename)][0]
            self.uid = template.uid
            sel_uid = True
            SELF_DATA.del_instance(self.uid)

        while not sel_uid:
            self.uid = AFDATA.Functions.generate_uid(seed=-random.random())
            if not SELF_DATA.check_uid_exs(self.uid): sel_uid = True

        ### ADD INSTANCE

        if self.flags['isFile']:
            SELF_DATA.add_file_instance(self.flags['filename'], self.uid, self, _owr_exs=False)

        else:
            SELF_DATA.add_non_file_instance(self.uid, self, _owr_exs=False)

    def _load_flags(self, user_in, template: dict = None) -> None:
        global _SELF_LOG

        if self._read_only:
            E = Exception("This instance cannot be modified (set as read-only.)")

            try:
                if _SELF_LOG is not None:
                    _SELF_LOG.log("AFIOObject::root: " + E.__str__())
            except:
                pass

            raise E

        if template is None:
            self.flags = AFDATA.Functions.flags({**self.flags_template}, user_in)

        else:
            n_flags = AFDATA.Functions.flags(template, user_in)
            for k, nv in n_flags.items():
                if k not in self._protected_flags:
                    self.flags[k] = nv
                else:
                    self._protected_flags[k] = nv

        self.flags['encoding'] = AFDATA.Functions.check_blacklist(self.flags['encoding'],
                                                                  AFDATA.Data.blacklists['encoding'],
                                                                  AFDATA.Data.defaults['encoding'])
        self.flags['re_type'] = AFDATA.Functions.check_blacklist(self.flags['re_type'], ["!!", [str, bytes]], str)

        if not self.flags_loaded:
            self._protected_flags = {'enc_key': self.flags['enc_key']}
            self.flags_loaded = True

        for _pflag in self._protected_flags:
            if _pflag in self.flags:
                self.flags.pop(_pflag)

        if self.flags['encrypt']:
            if type(self._protected_flags['enc_key']) is not bytes:

                E = TypeError(
                    "Expected type 'bytes' for flag 'enc_key;' got %s" % str(type(self._protected_flags['enc_key'])))

                try:
                    if _SELF_LOG is not None:
                        _SELF_LOG.log("AFIOObject::root: " + E.__str__())
                except:
                    pass

                raise E

            elif len(self._protected_flags['enc_key']) != 44:
                E = cryptography.fernet.InvalidToken("Invalid token given for encryption key - Code INV_L_1")
                try:
                    if _SELF_LOG is not None:
                        _SELF_LOG.log("AFIOObject::root: " + E.__str__())
                except:
                    pass

                raise E

            else:
                self.fernet = Fernet(self._protected_flags['enc_key'])  # Will also work as a final check

        else:
            self.fernet = None

    def delete_instance(self):
        global _SELF_LOG
        if not self.valid_instance:
            E = exceptions.ReadOnlyIOObjectException(self.uid)
            try:
                if _SELF_LOG is not None:
                    _SELF_LOG.log("AFIOObject::del_inst: " + E.__str__())
            except:
                pass

            raise E

        global SELF_DATA
        self.valid_instance = False
        SELF_DATA.del_instance(self.uid)

    def mark_read_only(self):
        self._read_only = True

    def edit_flag(self, **kwargs):
        global _SELF_LOG
        if not self.valid_instance:
            E = Exception("This instance cannot be modified (invalid/deleted instance.)")
            try:
                if _SELF_LOG is not None:
                    _SELF_LOG.log("AFIOObject::ed_flag: " + E.__str__())
            except:
                pass

            raise E

        if self._read_only:
            E = exceptions.ReadOnlyIOObjectException(self.uid)
            try:
                if _SELF_LOG is not None:
                    _SELF_LOG.log("AFIOObject::ed_flag: " + E.__str__())
            except:
                pass

            raise E

        template = {}
        for k, v in kwargs.items():
            if k in {**self.flags, **self._protected_flags}:
                template[k] = self.flags_template[k]
            else:
                raise AttributeError("Invalid flag name '%s'" % str(k))

        self._load_flags(kwargs, template)

    def __del__(self):
        pass


class AFIOObjectInterface:
    def __init__(self, uid: str) -> None:
        global SELF_DATA, _SELF_LOG
        if uid not in SELF_DATA.uid_instance_map:
            E = exceptions.InitializationError("AFIOObjectInterface", 'Invalid uid provided.')

            try:
                if _SELF_LOG is not None:
                    _SELF_LOG.log("AFIOObjectInterface::root: " + E.__str__())
            except:
                pass

            raise E

        self.instance = SELF_DATA.uid_instance_map[uid][0]
        self.filename = self.instance.filename
        self.uid = uid
        self.isFile = self.instance.flags['isFile']
        self.re_type = self.instance.flags['re_type']
        self.lines_mode = self.instance.flags['lines_mode']
        self.encoding = self.instance.flags['encoding']
        self.encrypt = self.instance.flags['encrypt']
        self._pr_flags = self.instance._protected_flags
        self._IS_DE_ENC_METH_GEN = None


class AFEncryption:
    def __init__(self, uid):
        global _SELF_LOG
        self.class_name = "ENC_MASTER"
        self.uid = uid
        self.instance = None
        self.raw_instance = None
        self.fernet: cryptography.fernet.Fernet = None
        self._nObject = None
        try:
            self.update_instance()
        except Exception as e:
            E = exceptions.InitializationError(
                self.class_name,
                str(e)
            )

            try:
                if _SELF_LOG is not None:
                    _SELF_LOG.log(self.class_name + ": " + E.__str__())
            except:
                pass

            raise E

    def update_instance(self):
        global _SELF_LOG

        function_name = "ENC.UPD_INST"
        self.instance = AFIOObjectInterface(self.uid)
        self.raw_instance = self.instance.instance
        self._nObject = AFIOObject(
            False,
            'DE_ENC_METH',
            isFile=self.instance.isFile,
            filename=self.instance.filename,
            encrypt=True,
            lines_mode=True,
            re_type=bytes,
            encoding=self.instance.encoding
        )

        try:
            self.fernet = self.raw_instance.fernet
        except Exception as E:
            E = exceptions.EncryptionException(function_name, 'ENC.UPD.INV_FER', "Failed to create fernet: %s" % E)

            try:
                if _SELF_LOG is not None:
                    _SELF_LOG.log(function_name + ": " + E.__str__())
            except:
                pass

            raise E

        return 

    def decrypt(self, _raw, *args, **kwargs) -> bytes:
        global _SELF_LOG

        function_name = "ENC.DEC[RE,INP::F]"
        self.update_instance()

        E = None

        if None in [self.instance, self.raw_instance]:
            E = exceptions.EncryptionException(function_name, 'ENC.DEC[RE,INP::F]::!INST[-0]')
        elif not self.instance.encrypt:
            E = exceptions.EncryptionException(function_name, 'ENC.GLOBAL[G]::!ENC[-1]')
        elif self.fernet is None:
            E = exceptions.EncryptionException(function_name, 'ENC.GLOBAL[G]::!FER[-0]')
        elif type(_raw) is not bytes:
            E = exceptions.EncryptionException(function_name, 'ENC.GLOBAL[INP]::TP-RAW!:BYTES')

        if E is not None:
            try:
                if _SELF_LOG is not None:
                    _SELF_LOG.log(function_name + ": " + E.__str__())
            except:
                pass

            raise E

        return self.fernet.decrypt(_raw)

    def encrypt(self, _data, *args, **kwargs) -> bytes:
        global _SELF_LOG

        function_name = "ENC.ENC[RE,INP::F]"
        self.update_instance()

        E = None

        if None in [self.instance, self.raw_instance]:
            E = exceptions.EncryptionException(function_name, 'ENC.ENC[RE,INP::F]::!INST[-0]')
        elif not self.instance.encrypt:
            E = exceptions.EncryptionException(function_name, 'ENC.GLOBAL[G]::!ENC[-1]')
        elif self.fernet is None:
            E = exceptions.EncryptionException(function_name, 'ENC.GLOBAL[G]::!FER[-0]')
        elif type(_data) is not bytes:
            E = exceptions.EncryptionException(function_name, 'ENC.GLOBAL[INP]::TP-RAW!:BYTES')

        if E is not None:
            try:
                if _SELF_LOG is not None:
                    _SELF_LOG.log(function_name + ": " + E.__str__())
            except:
                pass

            raise E

        return self.fernet.encrypt(_data)

    def _encFile(self, *args, **kwargs) -> None:  # ENC.HDN_EN_FILE_OWR
        global _SELF_LOG

        function_name = 'ENC.HDN_EN_FILE_OWR'
        self.update_instance()
        E = None
        if not self.instance.isFile:
            E = exceptions.FileIOException(function_name, "Invalid AFIOObject supplied.")
        elif not self.instance.encrypt:
            E = exceptions.EncryptionException(function_name, 'ENC.GLOBAL[G]::!ENC[-1]')
        elif self.raw_instance.fernet is None:
            E = exceptions.EncryptionException(function_name, 'ENC.GLOBAL[G]::!FER[-0]')
        elif not os.path.exists(self.instance.filename):
            return

        if E is not None:
            try:
                if _SELF_LOG is not None:
                    _SELF_LOG.log(function_name + ": " + E.__str__())
            except:
                pass

            raise E

        # Used tuples rather than lists as an optimization
        #       - Tuples are faster than lists for larger _data sets.
        self._nObject.edit_flag(lines_mode=True)
        _raw = (*AFFileIO(self._nObject.uid).load_file(),)
        _c = ()

        for _line in _raw:
            try:
                _c = (*_c, self.decrypt(_line))
            except:
                _c = (*_c, _line)

        _c = (*_c, )
        _enc = ()
        for _line in _c:
            _l = b""
            if type(_line) is bytes:
                _l = _line

            elif type(_line) is str:
                _l = _line.encode(self.instance.encoding)

            elif type(_line) in [list, tuple, set]:
                _l = (AFDATA.Functions.recursive_list_conversion(_line)).encode(self.instance.encoding)

            elif type(_line) is dict:
                _l = (AFDATA.Functions.recursive_dict_conversion(_line)).encode(self.instance.encoding)

            _enc = (*_enc, _l.strip(), "\n".encode(self.instance.encoding))

        _enc = "".encode(self.instance.encoding).join(_item for _item in _enc)
        _enc = self.encrypt(_enc)

        AFFileIO(self.uid).secure_save(_enc, 'DE_ENC_METH', append=False)

    def _decFile(self, *args, **kwargs) -> None:  # ENC.HDN_DE_FILE_OWR
        global _SELF_LOG

        function_name = 'ENC.HDN_DE_FILE_OWR'
        self.update_instance()

        E = None

        if not self.instance.isFile:
            E = exceptions.FileIOException(function_name, "Invalid AFIOObject supplied.")
        elif not self.instance.encrypt:
            E = exceptions.EncryptionException(function_name, 'ENC.GLOBAL[G]::!ENC[-1]')
        elif self.raw_instance.fernet is None:
            E = exceptions.EncryptionException(function_name, 'ENC.GLOBAL[G]::!FER[-0]')
        elif not os.path.exists(self.instance.filename):
            return

        if E is not None:
            try:
                if _SELF_LOG is not None:
                    _SELF_LOG.log(function_name + ": " + E.__str__())
            except:
                pass

            raise E

        # Used tuples rather than lists as an optimization
        #       - Tuples are faster than lists for larger _data sets.
        self._nObject.edit_flag(lines_mode=False)
        _raw = AFFileIO(self.instance.uid).load_file('cbr')  # Load file with 'cbr' flag
        self._nObject.edit_flag(lines_mode=True)

        _dec = self.decrypt(_raw)

        AFFileIO(self.uid).secure_save(_dec, 'DE_ENC_METH', append=False)
        
        return

    def __del__(self):
        pass


class AFFileIO:
    def __init__(self, uid):
        global SELF_DATA, _SELF_LOG
        self.class_name = "AFFileIO"
        function_name = "FIO_INIT"

        self.uid = uid
        if uid not in SELF_DATA.uid_instance_map:
            E = exceptions.InitializationError(
                self.class_name,
                'Invalid input for parameter \'uid\''
            )

            try:
                if _SELF_LOG is not None:
                    _SELF_LOG.log(function_name + ": " + E.__str__())
            except:
                pass

            raise E

        self.file: AFIOObjectInterface = object
        self.update_instance()

        if not self.file.isFile:
            E = exceptions.InitializationError(self.class_name,
                                                 "Invalid instance uid provided: parameter 'isFile' is invalid.")

            try:
                if _SELF_LOG is not None:
                    _SELF_LOG.log(function_name + ": " + E.__str__())
            except:
                pass

            raise E

        elif type(self.file.filename) is not str:
            E = exceptions.InitializationError(self.class_name,
                                                 "Invalid instance uid provided: parameter 'filename' is invalid.")

            try:
                if _SELF_LOG is not None:
                    _SELF_LOG.log(function_name + ": " + E.__str__())
            except:
                pass

            raise E

    def update_instance(self):  # FIO_UPD_INST
        function_name = "FIO_UPD_INST"
        self.file = AFIOObjectInterface(self.uid)  # instance translator

    def save(self, _data, **kwargs):  # FIO_NR_SAVE
        global _SELF_LOG

        function_name = "FIO_NR_SAVE"
        self.update_instance()

        flags = {
            'append': [False, True, True],
            'separator': ['\n', True, True],
            'dict_kv_sep': [' ', True, True],
            'strip_data': [True, True, True]
        }
        flags = AFDATA.Functions.flags(flags, kwargs)

        flags['separator'] = flags['separator'].encode(self.file.encoding)
        flags['dict_kv_sep'] = flags['dict_kv_sep'].encode(self.file.encoding)

        if not self.file.isFile:
            E = exceptions.FileIOException(function_name)

            try:
                if _SELF_LOG is not None:
                    _SELF_LOG.log(function_name + ": " + E.__str__())
            except:
                pass

            raise E

        if not os.path.exists(self.file.filename):
            with open(self.file.filename, 'x') as file:
                file.close()

        if type(_data) is str:
            new_data: bytes = _data.encode(self.file.encoding)

        elif type(_data) is bytes:
            cenco = AFDATA.Functions.check_encoding(_data, True)
            if cenco != self.file.encoding:
                new_data = _data.decode(cenco).encode(self.file.encoding)
            else:
                new_data = _data

        elif type(_data) in [list, tuple, set]:
            new_data = AFDATA.Functions.recursive_list_conversion(_data, flags['separator'], flags['dict_kv_sep']).encode(
                self.file.encoding)

        elif type(_data) is dict:
            new_data = AFDATA.Functions.recursive_dict_conversion(_data, flags['separator'], flags['dict_kv_sep']).encode(
                self.file.encoding)

        else:
            new_data = str(_data).encode(self.file.encoding)

        if flags['strip_data']:
            new_data = new_data.strip()

        dataToSave = new_data  # If not going to append, this will work

        if flags['append'] and len(self.load_file()) > 0:
            old_data = self.read_file().encode(self.file.encoding)

            if flags['strip_data']:
                old_data = old_data.strip()

            try:
                dataToSave = old_data + flags['separator'] + new_data
            except exceptions.ParameterException:
                dataToSave = flags['separator'] + new_data

        dataToSave = dataToSave.rstrip()

        with open(self.file.filename, 'wb') as file:
            file.write(dataToSave)
            file.close()

    def secure_save(self, _data, *flag_args, **kwargs):  # FIO_SC_SAVE
        global SELF_DATA, _SELF_LOG
        function_name = "FIO_SC_SAVE"

        self.update_instance()
        if not self.file.isFile:
            E = exceptions.FileIOException(function_name)

            try:
                if _SELF_LOG is not None:
                    _SELF_LOG.log(function_name + ": " + E.__str__())
            except:
                pass

            raise E

        flags = {
            'append': [False, True, True],
            'separator': ['\n', True, True],
            'dict_kv_sep': [' ', True, True],
            'strip_data': [True, True, True],
            'delete_backup_after': [True, True, True]
        }
        flags = AFDATA.Functions.flags(flags, kwargs)

        flags['separator'] = flags['separator'].encode(self.file.encoding)
        flags['dict_kv_sep'] = flags['dict_kv_sep'].encode(self.file.encoding)

        # Step 1: Create Backup
        # Step 2: Store Backup to file
        # Step 3: Save New Data ([+] encryption)
        #   3-1: If OK, delete backup (FLAGGED)
        #   3-2: Else, restore backup
        #       - Then delete backup

        if not os.path.exists(self.file.filename):
            self.save(_data=_data,
                      append=flags['append'],
                      separator=flags['separator'],
                      dict_kv_sep=flags['dict_kv_sep'],
                      strip_data=flags['strip_data']
                      )

        else:
            # Step 1: Create backup
            try:
                with open(self.file.filename, 'rb') as file:
                    _backup_data = file.read()
                    file.close()

            except:
                E = exceptions.FileIOException(function_name,
                                              "Failed to load backup _data; aborting operation for safety.")

                try:
                    if _SELF_LOG is not None:
                        _SELF_LOG.log(function_name + ": " + E.__str__())
                except:
                    pass

                raise E

            time = AFDATA.Functions.time().strftime('%d%m%y%S%f%z%Z%j')
            _backup_file_name = SELF_DATA.apploc + "\\Temporary Files\\AFFileIO\\%s\\%s\\%s.cmfbackup" % (
            function_name, "__".join(i for i in self.file.filename.split("\\")[-1].split('.')), time)
            _backup_directory = "\\".join(i for i in _backup_file_name.split("\\")[:-1])

            # Step 2: Store Backup to file
            try:
                if not os.path.exists(_backup_directory):
                    os.makedirs(_backup_directory)
                with open(_backup_file_name, 'wb') as _backup_file:
                    _backup_file.write(_backup_data)
                    _backup_file.close()
            except:
                print(traceback.format_exc())
                E = exceptions.FileIOException(function_name,
                                                 "Failed to save temporary backup; aborting operation for safety.")

                try:
                    if _SELF_LOG is not None:
                        _SELF_LOG.log(function_name + ": " + E.__str__())
                except:
                    pass

                raise E

            # Step 3: Save New Data
            try:
                self.save(_data=_data,
                          append=flags['append'],
                          separator=flags['separator'],
                          dict_kv_sep=flags['dict_kv_sep'],
                          strip_data=flags['strip_data']
                          )

                if self.file.encrypt and 'DE_ENC_METH' not in flag_args:
                    AFEncryption(self.uid)._encFile()

            except:
                try:
                    with open(self.file.filename, 'wb') as file:
                        file.write(_backup_data)
                        file.close()

                    with open(self.file.filename, 'rb') as file:
                        _br = file.read()
                        file.close()

                    if _br.strip() != _backup_data.strip():
                        try:
                            if _SELF_LOG is not None:
                                _SELF_LOG.log(function_name + ": _br.strip() != _backup_data.strip() (P_B_R)")
                        except:
                            pass

                        raise Exception  # Passes on to the exception handler (1)

                except:
                    E = exceptions.FileIOException(
                        function_name,
                        "FAILED TO SAVE BACKUP [FATAL] [CRITICAL]"
                    )

                    try:
                        if _SELF_LOG is not None:
                            _SELF_LOG.log(function_name + ": " + E.__str__())
                    except:
                        pass

                    raise E

                else:
                    E = exceptions.FileIOException(
                        function_name,
                        "Failed to save _data (restored backup.) :: %s" % traceback.format_exc()
                    )

                    try:
                        if _SELF_LOG is not None:
                            _SELF_LOG.log(function_name + ": " + E.__str__())
                    except:
                        pass

                    raise E

        if flags['delete_backup_after']:
            os.remove(_backup_file_name)
        
        return

    def read_file(self) -> str:  # FIO_RD_FILE
        global _SELF_LOG

        function_name = "FIO_RD_FILE"
        self.update_instance()
        if not os.path.exists(self.file.filename) or not self.file.isFile:
            E = exceptions.FileIOException(function_name, "File '%s' does not exist." % self.file.filename)

            try:
                if _SELF_LOG is not None:
                    _SELF_LOG.log(function_name + ": " + E.__str__())
            except:
                pass

            raise E

        raw = self.load_file('cbr')
        # print('[1]', raw)
        if self.file.encrypt:
            try:
                raw = AFEncryption(self.uid).decrypt(raw)
                # print('[2.1]', raw)
            except exceptions.EncryptionException as E:
                print(function_name, '[E1]', E)
                raw = raw
                # print('[2.2]', raw)
            except cryptography.fernet.InvalidToken as E:
                print(function_name, '[E1]', E)
                raw = raw
                # print('[2.3]', raw)
            except Exception as E:
                E = E.__class__(str(E))

                try:
                    if _SELF_LOG is not None:
                        _SELF_LOG.log(function_name + ": " + E.__str__())
                except:
                    pass

                raise E

        # print('[3]', raw)

        if type(raw) is bytes:
            if len(raw) > 0:
                enco = AFDATA.Functions.check_encoding(raw, True)
                Str = raw.decode(enco)
            else:
                Str = ""

        else:
            Str = raw

        # print('[4]', type(raw) is bytes, Str)

        return Str

    def load_file(self, *flags):  # FIO_LD_FILE
        global _SELF_LOG

        self.update_instance()
        function_name = "FIO_LD_FILE"

        if not os.path.exists(self.file.filename) or not self.file.isFile:
            E = exceptions.FileIOException("FIO_LD_FILE", "File '%s' does not exist." % self.file.filename)

            try:
                if _SELF_LOG is not None:
                    _SELF_LOG.log(function_name + ": " + E.__str__())
            except:
                pass

            raise E

        with open(self.file.filename,
                  'rb' if 'cbr' in flags else ('rb' if self.file.re_type is bytes else 'r')) as file:
            if 'CALL_BY_RE' in flags or not self.file.lines_mode:
                output = file.read()
            elif self.file.lines_mode:
                output = file.readlines()

            file.close()

        return output

    def clear_file(self):
        global _SELF_LOG

        self.update_instance()
        function_name = "FIO_CLEAR"

        if not os.path.exists(self.file.filename) or not self.file.isFile:
            E = exceptions.FileIOException(function_name, "File '%s' does not exist." % self.file.filename)

            try:
                if _SELF_LOG is not None:
                    _SELF_LOG.log(function_name + ": " + E.__str__())
            except:
                pass

            raise E

        with open(self.file.filename, 'w') as file:
            file.close()


class AFJSON:
    def __init__(self, uid: str):
        self.uid = uid
        self.instance = None
        self.raw_instance = None
        self.update_instance()

    def update_instance(self):
        self.instance = AFIOObjectInterface(self.uid)
        self.raw_instance = self.instance.instance

    def set_data(self, key: str, data: any, d_sub_one_k: str = None, append: bool = True, a2k: bool = True,
                 lsd_extract: bool = True, ls_sep: str = " ", kv_sep: str = ">>>",
                 dv_sep: str = ">>"):  # AFJSON.G_ST_DATA
        global _SELF_LOG

        function_name = "AFJSON.G_ST_DATA"
        self.update_instance()

        E = None

        if not self.instance.isFile:
            E = exceptions.FileIOException(function_name, "param 'isFile' is set to False for AFIOObject")
        elif not os.path.exists(self.instance.filename):
            E = FileNotFoundError("File '%s' does not exist." % self.instance.filename)

        if E is not None:
            try:
                if _SELF_LOG is not None:
                    _SELF_LOG.log(function_name + ": " + E.__str__())
            except:
                pass

            raise E

        if append:
            raw = self.load_file()
            if a2k:
                if key in raw:
                    v = raw[key]
                    if type(v) in [str, bytes]:
                        # DV
                        if type(dv_sep) is type(v):
                            dv = dv_sep

                        else:
                            if type(dv_sep) is bytes:
                                dv = dv_sep.decode(AFDATA.Functions.check_encoding(dv_sep, True))
                            else:
                                dv = dv_sep.encode(AFDATA.Functions.check_encoding(v, True))

                        # AFDATA, V
                        # SAME
                        if type(data) is type(v) and type(data):
                            v += dv + data

                        # STR/BYTES
                        elif type(data) in [str, bytes]:
                            if type(v) is bytes:
                                v += dv + data.decode(AFDATA.Functions.check_encoding(v, True))

                            else:
                                v += dv + data.decode(AFDATA.Functions.check_encoding(data, True))

                        # LIST/TUPLE/SET
                        elif type(data) in [list, tuple, set]:
                            d = AFDATA.Functions.recursive_list_conversion(data, ls_sep, kv_sep)
                            if type(d) is type(v):
                                v += dv + d

                            elif type(d) in [str, bytes]:
                                if type(v) is bytes:
                                    v += dv + d.decode(AFDATA.Functions.check_encoding(v, True))

                                else:
                                    v += dv + d.decode(AFDATA.Functions.check_encoding(d, True))

                            else:
                                raise Exception("-1")

                        # DICT
                        elif type(data) is dict:
                            d = AFDATA.Functions.recursive_dict_conversion(data, kv_sep, ls_sep)

                            if type(d) is type(v):
                                v += dv + d

                            elif type(d) in [str, bytes]:
                                if type(v) is bytes:
                                    v += dv + d.decode(AFDATA.Functions.check_encoding(v, True))

                                else:
                                    v += dv + d.decode(AFDATA.Functions.check_encoding(d, True))

                            else:
                                raise Exception("-1")

                        # NUMERICAL
                        elif type(data) in [int, float, complex]:
                            d = str(data)

                            if type(d) is type(v):
                                v += d

                            elif type(d) in [str, bytes]:
                                if type(v) is bytes:
                                    v += d.decode(AFDATA.Functions.check_encoding(v, True))

                                else:
                                    v += d.decode(AFDATA.Functions.check_encoding(d, True))

                        # EXCEPTION
                        else:
                            E = exceptions.ParameterException(
                                function_name,
                                'description',
                                '[ACCEPTED_DATA_TYPE]',
                                str(type(data)).upper(),
                                True,
                                'J_G_ST_D::AFDATA[UINP-1][TPE:?]{merge_error}'
                            )

                            try:
                                if _SELF_LOG is not None:
                                    _SELF_LOG.log(function_name + ": " + E.__str__())
                            except:
                                pass

                            raise E

                        raw[key] = v

                    elif type(v) in [list, tuple, set]:
                        if type(data) not in [list, tuple, set]:
                            E = exceptions.ParameterException(
                                function_name,
                                'description',
                                'MULT[any]<={match}',
                                str(type(data)).upper(),
                                True,
                                'J_G_ST_D::AFDATA[UINP-1][()]{merge_error}'
                            )

                            try:
                                if _SELF_LOG is not None:
                                    _SELF_LOG.log(function_name + ": " + E.__str__())
                            except:
                                pass

                            raise E

                        d = [*data, ]
                        v = (*v, *((*d,) if lsd_extract else (d,)))  # Less mem; quicker
                        v = [*v, ]  # Compatibility with AFJSON

                        raw[key] = v

                    elif type(v) in [int, float, complex]:
                        if type(data) not in [int, float, complex]:
                            E = exceptions.ParameterException(
                                function_name,
                                'description',
                                'NUM[any]<={match}',
                                str(type(data)).upper(),
                                True,
                                'J_G_ST_D::AFDATA[UINP-1][##]{merge_error}'
                            )

                            try:
                                if _SELF_LOG is not None:
                                    _SELF_LOG.log(function_name + ": " + E.__str__())
                            except:
                                pass

                            raise E

                        v += data
                        raw[key] = v

                    elif type(v) is dict:
                        if type(data) is not dict:
                            E = exceptions.ParameterException(
                                function_name,
                                'description',
                                'DICT[any]<={match}',
                                str(type(data)).upper(),
                                True,
                                'J_G_ST_D::AFDATA[UINP-1][dict=>?]{merge_error}'
                            )

                            try:
                                if _SELF_LOG is not None:
                                    _SELF_LOG.log(function_name + ": " + E.__str__())
                            except:
                                pass

                            raise E

                        if lsd_extract:
                            v = {**v, **data}
                        else:
                            v = {**v, d_sub_one_k: data, }

                        raw[key] = v

                    else:
                        E = exceptions.ParameterException(
                            function_name,
                            'pro_conf_version_id',
                            '[ACCEPTED_DATA_TYPE]',
                            str(type(data)).upper(),
                            True,
                            'J_G_ST_D::AFDATA[UINP-1][TPE:?]{merge_error}'
                        )

                        try:
                            if _SELF_LOG is not None:
                                _SELF_LOG.log(function_name + ": " + E.__str__())
                        except:
                            pass

                        raise E

                else:
                    raw[key] = data

            else:
                raw[key] = data
            _dataToSave = json.dumps(raw, indent=4)

        else:
            _dataToSave = json.dumps({key: data}, indent=4)

        AFFileIO(self.uid).secure_save(
            _dataToSave,
            append=False
        )

    def get_data(self, key: str, re_exs_val: bool = False):  # AFJSON.S_GT_DATA
        global _SELF_LOG

        function_name = "AFJSON.S_GT_DATA"

        E = None

        if not self.instance.isFile:
            E = exceptions.FileIOException(function_name, "param 'isFile' is set to False for AFIOObject")
        elif not os.path.exists(self.instance.filename):
            E = FileNotFoundError("File '%s' does not exist." % self.instance.filename)

        if E is not None:
            try:
                if _SELF_LOG is not None:
                    _SELF_LOG.log(function_name + ": " + E.__str__())
            except:
                pass

            raise E

        raw_json = self.load_file()
        return (key in raw_json) if re_exs_val else raw_json.get(key)

    def delete_key(self, key):
        global _SELF_LOG

        raw = self.load_file()
        if key not in raw:
            return 0
        del raw[key]
        AFFileIO(self.uid).secure_save(
            json.dumps(raw, indent=4),
            append=False
        )

    def load_file(self) -> dict:  # AFJSON.C_LD_FILE
        global _SELF_LOG

        function_name = "AFJSON.C_LD_FILE"

        E = None
        
        if not self.instance.isFile:
            E = exceptions.FileIOException(function_name, "param 'isFile' is set to False for AFIOObject")
        elif not os.path.exists(self.instance.filename):
            E = FileNotFoundError("File '%s' does not exist." % self.instance.filename)

        if E is not None:
            try:
                if _SELF_LOG is not None:
                    _SELF_LOG.log(function_name + ": " + E.__str__())
            except:
                pass

            raise E

        raw_s = AFFileIO(self.uid).read_file()
        json_data = {}

        try:
            json_data = json.loads(raw_s)

        except json.JSONDecodeError as E:

            try:
                if _SELF_LOG is not None:
                    _SELF_LOG.log(function_name + ": " + E.__str__())
            except:
                pass

            json_data = {"__AF__DEBUG::AFJSON.load_file() => JSONDecodeError": True}

        except Exception as E:
            try:
                if _SELF_LOG is not None:
                    _SELF_LOG.log(function_name + ": " + E.__str__())
            except:
                pass

            raise E.__class__(E.__str__())

        finally:
            return json_data

    def __del__(self):
        pass


class AFLogger:
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
            self.o_file = AFIOObjectInterface(self.O_IOInstance.uid)
            self.O_IOInstance = self.o_file.instance
            self.j = AFJSON(self.o_file.uid)
            log_file_name = self.j.load_file()[self.open_logs_dir][self.sdate][self.sid]['filename']
            self.L_IOInstance = AFIOObject(
                filename=log_file_name,
                owr_exs_err_par_owr_meth=True,
                lines_mode=False,
                re_type=str,
                isFile=True
            )
            self.log_file = AFIOObjectInterface(self.L_IOInstance.uid)
            self.scname = self.j.load_file()[self.open_logs_dir][self.sdate][self.sid]['script_name']

        def log(self, *data, empty_line: bool = False):

            self.update_instance()

            if not self.log_file.isFile:
                raise exceptions.FileIOException("LOGGER.THREADED_LOGGER", "Attribute 'isFile' is set to 'False.'")

            if not os.path.exists(self.log_file.filename):
                raise FileNotFoundError(self.log_file.filename)

            global for_log

            if empty_line:
                d2l = "\n"
            else:
                time = AFDATA.Functions.time().strftime(for_log)
                d2l = self.scname + "@" + time + ": " + "\n\t".join(str(i) for i in data).strip()

            d2l = "\n" + d2l

            AFFileIO(self.log_file.uid).save(d2l, append=True, strip_data=False)

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
            self.o_file = AFIOObjectInterface(self.O_IOInstance.uid)
            self.O_IOInstance = self.o_file.instance
            self.j = AFJSON(self.o_file.uid)
            log_file_name = self.j.load_file()[self.open_logs_dir][self.sdate][self.sid]['filename']
            self.L_IOInstance = AFIOObject(
                filename=log_file_name,
                owr_exs_err_par_owr_meth=True,
                lines_mode=False,
                re_type=str,
                isFile=True
            )
            self.log_file = AFIOObjectInterface(self.L_IOInstance.uid)
            self.scname = self.j.load_file()[self.open_logs_dir][self.sdate][self.sid]['script_name']

        def log(self, *data, e=None, empty_line=False):
            self.update_instance()
            if not self.log_file.isFile:
                raise exceptions.FileIOException("LOGGER.REL_LOGGER", "Attribute 'isFile' is set to 'False.'")

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
                time = AFDATA.Functions.time().strftime(for_log)
                d2l = self.scname + "@" + time + ": " + "\n\t".join(str(i) for i in data).strip()
                if e is not None:
                    d2l += " \n\t>>EXCEP_REPORT::" + str(e)

            d2l = "\n" + d2l

            AFFileIO(self.log_file.uid).secure_save(d2l, append=True, strip_data=False)

        def change_log_file_kwargs(self, **kwargs):
            self.L_IOInstance.edit_flag(**kwargs)
            self.update_instance()

        def __del__(self):
            pass


class AFLog:  # AFLog-USER_ACCESS-interface:auto
    def __init__(self, script_name: str, script_init_identifier: str):
        """
        **CRITICAL: DO NOT OVERWRITE VARIABLES LOGGING VARIABLES; DOING SO WILL ACTIVATE LOGGER_REQ_CLEAR; ALL PREVIOUS LOGS WILL BE MARKED AS 'CLOSED' WHENEVER THIS CLASS IS NEXT INITIALIZED.**

        :param script_name: Script name (str)
        :param script_init_identifier: UID (str)
        """

        self.TCF_LOC: str = os.path.join(conf.Application.AppDataLoc, *protected_conf.Application.Logging.TCF_AD_TREE)
        self.TCF_NAME: str = os.path.join(self.TCF_LOC, protected_conf.Application.Logging.TCF_NAME)
        self.TCF_I: AFIOObjectInterface = object
        self.TCF_OVR_FL_VAL: int = protected_conf.Application.Logging.env['usage']['TCF']['TCF_OVR_FL_VAL']
        self._o: AFIOObject = object

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

        self.refresh()

        if log_cleaner.BootCheck.clear_logs():
            log_cleaner.Actions.clear_logs(self.TCF_NAME, self.open_logs_dir)
            self.refresh()

        # Run this after the statement prior as that can cause the TCF file to reset.
        self.add_log_name()
        self.performance_logger = AFLogger.PerformanceLogger(self._o, self.open_logs_dir, script_init_identifier, self.date)
        self.reliable_logger = AFLogger.ReliableLogger(self._o, self.open_logs_dir, script_init_identifier, self.date)

    def refresh(self):
        global SELF_DATA

        ndate = AFDATA.Functions.time()
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

        uid_inst_files = (*set(SELF_DATA.uid_instance_map[file][-1] for file in SELF_DATA.uid_instance_map),)

        if self._o is object or self.TCF_NAME not in uid_inst_files:
            self._o = AFIOObject(
                filename=self.TCF_NAME,
                encrypt=False,
                isFile=True,
                encoding=str,
                lines_mode=False,
                re_type=str,
                owr_exs_err_par_owr_meth=True
            )

        self.TCF_I = AFIOObjectInterface(self._o.uid)
        self._o = self.TCF_I.instance
        self.j = AFJSON(self._o.uid)

        if not f_1:
            try:
                if 'header' not in self.j.load_file():
                    f_1 = True
            except:
                f_1 = True

        if f_1:
            self.j.set_data("header", protected_conf.Application.Logging.TCF_HEADER,
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
            # n = {'header': r['header'], 'open_logs': r['open_logs']}
            # for date in (*{self.min_date, self.date, self.max_date, *self.find_dates_in_use()}, ):

            # Cleanup
            n = {**r, 'closed_files': {}}
            # for date, scis in self.find_in_use_logs(True).items():
            #     print(scis)
            #     for sci in scis:
            #         del n[self.open_logs_dir][date][sci]

            AFFileIO(self._o.uid).secure_save(json.dumps(n, indent=4))

    def find_script_logger(self, exsc=False):
        self.refresh()
        r = self.j.load_file()
        for date in self.find_dates_in_use():  # IMPORTANT: KEEP DATES IN THIS EXACT ORDER
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
                o = (*o, date, )

            o = (*set(o), )
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
                        o[date] = (sci, )

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
        
        if len(a) > protected_conf.Application.Logging.critical_point:
            a = tk.Tk()
            a.withdraw()
            tkmsb.showwarning(conf.Application.app_name,
                              "File 'LCF File.json' is approaching a critical point that can cause severe lag (>%s lines.) Attempting to clear some older application description." % str(
                                  protected_conf.Application.Logging.critical_point
                              ))
            a.after(0, a.destroy)

            op1 = dict(list(r.items())[:len(r) // 2])
            o1 = {"header": r['header'], self.open_logs_dir: op1, "closed_files": {}}
            s2 = json.dumps(o1, indent=4)
            AFFileIO(self._o.uid).secure_save(s2, append=False)

        elif len(a) > protected_conf.Application.Logging.min_crit_point:
            ### CLEAR CLOSED FILES LOGS
            tkmsb.showwarning(conf.Application.app_name, "File 'LCF File.json' is approaching a critical point that can cause lag (>%s lines.) Attempting to clear some older application description." % str(
                protected_conf.Application.Logging.min_crit_point
            ))
            r['closed_files'] = {}
            s1 = json.dumps(r, indent=4)
            AFFileIO(self._o.uid).secure_save(s1, append=False)

        if self.open_logs_dir not in r:
            r[self.open_logs_dir] = {}

        if self.date not in r[self.open_logs_dir]:
            r[self.open_logs_dir][self.date] = {}

        r[self.open_logs_dir][self.date][self.script_identifier_code] = {
            'script_name': self.script_name,
            'filename': "%s.%s" % (
                os.path.join(
                    conf.Application.AppDataLoc,
                    "Logs",
                    self.script_name,
                    AFDATA.Functions.time().strftime(for_log_name).replace(":", "-")
                ), protected_conf.Application.Logging.extention
            ),
            'time': AFDATA.Functions.time().strftime(for_log),
            'is_open': True
        }

        s = json.dumps(r, indent=4)
        AFFileIO(self._o.uid).secure_save(s, append=False)

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
            AFFileIO(self._o.uid).secure_save(s, append=False)

    def log(self, *data, empty_line: bool = False):
        """
        **AFLog.log**
        Will log _data (attempts to do so with 'PerformanceLogger,' if fails, will try to use 'ReliableLogger'

        :param data: _data
        :param empty_line: [bool] add an empty line [[NO AFDATA WILL BE LOGGED]] (optional)
        :return: None
        """

        self.refresh()
        print("Logging data")

        try:
            self.performance_logger.log(*data, empty_line=empty_line)
        except Exception as E:
            try:
                print(E)
                t = traceback.format_exc()
                self.reliable_logger.log(*data, e=t, empty_line=empty_line)
            except Exception as E:
                print("Failed to log data; E; TB; DATA:", E, traceback.format_exc(), ("\n\t".join(d for d in data)))

    def performance(self, *data, empty_line: bool = False):
        """
         **AFLog.performance**
         Will use 'PerformanceLogger'

        :param data: _data
        :param empty_line: [bool] add an empty line [[NO AFDATA WILL BE LOGGED]] (optional)
        :return: None
        """

        self.refresh()

        self.performance_logger.log(*data, empty_line=empty_line)

    def reliable(self, *data, e=None, empty_line: bool = False):
        """
         **AFLog.performance**
         Will use 'ReliableLogger'

        :param data: _data
        :param e: exception (optional)
        :param empty_line: [bool] add an empty line [[NO AFDATA WILL BE LOGGED]] (optional)
        :return: None
        """

        self.refresh()

        self.reliable_logger.log(*data, e=e, empty_line=empty_line)

    def change_io_instance(self, **kwargs):
        # self._o.edit_flag(**kwargs)
        self.performance_logger.change_log_file_kwargs(**kwargs)
        self.reliable_logger.change_log_file_kwargs(**kwargs)

    def __del__(self):
        # Cannot refer to outside functions freely

        # Will activate 'logger_req_clear' flag; next time 'AFLog' is called, all previous log desc. will be marked as 'closed.'

        log_cleaner.Actions.set_logger_req_clear()


if __name__ == "__main__" and protected_conf.dsb_mod_run_stdnalone:
    sys.exit(-1)

_SELF_LOG = AFLog("appfunctions-core", AFDATA.Functions.generate_uid())
_SELF_LOG.log("Started appfunctions script at '%s'" % datetime.now().strftime("%H:%M:%S"))
