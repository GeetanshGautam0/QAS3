import sys
from datetime import datetime
import qa_protected_conf as protected_conf

# The following are imported and defined to allow legacy inheritance

import qa_af_module_AFIOObject
import qa_af_module_AFData
import qa_af_module_AFIO
import qa_af_module_AFLogging
from qa_af_module_AFJSON import JSONModule as AFJSON


self_data = qa_af_module_AFData.self_data
AFData = qa_af_module_AFData.DataModule

AFLog = qa_af_module_AFLogging.LoggerModule
AFLogger = qa_af_module_AFLogging._Loggers

AFEncryption = qa_af_module_AFIO.EncryptionModule
AFFileIO = qa_af_module_AFIO.FileIOModule

AFIOObject = qa_af_module_AFIOObject.IOObjectModule
AFIOObjectInterface = qa_af_module_AFIOObject.IOOInterfaceModule


if __name__ == "__main__" and protected_conf.dsb_mod_run_stdnalone:
    sys.exit(-1)

_self_log = AFLog("app_functions-core", AFData.Functions.generate_uid())
_self_log.log('INFO', "Started app_functions script at '%s'" % datetime.now().strftime("%H:%M:%S"))

# TODO: Sync. all self_data instances
# qa_af_module_AFLogging
# qa_af_module_AFIO
# qa_af_module_AFIOObject


def synchronize_data(master_module, *slave_modules):
    for module in slave_modules:
        try:
            module.self_data = master_module.self_data
            _self_log.log('INFO', f'Synchronized {module} and {master_module} (master)', print_d=True)
        except Exception as E:
            _self_log.log('WARNING', f'Failed to sync. {module} and {master_module} (master): {E}', print_d=True)

    return


synchronize_data(qa_af_module_AFData, qa_af_module_AFData, qa_af_module_AFIO, qa_af_module_AFLogging)
