#!/usr/bin/env python

"""
App common library with App class
"""

# region imports
import sys
from os import path, environ, devnull, getenv
from datetime import datetime
from tempfile import mkdtemp
import configparser

from .shell import make_dir, remove_dir, full_path
# endregion

# region: constants
__author__ = 'David Managadze'
# endregion

# region: variables

# endregion


class App(object):      # HomoloGene App Class
    """
    Template class for HomoloGene apps
    """

    @classmethod
    def main(cls, **kwargs):
        """
        main class method to create, run and exit application
        calls init(), run(), exit() methods
        they should be overriden and re-created in the actual application
        :return: return code of the application
        :rtype: int
        """
        # print "MAIN: kwargs:", kwargs
        app = cls(**kwargs)
        app.init(**kwargs)
        app.run(**kwargs)
        app.exit(**kwargs)
        app.mark_task_done()
        return 0

    def __init__(self, name=None, version="0.0", debugmode=False, conf=None, env=environ,
                 input=None, input_manifest=None, workdir=None, is_wnode=False, continue_task=False,
                 logfile=None, stdout=sys.stdout, stderr=sys.stderr, quiet=False, **kwargs):
        """
        :param name:        app name
        :param version:     app version
        :param conf:        config file name
        :param logmode:     'normal' or 'debug', determines whether to show debug messages
        :param argv:        arguments
        :param env:         environment variables (or dictionary with similar data)
        :param logfile:     log file name
        :param workdir:     work directory path
        :param input:       input data (file/directory path)
        """
        # print "*** Initializing HGApp..."
        self.argv = sys.argv
        self.conf_path = full_path(conf)
        self.env = env
        self.name = name
        self.ver = version
        self.input = full_path(input)
        self.input_manifest = full_path(input_manifest)
        self.workdir = full_path(workdir)
        self.is_wnode = is_wnode
        self.continue_task = continue_task
        self.quiet = quiet  # be quite, don't log anything to the sceen

        if self.input_manifest and self.input:
            print("\n\nERROR: please provide either input or input manifest, *not* both.\n\n", file=sys.stderr)
            sys.exit(1)
        if self.input_manifest and not path.exists(self.input_manifest):
            print("\n\nERROR: input manifest file does not exist: ", self.input_manifest, "\n\n", file=sys.stderr)
            sys.exit(1)
        if self.input and not path.exists(self.input):
            # using this way of reporting because the outputs are not yet initialized
            print("\n\nERROR: input does not exist: ", self.input, "\n\n", file=sys.stderr)
            sys.exit(1)

        if not self.workdir:
            # using this way of reporting because the outputs are not yet initialized
            print("\n\nERROR: you need to provide working directory path by --workdir or -d parameters\n\n", file=sys.stderr)
            sys.exit(1)

        # workdir subdir names
        self.dir_tmp = path.join(self.workdir, "tmp")
        self.dir_in = path.join(self.workdir, "in")
        self.dir_out = path.join(self.workdir, "out")
        self.dir_log = path.join(self.workdir, "log")
        # create directory structure, if init_dirs was provided

        # if we are running as a worker node, we don't need to create all dirs,
        # we just need our own tmp dir
        if self.is_wnode:
            # we are a worker node, so:
            try:
                self.dir_tmp = mkdtemp(prefix="job_", dir=self.dir_tmp)
            except OSError:
                raise Exception("HGApp Class: can not create tmp directory for --wnode mode: " + self.dir_tmp + "/job_*")
        elif not self.continue_task:
            # if this is a normal task and NOT a continuing task, (re-)create workdir and all subdirs
            if path.exists(self.workdir):
                remove_dir(self.workdir)
            make_dir(self.workdir)
            make_dir(self.dir_tmp)
            make_dir(self.dir_in)
            make_dir(self.dir_out)
            make_dir(self.dir_log)

        # create log file
        self.logfile = logfile or path.join(self.dir_log, self.name + ".log")

        # set up stdout
        if self.quiet:
            self._stdouth = open(devnull, 'w')
        elif stdout == sys.stdout:
            self._stdouth = stdout
        elif isinstance(stdout, str):
            self._stdouth = open(stdout, 'w', )

        # set up stderr
        if stderr == sys.stderr:
            self._stderrh = stderr
        elif isinstance(stdout, str):
            self._stderrh = open(stderr, 'w', )

        # set log mode
        if debugmode:
            self.log_info("\n\n!!! --- Running in debug mode! --- !!!\n\n")
            self.logmode = "debug"
        else:
            self.logmode = "normal"

        # set up configuration
        if self.conf_path is not None:
            self.conf_read(self.conf_path)

        self.log_info("\n\n# ---   APP: {0}   --- #\n".format(self.name))
        self.log_info("---   INITIALIZING       ---")
        self.log_info("COMMAND:          ", ' '.join(self.argv))
        self.log_info("\n\n")
        self.log_info("* input:          ", self.input)
        self.log_info("* input manifest: ", self.input_manifest)
        self.log_info("* work dir:       ", self.workdir)
        self.log_info("//\n")
        self.log_info("\n---      RUNNING         ---\n")

    def init(self, **kwargs):
        """
        virtual method, must be overridden in the child class
        """
        raise NotImplementedError

    def run(self, **kwargs):
        """
        virtual method, must be overridden in the child class
        """
        # print "RUN: kwargs:", kwargs
        raise NotImplementedError

    def exit(self, **kwargs):
        """
        clean exit from application
        """
        self.log_info("* cleaning up")
        # examples
        # ddir = os.path.join(app.dir_out, os.path.basename(app.dir_out_accs))
        # app.log_info("  + moving", app.dir_out_accs, "to:", ddir)
        # move_dir(app.dir_out_accs, ddir)
        # ddir = os.path.join(app.dir_out, os.path.basename(app.dir_out_fasta))
        # app.log_info("  + moving", app.dir_out_fasta, "to:", ddir)
        # move_dir(app.dir_out_fasta, ddir)
        # remove(app.dir_tmp)

        self.log_info("\n# ---   FINISHED   --- #\n")

    def crash_exit(self):
        """
        Crash exit from application
        """
        self.log_info("\n# ---   APP CRASHED!--- #\n")
        self.log_info("* cleaning up")
        # remove(self.dir_tmp)
        self.log_info("\n# ---   FINISHED   --- #\n")

    def mark_task_done(self):
        """ Mark task of the app as done. Just creates file '.done' in workdir. """
        trigger_fname = path.join(self.workdir, '.done')
        with open(trigger_fname, 'w') as fh:
            pass
