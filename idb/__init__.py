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


def inventories(session, n_samples=1, study_area_id=None, species_id=None,
                is_interpreted=False):
    """Query the Inventory table with optional filters

    Only returns samples with ``is_interpreted`` set to False

    Args:
        session: A database session (see idb.db.session_scope)
        n_samples (int): Number of samples
        study_area_id (int): Optinal Studyarea id
        species_id (int): Optional Species id
        is_interpreted (bool): Filter on ``is_interpreted`` field,
            defaults to False (keep only records that have not yet been interpreted)
            Can also be None, in which case all interpreted and not interpreted
            records are returned

    Returns:
        dict: A feature collection
    """
    objects = session.query(Inventory)
    # is_interpreted filter (default is False)
    if is_interpreted is not None:
        objects = objects.filter(Inventory.is_interpreted.is_(is_interpreted))
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


def inventory(session, id):
    """Get a single inventory record by id
    """
    obj = session.query(Inventory).get(id)
    if obj is not None:
        obj = obj.geojson
    return obj


def update_inventory(session, id, is_interpreted):
    """Update an inventory record

    Usually used to change the is_interpreted column to True after interpreting
    or skipping the sample

    Return:
        int: 1 when successful, 0 otherwise
    """
    updated = session.query(Inventory)\
            .filter_by(id=id)\
            .update(dict(is_interpreted=is_interpreted))
    return updated


def add_interpreted(session, fc):
    """Add one or many interpreted records to the database

    Args:
        session (Session): sqlalchemy database session;
            see ``idb.db.session_scope``
        fc (list): List of geojson features (or a single feature)

    Returns:
        list: list of geojson representations of inserted features
    """
    if not isinstance(fc, list):
        fc = [fc]
    instance_list = [Interpreted.from_geojson(feature=x)
                     for x in fc]
    session.add_all(instance_list)
    session.flush()
    return [x.geojson for x in instance_list]


def interpreted(session, n_samples=10):
    """Return a list of all interpreted records registered in the database

    Args:
        session: sqlalchemy database session
        n_samples (int): Limit number of objects returned

    Return:
        dict: A feature collection
    """
    objects = session.query(Interpreted).limit(n_samples).all()
    return {'type': 'FeatureCollection',
            'features': [x.geojson for x in objects]}


def interpreted_by_id(session, id):
    """Get a single interpreted record by its id
    """
    obj = session.query(Interpreted).get(id)
    if obj is not None:
        obj = obj.geojson
    return obj


def species(session):
    """Return a list of all species registered in the database

    Args:
        session: sqlalchemy database session

    Return:
        list: List of species (list of dict)
    """
    objects = session.query(Species)
    return [x.dict for x in objects]


def studyareas(session):
    """Return a list of all study areas registered in the database

    Args:
        session: sqlalchemy database session

    Return:
        list: List of study areas (list of dict)
    """
    objects = session.query(Studyarea)
    return {'type': 'FeatureCollection',
            'features': [x.geojson for x in objects]}


def studyarea(session, id):
    """Query study area by id
    """
    obj = session.query(Studyarea).get(id)
    if obj is not None:
        obj = obj.geojson
    return obj
