from sqlalchemy import Update, update, func, text

from src.db.models.instantiations.state.sync.data_sources import DataSourcesSyncState


def get_mark_full_data_sources_sync_query() -> Update:
    return update(
        DataSourcesSyncState
    ).values(
        last_full_sync_at=func.now(),
        current_cutoff_date=func.now() - text('interval \'1 day\''),
        current_page=None
    )