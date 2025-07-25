This page provides a full list, with description, of all the environment variables used by the application.

Please ensure these are properly defined in a `.env` file in the root directory.

| Name                 | Description                                                                                                                                                                                                                                                       | Example                        |
|----------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------|
| `GOOGLE_API_KEY`     | The API key required for accessing the Google Custom Search API                                                                                                                                                                                                   | `abc123`                       |
| `GOOGLE_CSE_ID`      | The CSE ID required for accessing the Google Custom Search API                                                                                                                                                                                                    | `abc123`                       |
|`POSTGRES_USER`       | The username for the test database                                                                                                                                                                                                                                | `test_source_collector_user`   |
|`POSTGRES_PASSWORD`   | The password for the test database                                                                                                                                                                                                                                | `HanviliciousHamiltonHilltops` |
|`POSTGRES_DB`         | The database name for the test database                                                                                                                                                                                                                           | `source_collector_test_db`     |
|`POSTGRES_HOST`       | The host for the test database                                                                                                                                                                                                                                    | `127.0.0.1`                    |
|`POSTGRES_PORT`       | The port for the test database                                                                                                                                                                                                                                    | `5432`                         |
|`DS_APP_SECRET_KEY`| The secret key used for decoding JWT tokens produced by the Data Sources App. Must match the secret token `JWT_SECRET_KEY` that is used in the Data Sources App for encoding.                                                                                     | `abc123`                       |
|`DEV`| Set to any value to run the application in development mode.                                                                                                                                                                                                      | `true`                         |
|`DEEPSEEK_API_KEY`| The API key required for accessing the DeepSeek API.                                                                                                                                                                                                              | `abc123`                       |
|`OPENAI_API_KEY`| The API key required for accessing the OpenAI API.                                                                                                                                                                                                                | `abc123`                       |
|`PDAP_EMAIL`| An email address for accessing the PDAP API.[^1]                                                                                                                                                                                                                  | `abc123@test.com`               |
|`PDAP_PASSWORD`| A password for accessing the PDAP API.[^1]                                                                                                                                                                                                                        | `abc123`               |
|`PDAP_API_KEY`| An API key for accessing the PDAP API.                                                                                                                                                                                                                            | `abc123`               |
|`PDAP_API_URL`| The URL for the PDAP API| `https://data-sources-v2.pdap.dev/api`|
|`DISCORD_WEBHOOK_URL`| The URL for the Discord webhook used for notifications| `abc123`               |
|`HUGGINGFACE_INFERENCE_API_KEY` | The API key required for accessing the Huggingface Inference API. | `abc123` |

[^1:] The user account in question will require elevated permissions to access certain endpoints. At a minimum, the user will require the `source_collector` and `db_write` permissions.

## Foreign Data Wrapper (FDW)
```
FDW_DATA_SOURCES_HOST=127.0.0.1  # The host of the Data Sources Database, used for FDW setup
FDW_DATA_SOURCES_PORT=1234                  # The port of the Data Sources Database, used for FDW setup
FDW_DATA_SOURCES_USER=fdw_user           # The username for the Data Sources Database, used for FDW setup
FDW_DATA_SOURCES_PASSWORD=password          # The password for the Data Sources Database, used for FDW setup
FDW_DATA_SOURCES_DB=db_name                  # The database name for the Data Sources Database, used for FDW setup

```

## Data Dumper

```
PROD_DATA_SOURCES_HOST=127.0.0.1  # The host of the production Data Sources Database, used for Data Dumper
PROD_DATA_SOURCES_PORT=1234                  # The port of the production Data Sources Database, used for Data Dumper
PROD_DATA_SOURCES_USER=dump_user           # The username for the production Data Sources Database, used for Data Dumper
PROD_DATA_SOURCES_PASSWORD=password          # The password for the production Data Sources Database, used for Data Dumper
PROD_DATA_SOURCES_DB=db_name                  # The database name for the production Data Sources Database, used for Data Dumper
```