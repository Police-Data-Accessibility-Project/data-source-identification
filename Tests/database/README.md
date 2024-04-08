
## Setup

Install requirements located in `database_test_requirements.txt` via the command

```shell
pip install -r database_test_requirements.txt
```

Additionally, you will need to install [PostgreSQL](https://www.postgresql.org/download/) for your operating system.
This is necessary in order to run the `pg_dump` command which pulls the production database schema for development.

## Environment Variable

Create a file named `setup.env` and fill it with the following values. 
Note that `your_username` and `your_password` are placeholders to be replaced with your own values.

* DIGITAL_OCEAN_DB_USERNAME=your_username
* DIGITAL_OCEAN_DB_PASSWORD=your_password
* DIGITAL_OCEAN_DB_HOST=db-postgresql-nyc3-38355-do-user-8463429-0.c.db.ondigitalocean.com
* DIGITAL_OCEAN_DB_PORT=25060
* DIGITAL_OCEAN_DB_NAME=defaultdb
* TEST_DATABASE_HOST=localhost (or whatever host the test database is on, such as `host.docker.internal`)

## Testing database is online

Run the following command:
```shell
psql -h localhost -p 5432 -U myuser
```

Followed by your password for the dev environment (which by default is `mypassword`).

## Permissions

In order to properly export the schema to the test database, the user will need specific permissions assigned to them in the database:
* FILL IN WHAT THESE ARE, MAX

## Troubleshooting

This is a more-complicated-than-usual system, so bugs are to be expected. Here are some of the more common errors:

### pgdump not up to date

If the pgdump is not up to date (as of this writing, to Postgres-15), this may not work. In Linux, the solution to this is the following series of commands:
```shell
sudo apt install -y postgresql-common
sudo /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh
sudo apt update
sudo apt install postgresql-15
```

### Check connecting host

While the port, user, and password should remain generally static, the host can vary depending on the container the postgres database is hosted on.
In `test_dev_database.py`, the `host` parameter is set to `localhost` by default. 

However, in some contexts, this host parameter may differ, and will need to be modified. To do so, modify the `TEST_DATABASE_HOST` environmental variable in your `setup.env` file.
