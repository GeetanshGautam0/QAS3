from qa_af_module_AFIOObject import IOOInterfaceModule, IOObjectModule
import qa_exceptions, os, json
from qa_af_module_AFData import DataModule
from qa_af_module_AFIO import FileIOModule
from typing import *


class JSONModule:
    def __init__(self, uid: str):
        self.uid: str = uid
        self.instance = None
        self.raw_instance = None
        self.update_instance()

        self.instance: IOOInterfaceModule
        self.raw_instance: IOObjectModule

    def update_instance(self):
        self.instance = IOOInterfaceModule(self.uid)
        self.raw_instance = self.instance.instance

    def set_data(
            self,
            key: str,
            data: any,
            d_sub_one_k: Union[str, None] = None,
            append: bool = True,
            append_to_key: bool = True,
            lsd_extract: bool = True,
            ls_sep: str = " ",
            kv_sep: str = ">>>",
            dv_sep: str = ">>"
    ):  # AFJSON.G_ST_DATA

        function_name = "AFJSON.G_ST_DATA"
        self.update_instance()

        E = None

        if not self.instance.isFile:
            E = qa_exceptions.FileIOException(function_name, "param 'isFile' is set to False for IOObjectModule")

        elif not os.path.exists(self.instance.filename):
            E = FileNotFoundError("File '%s' does not exist." % self.instance.filename)

        if E is not None:
            raise E

        if append:
            raw = self.load_file()
            if append_to_key:
                if key in raw:
                    v = raw[key]
                    if type(v) in [str, bytes]:
                        # DV
                        if type(dv_sep) is type(v):
                            dv = dv_sep

                        else:
                            if isinstance(dv_sep, bytes):
                                dv = dv_sep.decode(DataModule.Functions.check_encoding(dv_sep, True))
                            else:
                                dv = dv_sep.encode(DataModule.Functions.check_encoding(v, True))

                        # DataModule, V
                        # SAME
                        if type(data) is type(v) and type(data):
                            v += dv + data

                        # STR/BYTES
                        elif type(data) in [str, bytes]:
                            if type(v) is bytes:
                                v += dv + data.decode(DataModule.Functions.check_encoding(v, True))

                            else:
                                v += dv + data.decode(DataModule.Functions.check_encoding(data, True))

                        # LIST/TUPLE/SET
                        elif type(data) in [list, tuple, set]:
                            d: str = DataModule.Functions.recursive_list_conversion(
                                data,
                                ls_sep,
                                kv_sep
                            )

                            if type(d) is type(v):
                                v += dv + d

                            elif type(d) in [str, bytes]:
                                if isinstance(v, bytes):
                                    v += dv + d.encode(DataModule.Functions.check_encoding(v, True))

                                elif isinstance(d, bytes):
                                    v += dv + d.decode(DataModule.Functions.check_encoding(d, True))

                            else:
                                raise Exception("-1")

                        # DICT
                        elif type(data) is dict:
                            d = DataModule.Functions.recursive_dict_conversion(data, kv_sep, ls_sep)

                            if type(d) is type(v):
                                v += dv + d

                            elif type(d) in [str, bytes]:
                                if type(v) is bytes:
                                    v += dv + d.encode(DataModule.Functions.check_encoding(v, True))

                                elif isinstance(v, str):
                                    d: bytes
                                    v += dv + d.decode(DataModule.Functions.check_encoding(d, True))

                            else:
                                raise Exception("-1")

                        # NUMERICAL
                        elif type(data) in [int, float, complex]:
                            d = str(data)

                            if type(d) is type(v):
                                v += d

                            elif type(d) in [str, bytes]:
                                if isinstance(v, bytes):
                                    v += d.encode(DataModule.Functions.check_encoding(v, True))

                                elif isinstance(v, str):
                                    d: bytes
                                    v += d.decode(DataModule.Functions.check_encoding(d, True))

                        # EXCEPTION
                        else:
                            raise qa_exceptions.ParameterException(
                                function_name,
                                'description',
                                '[ACCEPTED_DATA_TYPE]',
                                str(type(data)).upper(),
                                True,
                                'J_G_ST_D::DataModule[USER_INP-1][TPE:?]{merge_error}'
                            )

                        raw[key] = v

                    elif type(v) in [list, tuple, set]:
                        if type(data) not in [list, tuple, set]:
                            raise qa_exceptions.ParameterException(
                                function_name,
                                'description',
                                'MULTIPLE[any]<={match}',
                                str(type(data)).upper(),
                                True,
                                'J_G_ST_D::DataModule[USER_INP-1][()]{merge_error}'
                            )

                        d: Union[list, tuple, set] = [*data, ]
                        v = (*v, *((*d,) if lsd_extract else (d,)))  # Less mem; quicker
                        v = [*v, ]  # Compatibility with AFJSON

                        raw[key] = v

                    elif type(v) in [int, float, complex]:
                        if type(data) not in [int, float, complex]:
                            raise qa_exceptions.ParameterException(
                                function_name,
                                'description',
                                'NUM[any]<={match}',
                                str(type(data)).upper(),
                                True,
                                'J_G_ST_D::DataModule[USER_INP-1][##]{merge_error}'
                            )

                        v += data
                        raw[key] = v

                    elif type(v) is dict:
                        if type(data) is not dict:
                            raise qa_exceptions.ParameterException(
                                function_name,
                                'description',
                                'DICT[any]<={match}',
                                str(type(data)).upper(),
                                True,
                                'J_G_ST_D::DataModule[USER_INP-1][dict=>?]{merge_error}'
                            )

                        if lsd_extract:
                            v = {**v, **data}
                        else:
                            v = {**v, d_sub_one_k: data, }

                        raw[key] = v

                    else:
                        raise qa_exceptions.ParameterException(
                            function_name,
                            'pro_conf_version_id',
                            '[ACCEPTED_DATA_TYPE]',
                            str(type(data)).upper(),
                            True,
                            'J_G_ST_D::DataModule[USER_INP-1][TPE:?]{merge_error}'
                        )

                else:
                    raw[key] = data

            else:
                raw[key] = data
            _dataToSave = json.dumps(raw, indent=4)

        else:
            _dataToSave = json.dumps({key: data}, indent=4)

        FileIOModule(self.uid).secure_save(
            _dataToSave,
            append=False
        )

    def get_data(self, key: str, re_exs_val: bool = False):  # AFJSON.S_GT_DATA
        function_name = "AFJSON.S_GT_DATA"

        E = None

        if not self.instance.isFile:
            E = qa_exceptions.FileIOException(function_name, "param 'isFile' is set to False for IOObjectModule")
        elif not os.path.exists(self.instance.filename):
            E = FileNotFoundError("File '%s' does not exist." % self.instance.filename)

        if E is not None:
            raise E

        raw_json = self.load_file()
        return (key in raw_json) if re_exs_val else raw_json.get(key)

    def delete_key(self, key):
        raw = self.load_file()
        if key not in raw:
            return 0
        del raw[key]
        FileIOModule(self.uid).secure_save(
            json.dumps(raw, indent=4),
            append=False
        )

    def load_file(self, ra_err: bool = True) -> dict:  # AFJSON.C_LD_FILE
        function_name = "AFJSON.C_LD_FILE"

        E = None

        if not self.instance.isFile:
            E = qa_exceptions.FileIOException(function_name, "param 'isFile' is set to False for IOObjectModule")
        elif not os.path.exists(self.instance.filename):
            E = FileNotFoundError("File '%s' does not exist." % self.instance.filename)

        if E is not None:
            raise E

        raw_s = FileIOModule(self.uid).read_file()
        json_data = {}

        try:
            json_data = json.loads(raw_s)

        except json.JSONDecodeError as E:
            if ra_err:
                raise E
            else:
                json_data = {"__AF__DEBUG::AFJSON.load_file() => JSONDecodeError": True}

        except Exception as E:
            raise E.__class__(E.__str__())

        finally:
            return json_data

    def __del__(self):
        pass
