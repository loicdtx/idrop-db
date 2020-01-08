#!/usr/bin/env python3

import argparse
import csv

from idb.db import init_db, session_scope
from idb.models import Species
from idb.utils import get_or_create

if __name__ == '__main__':
    epilog = """
Create database tables according to schemas defined in idb/models.py
Optionally populates species table using records from a csv file

Example:
    echo "SAP,sapelli\\nKOS,kossipo" > species.csv
    db_init.py --species species.csv
"""


    parser = argparse.ArgumentParser(epilog=epilog,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-s', '--species',
                        required=False,
                        default=None,
                        type=str,
                        help='csv file containing species codes and species names')

    parser.add_argument('-env', '--env',
                        required=False,
                        default='main',
                        type=str,
                        help='env to use (database), as defined in the .idb file')

    parsed_args = parser.parse_args()

    csv_path = vars(parsed_args)['species']
    env = vars(parsed_args)['env']
    init_db(env=env)

    if csv_path is not None:
        with open(csv_path) as src:
            reader = csv.reader(src)
            with session_scope(env=env) as session:
                for row in reader:
                    get_or_create(session=session, model=Species,
                                  code=row[0], name=row[1])



