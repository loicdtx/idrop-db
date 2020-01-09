#!/usr/bin/env python3

import argparse

from sqlalchemy.orm.session import make_transient

from idb.db import session_scope
from idb.models import Tile, Studyarea, Species, Inventory, Interpreted



if __name__ == '__main__':
    epilog = """
Copy all the content of a database to another existing database.
The second database must already exist (e.g. create with db_init.py)
Particularly useful for dumping data to spatialite to facilitate data exchange

Example:
    copy_db.py --src-env main --dst-env sqlite
"""
    parser = argparse.ArgumentParser(epilog=epilog,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-src-env', '--src-env',
                        required=True,
                        type=str,
                        help='source env to use (database), as defined in the .idb file')

    parser.add_argument('-dst-env', '--dst-env',
                        required=True,
                        type=str,
                        help='destination env to use (database), as defined in the .idb file')

    parsed_args = parser.parse_args()


    src_env = vars(parsed_args)['src_env']
    dst_env = vars(parsed_args)['dst_env']


    def transfer_table(table, src_env, dst_env):
        with session_scope(env=src_env) as session:
            all_obj = session.query(table).all()
            session.expunge_all()

        with session_scope(env=dst_env) as session:
            for obj in all_obj:
                session.merge(obj)

    for table in [Species, Tile, Studyarea, Inventory, Interpreted]:
        transfer_table(table, src_env, dst_env)


