Install
=======

1- Install postgres + postgis
2- Create database configuration file

Example minimum configuration file (name: ``~/.idb``)

.. code-block:: python

    [idb]
    db_database=idrop
    # db_hostname=
    # db_password=
    # db_username=


3- Create database and add postgis extention

.. code-block:: bash

    createdb idrop
    psql idrop -c "CREATE EXTENSION postgis;"
    psql idrop -c "CREATE EXTENSION postgis_topology;"

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
