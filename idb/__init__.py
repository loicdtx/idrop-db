from sqlalchemy.types import Numeric
from shapely.geometry import shape

from idb.models import Species, Inventory, Interpreted

__version__ = '0.0.1'


def add_inventory_list(session, fc):
    """Add one or many inventory records to the database

    Table Species must already contain all species, see db_init.py command line
    to populate it

    Args:
        session (Session): sqlalchemy database session
        fc (list): Feature collection (list of geojson features)
    """
    if not isinstance(fc, list):
        fc = [fc]
    collection = session.query(Collection).filter_by(name=collection).first()
    instance_list = [Inventory.from_geojson(feature=x, session=session)
                     for x in fc]
    session.add_all(instance_list)



