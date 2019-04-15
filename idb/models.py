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

    @property
    def dict(self):
        return {'id': self.id,
                'code': self.code,
                'name': self.name}


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

    @property
    def geojson(self):
        feature = {'type': 'Feature',
                   'properties': {'species_name': self.species.name,
                                  'species_code': self.species.code,
                                  'species_id': self.species_id,
                                  'quality': self.quality,
                                  'dbh': self.dbh,
                                  'id': self.id},
                   'geometry': mapping(to_shape(self.geom))}
        return feature


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
    def from_geojson(cls, feature):
        """Class method to instantiate an Interpreted object from a feature

        Args:
            feature (dict): A geojson feature with at least ``species_id`` and
                ``inventory_id`` attributes
        """
        # Build geom
        geom = from_shape(shape(feature['geometry']), 4326)
        # Build object
        return cls(geom=geom,
                   species_id=feature['properties']['species_id'],
                   inventory_id=feature['properties']['inventory_id'])

    @property
    def geojson(self):
        feature = {'type': 'Feature',
                   'properties': {'species_id': self.species_id,
                                  'species_name': self.species.name,
                                  'inventory_id': self.inventory_id,
                                  'id': self.id},
                   'geometry': mapping(to_shape(self.geom))}
        return feature


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

    @property
    def geojson(self):
        feature = {'type': 'Feature',
                   'properties': {'name': self.name,
                                  'id': self.id},
                   'geometry': mapping(to_shape(self.geom))}
        return feature

    @classmethod
    def from_geojson(cls, feature):
        geom = from_shape(shape(feature['geometry']), 4326)
        return cls(geom=geom,
                   name=feature['properties']['name'])




