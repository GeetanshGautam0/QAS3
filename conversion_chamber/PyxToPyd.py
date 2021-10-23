from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
from Cython.Build import cythonize

name = "appfunctions.pyx"

directives = {'linetrace': False, 'language_level': 3}
setup(
    ext_modules=cythonize(name)
)

#### RUN "python setup.py build_ext --inplace"
