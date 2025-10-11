from fastapi import APIRouter, Query, HTTPException
from tortoise.expressions import Q
from src.admin.models import User
from src.admin.schemas import Success, SuccessExtra, Fail
from src.core.ctx import CTX_USER_ID, CTX_Q

from .schemas import AccountInfoCreate, AccountInfoUpdate
from .controllers import account_info_controller

router = APIRouter()

@router.get("/list", summary="查看用户账户信息列表")
async def get_list(
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页条数"),
    user_name: str = Query(None, description="用户名"),
    token: str = Query(None, description="Token"),
):
    q = CTX_Q.get()
    if user_name:
        q &= Q(user__username__icontains=user_name)
    if token:
        q &= Q(token__icontains=token)
    total, account_info_objs = await account_info_controller.list(page=page, page_size=page_size, search=q, order=["id"])
    data = [await obj.to_dict(fk=True,exclude_fields=["password"]) for obj in account_info_objs]
    return SuccessExtra(data=data, total=total, page=page, page_size=page_size)

@router.get("/", summary="查看用户余额")
async def get_balance(
):
    user_id = CTX_USER_ID.get()
    user = await User.get(id=user_id)
    account_info_obj = await account_info_controller.get_by_user(user)
    return Success(data=await account_info_obj.to_dict(fk=True,exclude_fields=["password"]),msg="获取用户信息成功")

@router.post("/update", summary="更新用户账户信息")
async def update_account_info(
    account_info_update: AccountInfoUpdate,
):
    q = CTX_Q.get()
    q &= Q(id=account_info_update.id)
    account_info_obj = await account_info_controller.model.filter(q).first()
    if account_info_obj is None:
        raise HTTPException(status_code=404, detail="没有权限更新用户账户信息")
    account_info_obj = await account_info_controller.update(obj_in=account_info_update)
    return Success(data=await account_info_obj.to_dict(fk=True,exclude_fields=["password"]),msg="更新用户账户信息成功")
