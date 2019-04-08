from configparser import ConfigParser
import os
import json
import pkgutil


conf_file = os.path.expanduser('~/.idb')
config = ConfigParser()
config.read(conf_file)

DB_DATABASE = config['idb'].get('db_database', None)
DB_HOSTNAME = config['idb'].get('db_hostname', None)
DB_USERNAME = config['idb'].get('db_username', None)
DB_PASSWORD = config['idb'].get('db_password', None)

