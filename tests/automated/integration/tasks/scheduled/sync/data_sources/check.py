from datetime import timedelta

from sqlalchemy import select, cast, func, TIMESTAMP

from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.instantiations.state.sync.data_sources import DataSourcesSyncState
from src.db.models.instantiations.url.core.sqlalchemy import URL


async def check_sync_concluded(
    db_client: AsyncDatabaseClient,
    check_updated_at: bool = True
):

    current_db_datetime = await db_client.scalar(
        select(
            cast(func.now(), TIMESTAMP)
        )
    )

    sync_state_results = await db_client.scalar(
        select(
            DataSourcesSyncState
        )
    )
    assert sync_state_results.current_page is None
    assert sync_state_results.last_full_sync_at > current_db_datetime - timedelta(minutes=5)
    assert sync_state_results.current_cutoff_date > (current_db_datetime - timedelta(days=2)).date()

    if not check_updated_at:
        return

    updated_ats = await db_client.scalars(
        select(
            URL.updated_at
        )
    )
    assert all(
        updated_at > current_db_datetime - timedelta(minutes=5)
        for updated_at in updated_ats
    )