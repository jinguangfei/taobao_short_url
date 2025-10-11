from datetime import datetime
from fastapi import APIRouter, Query, HTTPException
from tortoise.expressions import Q
from src.admin.schemas import Success, SuccessExtra, Fail
from src.core.ctx import CTX_USER_ID, CTX_Q

from .schemas import AccountCostCreate, AccountCostUpdate, CostType
from .controllers import account_cost_controller

router = APIRouter()

@router.get("/list", summary="查看Cost列表")
async def list_cost(
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    cost_type: CostType = Query(None, description="消费类型"),
    start_time: datetime = Query(None, description="开始时间"),
    end_time: datetime = Query(None, description="结束时间"),
    username: str = Query(None, description="用户名"),
    remark: str = Query(None, description="备注"),
    item: str = Query(None, description="消费项目"),
):
    q = CTX_Q.get()
    if cost_type is not None:
        q &= Q(cost_type=cost_type)
    if start_time is not None:
        q &= Q(created_at__gte=start_time)
    if end_time is not None:
        q &= Q(created_at__lte=end_time)
    if username:
        q &= Q(user__username=username)
    if remark:
        q &= Q(remark__icontains=remark)
    if item:
        q &= Q(item=item)
    total, cost_objs = await account_cost_controller.list(page=page, page_size=page_size, search=q, order=["id"])
    data = [await obj.to_dict(fk=True,exclude_fields=["password"]) for obj in cost_objs]
    return SuccessExtra(data=data, total=total, page=page, page_size=page_size)

@router.post("/create", summary="创建订单")
async def create_cost(
    cost_in: AccountCostCreate,
):
    cost_obj = await account_cost_controller.create(obj_in=cost_in)
    return Success(data=await cost_obj.to_dict())
