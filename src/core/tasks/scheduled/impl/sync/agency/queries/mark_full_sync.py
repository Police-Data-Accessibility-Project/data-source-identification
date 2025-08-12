from sqlalchemy import update, func, text, Update

from src.db.models.impl.state.sync.agencies import AgenciesSyncState


def get_mark_full_agencies_sync_query() -> Update:
    return update(
        AgenciesSyncState
    ).values(
        last_full_sync_at=func.now(),
        current_cutoff_date=func.now() - text('interval \'1 day\''),
        current_page=None
    )