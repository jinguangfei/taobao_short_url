from src.core.crud import CRUDBase
from .models import ExtFunction
from .schemas import ExtFunctionCreate, ExtFunctionUpdate

class ExtFunctionController(CRUDBase[ExtFunction, ExtFunctionCreate, ExtFunctionUpdate]):
    def __init__(self):
        super().__init__(model=ExtFunction)

    async def get_by_name(self, name: str) -> ExtFunction:
        return await self.model.get_or_none(name=name)

ext_function_controller = ExtFunctionController()