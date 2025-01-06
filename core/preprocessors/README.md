This directory consists of batch preprocessors - classes that take the bespoke outputs of collectors and standardizes their content into a set of URLs with associated metadata to be inserted into the database.

Aside from the `preprocess` method (and any methods called within that), each of these classes follow the same structure, owing to their shared inheritance from `PreprocessorBase`.