import qa_exceptions, qa_af_module_AFData, random, cryptography
from cryptography.fernet import Fernet
from qa_af_module_AFData import DataModule


self_data = qa_af_module_AFData.self_data


class IOObjectModule:
    def __init__(self, owr_exs_err_par_owr_meth: bool = False, *args, **kwargs):
        """
        **O_IOInstance:**
            * Will create an instance for any object/file you want
            * Allows seamless usage of all functions within the 'app_functions.py' script
            * Access 'UID' by getting the 'id' attribute from this instance.

        **Supported KWARGS**
            1. 'isFile':
                - type: boolean
                - default: false

            2. 'encoding':
                - type: str
                - default: 'DataModule.Data.defaults.encoding'

            3. 'encrypt':
                - type: boolean
                - default: false

            4. 'filename':
                - type: str
                - default: None

            5. 'enc_key':
                - type: bytes
                - default: DataModule.Data.defaults.enc_key
                - comments: This attribute controls the RSA encryption key that is used by all functions relating to the 'encrypt' flag.

            6. 're_type':
                - type: type [accepts bytes, str]
                - default: bytes
                - comments: 'Read Type:' Bytes / String

            7. 'lines_mode':
                - type: bool
                - default: false
                - comments: use 'read_lines' when reading (writing is automatic.)

        :keyword isFile [bool] Is this object a file? Def=False
        :keyword encoding [str] Data encoding Def=DataModule.Data.defaults['encoding']
        :keyword encrypt [bool] Encrypt data? Def=False
        :keyword filename [str] path to file Def=None
        :keyword enc_key [bytes] Key to encrypt data with Def=(default_key)
        :keyword re_type [type (str/bytes) Return type Def=bytes
        :keyword lines_mode [bool] Use 'read lines' and 'write lines' Def=False
        """
        global self_data
        self.flags_loaded = self.read_only = False
        self.flags_template = self_data.data['class']['AFIOObject']['flags_template']
        self.flags = self.protected_flags = {}
        self.protected_flags = {}
        self.valid_instance = True
        self.fer = None
        self._load_flags(kwargs)

        if self.flags['isFile']:
            if type(self.flags['filename']) is not str and 'DE_ENC_METH' not in args:
                raise TypeError(
                    "Expected type 'str' for flag 'filename;' got type %s" % str(type(self.flags['filename'])))

            self.filename = self.flags['filename']

        else:
            self.filename = None

        sel_uid = False

        if self_data.check_file_exs(self.filename)[0] and 'DE_ENC_METH' not in args:
            if not owr_exs_err_par_owr_meth and 'DE_ENC_METH':
                raise qa_exceptions.FileInstanceEXSException(self.filename)

            template = self_data.uid_instance_map[self_data.get_uid_from_filename(self.filename)][0]
            self.uid = template.uid
            sel_uid = True
            self_data.del_instance(self.uid)

        while not sel_uid:
            self.uid = DataModule.Functions.generate_uid(salt=-random.random())
            if not self_data.check_uid_exs(self.uid):
                sel_uid = True

        # ADD INSTANCE

        if self.flags['isFile']:
            self_data.add_file_instance(self.flags['filename'], self.uid, self, _owr_exs=False)

        else:
            self_data.add_non_file_instance(self.uid, self, _owr_exs=False)

    def _load_flags(self, user_in, template: dict = None) -> None:

        if self.read_only:
            raise Exception("This instance cannot be modified (set as read-only.)")

        if template is None:
            self.flags = DataModule.Functions.flags({**self.flags_template}, user_in)

        else:
            n_flags = DataModule.Functions.flags(template, user_in)
            for k, nv in n_flags.items():
                if k not in self.protected_flags:
                    self.flags[k] = nv
                else:
                    self.protected_flags[k] = nv

        self.flags['encoding'] = DataModule.Functions.check_blacklist(self.flags['encoding'],
                                                                      DataModule.Data.blacklists['encoding'],
                                                                      DataModule.Data.defaults['encoding'])
        self.flags['re_type'] = DataModule.Functions.check_blacklist(self.flags['re_type'], ["!!", [str, bytes]], str)

        if not self.flags_loaded:
            self.protected_flags = {'enc_key': self.flags['enc_key']}
            self.flags_loaded = True

        for _protected_flag in self.protected_flags:
            if _protected_flag in self.flags:
                self.flags.pop(_protected_flag)

        if self.flags['encrypt']:
            if type(self.protected_flags['enc_key']) is not bytes:

                raise TypeError(
                    "Expected type 'bytes' for flag 'enc_key;' got %s" % str(type(self.protected_flags['enc_key'])))

            elif len(self.protected_flags['enc_key']) != 44:
                raise cryptography.fernet.InvalidToken("Invalid token given for encryption key - Code INV_L_1")

            else:
                self.fer = Fernet(self.protected_flags['enc_key'])  # Will also work as a final check

        else:
            self.fer = None

    def delete_instance(self):
        if not self.valid_instance:
            raise qa_exceptions.ReadOnlyIOObjectException(self.uid)

        global self_data
        self.valid_instance = False
        self_data.del_instance(self.uid)

    def mark_read_only(self):
        self.read_only = True

    def edit_flag(self, **kwargs):
        if not self.valid_instance:
            raise Exception("This instance cannot be modified (invalid/deleted instance.)")

        if self.read_only:
            raise qa_exceptions.ReadOnlyIOObjectException(self.uid)

        template = {}
        for k, v in kwargs.items():
            if k in {**self.flags, **self.protected_flags}:
                template[k] = self.flags_template[k]
            else:
                raise AttributeError("Invalid flag name '%s'" % str(k))

        self._load_flags(kwargs, template)

    def __del__(self):
        pass


class IOOInterfaceModule:
    def __init__(self, uid: str) -> None:
        global self_data
        if uid not in self_data.uid_instance_map:
            raise qa_exceptions.InitializationError("AFIOObjectInterface", 'Invalid uid provided.')

        self.instance: IOObjectModule = self_data.uid_instance_map[uid][0]
        self.filename = self.instance.filename
        self.uid = uid
        self.isFile = self.instance.flags['isFile']
        self.re_type = self.instance.flags['re_type']
        self.lines_mode = self.instance.flags['lines_mode']
        self.encoding = self.instance.flags['encoding']
        self.encrypt = self.instance.flags['encrypt']
        self.pr_flags = self.instance.protected_flags
        self.IS_DE_ENC_METH_GEN = None
