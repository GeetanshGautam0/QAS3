import cryptography, qa_exceptions, os, traceback
from qa_af_module_AFIOObject import IOObjectModule as AFIOObject, \
    IOOInterfaceModule as AFIOObjectInterface
from qa_af_module_AFData import DataModule
import qa_af_module_AFData


self_data = qa_af_module_AFData.self_data


class EncryptionModule:
    def __init__(self, uid):
        global _self_log
        self.class_name = "ENC_MASTER"
        self.uid = uid
        self.instance = None
        self.raw_instance = None
        self.fernet: cryptography.fernet.Fernet = None
        self._nObject = None
        try:
            self.update_instance()
        except Exception as e:
            E = qa_exceptions.InitializationError(
                self.class_name,
                str(e)
            )

            try:
                if _self_log is not None:
                    _self_log.log('ERROR', self.class_name + ": " + E.__str__())
            except:
                pass

            raise E

    def update_instance(self):
        global _self_log

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
            E = qa_exceptions.EncryptionException(function_name, 'ENC.UPD.INV_FER', "Failed to create fernet: %s" % E)

            try:
                if _self_log is not None:
                    _self_log.log('ERROR', function_name + ": " + E.__str__())
            except:
                pass

            raise E

        return

    def decrypt(self, _raw, *args, **kwargs) -> bytes:
        global _self_log

        function_name = "ENC.DEC[RE,INP::F]"
        self.update_instance()

        E = None

        if None in [self.instance, self.raw_instance]:
            E = qa_exceptions.EncryptionException(function_name, 'ENC.DEC[RE,INP::F]::!INST[-0]')
        elif not self.instance.encrypt:
            E = qa_exceptions.EncryptionException(function_name, 'ENC.GLOBAL[G]::!ENC[-1]')
        elif self.fernet is None:
            E = qa_exceptions.EncryptionException(function_name, 'ENC.GLOBAL[G]::!FER[-0]')
        elif type(_raw) is not bytes:
            E = qa_exceptions.EncryptionException(function_name, 'ENC.GLOBAL[INP]::TP-RAW!:BYTES')

        if E is not None:
            try:
                if _self_log is not None:
                    _self_log.log('ERROR', function_name + ": " + E.__str__())
            except:
                pass

            raise E

        return self.fernet.decrypt(_raw)

    def encrypt(self, _data, *args, **kwargs) -> bytes:
        global _self_log

        function_name = "ENC.ENC[RE,INP::F]"
        self.update_instance()

        E = None

        if None in [self.instance, self.raw_instance]:
            E = qa_exceptions.EncryptionException(function_name, 'ENC.ENC[RE,INP::F]::!INST[-0]')
        elif not self.instance.encrypt:
            E = qa_exceptions.EncryptionException(function_name, 'ENC.GLOBAL[G]::!ENC[-1]')
        elif self.fernet is None:
            E = qa_exceptions.EncryptionException(function_name, 'ENC.GLOBAL[G]::!FER[-0]')
        elif type(_data) is not bytes:
            E = qa_exceptions.EncryptionException(function_name, 'ENC.GLOBAL[INP]::TP-RAW!:BYTES')

        if E is not None:
            try:
                if _self_log is not None:
                    _self_log.log('ERROR', function_name + ": " + E.__str__())
            except:
                pass

            raise E

        return self.fernet.encrypt(_data)

    def _encFile(self, *args, **kwargs) -> None:  # ENC.HDN_EN_FILE_OWR
        global _self_log

        function_name = 'ENC.HDN_EN_FILE_OWR'
        self.update_instance()
        E = None
        if not self.instance.isFile:
            E = qa_exceptions.FileIOException(function_name, "Invalid AFIOObject supplied.")
        elif not self.instance.encrypt:
            E = qa_exceptions.EncryptionException(function_name, 'ENC.GLOBAL[G]::!ENC[-1]')
        elif self.raw_instance.fernet is None:
            E = qa_exceptions.EncryptionException(function_name, 'ENC.GLOBAL[G]::!FER[-0]')
        elif not os.path.exists(self.instance.filename):
            return

        if E is not None:
            try:
                if _self_log is not None:
                    _self_log.log('ERROR', function_name + ": " + E.__str__())
            except:
                pass

            raise E

        # Used tuples rather than lists as an optimization
        #       - Tuples are faster than lists for larger _data sets.
        self._nObject.edit_flag(lines_mode=True)
        _raw = (*FileIOModule(self._nObject.uid).load_file(),)
        _c = ()

        for _line in _raw:
            try:
                _c = (*_c, self.decrypt(_line))
            except:
                _c = (*_c, _line)

        _c = (*_c,)
        _enc = ()
        for _line in _c:
            _l = b""
            if type(_line) is bytes:
                _l = _line

            elif type(_line) is str:
                _l = _line.encode(self.instance.encoding)

            elif type(_line) in [list, tuple, set]:
                _l = (DataModule.Functions.recursive_list_conversion(_line)).encode(self.instance.encoding)

            elif type(_line) is dict:
                _l = (DataModule.Functions.recursive_dict_conversion(_line)).encode(self.instance.encoding)

            _enc = (*_enc, _l.strip(), "\n".encode(self.instance.encoding))

        _enc = "".encode(self.instance.encoding).join(_item for _item in _enc)
        _enc = self.encrypt(_enc)

        FileIOModule(self.uid).secure_save(_enc, 'DE_ENC_METH', append=False)

    def _decFile(self, *args, **kwargs) -> None:  # ENC.HDN_DE_FILE_OWR
        global _self_log

        function_name = 'ENC.HDN_DE_FILE_OWR'
        self.update_instance()

        E = None

        if not self.instance.isFile:
            E = qa_exceptions.FileIOException(function_name, "Invalid AFIOObject supplied.")
        elif not self.instance.encrypt:
            E = qa_exceptions.EncryptionException(function_name, 'ENC.GLOBAL[G]::!ENC[-1]')
        elif self.raw_instance.fernet is None:
            E = qa_exceptions.EncryptionException(function_name, 'ENC.GLOBAL[G]::!FER[-0]')
        elif not os.path.exists(self.instance.filename):
            return

        if E is not None:
            try:
                if _self_log is not None:
                    _self_log.log('ERROR', function_name + ": " + E.__str__())
            except:
                pass

            raise E

        # Used tuples rather than lists as an optimization
        #       - Tuples are faster than lists for larger _data sets.
        self._nObject.edit_flag(lines_mode=False)
        _raw = FileIOModule(self.instance.uid).load_file('cbr')  # Load file with 'cbr' flag
        self._nObject.edit_flag(lines_mode=True)

        _dec = self.decrypt(_raw)

        FileIOModule(self.uid).secure_save(_dec, 'DE_ENC_METH', append=False)

        return

    def __del__(self):
        pass


