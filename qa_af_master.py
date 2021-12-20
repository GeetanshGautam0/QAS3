import sys
from datetime import datetime
import qa_protected_conf as protected_conf

# The following are imported to allow legacy inheritance

from qa_af_module_AFIOObject import IOObjectModule as AFIOObject, IOOInterfaceModule as AFIOObjectInterface
import qa_af_module_AFData
from qa_af_module_AFIO import EncryptionModule as AFEncryption, FileIOModule as AFFileIO
from qa_af_module_AFLogging import LoggerModule as AFLog, _Loggers as AFLogger
from qa_af_module_AFJSON import JSONModule as AFJSON


self_data = qa_af_module_AFData.self_data
AFData = qa_af_module_AFData.DataModule


if __name__ == "__main__" and protected_conf.dsb_mod_run_stdnalone:
    sys.exit(-1)

_self_log = AFLog("app_functions-core", AFData.Functions.generate_uid())
_self_log.log('INFO', "Started app_functions script at '%s'" % datetime.now().strftime("%H:%M:%S"))