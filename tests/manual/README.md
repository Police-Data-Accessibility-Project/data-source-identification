This directory contains manual tests -- that is, tests which are designed to be run separate from automated tests.
 

This is typically best the tests in question involve calls to third party APIs and retrieval of life dave. Thus, they are not cost effective to run automatically.

Unlike `test_automated`, which has the `test` prefix so it can be automatically run by Pytest, this directory does not have the `test` prefix, just to further emphasize that you should NOT run these all at once.