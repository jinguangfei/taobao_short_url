import secrets

from src.core.crud import CRUDBase

from src.admin.models import User
from .models import AccountInfo
from .schemas import AccountInfoCreate, AccountInfoUpdate

class AccountInfoController(CRUDBase[AccountInfo, AccountInfoCreate, AccountInfoUpdate]):
    def __init__(self):
        super().__init__(model=AccountInfo)

    def update(self, obj_in: AccountInfoUpdate):
        if obj_in.token is not None:
            obj_in.token = secrets.token_hex(16).upper()
        return super().update(id=obj_in.id, obj_in=obj_in)

    async def get_by_user(self, user: User) -> AccountInfo:
        account_info = await self.model.filter(user=user).first()
        if account_info is None:
            account_info = await self.model.create(
                user=user,
                token=secrets.token_hex(16).upper(),
                balance=0.00,
                is_active=True
            )
        return account_info


account_info_controller = AccountInfoController()

if __name__ == "__main__":
    pass