import hashlib, random
from datetime import datetime
import qa_conf, qa_std, qa_exceptions
from tkinter import messagebox as tkmsb
import tkinter as tk


class DataModule:
    class Data:
        defaults = {
            'container_title': qa_conf.AppContainer.general_title,
            'encoding': 'utf-8',
            'enc_key': qa_conf.Encryption.key,
            'class': {
                'AFIOObject': {}
            }
        }

        prompts = {
            'ync': {
                'D_AFI_OWR_EXS:FALSE_EXS:TRUE': """Undefined behaviour encountered:
DataModule.AFI.OWR_EXS=FALSE && EXS=TRUE

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
            self.apploc = qa_conf.Application.AppDataLoc

        def add_file_instance(self, filename: str, uid: str, instance: object, _owr_exs: bool = True) -> None:
            function_name = "ScDATA_AD_F_INST"
            if _owr_exs or uid not in self.uid_instance_map:
                self.uid_instance_map[uid] = [instance, filename]
                self.instances.append(instance)

            elif uid in self.uid_instance_map:
                r = tk.Tk()
                r.withdraw()
                confirmation = tkmsb.askyesno(
                    DataModule.Data.defaults['container_title'],
                    DataModule.Data.prompts['ync']['D_AFI_OWR_EXS:FALSE_EXS:TRUE']
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
                    DataModule.Data.defaults['container_title'],
                    DataModule.Data.prompts['ync']['D_AFI_OWR_EXS:FALSE_EXS:TRUE']
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
            return datetime.now()

        @staticmethod
        def generate_uid(salt=0.00) -> str:
            I = str(random.randint(100000000000000, 999999999999999)) + "." + \
                str(random.random() * (random.random() * 10 ** 5)) + \
                "." + str(random.random() * random.randint(0, 9)) + ":" + \
                str(random.random() * salt)
            _time = datetime.now().strftime(f"%d:%m:%Y:%H:%M:%S:%f::%z::%j--{str(salt)}-%X")
            _rs = ["~~", "1~", "`@", "3~@", "#@~", "$%@~"]
            _o0 = _time + I + _rs[random.randint(0, len(_rs) - 1)]
            _o1 = hashlib.sha3_512(_o0.encode()).hexdigest()  # Because hashed hex looks better.

            del I, _time, _rs, _o0
            return _o1

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
                    E = qa_exceptions.ParameterException(
                        function_name,
                        'USER_IN_DICT[DICT]',
                        'FUNC_DESC_TYPE[ANY--ANY]: NAME_ERROR',
                        str(flag),
                        True,
                        'DataModule.Functions.flags::flag[name_error]'
                    )

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

            return _output

        @staticmethod
        def check_blacklist(user_in: any, template: list, default: any) -> any:
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

            if ok:
                return user_in
            else:
                return default

        @staticmethod
        def check_encoding(data: bytes, use_default: bool, lst=('utf-8',)):
            function_name = "FUN_C_ENCO_NAME"
            global _SELF_LOG

            if use_default:
                lst = (*DataModule.Data.encoding_lookup,)

            if len(lst) < 0:
                E = qa_exceptions.ParameterException(
                    function_name,
                    'lst',
                    'LIST[LEN>0]',
                    'LIST[LEN<=0]',
                    True,
                    'DataModule.Data.check_encoding::lst'
                )

                try:
                    if _SELF_LOG is not None:
                        _SELF_LOG.log('ERROR', function_name + ": " + E.__str__())
                except:
                    pass

                raise E

            elif type(data) is not bytes:
                E = qa_exceptions.ParameterException(
                    function_name,
                    '_data',
                    'BYTES[LEN>0]',
                    str(type(data)).upper(),
                    True,
                    'DataModule.Data.check_encoding::_data'
                )

                try:
                    if _SELF_LOG is not None:
                        _SELF_LOG.log('ERROR', function_name + ": " + E.__str__())
                except:
                    pass

                raise E

            elif len(data) <= 0:
                E = qa_exceptions.ParameterException(
                    function_name,
                    '_data',
                    'BYTES[LEN>0]',
                    'BYTES[LEN<=0]',
                    True,
                    'DataModule.Data.check_encoding::_data[1]'
                )

                try:
                    if _SELF_LOG is not None:
                        _SELF_LOG.log('ERROR', function_name + ": " + E.__str__())
                except:
                    pass

                raise E

            for encoding in lst:
                if type(encoding) is str and encoding not in (enco[-1] for enco in DataModule.Data.blacklists['encoding']):
                    try:
                        data.decode(encoding)
                    except:
                        pass
                    else:
                        return encoding

                else:
                    E = qa_exceptions.ParameterException(
                        function_name,
                        'lst >>> gen >>> ENCODING',
                        'STR[ENCO, !in_D.D.BLKLST.ENCO(s)]',
                        'STR[in_D.D.BLKLST.ENCO(s)] || !STR (\'{}\')'.format(encoding),
                        True,
                        'DataModule.Data.check_encoding::lst>>gen>>encoding'
                    )

                    try:
                        if _SELF_LOG is not None:
                            _SELF_LOG.log('ERROR', function_name + ": " + E.__str__())
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
                E = qa_exceptions.ParameterException(
                    function_name,
                    '_data',
                    'LIST||TUPLE[ANY, LEN>0]',
                    str(type(_data)).upper(),
                    True,
                    'DataModule.Data.recursive_list_conversion::_data[0]'
                )

                try:
                    if _SELF_LOG is not None:
                        _SELF_LOG.log('ERROR', function_name + ": " + E.__str__())
                except:
                    pass

                raise E

            _data = (*_data,)

            if len(_data) <= 0:
                E = qa_exceptions.ParameterException(
                    function_name,
                    '_data',
                    'LIST||TUPLE[ANY, LEN>0]',
                    'LIST||TUPLE[LEN<=0]',
                    True,
                    'DataModule.Data.recursive_list_conversion::_data[1]'
                )

                try:
                    if _SELF_LOG is not None:
                        _SELF_LOG.log('ERROR', function_name + ": " + E.__str__())
                except:
                    pass

                raise E

            _output_comp = []

            for item in _data:
                if type(item) in [list, tuple, set]:
                    _output_comp.append(DataModule.Functions.recursive_list_conversion(item, sep, kv_sep))
                elif type(item) is str:
                    _output_comp.append(item.strip())
                elif type(item) is bytes:
                    _output_comp.append(item.decode(DataModule.Functions.check_encoding(item, True)).strip())
                elif type(item) is dict:
                    _output_comp.append(DataModule.Functions.recursive_dict_conversion(item, sep, kv_sep))
                elif type(item) in [int, float]:
                    _output_comp.append(str(item))

            _sample = _output_comp[0]

            if type(_sample) is bytes and type(sep) is str:
                sep2use = sep.encode(DataModule.Functions.check_encoding(_sample, True))

            elif isinstance(_sample, str) and isinstance(sep, bytes):
                sep2use = sep.decode(DataModule.Functions.check_encoding(sep, True))

            else:
                sep2use = sep

            return sep2use.join(_line for _line in _output_comp)

        @staticmethod
        def recursive_dict_conversion(data, kv_sep: str = " ", sep: str = "\n") -> str:  # DataModule.Data.RDConv
            function_name = "FUNC_REC_CON_F_DICT"
            global _SELF_LOG

            # Error conditions
            if type(data) is not dict:
                E = qa_exceptions.ParameterException(
                    function_name,
                    '_data',
                    'DICT[ANY, LEN::ANY]',
                    str(type(data)).upper(),
                    True,
                    'DataModule.Data.recursive_dict_conversion::_data[0]'
                )

                try:
                    if _SELF_LOG is not None:
                        _SELF_LOG.log('ERROR', function_name + ": " + E.__str__())
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
                    k = DataModule.Functions.recursive_list_conversion(key, sep, kv_sep)
                elif type(key) is dict:
                    k = DataModule.Functions.recursive_dict_conversion(key, sep, kv_sep)
                elif type(key) is str:
                    k = key.strip()
                elif type(key) is bytes:
                    k = key.decode(DataModule.Functions.check_encoding(key, True)).strip()
                elif type(key) in [int, float]:
                    k = str(key)

                # Value
                if type(value) in [list, tuple, set]:
                    v = DataModule.Functions.recursive_list_conversion(value, sep, kv_sep)
                elif type(value) is dict:
                    v = DataModule.Functions.recursive_dict_conversion(value, sep, kv_sep)
                elif type(value) is str:
                    v = value.strip()
                elif type(value) is bytes:
                    v = value.decode(DataModule.Functions.check_encoding(value, True)).strip()
                elif type(value) in [int, float]:
                    v = str(value)

                output_comp.append(f"%s%s%s" % (k, kv_sep, v))

            output: str = sep.join(new for new in output_comp)
            return output


self_data = DataModule.ScriptData()
self_data.data['class']['AFIOObject']['flags_template'] = {
    'isFile': [False, True, True],
    'encoding': [DataModule.Data.defaults['encoding'], True, True],
    'encrypt': [False, True, True],
    'filename': [None, str, False, True],
    'enc_key': [DataModule.Data.defaults['enc_key'], True, True],
    're_type': [bytes, True, True],
    'lines_mode': [False, True, True]
}
