from sqlalchemy import update, Update

from src.db.models.instantiations.sync_state.data_sources import DataSourcesSyncState


def get_update_data_sources_sync_progress_query(page: int) -> Update:
    return update(
        DataSourcesSyncState
    ).values(
        current_page=page
    )
