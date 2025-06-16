"""
This module tests that revisions perform as expected.
"""


def test_full_upgrade_downgrade(alembic_runner):
    # Both should run without error
    alembic_runner.upgrade("head")
    alembic_runner.downgrade("base")