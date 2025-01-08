Generic single-database configuration.


- `script.py.mako`: This is a Mako template file which is used to generate new migration scripts. Whatever is here is used to generate new files within `versions/`. This is scriptable so that the structure of each migration file can be controlled, including standard imports to be within each, as well as changes to the structure of the `upgrade()` and `downgrade()` functions
- `env.py`: The main script that sets up the migration environment.
- `alembic.ini`: The `alembic` configuration file. Located in the root of the repository
- `/versions`: The directory which contains the migration scripts


To generate a new migration, run the following command from the root directory:

```bash
alembic revision --autogenerate -m "Description for migration"
```

Then, locate the new revision script in `/versions` and modify the update and downgrade functions as needed