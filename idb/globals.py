from configparser import ConfigParser
import os
import json
import pkgutil


conf_file = os.path.expanduser('~/.idb')
config = ConfigParser(defaults={'drivername': 'postgresql'})
config.read(conf_file)

# Put everything in a separate variable to avoid confusion
DB_CONFIG = config