class FileIOModule:
    def __init__(self, uid: str):
        global self_data, _self_log
        self.class_name = "AFFileIO"
        function_name = "FIO_INIT"

        self.uid = uid
        if uid not in self_data.uid_instance_map:
            E = qa_exceptions.InitializationError(
                self.class_name,
                'Invalid input for parameter \'uid\''
            )

            try:
                if _self_log is not None:
                    _self_log.log('ERROR', function_name + ": " + E.__str__())
            except:
                pass

            raise E

        self.file: AFIOObjectInterface = object
        self.update_instance()

        if not self.file.isFile:
            E = qa_exceptions.InitializationError(self.class_name,
                                               "Invalid instance uid provided: parameter 'isFile' is invalid.")

            try:
                if _self_log is not None:
                    _self_log.log('ERROR', function_name + ": " + E.__str__())
            except:
                pass

            raise E

        elif type(self.file.filename) is not str:
            E = qa_exceptions.InitializationError(self.class_name,
                                               "Invalid instance uid provided: parameter 'filename' is invalid.")

            try:
                if _self_log is not None:
                    _self_log.log('ERROR', function_name + ": " + E.__str__())
            except:
                pass

            raise E

    def update_instance(self):  # FIO_UPD_INST
        function_name = "FIO_UPD_INST"
        self.file = AFIOObjectInterface(self.uid)  # instance translator

    def save(self, _data, **kwargs):  # FIO_NR_SAVE
        """
        **appfunctions.AFFIleIO.save**


        :param _data: data to save
        :param kwargs: kw args
        :keyword append append new data
        :keyword separator separator used between new lines (list, tuple, set, dict)
        :keyword dict_kv_sep separator used between dict key(s) and value(s)
        :keyword strip_data strip data before saving
        :return: None
        """

        global _self_log

        assert not self.file.instance._read_only, "Cannot save to this file; marked as 'read_only'"

        function_name = "FIO_NR_SAVE"
        self.update_instance()

        flags = {
            'append': [False, True, True],
            'separator': ['\n', True, True],
            'dict_kv_sep': [' ', True, True],
            'strip_data': [True, True, True]
        }
        flags = DataModule.Functions.flags(flags, kwargs)

        flags['separator'] = flags['separator'].encode(self.file.encoding)
        flags['dict_kv_sep'] = flags['dict_kv_sep'].encode(self.file.encoding)

        if not self.file.isFile:
            E = qa_exceptions.FileIOException(function_name)

            try:
                if _self_log is not None:
                    _self_log.log('ERROR', function_name + ": " + E.__str__())
            except:
                print('[ERROR]', function_name + ": " + E.__str__())

            raise E

        if not os.path.exists(self.file.filename):
            with open(self.file.filename, 'x') as file:
                file.close()

        if type(_data) is str:
            new_data: bytes = _data.encode(self.file.encoding)

        elif type(_data) is bytes:
            cenco = DataModule.Functions.check_encoding(_data, True)
            if cenco != self.file.encoding:
                new_data = _data.decode(cenco).encode(self.file.encoding)
            else:
                new_data = _data

        elif type(_data) in [list, tuple, set]:
            new_data = DataModule.Functions.recursive_list_conversion(_data, flags['separator'],
                                                                  flags['dict_kv_sep']).encode(
                self.file.encoding)

        elif type(_data) is dict:
            new_data = DataModule.Functions.recursive_dict_conversion(_data, flags['separator'],
                                                                  flags['dict_kv_sep']).encode(
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
            except qa_exceptions.ParameterException:
                dataToSave = flags['separator'] + new_data

        dataToSave = dataToSave.rstrip()

        with open(self.file.filename, 'wb') as file:
            file.write(dataToSave)
            file.close()

    def secure_save(self, _data, *flag_args, **kwargs):  # FIO_SC_SAVE
        global self_data, _self_log
        function_name = "FIO_SC_SAVE"

        self.update_instance()
        if not self.file.isFile:
            E = qa_exceptions.FileIOException(function_name)

            try:
                if _self_log is not None:
                    _self_log.log('ERROR', function_name + ": " + E.__str__())
            except:
                print('[ERROR]', function_name + ": " + E.__str__())

            raise E

        flags = {
            'append': [False, True, True],
            'separator': ['\n', True, True],
            'dict_kv_sep': [' ', True, True],
            'strip_data': [True, True, True],
            'delete_backup_after': [True, True, True]
        }
        flags = DataModule.Functions.flags(flags, kwargs)

        flags['separator'] = flags['separator'].encode(self.file.encoding)
        flags['dict_kv_sep'] = flags['dict_kv_sep'].encode(self.file.encoding)

        # Method Structure:
        # Step 1: Create Backup
        # Step 2: Store Backup to file
        # Step 3: Save New Data ([+] encryption)
        #   3-1: If OK, delete backup (FLAGGED)
        #   3-2: Else, restore backup
        #       - Then delete backup [optional w/ `delete_backup_after`]

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
                # READ + WRITE BACKUP IN BYTES ONLY

                with open(self.file.filename, 'rb') as file:
                    _backup_data = file.read()
                    file.close()

            except:
                E = qa_exceptions.FileIOException(function_name,
                                               "Failed to load backup _data; aborting operation for safety.")

                try:
                    if _self_log is not None:
                        _self_log.log('ERROR', function_name + ": " + E.__str__())
                except:
                    print('[ERROR]', function_name + ": " + E.__str__())

                raise E

            time = DataModule.Functions.time().strftime('%d%m%y%S%f%z%Z%j')
            _backup_file_name = self_data.apploc + "\\Temporary Files\\AFFileIO\\%s\\%s\\%s.cmfbackup" % (
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
                E = qa_exceptions.FileIOException(function_name,
                                               "Failed to save temporary backup; aborting operation for safety.")

                try:
                    if _self_log is not None:
                        _self_log.log('ERROR', function_name + ": " + E.__str__())
                except:
                    print('[ERROR]', function_name + ": " + E.__str__())

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
                    EncryptionModule(self.uid)._encFile()

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
                            if _self_log is not None:
                                _self_log.log('ERROR', function_name + ": _br.strip() != _backup_data.strip() (P_B_R)")

                        except Exception as E:
                            print('[ERROR]', function_name + ": " + E.__str__())

                        raise Exception  # Passes on to the exception handler (1)

                except:
                    E = qa_exceptions.FileIOException(
                        function_name,
                        "FAILED TO SAVE BACKUP [FATAL] [CRITICAL]"
                    )

                    try:
                        if _self_log is not None:
                            _self_log.log('ERROR', function_name + ": " + E.__str__())
                    except:
                        print('[ERROR]', function_name + ": " + E.__str__())

                    raise E

                else:
                    E = qa_exceptions.FileIOException(
                        function_name,
                        "Failed to save _data (restored backup.) :: %s" % traceback.format_exc()
                    )

                    try:
                        if _self_log is not None:
                            _self_log.log('ERROR', function_name + ": " + E.__str__())
                    except:
                        print('[ERROR]', function_name + ": " + E.__str__())

                    raise E

            # Delete backup file after (optional)
            if flags['delete_backup_after']:
                os.remove(_backup_file_name)

        return

    def read_file(self) -> str:  # FIO_RD_FILE
        global _self_log

        function_name = "FIO_RD_FILE"
        self.update_instance()
        if not os.path.exists(self.file.filename) or not self.file.isFile:
            E = qa_exceptions.FileIOException(function_name, "File '%s' does not exist." % self.file.filename)

            try:
                if _self_log is not None:
                    _self_log.log('ERROR', function_name + ": " + E.__str__())
            except:
                pass

            raise E

        raw = self.load_file('cbr')
        # print('[1]', raw)
        if self.file.encrypt:
            try:
                raw = EncryptionModule(self.uid).decrypt(raw)
                # print('[2.1]', raw)
            except qa_exceptions.EncryptionException as E:
                print(function_name, '[E1.2]', E)
                raw = raw
                # print('[2.2]', raw)
            except cryptography.fernet.InvalidToken as E:
                print(function_name, '[E1.3]', E)
                raw = raw
                # print('[2.3]', raw)
            except Exception as E:
                E = E.__class__(str(E))

                try:
                    if _self_log is not None:
                        _self_log.log('ERROR', function_name + ": " + E.__str__())
                except:
                    pass

                raise E

        # print('[3]', raw)

        if type(raw) is bytes:
            if len(raw) > 0:
                enco = DataModule.Functions.check_encoding(raw, True)
                Str = raw.decode(enco)
            else:
                Str = ""

        else:
            Str = raw

        # print('[4]', type(raw) is bytes, Str)

        return Str

    def load_file(self, *flags):  # FIO_LD_FILE
        global _self_log

        self.update_instance()
        function_name = "FIO_LD_FILE"

        if not os.path.exists(self.file.filename) or not self.file.isFile:
            E = qa_exceptions.FileIOException("FIO_LD_FILE", "File '%s' does not exist." % self.file.filename)

            try:
                if _self_log is not None:
                    _self_log.log('ERROR', function_name + ": " + E.__str__())
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
        global _self_log

        self.update_instance()
        function_name = "FIO_CLEAR"

        if not os.path.exists(self.file.filename) or not self.file.isFile:
            E = qa_exceptions.FileIOException(function_name, "File '%s' does not exist." % self.file.filename)

            try:
                if _self_log is not None:
                    _self_log.log('ERROR', function_name + ": " + E.__str__())
            except:
                pass

            raise E

        with open(self.file.filename, 'w') as file:
            file.close()
