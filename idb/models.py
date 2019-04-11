import datetime as dt

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy import DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
from geoalchemy2.shape import from_shape, to_shape

from shapely.geometry import shape, mapping

from idb.db import Base
from idb.utils import get_or_create


class Species(Base):
    """Species of the inventory"""
    __tablename__ = 'species'
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True)
    name = Column(String, unique=True)

    inventories = relationship("Inventory", back_populates='species')
    interpreted = relationship("Interpreted", back_populates='species')


class Inventory(Base):
    """Inventory data from IFO"""
    __tablename__ = 'inventory'
    id = Column(Integer, primary_key=True)
    geom = Column(Geometry(geometry_type='POINT', srid=4326))
    species_id = Column(Integer, ForeignKey('species.id'), index=True)
    quality = Column(String)
    tile_id = Column(Integer, ForeignKey('tile.id'), index=True, nullable=True)
    exp_num = Column(Integer) # Exploitation number
    dbh = Column(Integer)
    is_interpreted = Column(Boolean) # Whether this sample has already been interpreted or not
    UniqueConstraint(tile_id, exp_num)

    species = relationship("Species", back_populates="inventories")
    tile = relationship("Tile", back_populates="inventories")

    @classmethod
    def from_geojson(cls, feature, session):
        """Create an instance of Inventory from a geojson feature

        The feature must be a point with at least the following attributes.
        ESPE_CODE: 3 letter code of the species
        CLAS_CODE: Diameter
        QUAL_CODE: Quality code
        EXPLOIT_NU: exploitation number
        PLACETTE: Name of the inventory tile
        """
        # Load Species object
        sp = session.query(Species)\
                .filter_by(code=feature['properties']['ESPE_CODE'])\
                .first()
        tile = get_or_create(session=session, model=Tile,
                             name=feature['properties']['PLACETTE'])
        geom = from_shape(shape(feature['geometry']), 4326)
        return cls(geom=geom,
                   species=sp,
                   tile=tile,
                   quality=feature['properties'].get('QUAL_CODE', None),
                   exp_num=int(feature['properties']['EXPLOIT_NU']),
                   dbh=int(feature['properties']['CLAS_CODE']),
                   is_interpreted=False)


class Interpreted(Base):
    """Visually interpreted data"""
    __tablename__ = 'interpreted'
    id = Column(Integer, primary_key=True)
    geom = Column(Geometry(geometry_type='POLYGON', srid=4326))
    species_id = Column(Integer, ForeignKey('species.id'), index=True)
    inventory_id = Column(Integer, ForeignKey('inventory.id'))
    time_created = Column(DateTime(timezone=True), server_default=func.now())

    species = relationship("Species", back_populates="interpreted")

    @classmethod
    def from_geojson(cls, feature, species, session=None):
        """Class method to instantiate an Item object from a metadata description

        Args:
            feature (dict): A geojson feature that complies with the item json
                schema
            species (str or idb.models.Species): Species associated with the interpreted sample
            session (Session): Optional database session. Only required when species is
                a string.
        """
        # Load collection object
        if isinstance(collection, str):
            collection = session.query(Collection).filter_by(name=collection).first()
        # Validate geojson feature
        validate(feature, ITEM_SCHEMA)
        # Build geom
        geom = from_shape(shape(feature['geometry']), 4326)
        # Parse datetime
        t = dt.datetime.strptime(feature['properties']['datetime'],
                                 '%Y-%m-%dT%H:%M:%SZ')
        # Build object
        return cls(name=feature['id'],
                   geom=geom,
                   time=t,
                   meta=feature,
                   collection=collection)

    @property
    def geojson(self):
        pass


class Tile(Base):
    """An IFO 50ha tile"""
    __tablename__ = 'tile'
    id = Column(Integer, primary_key=True)
    geom = Column(Geometry(geometry_type='POLYGON', srid=4326))
    name = Column(String, unique=True)

    inventories = relationship("Inventory", back_populates='tile')

    @classmethod
    def from_geojson(cls, feature):
        """Create an instance of Tile from a geojson feature

        The feature must be a polygon with name as attribute
        """
        geom = from_shape(shape(feature['geometry']), 4326)
        return cls(geom=geom,
                   name=feature['properties']['name'])


class Studyarea(Base):
    """Study areas, mostly used to restrict query to a given zone

    Does not have explicit relation with other tables
    """
    __tablename__ = 'studyarea'
    id = Column(Integer, primary_key=True)
    geom = Column(Geometry(geometry_type='POLYGON', srid=4326))
    name = Column(String, unique=True)


