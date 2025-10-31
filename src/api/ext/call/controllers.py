from src.core.crud import CRUDBase

from .models import ExtFunctionCall
from .schemas import (
    ExtFunctionCallCreate,
    ExtFunctionCallUpdate
)


class ExtFunctionCallController(CRUDBase[ExtFunctionCall, ExtFunctionCallCreate, ExtFunctionCallUpdate]):
    def __init__(self):
        super().__init__(model=ExtFunctionCall)

ext_function_call_controller = ExtFunctionCallController()

if __name__ == "__main__":
    pass