import qa_conf as conf
root = "CMF::%s" % conf.Application.app_name.upper()


class ParameterException(Exception):
    def __init__(self, function_name, parameter_name, expected: str, rec: str, fatal: bool, var_code: str):
        self.args = (function_name, parameter_name, expected, rec, fatal, )
        self.var_code = str(conf.Exceptions.error_var_codes.get(var_code))
        self.msg = "Function/Class '%s' failed to function [%s] as a parameter inputted ('%s') expected '%s' as its input, but got '%s'" % \
                   (function_name, 'non-fatal' if not fatal else 'fatal', parameter_name, expected, rec)

    def __str__(self):
        global root
        return "%s:: %s (TECHNICAL_VAR_CODE=%s, NAME=%s)" % (root, self.msg, self.var_code, self.args[0])


class FileIOException(Exception):
    def __init__(self, function: str, *info, sep=" "):
        self.info = sep.join(str(i) for i in info) if len(info) > 0 else None
        self.function = function
        self.default = "Failed to run AFFileIO function '%s.'" % str(function)

    def __str__(self):
        global root
        return "%s:: %s (FUNCTION=%s)" % (root, self.info if type(self.info) is str else self.default, self.function)


class FileInstanceEXSException(Exception):
    def __init__(self, filename: str, *info, sep=" "):
        self.info = sep.join(str(i) for i in info) if len(info) > 0 else None
        self.filename = filename
        self.default = "Failed to create instance for file '%s'" % filename

    def __str__(self):
        global root
        return "%s:: %s (FILENAME=%s)" % (root, self.info if type(self.info) is str else self.default, self.filename)


class InitializationError(Exception):
    def __init__(self, class_name: str, *info, sep=" "):
        self.info = sep.join(str(i) for i in info) if len(info) > 0 else None
        self.class_name = class_name
        self.default = "Failed to initialize class '%s.'" % str(class_name)

    def __str__(self):
        global root
        return "%s:: %s (CLASS_NAME=%s)" % (root, self.info if type(self.info) is str else self.default, self.class_name)


class ReadOnlyIOObjectException(Exception):
    def __init__(self, uid: str, *info, sep=" "):
        self.info = sep.join(str(i) for i in info) if len(info) > 0 else None
        self.uid = uid
        self.default = "The AFIOObject you attempted to edit is marked as 'read_only'"

    def __str__(self):
        global root
        return "%s:: %s (UID=%s)" % (root, self.info if type(self.info) is str else self.default, self.uid)


class EncryptionException(Exception):
    def __init__(self, function_name: str, err_code_key: str, info: str = None):
        self.func_name = function_name
        self.errKey = err_code_key
        if type(info) is not str:
            self.info = "EncryptionException:: %s" % conf.Exceptions.error_var_codes[self.errKey]
        else:
            self.info = "EncryptionException:: %s (%s)" % (info, conf.Exceptions.error_var_codes[self.errKey])

    def __str__(self):
        global root
        return "%s:: %s (FUNC_NAME=%s)" % (root, self.info, self.func_name)

