

"""
A class which, on run, checks to see if the prod-schema.sql exists.
If it doesn't, it pulls it using information from the .env file
"""
import os
import subprocess
from pathlib import Path
from dotenv import load_dotenv

def is_file_empty(file_path):
    """Check if file is empty by confirming if its size is 0 bytes"""
    # Check if file exist and it is empty
    return os.path.exists(file_path) and os.stat(file_path).st_size == 0


class ProdSchemaManager:

    def load_environment_variables(self, env_vars: list[str]) -> dict[str, str]:
        env_vars_dict = {}
        for env_var in env_vars:
            env_vars_dict[env_var] = os.getenv(env_var)

        # Check if any of the variables are None
        missing_vars = {k: v for k, v in env_vars_dict.items() if v is None}

        if missing_vars:
            s = "The following required environment variables are missing:\n"
            for k, v in missing_vars.items():
                s += f"- {k}\n"
            raise EnvironmentError(s)
        else:
            print("All required environment variables are set.")

        return env_vars_dict

    def get_absolute_path_of_file_in_same_directory(self, file_name) -> Path:
        # Get the absolute path of the directory where the class is located
        dir_path = os.path.dirname(os.path.abspath(__file__))
        # Combine dir_path and filename
        return Path(os.path.join(dir_path, file_name))

    def __init__(self, env_file: str = 'setup.env'):
        self.env_file = Path(env_file)
        self.schema_path = self.get_schema_path()

    def get_schema_path(self) -> Path:
        """
        Get absolute path of prod-schema.sql file
        If it does not exist, use information from the env file to retrieve it
        Returns:
        """

        # prod-schema.sql should be in the same directory of this class.
        # If it is not found, must retrieve it
        file_path = self.get_absolute_path_of_file_in_same_directory('prod-schema.sql')
        if is_file_empty(file_path):
            print("prod-schema.sql file not found: Attempting to download...")
            self.download_production_schema(file_path)
            print(f"Schema file downloaded: {file_path}")

        assert not is_file_empty(file_path)
        return file_path

    def download_production_schema(self, file_path: Path):
        env_file_path = self.get_absolute_path_of_file_in_same_directory(self.env_file)
        load_dotenv(dotenv_path=env_file_path)

        env_vars = self.load_environment_variables(
            env_vars = [
                'DIGITAL_OCEAN_DB_HOST',
                'DIGITAL_OCEAN_DB_PORT',
                'DIGITAL_OCEAN_DB_USERNAME',
                'DIGITAL_OCEAN_DB_NAME',
                'DIGITAL_OCEAN_DB_PASSWORD',
            ]
        )

        cmd = [
            'pg_dump',
            '-h', env_vars['DIGITAL_OCEAN_DB_HOST'],
            '-p', env_vars['DIGITAL_OCEAN_DB_PORT'],
            '-U', env_vars['DIGITAL_OCEAN_DB_USERNAME'],
            '-d', env_vars['DIGITAL_OCEAN_DB_NAME'],
            '--no-owner',
            '--no-privileges',
            '-s'
        ]

        with open(file_path, 'w') as output_file:
            pg_dump_process = subprocess.Popen(
                cmd,
                env=dict(
                    **os.environ,
                    PGPASSWORD=env_vars['DIGITAL_OCEAN_DB_PASSWORD']
                ),
                stdout=output_file,
            )
            stdout, stderr = pg_dump_process.communicate()

        if pg_dump_process.returncode != 0:
            # Handle error
            raise IOError(f'Error occurred: {stderr}')
        else:
            print('Command executed successfully')

if __name__ == "__main__":
    manager = ProdSchemaManager()
    print(f"production schema is located at {manager.schema_path}")