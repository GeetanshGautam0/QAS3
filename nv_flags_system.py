import os, conf

_p = [conf.Application.AppDataLoc, '.appdata', '.boot_flags']


class FlagsLookup:
    logging = {
        'log_cleaner': {
            'request clear': '_logger_req_clear'
        }
    }


class FlagsIO:
    @staticmethod
    def create(name):
        global _p

        n = os.path.join(*_p, name.split('.')[0]).strip()
        if not os.path.exists(os.path.join(*_p)):
            os.makedirs(os.path.join(*_p))

        if not os.path.exists(n):
            os.system("fsutil file createNew \"%s\" 0" % n)

    @staticmethod
    def check(name):
        n = os.path.join(*_p, name.split('.')[0]).strip()
        return os.path.exists(n)

    @staticmethod
    def delete(name):
        n = os.path.join(*_p, name.split('.')[0]).strip()
        if os.path.exists(n):
            os.remove(n)

