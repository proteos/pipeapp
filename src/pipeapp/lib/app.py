#!/usr/bin/env python

"""
App common library with App class
"""

# region: imports
import sys
from os import environ, getenv, path, getcwd
import logging

from .config import Config
from primerdesign.shell import full_path, make_dir, remove_dir


# endregion

# region: classes
class BasicApp:
    @classmethod
    def main(cls, **kwargs):
        """
        Main class and organizing method to create, run and exit app,
        calls hook methods e.g. init(), run(), exit() which should be overridden
        and re-created in the actual application.

        :return: return code of the application
        :rtype: int
        """
        app = cls(**kwargs)
        try:
            app.log.info('# --- Initializing app --- #')
            app.init(**kwargs)
            app.log.info('//\n')
            app.log.info('# --- Running main body --- #')
            app.run(**kwargs)
            app.log.info('//\n')
            app.log.info('# --- Exiting --- #')
            app.exit(**kwargs)
            app.post_exit(**kwargs)
            app.log.info('//\n')
            app.log.info('---   FINISHED   ---\n\n')
            return 0

        except Exception as e:
            app.log.exception(str(e))
            return -1

    def __init__(self, name=None, conf=None, log=None, debug=False, no_conf_root_key=False, **kwargs):
        """
        Initialize BasicApp instance.

        :param name:    app name
        :param conf:    config file name
        :param log:     log file name
        :param debug:   debug mode
        :param workdir: work directory path
        :param no_conf_root_key:    expect to have a root key with this app name in the config file
        """
        self.name = name or 'app'
        self.argv = sys.argv
        self.logfile = log
        self.log = self._make_logger(logfile_name=self.logfile, debug=debug)
        self.log.info('\n\n# ---   Starting app: {0}   --- #'.format(self.name))
        self.log.info('Command: {}'.format(' '.join(self.argv)))
        conf_root_key = None
        if not no_conf_root_key:
            conf_root_key = self.name
        self.conf = self._make_config(conf_file=conf, root_key=conf_root_key)
        self.debug = debug
        self.conf.DEBUG = debug

    def init(self, **kwargs):
        """Virtual method to initialize app, must be overridden in the child class."""
        raise NotImplementedError

    def run(self, **kwargs):
        """Virtual method to run the app, must be overridden in the child class."""
        raise NotImplementedError

    def exit(self, **kwargs):
        """Clean exit from application."""
        raise NotImplementedError

    def post_exit(self, **kwargs):
        """Clean exit from application."""
        pass

    def _make_config(self, conf_file=None, root_key=None):
        """
        Create app configuration.

        :param conf_file: file with configuration
        :return: configuration object
        """
        conf = Config()
        var_prefix = self.name.upper() + '_'  # env vars must begin with APP_NAME_ to be added to config

        # read config file name from conf_file variable and read config from that file
        conf_file_yaml = None
        conf_file_env_var = '{}CONFIG_YAML'.format(var_prefix)
        conf_file_env = getenv(conf_file_env_var)
        if conf_file is not None:
            conf_file_yaml = conf_file
        # otherwise, read env var <APP_NAME>_CONFIG_YAML as config file name
        elif conf_file_env is not None:
            conf_file_yaml = conf_file_env
        self.log.info('Reading config from file: {}'.format(conf_file_yaml))
        conf.from_yaml(filename=conf_file_yaml, root_key=root_key)

        # read env vars and update conf
        self.log.info('Reading environment variables')
        # self.log.info('var_prefix: ' + var_prefix)
        for var in environ:
            # self.log.info('@ var: ' + str(var))
            if var.startswith(var_prefix):
                # self.log.info('    add to config')
                key = var[len(var_prefix):]
                val = environ[var]
                conf[key] = val
                self.log.info('    env var: ${}={}'.format(key, val))
        return conf

    def _make_logger(self, logfile_name, file_mode='w', debug=False):
        """
        Create logger object for the app with streams to console and logfile.

        :param logfile_name: logfile name
        :param file_mode: mode of writing to file; should be a valid file mode (e.g. 'w', 'a', etc)
        :param debug: should we use DEBUG mode?
        :return: logger object
        """
        # create logger
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        # create console handler with default level INFO, unless function arg `debug` says it to be DEBUG
        console_h = logging.StreamHandler(stream=sys.stdout)
        if debug:
            console_h.setLevel(logging.DEBUG)
        else:
            console_h.setLevel(logging.INFO)
        console_fmt = logging.Formatter(fmt='%(message)s')
        console_h.setFormatter(console_fmt)
        logger.addHandler(console_h)
        # create logfile handler and set its level do DEBUG
        if logfile_name is not None:
            logf_h = logging.FileHandler(filename=logfile_name, mode=file_mode)
            logf_h.setLevel(logging.DEBUG)
            logf_fmt = logging.Formatter(fmt='%(asctime)s\t%(levelname)s:\t%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
            logf_h.setFormatter(logf_fmt)
            logger.addHandler(logf_h)
        return logger

    def log_info(self, *args):
        text_out = ' '.join(str(a) for a in args)
        self.log.info(text_out.strip())

    def log_debug(self, *args):
        text_out = ' '.join(str(a) for a in args)
        self.log.debug(text_out.strip())

    def log_die(self, *args):
        text_out = 'CRITICAL ERROR:' + ' '.join(str(a) for a in args) + '\n\n'
        if self.debug:
            raise SystemError(text_out)
        else:
            self.log.exception(text_out.strip())
            sys.exit(1)


class BasicPipelineApp(BasicApp):
    def __init__(self, workdir=None, **kwargs):

        # workdir and subdir names
        if workdir:
            self.workdir = full_path(workdir)
        else:
            self.workdir = full_path(path.join(getcwd(), self.name))

        self.dir_tmp = path.join(self.workdir, "tmp")
        self.dir_in = path.join(self.workdir, "in")
        self.dir_out = path.join(self.workdir, "out")
        self.dir_log = path.join(self.workdir, "log")
        # create directory structure, if init_dirs was provided

        # create workdir and all subdirs
        if path.exists(self.workdir):
            remove_dir(self.workdir)
        make_dir(self.workdir)
        make_dir(self.dir_tmp)
        make_dir(self.dir_in)
        make_dir(self.dir_out)
        make_dir(self.dir_log)
        # create log file
        if 'log' not in kwargs or kwargs.get('log') is None:
            log = path.join(self.dir_log, kwargs['name'] + ".log")
            kwargs['log'] = log
        super().__init__(**kwargs)
        self.log.info('Work directory: {}'.format(self.workdir))
        self.log.info('//\n')

    def post_exit(self, **kwargs):
        """ Cleanup procedures after exit() """
        if not self.debug:
            remove_dir(self.dir_tmp)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """ Cleanup procedures after exit() """
        if not self.debug:
            remove_dir(self.dir_tmp)

# endregion

# region: functions

# endregion
