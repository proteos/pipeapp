"""
Shell functions e.g. copy/move files/dirs, run commands, ftp, etc
"""

import ftplib
from os.path import expanduser, expandvars, realpath, isfile, getsize
from os import makedirs, walk, path, rename as rename_file, remove
from shutil import Error as shutil_Error, rmtree, copytree, copy2, move
from shlex import split as shlex_split
from glob import glob
from subprocess import Popen, PIPE, call
import errno
from gzip import open as gz_open
from codecs import open as codecs_open
from zipfile import ZipFile


# region: classes

# endregion


# region: functions
def full_path(pathname):
    """ Normalizes file/dir pathname. """
    if pathname:
        return realpath(expandvars(expanduser(pathname)))


def gzip_filehandle(fname):
    """
    Return file handle for the gzip file opened in read-text mode.
    """
    fh = gz_open(filename=fname, mode='rt', encoding='utf-8')
    return fh


def unzip(zip_path, extract_dir=None, remove_zip=False):
    """
    Extract all members from a zip archive.

    :param zip_path: file path to zip archive
    :param out_dir: directory to extract to (current working directory by default)
    :param remove_zip: if True, delete the zip file after extracting it
    :type zip_path: str
    :type out_dir: str
    :type remove_zip: bool
    """
    with ZipFile(zip_path) as zf:
        archive_members = zf.namelist()
        zf.extractall(extract_dir)

    if remove_zip:
        remove_file(zip_path)

    return archive_members


def open_file(filename):
    """ Open text file, wether gzipped or not. Return open file handle. """
    if filename.endswith('.gz'):
        fh = gz_open(filename=filename, mode='rt', encoding='utf-8')
    else:
        fh = codecs_open(filename, 'r', 'utf-8')
    return fh


def tab_file_reader(filename, headline=True, fieldnames=None, gzip=False):
    """
    Read tab-delimited file; create generator of dict dictionaries.
    :param filename: input file name
    :type filename: str
    :param headline: should we use the first line as the headline (containing field names)?
    :type headline: bool
    :param gzip: is file gzipped?
    :type gzip: bool
    :return: generator of dictionaries
    :rtype: generator
    """
    if gzip:
        fh = gzip_filehandle(filename)
    else:
        fh = codecs_open(filename, 'r', 'utf-8')
    if headline:
        headline = next(fh)
        # fieldnames = headline.replace('#','').replace('-', '_').strip().split('\t')
        fieldnames = headline.replace('#', '').strip().split('\t')
    for line in fh:
        fields = line.strip().split('\t')
        record = dict(zip(fieldnames, fields))
        yield record
    fh.close()


def run_shell_cmd(cmd):
    """
    Run piped commands in shell, return stdout and stderr of the last command in pipe

    # example:
    >>> c = 'ls -al | cut -f1 | sed "s/|//"'
    >>> sout, serror = run_shell_cmd(c)
    >>> for line in sout:
    >>>   print line,

    :param cmd: command
    :type cmd: str
    :return:
    :rtype:
    """
    tokens = shlex_split(cmd)
    length = len(tokens)
    start = 0
    stop = 1000000
    l_cmds = []

    # split list to the list of commands
    for _ in range(length):
        try:
            stop = tokens.index('|', start)
        except ValueError:
            stop = length
        cmds = tokens[start:stop]
        l_cmds.append(cmds)
        start = stop + 1
        if stop == length:
            break
    # run commands
    n_cmd = len(l_cmds)  # number of commands in pipe
    l_proc = []
    for n in range(n_cmd):
        if n == 0:  # first command
            l_proc.append(Popen(l_cmds[n], stdout=PIPE, stderr=PIPE))
        else:  # non-first (or last) command
            l_proc.append(Popen(l_cmds[n], stdin=l_proc[n - 1].stdout, stdout=PIPE, stderr=PIPE))
    # get outputs
    pipe_stdout = l_proc[n_cmd - 1].stdout
    pipe_stderr = l_proc[n_cmd - 1].stderr
    return pipe_stdout, pipe_stderr


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


def copy_files(src_files_path, dst):
    """
    copy source file(s) to the destination
    :param src_files_path: source path (file name or path with wildcard)
    :type src_files_path: str
    :param dst: destination path; if directory, files will be copied in it
    :type dst: str
    """
    src_files = glob(src_files_path)
    for fsrc in src_files:
        try:
            copy2(fsrc, dst)
        except shutil_Error:
            raise shutil_Error('Error copying file ' + fsrc + ' to ' + dst)


def move_dir(src, dst):
    """
    move source directory to the destination
    :param src: source path
    :type src: str
    :param dst: destination path
    :type dst: str
    """
    try:
        move(src, dst)
    except OSError as e:
        # If the error was caused because the source wasn't a directory
        if e.errno == errno.ENOTDIR:
            copy_dir(src, dst)
        else:
            print(('File/Directory not moved. Error: %s' % e))


def copy_dir(src, dest):
    try:
        copytree(src, dest)
    except OSError as e:
        # If the error was caused because the source wasn't a directory
        if e.errno == errno.ENOTDIR:
            copy_dir(src, dest)
        else:
            print(('File/Directory not copied. Error: %s' % e))

        def cat_files(dir_in, wildcard, fout):
            """
            concatenate many files into one output
            :param dir_in: path to input files
            :type dir_in: str
            :param wildcard: wildcard to be added to the input directory
            :type wildcard: str
            :param fout: output file name
            :type fout: str
            """
            cmd = "find {dir_in} -type f -name '{wildcard}' | xargs cat > {fout}".format(**locals())
            run_shell_cmd(cmd)


def is_non_zero_file(fpath):
    """ Check if file exists and is non-zero length. """
    return isfile(fpath) and getsize(fpath) > 0


def _ftp_split_path(fname):
    """
    split ftp path into host, path, filename
    :param fname: full path to file
    :type fname: str
    :return: tuple (host, path, filename)
    :rtype: tuple
    """
    # get host, path, file name
    f = fname.replace("ftp://", "")
    host = f.split("/", 1)[0]
    pathname, filename = f.rsplit("/", 1)
    pathname = pathname.replace(host, "")
    return host, pathname, filename


def ftp_glob(dirname):
    """
    return list of files/dirs that correspond to the wildcard-containing dirname
    :param dirname: ftp dirname to file/dir
    :type dirname: str
    :return: list of files/dirs
    :rtype: list
    """
    f = dirname.replace("ftp://", "")
    host, fpath = f.split("/", 1)
    fpath = "/" + fpath
    ftp = ftplib.FTP(host)
    ftp.login()
    try:
        files = ftp.nlst(fpath)
    except:
        files = None
    return files


def ftp_get_file(fname, fout):
    """
    download file via ftp
    """
    hostname, pathname, fin = _ftp_split_path(fname)
    ftp = ftplib.FTP(hostname)
    ftp.login()
    ftp.cwd(pathname)
    try:
        ftp.retrbinary("RETR " + fin, open(fout, 'wb').write)
    except:
        print("Error downloading file:", fin)
        remove_dir(fout)


def get_gzip_filehandle(fname):
    """
    Return file handle for the gzip file opened in read-text mode.
    """
    from gzip import open as gz_open
    # fh = gz_open(fname, 'rt')
    fh = gz_open(filename=fname, mode='rt', encoding='utf-8')
    return fh

# endregion