# region messaging/logging methods

    @property
    def logfile(self):
        return self._logfile

    @logfile.setter
    def logfile(self,f):
        self._logfile = path.expanduser(f)
        self._logfh = open(self._logfile, 'w')

    def log_debug(self, *args):
        if self.logmode == "normal":
            return
        elif self.logmode == "debug":
            text_out = ' '.join(str(a) for a in args)
            print(text_out, file=self._stdouth)
            self.log(text_out)
        else:
            self.die('HGApp logmode must be either "normal" or "debug"')

    def log_info(self, *args):
        text_out = ' '.join(str(a) for a in args)
        print(text_out, file=self._stdouth)
        self.log(text_out.strip())

    def log_warning(self, *args):
        text_out = 'WARNING: '
        text_out += ' '.join(str(a) for a in args)
        print(text_out, file=self._stdouth)
        self.log(text_out)

    def log_error(self, *args):
        text_out = 'ERROR: '
        text_out += ' '.join(str(a) for a in args)
        print(text_out, file=self._stderrh)
        self.log(text_out)

    def die(self, *args):
        text_out = 'CRITICAL ERROR: '
        text_out += ''.join(str(a) for a in args)
        text_out += '\n\nTERMINATING...\n\n'
        print(text_out, file=self._stdouth)
        self.log(text_out)
        sys.exit(1)

    def log(self, *args):
        now = datetime.now()
        date = now.strftime('%Y-%m-%d')
        time = now.strftime('%H:%M')
        text_out = date + '\t' + time + '\t'
        text_out += ' '.join(str(a) for a in args)
        print(text_out, file=self._logfh)
        self._logfh.flush()
# endregion

    def conf_read(self, conffile):
        if path.isfile(conffile):
            self.conf = conffile
        self.conf = configparser.RawConfigParser()
        self.conf.read(conffile)

    def config_write(self, conffile):
        pass

    def status(self):
        pass

