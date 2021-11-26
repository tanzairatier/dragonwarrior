from distutils.core import setup
import py2exe, pygame, numpy, sys, glob, os

sys.argv.append('py2exe')

def find_data_files(source,target,patterns):
    """Locates the specified data-files and returns the matches
    in a data_files compatible format.

    source is the root of the source data tree.
        Use '' or '.' for current directory.
    target is the root of the target data tree.
        Use '' or '.' for the distribution directory.
    patterns is a sequence of glob-patterns for the
        files you want to copy.
    """
    if glob.has_magic(source) or glob.has_magic(target):
        raise ValueError("Magic not allowed in src, target")
    ret = {}
    for pattern in patterns:
        pattern = os.path.join(source,pattern)
        for filename in glob.glob(pattern):
            if os.path.isfile(filename):
                targetpath = os.path.join(target,os.path.relpath(filename,source))
                path = os.path.dirname(targetpath)
                ret.setdefault(path,[]).append(filename)
    return sorted(ret.items())


os.system("rmdir /s /q dist")

origIsSystemDLL = py2exe.build_exe.isSystemDLL # save the orginal before we edit it
def isSystemDLL(pathname):
    # checks if the freetype and ogg dll files are being included
    if os.path.basename(pathname).lower() in ("libfreetype-6.dll", "libogg-0.dll", "sdl_ttf.dll"):
            return 0
    return origIsSystemDLL(pathname) # return the orginal function
py2exe.build_exe.isSystemDLL = isSystemDLL # override the default function with this one


setup(
    windows = [{'script': "game.py"}],
    zipfile = None,
    data_files=find_data_files('C:\Users\Joe\PycharmProjects\dragonwarrior/', '', ['images/*', 'images/enemies/*', 'spritesheets/*', 'tiles/*', 'fonts/*', 'music/*']),
    options={'py2exe': dict(excludes=['_ssl', 'numpy', 'scipy'],  # Exclude standard library
                            dll_excludes=['msvcr71.dll', 'w9xpopen.exe',
                                          'API-MS-Win-Core-LocalRegistry-L1-1-0.dll',
                                          'API-MS-Win-Core-ProcessThreads-L1-1-0.dll',
                                          'API-MS-Win-Security-Base-L1-1-0.dll',
                                          'KERNELBASE.dll',
                                          'POWRPROF.dll',
                                          ],
                            includes = ['dbhash', 'anydbm'],
                            optimize=2,
                            bundle_files=1,),  # Exclude msvcr71
    }
)