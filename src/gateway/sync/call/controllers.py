from src.core.crud import CRUDBase

from .models import SyncAPICall
from .schemas import (
    SyncAPICallCreate,
    SyncAPICallUpdate
)


class SyncAPICallController(CRUDBase[SyncAPICall, SyncAPICallCreate, SyncAPICallUpdate]):
    def __init__(self):
        super().__init__(model=SyncAPICall)

sync_api_call_controller = SyncAPICallController()

if __name__ == "__main__":
    pass