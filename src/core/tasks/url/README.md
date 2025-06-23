URL Tasks are tasks that operate on the URL level. 

Such tasks will operate if a single URL meets that tasks's prerequisites, but typically operate on a batch of URLs at a time.

The suite of URL tasks are checked on an hourly basis (via a scheduled task) and are also triggered in response to certain events, such as the completion of a batch. 

## Terminology

Task Data Objects (or TDOs) are data transfer objects (DTOs) used within a given task operation. Each Task type has one type of TDO.