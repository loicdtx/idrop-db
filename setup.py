#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
from setuptools import setup, find_packages
import os

# Parse the version from the main __init__.py
with open('idb/__init__.py') as f:
    for line in f:
        if line.find("__version__") >= 0:
            version = line.split("=")[1].strip()
            version = version.strip('"')
            version = version.strip("'")
            continue


setup(name='idb',
      version=version,
      description=u"Database model for idrop labelling tool",
      author=u"Loic Dutrieux",
      author_email='loic.dutrieux@cirad.fr',
      license='GPLv3',
      packages=find_packages(),
      install_requires=[
          'geoalchemy2',
          'sqlalchemy',
          'shapely',
          'jsonschema',
          'psycopg2'
      ])
