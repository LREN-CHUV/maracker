# maracker

API aiming to make Human Brain Project's [Medical Informatics Platform's](https://mip.humanbrainproject.eu/intro) developped apps deployment on Mesos Marathon easier.

[![Build Status](https://travis-ci.org/groovytron/maracker.svg?branch=master)](https://travis-ci.org/groovytron/maracker)

## Requirements

* PostgreSQL
* Python 3.6+

*The docker images you want to enter into the database **must** be indexed on the [MicroBadger platform](https://microbadger.com/) as Maracker depends on this API.*

## Installation for local testing

Assuming you already have a working instance of **PostgreSQL** and **Python 3.6**
or later installed and your operating system is **GNU/Linux**, you can install
the API by doing the following actions:

1. `python -m venv venv` to create a virtual environment.
2. `source venv/bin/activate` to activate the environement.
3. `pip install -r requirements.txt` to install the project's dependencies.
4. Create a database named `maracker` in PostgreSQL or choose another name.
5. If you choose another database name and your database user is not
   `postgres`, set the following environment variables  using `export` so
   that Django will have the right database connection information:
   * `DB_NAME`
   * `DB_USER`
   * `DB_PASSWORD`
   * `DB_HOST`
   * `DB_PORT`
6. `cd maracker && python manage.py migrate` to create the database.
7. `python manage.py runserver` to run the API.
8. You can test the API and query it with `curl http://localhost:8000/mipapps`
   which lists the available MIP applications in the database.
9. If you want to add a new application, you can test it using the `test.json`
   file which adds the [MIP's woken container's](https://hub.docker.com/r/hbpmip/woken/)
   data in the database. Just run `curl -X POST http://localhost:8000/mipapps
   -d @test.json -H "Content-Type: application/json"`.

If you want to run the unit tests, use the `manage.py` script and run
`python manage.py test`.
