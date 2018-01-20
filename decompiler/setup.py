from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

snowman = Extension('snowman',
                    define_macros = [('MAJOR_VERSION', '1'),
                                     ('MINOR_VERSION', '0'),
                                     # get around automake
                                     ('PACKAGE', 1),
                                     ('PACKAGE_VERSION', 1)],
                    include_dirs = [
                    ],
                    libraries = [
                        'pysnowman',
                    ],
                    library_dirs = [
                        '../build/pysnowman',
                    ],
                    sources = ['snowman.pyx'])

setup (name = 'Snowman Decompiler',
       version = '1.0',
       description = 'Python wrapper for the Snowman decompiler',
       author = 'Anthony DeRosa',
       author_email = 'Anthony@onlinedisassembler.com',
       url = '',
       long_description = '''Access to Snowman from Python''',
       cmdclass = {'build_ext': build_ext},
       ext_modules = [snowman])
