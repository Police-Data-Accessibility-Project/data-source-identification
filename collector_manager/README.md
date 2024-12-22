The Collector Manager is a class used to manage collectors. It can start, stop, and get info on running collectors.

The following commands are available:

| Command                                  | Description                                                    |
|------------------------------------------|----------------------------------------------------------------|
| list                                     | List running collectors                                        |
| start {collector_name} --config {config} | Start a collector, optionally with a given configuration       |
| status {collector_id}                    | Get status of a collector, or all collectors if no id is given |
| info {collector_id}                      | Get info on a collector, including recent log updates          |
| close {collector_id}                     | Close a collector                                              |
| exit                                     | Exit the collector manager                                     |

This directory consists of the following files:

| File              | Description                                                    |
|-------------------|----------------------------------------------------------------|
| CollectorManager.py      | Main collector manager class                                    |
| CommandHandler.py | Class used to handle commands from the command line interface     |
| CollectorBase.py  | Base class for collectors                                      |
|enums.py           | Enumerations used in the collector manager                      |
| ExampleCollector.py | Example collector                                              |
| main.py           | Main function for the collector manager                         |