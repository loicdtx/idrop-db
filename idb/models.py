import datetime as dt

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy import DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
from geoalchemy2.shape import from_shape, to_shape

from shapely.geometry import shape, mapping

from idb.db import Base


class Inventory(Base):
    """Inventory data from IFO"""
    __tablename__ = 'inventories'
    id = Column(Integer, primary_key=True)
    geom = Column(Geometry(geometry_type='POINT', srid=4326))
    species_id = Column(Integer, ForeignKey('species.id'), index=True)
    quality = Column(String)
    tile_id = Column(Integer, ForeignKey('tiles.id'), index=True)
    exp_num = Column(Integer) # Exploitation number
    dbh = Column(Integer)
    interpreted = Column(Boolean) # Whether this sample has already been interpreted or not
    UniqueConstraint(tile_id, exp_num)

    species = relationship("Species", back_populates="inventories")


class Tile(Base):
    """An IFO 50ha tile"""
    __tablename__ = 'tiles'
    id = Column(Integer, primary_key=True)
    geom = Column(Geometry(geometry_type='POLYGON', srid=4326))
    name = Column(String, unique=True)


class Species(Base):
    """Species of the inventory"""
    __tablename__ = 'species'
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True)
    name = Column(String, unique=True)


class Interpreted(Base):
    """Visually interpreted data"""
    __tablename__ = 'interpreted'
    id = Column(Integer, primary_key=True)
    geom = Column(Geometry(geometry_type='POLYGON', srid=4326))
    species_id = Column(Integer, ForeignKey('species.id'), index=True)
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
        return self.meta

Species.interpreted = relationship("Interpreted", back_populates="species")
Species.inventory = relationship("Inventory", back_populates="species")




Collection.items = relationship("Item", back_populates="collection")


