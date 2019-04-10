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

    db_init.py

5- Verify that tables have been created properly



Ingest test data into the database
==================================

