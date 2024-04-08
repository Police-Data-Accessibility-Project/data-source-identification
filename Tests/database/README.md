
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

## Testing database is online

Run the following command:
```shell
psql -h localhost -p 5432 -U myuser
```

Followed by your password for the dev environment (which by default is `mypassword`).

## Permissions

In order to properly export the schema to the test database, the user will need specific permissions assigned to them in the database:
* FILL IN WHAT THESE ARE, MAX