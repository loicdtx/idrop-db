from sqlalchemy.types import Numeric
from shapely.geometry import shape

from  sqlalchemy.sql.expression import func

from idb.models import Species, Inventory, Interpreted, Studyarea

__version__ = '0.0.1'


def add_inventories(session, fc):
    """Add one or many inventory records to the database

    Table Species must already contain all species, see db_init.py command line
    to populate it

    Args:
        session (Session): sqlalchemy database session
        fc (list): Feature collection (list of geojson features)
    """
    if not isinstance(fc, list):
        fc = [fc]
    instance_list = [Inventory.from_geojson(feature=x, session=session)
                     for x in fc]
    session.add_all(instance_list)


def inventories(session, n_samples=1, study_area_id=None, species_id=None):
    """Query the Inventory table with optional filters

    Args:
        session: A database session (see idb.db.session_scope)
        n_samples (int): Number of samples
        study_area_id (int): Optinal Studyarea id
        species_id (int): Optional Species id

    Returns:
        dict: A feature collection
    """
    objects = session.query(Inventory)
    # Study area filter (st_intersects)
    if study_area_id is not None:
        study_area_geom = session.query(Studyarea)\
                .filter_by(id=study_area_id)\
                .first()\
                .geom
        objects = objects.filter(Inventory.geom.ST_Intersects(study_area_geom))
    # Restrict for only one species
    if species_id is not None:
        objects = objects.filter_by(species_id=species_id)
    # Select n random samples from the remaining rows
    objects = objects.order_by(func.random()).limit(n_samples).all()
    return {'type': 'FeatureCollection',
            'features': [x.geojson for x in objects]}
