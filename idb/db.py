from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL
from sqlalchemy.event import listen
from sqlalchemy.sql import select, func

from idb.globals import DB_CONFIG

# Make a dict of URLs and dict of engines
urls = {k:URL(**v) for k,v in DB_CONFIG.items()}
engines = {k:create_engine(v) for k,v in urls.items()}

Base = declarative_base()


def load_spatialite(dbapi_conn, connection_record):
    dbapi_conn.enable_load_extension(True)
    dbapi_conn.load_extension('/usr/lib/x86_64-linux-gnu/mod_spatialite.so')


def init_db(env='main', engines=engines):
    import idb.models
    engine = engines[env]
    if engine.url.drivername.startswith('sqlite'):
        listen(engine, 'connect', load_spatialite)
        conn = engine.connect()
        conn.execute(select([func.InitSpatialMetaData()]))
        conn.close()
    Base.metadata.create_all(bind=engine)


@contextmanager
def session_scope(env='main', engines=engines):
    """Provide a transactional scope around a series of operations.
    """
    engine = engines[env]
    if engine.url.drivername.startswith('sqlite'):
        listen(engine, 'connect', load_spatialite)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
