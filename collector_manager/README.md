The Collector Manager is a class used to manage collectors. It can start, stop, and get info on running collectors.


This directory consists of the following files:

| File              | Description                                                    |
|-------------------|----------------------------------------------------------------|
| CollectorManager.py      | Main collector manager class                                    |
| CommandHandler.py | Class used to handle commands from the command line interface     |
| CollectorBase.py  | Base class for collectors                                      |
|enums.py           | Enumerations used in the collector manager                      |
| ExampleCollector.py | Example collector                                              |
| main.py           | Main function for the collector manager                         |


## Creating a Collector

1. All collectors must inherit from the CollectorBase class.
2. Once created, the class must be added to the `COLLECTOR_MAPPING` dictionary located in `collector_mapping.py`
3. The class must have a `config_schema` attribute: a marshmallow schema that defines the configuration for the collector.
4. The class must have an `output_schema` attribute: a marshmallow schema that defines and validates the output of the collector.
5. The class must have a `run_implementation` method: this method is called by the collector manager to run the collector. It must regularly log updates to the collector manager using the `log` method, and set the final data to the `data` attribute.
6. For ease of use, the `run_implementation` method should call a method within the inner class that is a generator which returns regular status updates as a string after every iteration of the method's loop, to ensure granular status updates.