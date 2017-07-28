# maracker

API aiming to make Human Brain Project's [Medical Informatics Platform's](https://mip.humanbrainproject.eu/intro) developped apps deployment on Mesos Marathon easier.

[![Build Status](https://travis-ci.org/groovytron/maracker.svg?branch=master)](https://travis-ci.org/groovytron/maracker)

## Requirements

* PostgreSQL
* Python 3.6+

*The docker images you want to enter into the database **must** be indexed
on the [MicroBadger platform](https://microbadger.com/) as Maracker depends
on this API.*

Here's a [guide](https://medium.com/microscaling-systems/microbadger-keep-your-metadata-fresh-with-a-webhook-651ee26cd4a6)
explaining how to keep your container's metadatas up-to-date in MicroBadger
using a webhook.

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

## Execution details

The infrastructure (Mesos, Marathon, Chronos and Traefik) can be launched
by executing the `run.sh` script. This launches docker containers and
restarts the `traefik` container 50  seconds after the others have been started
so that it connects to `Marathon` correctly. This amount of time can be set
by modifying the `run.sh` script.

The following UIs are accessible after the script executed:

* Marathon: [http://marathon.localhost](http://marathon.localhost)
* Chronos: [http://chronos.localhost](http://chronos.localhost)
* Traefik: [http://traefik.localhost](http://traefik.localhost)
* Maracker: [https://localhost:8000](https://localhost:8000)

You can then try to deploy applications on Marathon using either the examples
in `tests/deployable-marathon-apps` or yours.

If you want to test the developped API, you can try to send the JSON files
in `tests/maracker-use-cases` (`docker-nginx.json`, `docker-webapp.json` or
`docker-webapp2.json`) to the API.

If you you want to stop the stack, launch
`docker-compose -f stack-compose.yml stop`.
