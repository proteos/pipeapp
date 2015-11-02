"""
Common classes and functions
"""

# region: imports
from os import environ, path
from yaml import load as load_yaml
import errno

from .shell import full_path
# endregion

# region: constants
default_config = {
    'DEBUG': False,
    'TESTING': False
}


# endregion

# region: classes
class Config(dict):
    def __init__(self, defaults=None):
        dict.__init__(self, defaults or default_config)

    def from_envvar(self, var_name, root_key=None, silent=False):
        """
        Loads a configuration from an environment variable pointing to a configuration file.
        Inspired by Flask's Config class.
        This is basically just a shortcut with nicer error messages for this line of code::
        app.conf.from_yaml(os.environ['APP_CONFIG'])
        :param var_name: name of the environment variable
        :param root_key: dict key that should be used as a root to update config
        :param silent: set to `True` if you want silent failure for missing files.
        :return: bool. `True` if able to load config, `False` otherwise.
        """
        rv = environ.get(var_name)
        if not rv:
            if silent:
                return False
            raise RuntimeError('The environment variable {} is not set '
                               'and as such configuration could not be '
                               'loaded.  Set this variable and make it '
                               'point to a configuration file'.format(var_name))
        return self.from_yaml(filename=rv, root_key=root_key, silent=silent)

    def from_yaml(self, filename, root_key=None, silent=False):
        """
        Updates the values in the config from a YAML file.
        :param filename: the filename of the config; either absolute or relative
        :param root_key: dict key that should be used as a root to update config
        :param silent: set to `True` if you want silent failure for missing files
        """
        if not filename:
            return False
        yaml = None
        try:
            conf_full_path = full_path(filename)
            if path.exists(conf_full_path):
                with open(conf_full_path) as yaml_fh:
                    yaml = load_yaml(yaml_fh.read())
            else:
                raise IOError('File not found: {}', conf_full_path)
        except IOError as e:
            if silent and e.errno in (errno.ENOENT, errno.EISDIR):
                return False
            e.strerror = 'Unable to load configuration file. ({})'.format(e.strerror)
            raise
        if root_key is not None:
            if root_key not in yaml:
                print('Root Key {} is not in config file: {}'.format(root_key, filename))
                return False
            yaml = yaml[root_key]
        self.update(yaml)
        return True

# endregion

# region: functions


# endregion
