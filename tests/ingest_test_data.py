#!/usr/bin/env python3

import fiona

from idb.db import session_scope
from idb import add_inventory_list


gpkg_file = 'data/test_data.gpkg'

with fiona.open(gpkg_file, layer='inventory') as src:
    with session_scope() as session:
        add_inventory_list(session, list(src))
