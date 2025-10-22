from typing import Any, Dict, Generic, List, NewType, Tuple, Type, TypeVar, Union
import uuid

from pydantic import BaseModel
from tortoise.expressions import Q
from tortoise.models import Model

Total = NewType("Total", int)
ModelType = TypeVar("ModelType", bound=Model)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, id: int) -> ModelType:
        return await self.model.get(id=id)

    async def list(
        self, 
        page: int, 
        page_size: int, 
        search: Q = Q(), 
        order: list = [],
        prefetch_related: list = [],  # 用于 m2m 关系
        select_related: list = []     # 用于 fk 关系
    ) -> Tuple[Total, List[ModelType]]:
        query = self.model.filter(search)
        
        # 预加载多对多关系
        if prefetch_related:
            query = query.prefetch_related(*prefetch_related)
        
        # 预加载外键关系
        if select_related:
            query = query.select_related(*select_related)
            
        return await query.count(), await query.offset((page - 1) * page_size).limit(page_size).order_by(*order)

    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        if isinstance(obj_in, Dict):
            obj_dict = obj_in
        else:
            obj_dict = obj_in.model_dump()
        
        # 检查模型是否有 uuid 字段，如果有则自动生成
        if hasattr(self.model, 'uuid') and 'uuid' not in obj_dict:
            obj_dict['uuid'] = uuid.uuid4()
        
        obj = self.model(**obj_dict)
        await obj.save()
        return obj

    async def update(self, id: int, obj_in: Union[UpdateSchemaType, Dict[str, Any]]) -> ModelType:
        if isinstance(obj_in, Dict):
            obj_dict = obj_in
        else:
            obj_dict = obj_in.model_dump(exclude_unset=True, exclude={"id"})
        obj = await self.get(id=id)
        obj = obj.update_from_dict(obj_dict)
        await obj.save()
        return obj

    async def remove(self, id: int) -> None:
        obj = await self.get(id=id)
        await obj.delete()
    
    async def update_or_create(self, defaults: Dict[str, Any], **kwargs) -> Tuple[ModelType, bool]:
        """
        更新或创建对象
        :param defaults: 要更新/创建的字段值
        :param kwargs: 用于查询的条件
        :return: (对象, 是否创建) - created=True 表示新创建，False 表示更新
        """
        obj, created = await self.model.update_or_create(defaults=defaults, **kwargs)
        return obj, created