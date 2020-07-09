from sqlalchemy.types import Numeric
from shapely.geometry import shape, mapping

from sqlalchemy.sql.expression import func, cast
from geoalchemy2 import Geography
from geoalchemy2.shape import to_shape

from idb.models import Species, Inventory, Interpreted, Studyarea
from idb.models import Trainwindow, Experiment

__version__ = '0.2.0'


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


def _inventories(session, n_samples=None, study_area_id=None, species_id=None,
                 is_interpreted=False):
    """Build a Query to filter the Inventory table

    Args:
        session: A database session (see idb.db.session_scope)
        n_samples (int): Number of samples (no limit if None (default))
        study_area_id (int): Optinal Studyarea id
        species_id (int): Optional Species id
        is_interpreted (bool): Filter on ``is_interpreted`` field,
            defaults to False (keep only records that have not yet been interpreted)
            Can also be None, in which case all interpreted and not interpreted
            records are returned

    Returns:
        sqlalchemy.Query: The sqlalchemy query
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
    objects = objects.order_by(func.random()).limit(n_samples)
    return objects


def inventories(session, n_samples=None, study_area_id=None, species_id=None,
                is_interpreted=False):
    """Query the Inventory table with optional filters

    Only returns samples with ``is_interpreted`` set to False

    Args:
        session: A database session (see idb.db.session_scope)
        n_samples (int): Number of samples (no limit if None (default))
        study_area_id (int): Optinal Studyarea id
        species_id (int): Optional Species id
        is_interpreted (bool): Filter on ``is_interpreted`` field,
            defaults to False (keep only records that have not yet been interpreted)
            Can also be None, in which case all interpreted and not interpreted
            records are returned

    Returns:
        dict: A feature collection
    """
    objects = _inventories(session=session, n_samples=n_samples,
                           study_area_id=study_area_id, species_id=species_id,
                           is_interpreted=is_interpreted)
    return {'type': 'FeatureCollection',
            'features': [x.geojson for x in objects.all()]}


def inventories_hits(session, n_samples=None, study_area_id=None, species_id=None,
                     is_interpreted=False):
    """Get the length of a query with filters on the Inventory table

    Is meant to know the length of samples that a call to ``idb.inventories``
    would return without actually returning the feature collection

    Args:
        session: A database session (see idb.db.session_scope)
        n_samples (int): Number of samples (no limit if None (default))
        study_area_id (int): Optinal Studyarea id
        species_id (int): Optional Species id
        is_interpreted (bool): Filter on ``is_interpreted`` field,
            defaults to False (keep only records that have not yet been interpreted)
            Can also be None, in which case all interpreted and not interpreted
            records are returned

    Returns:
        int: The length of rows queried
    """
    objects = _inventories(session=session, n_samples=n_samples,
                           study_area_id=study_area_id, species_id=species_id,
                           is_interpreted=is_interpreted)
    return objects.count()


def inventory(session, id):
    """Get a single inventory record by id
    """
    obj = session.query(Inventory).get(id)
    if obj is not None:
        obj = obj.geojson
    return obj


def update_inventory(session, id, is_interpreted=None, comment=None):
    """Update an inventory record

    Usually used to change the is_interpreted column to True after interpreting
    or skipping the sample
    Can also be used to add a comment (new feature)

    Return:
        int: 1 when successful, 0 otherwise
    """
    update_dict_0 = {'is_interpreted': is_interpreted,
                     'comment': comment}
    # Remove None to avoid overriding existing values
    update_dict_1 = {k:v for k,v in update_dict_0.items() if v is not None}
    updated = session.query(Inventory)\
            .filter_by(id=id)\
            .update(update_dict_1)
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


def replace_interpreted(session, id, feature):
    """Update an existing row (identified by id) in the interpreted table

    Args:
        session (Session): sqlalchemy database session;
            see ``idb.db.session_scope``
        id (int): Unique row id of the sample to update in the database
        feature (dict): The geojson like feature to use for updating the record
            Should contain a geometry and the two properties ``inventory_id`` and
            ``species_id``

    Returns:
        dict: The feature representation of the updated record
    """
    # The way replacement is done right now is a bit of a hack, there's probably
    # a better way to do it
    # Create an instance of Interpreted
    new_row = Interpreted.from_geojson(feature)
    new_row.id = id
    # Update by merging
    session.merge(new_row)
    return True


def interpreted(session, n_samples=None, species_id=None, inventory_id=None):
    """Return a list of all interpreted records registered in the database

    Args:
        session: sqlalchemy database session
        n_samples (int): Limit number of objects returned
        species_id (int): Optional species_id filter
        inventory_id (int): Optional inventory_id filter (returns a list of max
            one element)

    Return:
        dict: A feature collection
    """
    objects = session.query(Interpreted)
    if species_id is not None:
        objects = objects.filter_by(species_id=species_id)
    if inventory_id is not None:
        objects = objects.filter_by(inventory_id=inventory_id)
    # limit number of results
    objects = objects.limit(n_samples).all()
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


def neighborhood(session, inventory_id=None, distance=None, species_id=None):
    """Performs a spatial search of inventory records in a given radius around a point

    Args:
        session: sqlalchemy database session
        inventory_id (int): The database id of an inventory record. Seach will
            performed around the geometry of that record
        distance (float): Search radius in meters
        species_id (list): A list of species_id to restrict the search to

    Return:
        dict: A feature collection of the inventory features intersecting with
            the search radius around the feature provided. The input feature is
            automatically excluded from the collection
    """
    geog = cast(session.query(Inventory).get(inventory_id).geom, Geography)
    buff = geog.ST_Buffer(distance)
    # Run the spatial search with no other restriction
    objects = session.query(Inventory).filter(Inventory.geom.ST_Intersects(buff))
    # Remove initial inventory record from the queryset
    objects = objects.filter(Inventory.id != inventory_id)
    # Optionally restrict queryset to the species of interest
    if species_id is not None:
        if not isinstance(species_id, list):
            species_id = [species_id]
        objects = objects.filter(Inventory.species_id.in_(species_id))
    return {'type': 'FeatureCollection',
            'features': [x.geojson for x in objects]}

neighbourhood = neighborhood


def windows(session, experiment_id, union=True):
    """Retrieve all windows of an experiment

    Overlapping windows are optionally unioned and the properties of the
    individual windows aggregated

    Args:
        session: sqlalchemy database session
        experiment_id (int): Database id of an experiment record
        union (bool): Whether to union (see postgis' ST_Union) the overlapping
            windows

    Return:
        dict: A feature collection of the windows belonging to that experiment
    """
    if union:
        sq = session.query(Trainwindow.geom.ST_Union().ST_Dump().geom.label('geom'))\
                .filter(Trainwindow.experiment_id==experiment_id).subquery()
        q = session.query(sq.c.geom.label('geom'),
                          func.array_agg(Trainwindow.id).label('ids'),
                          func.bool_and(Trainwindow.complete).label('all_complete'))\
                .filter(Trainwindow.experiment_id==experiment_id)\
                .join(sq, sq.c.geom.ST_Intersects(Trainwindow.geom.ST_Centroid()))\
                .group_by(sq.c.geom).all()
        fc = [{'geometry': mapping(to_shape(item.geom)),
               'properties': {'ids': item.ids,
                              'all_complete': item.all_complete}} for item in q]
    else:
        q = session.query(Trainwindow).filter_by(experiment_id=experiment_id)
        fc = [{'geometry': mapping(to_shape(item.geom)),
               'properties': {'ids': [item.id],
                              'all_complete': item.complete}} for item in q]
    return {'type': 'FeatureCollection',
            'features': fc}


def experiments(session):
    """Retrieve all experiments

    Args:
        session: sqlalchemy database session

    Return:
        list: List of experiments (list of dict)
    """
    objects = session.query(Experiment)
    return [obj.dict for obj in objects]


