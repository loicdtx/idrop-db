Install
=======

1- Install postgres + postgis

2- Create database configuration file

Example minimum configuration file (name: ``~/.idb``)

.. code-block:: python

    [main]
    drivername=postgresql
    database=idrop
    # hostname=
    # password=
    # username=


3- Create database and add postgis extention

.. code-block:: bash

    createdb idrop
    psql idrop -c "CREATE EXTENSION postgis;"
    psql idrop -c "CREATE EXTENSION postgis_topology;"
    # Optionally create dedicated user (probably better for remote access)
    psql idrop -c "CREATE USER idrop_user WITH PASSWORD 'qwerty' CREATEDB;"

4- Create tables

.. code-block:: bash

    db_init.py --species tests/data/species.csv

5- Verify that tables have been created properly



Ingest test data into the database
==================================

Navigate to the ``tests`` directory and run the ``ingests_test_data.py`` script.

.. code-block:: bash

    cd tests
    ./ingests_test_data.py


Using different databases
=========================

Several databases can be configured in the same configuration file. For instance
the example below combines two postgis databases in addition to a spatialite file
database.

.. code-block:: python

    [main]
    drivername=postgresql
    database=idrop

    [test]
    drivername=postgresql
    database=idrop-tests

    [sqlite]
    drivername=sqlite
    database=/tmp/test_db.sqlite
    # Valid variable keys are those used by sqlalchemy.engine.url.URL

By default all idb commands and functions use the ``main`` environment. Using another
environment requires passing its name to the ``env=`` argument in ``idb.db.session_scope()`` (also ``idb.db.init_db()``) or using the ``--env`` argument of command lines.
