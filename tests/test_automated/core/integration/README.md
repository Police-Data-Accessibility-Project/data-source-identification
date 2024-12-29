These are automated integration tests which are designed to test the entire lifecycle of a source collector -- that is, its progression from initial call, to completion, to batch preprocessing and ingestion into the database.

These tests make use of the Example Collector - a simple collector which generates fake urls and saves them to the database.