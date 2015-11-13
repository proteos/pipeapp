#!/usr/bin/env python
"""
Manifest File manipulations
"""


# region imports
from datetime import datetime
from os import path
from .shell import full_path
# endregion

# region: constants
__author__ = 'David Managadze'
# endregion

# region: variables

# endregion


class ManifestFile:
    def __init__(self, filename, entries=None, generator='pipeapp', action=None):
        self.filename = path.expanduser(filename)
        self.generator = generator
        self._entries = entries or list()
        self._fh = None
        if action == 'read':
            self.read()
        elif action == 'write':
            self.write()
        else:
            raise Exception('ManifestFile: no such action: {}'.format(action))

    def read(self):
        if self._fh is not None and self._fh.mode == 'w':
            raise Exception('file is already opened in write mode')
        with open(self.filename) as self._fh:
            for line in self._fh:
                line = line.strip()
                if line.startswith('#') or line == '':
                    continue
                self._entries.append(line)

    def write(self):
        if self._fh is not None and self._fh.mode == 'r':
            raise Exception('file is already opened in read mode')
        with open(self.filename, 'w') as self._fh:
            ctime = datetime.now().strftime('%Y-%m-%d %H:%M')
            self._fh.write('# content: manifest file\n')
            self._fh.write('# generator: {}\n'.format(self.generator))
            self._fh.write('# date: {}\n'.format(ctime))
            self._fh.write('#\n')
            for e in self._entries:
                self._fh.write('{}\n'.format(full_path(e)))

    @property
    def entries(self):
        return self._entries

    @entries.setter
    def entries(self, e):
        if not isinstance(e, list):
            raise Exception('entries should be a list')
        self._entries = e
