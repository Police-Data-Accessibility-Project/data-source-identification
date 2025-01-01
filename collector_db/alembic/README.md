Generic single-database configuration.


- `script.py.mako`: This is a Mako template file which is used to generate new migration scripts. Whatever is here is used to generate new files within `versions/`. This is scriptable so that the structure of each migration file can be controlled, including standard imports to be within each, as well as changes to the structure of the `upgrade()` and `downgrade()` functions