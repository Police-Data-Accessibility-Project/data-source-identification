The Source Collector Core is a directory which integrates:
1. The Collector Manager
2. The Source Collector Database
3. The API (to be developed)
4. The PDAP API Client (to be developed)

# Nomenclature

- **Collector**: A submodule for collecting URLs. Different collectors utilize different sources and different methods for gathering URLs.
- **Batch**: URLs are collected in Collector Batches, with different collectors producing different Batches.
- **Cycle**: Refers to the overall lifecycle for Each URL -- from initial retrieval in a Batch to either disposal or incorporation into the Data Sources App Database
- **Task**: A semi-independent operation performed on a set of URLs. These include: Collection, retrieving HTML data, getting metadata via Machine Learning, and so on.
- **Task Set**: Refers to a group of URLs that are operated on together as part of a single task. These URLs in a set are not necessarily all from the same batch. URLs in a task set should only be operated on in that task once.
- **Task Operator**: A class which performs a single task on a set of URLs.
- **Subtask**: A subcomponent of a Task Operator which performs a single operation on a single URL. Often distinguished by the Collector Strategy used for that URL.