
The following files are present in this directory OR related to it:
- `script.py.mako`: This is a Mako template file which is used to generate new migration scripts. Whatever is here is used to generate new files within `versions/`. This is scriptable so that the structure of each migration file can be controlled, including standard imports to be within each, as well as changes to the structure of the `upgrade()` and `downgrade()` functions
- `env.py`: The main script that sets up the migration environment.
- `alembic.ini`: The `alembic` configuration file. Located in the root of the repository
- `/versions`: The directory which contains the migration scripts

## Generating a Migration

To generate a new migration, run the following command from the root directory:

```bash
alembic revision --autogenerate -m "Description for migration"
```

Then, locate the new revision script in `/versions` and modify the update and downgrade functions as needed

Once you have generated a new migration, you can upgrade and downgrade the database using the `alembic` command line tool.

Finally, make sure to commit your changes to the repository.