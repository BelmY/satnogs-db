Maintenance
===========


Updating Python dependencies
----------------------------
To update the Python dependencies:

#. Execute script to refresh `requirements.txt` file:

    $ ./contrib/refresh-requirements.sh

#. Stage and commit `requirements.txt` file


Updating frontend dependencies
------------------------------
The frontend dependencies are managed with `npm` as defined in the `package.json`.
The following are required to perform an update of the dependencies:

#. Bump versions in `package.json`

#. Download and install the latest version of the dependencies

    $ npm install

#. Move the installed version into to satnogs-db source tree

    $ ./node_modules/.bin/gulp

#. Stage & commit the updated files in `db/static/`.
