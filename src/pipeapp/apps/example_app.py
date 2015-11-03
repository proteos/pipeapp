#!/usr/bin/env python

"""
Example app that uses BasicPipelineApp class
"""

# region: imports
from argparse import ArgumentParser

from pipeapp.lib.app import BasicPipelineApp


# endregion
__author__ = 'David Managadze'
# region: constants


# endregion

# region: variables

# endregion


class ExampleApp(BasicPipelineApp):
    """
    Example of using the pipeline app class
    """

    def init(self, input=None, input_manifest=None, **kwargs):
        self.log_info('# reading configuration, setting variables')

    def run(self, input=None, input_manifest=None, **kwargs):
        self.log_info('# running app')

    def exit(self, **kwargs):
        self.log_info('# cleaning up')


def run_from_console():
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
    args_dict = vars(args)
    args_dict['name'] = arg_parser.prog
    args_dict['no_conf_root_key'] = True
    ExampleApp.main(**args_dict)


if __name__ == '__main__':
    exit(run_from_console())
