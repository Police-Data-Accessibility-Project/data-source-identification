from sqlalchemy import Update, update

from src.db.models.instantiations.sync_state.agencies import AgenciesSyncState


def get_update_agencies_sync_progress_query(page: int) -> Update:
    return update(
        AgenciesSyncState
    ).values(
        current_page=page
    )
