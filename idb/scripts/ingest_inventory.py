#!/usr/bin/env python3

import argparse

import fiona

from idb.db import session_scope
from idb import add_inventories
from idb.models import Tile, Studyarea


gpkg_file = 'data/test_data.gpkg'

if __name__ == '__main__':
    epilog = """
Ingest inventory data into the database. Data must be contained in a single multilayer
vector file (e.g. geopackage), with inventory tiles in layer 'tiles', inventory samples
in layer 'inventory' and study areas geometries in layer 'studyarea'

List of species must have been ingested previously (e.g. using the db_init command
with the --species flag)

Example:
    ingest_inventory.py inventory.gpkg --env main
"""
    parser = argparse.ArgumentParser(epilog=epilog,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('inventory',
                        type=str,
                        help='Multilayer geospatial vector file containing the inventory data')

    parser.add_argument('-env', '--env',
                        required=False,
                        default='main',
                        type=str,
                        help='env to use (database), as defined in the .idb file')

    parsed_args = parser.parse_args()

    gpkg_file = vars(parsed_args)['inventory']
    env = vars(parsed_args)['env']

# Add tiles
with fiona.open(gpkg_file, layer='tiles') as src:
    tile_list = [Tile.from_geojson(feature) for feature in src]
with session_scope(env=env) as session:
    session.add_all(tile_list)

# Add inventory samples
with fiona.open(gpkg_file, layer='inventory') as src:
    with session_scope(env=env) as session:
        add_inventories(session, list(src))

# Add study area
with fiona.open(gpkg_file, layer='studyarea') as src:
    studyarea_list = [Studyarea.from_geojson(feature) for feature in src]
with session_scope(env=env) as session:
    session.add_all(studyarea_list)

