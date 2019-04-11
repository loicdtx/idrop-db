#!/usr/bin/env python3

import fiona

from idb.db import session_scope
from idb import add_inventory_list
from idb.models import Tile


gpkg_file = 'data/test_data.gpkg'

# Add tiles
with fiona.open(gpkg_file, layer='tiles') as src:
    tile_list = [Tile.from_geojson(feature) for feature in src]
with session_scope() as session:
    session.add_all(tile_list)

# Add inventory samples
with fiona.open(gpkg_file, layer='inventory') as src:
    with session_scope() as session:
        add_inventory_list(session, list(src))
