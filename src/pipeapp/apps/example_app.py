#!/usr/bin/env python

'''
Align sequences using MUSCLE.

This app will:
* read fasta files from input dir or manifest file
* create alignments files

Example command:
align_muscle.py --input /path/to/fasta/files/ --workdir muscle_aln/ --conf homologene.conf --debug

Output: <workdir>/out/aln/*.aln alignment files
'''

# region: imports
from os import path, environ
from glob import glob
from argparse import ArgumentParser

from pipeapp.lib.app import App
from pipeapp.lib.shell import call_shell_cmd, file_name_no_ext, move_dir, make_dir, move_files, remove_dir


# endregion
__author__ = 'David Managadze'
# region: constants


# endregion

# region: variables

# endregion


class ExampleApp(App):
    '''
    Example of using the pipeline app class
    '''

    def init(self, input=None, input_manifest=None, **kwargs):
        self.log_info('# reading configuration, setting variables')

    def run(self, input=None, input_manifest=None, **kwargs):
        self.log_info('# running app')

    def exit(self, **kwargs):
        self.log_info('# cleaning up')


if __name__ == '__main__':
    # set up args
    arg_parser = ArgumentParser(prog='example_app',
                                description='',
                                usage='%(prog)s --input <inputdir> --workdir <workdir> [--conf <conffile> --debug]',
                                add_help=True)
    arg_parser.add_argument('-i', '--input', help='directory of input fasta (*.faa) files')
    arg_parser.add_argument('-d', '--workdir', required=True, help="task's work directory")
    arg_parser.add_argument('-c', '--conf', help='config file name')
    arg_parser.add_argument('-l', '--log', help='log file name')
    arg_parser.add_argument('--debug', action='store_true', help='run in debug mode')
    # initialize command line parameters
    args = arg_parser.parse_args()

    # set defaults
    # input_manifest = args.input_manifest
    conf = args.conf or path.join(environ['HG_ROOT'], 'homologene', 'conf/homologene.conf')

    ExampleApp.main(name=arg_parser.prog, debugmode=args.debug, conf=conf, env=environ,
                          input=args.input, input_manifest=args.input_manifest, workdir=args.workdir, is_wnode=args.wnode,
                          logfile=args.log)



