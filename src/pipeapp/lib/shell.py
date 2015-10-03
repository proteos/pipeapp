"""
Classes and functions
"""

# region: imports
from os.path import expanduser, expandvars, realpath
from os import makedirs, remove
from glob import glob
from shutil import Error as shutil_Error, rmtree, move
import errno
from codecs import open as codecs_open
from gzip import open as gz_open


# endregion

# region: global vars and constants

# endregion

# region: exception classes

# endregion

# region: interface functions
def full_path(pathname):
    """ Normalizes file/dir pathname. """
    if pathname:
        return realpath(expandvars(expanduser(pathname)))


def make_dir(dir_path):
    """
    Create directory given the directory path. This function can create nested directories, similar to `mkdir -p ...`.
    :param dir_path: path of a directory to be created
    :type dir_path: str
    :return:
    :rtype:
    """
    try:
        makedirs(dir_path)
        return True
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def move_files(src_files_path, dst):
    """
    move source file(s) to the destination
    :param src_files_path: source path (with wildcard)
    :type src_files_path: str
    :param dst: destination path
    :type dst: str
    """
    src_files = glob(src_files_path)
    for fsrc in src_files:
        try:
            move(fsrc, dst)
        except shutil_Error:
            pass


def remove_dir(dirname):
    """
    Recursively remove directory tree.
    :param dirname: dir dirname
    :type dirname: str
    """
    rmtree(dirname, ignore_errors=True)


def remove_file(filename):
    """
    Delete one file.
    :param filename: file name
    :type filename: str
    """
    try:
        remove(filename)
    except FileNotFoundError:
        pass


def open_file(filename):
    """ Open text file, wether gzipped or not. Return open file handle. """
    if filename.endswith('.gz'):
        fh = gz_open(filename=filename, mode='rt', encoding='utf-8')
    else:
        fh = codecs_open(filename, 'r', 'utf-8')
    return fh

# endregion

# region: classes

# endregion

# region: _internal functions

# endregion
