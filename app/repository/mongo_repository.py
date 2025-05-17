from typing import TypeVar, Generic, Type
from bson import ObjectId
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.infra.database import MongoManager
from app.models.model_base import MongoModel

T = TypeVar("T", bound=MongoModel)


class MongoRepository(Generic[T]):
    def __init__(self, model_cls: Type[T]):
        self.model_cls = model_cls
        self.collection_name = model_cls.__collection__

    def mongo_to_model(self, doc: dict) -> T:
        doc = dict(doc)
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])
        return self.model_cls(**doc)

    async def save(self, model: T):
        async with MongoManager.get_database() as db:
            return await db[self.collection_name].insert_one(model.to_dict())

    async def find_by_id(self, id: str) -> T | None:
        async with MongoManager.get_database() as db:
            return await db[self.collection_name].find_one({"_id": id})

    async def find_all(
        self, page: int = 1, limit: int = 10
    ) -> list[T]:
        async with MongoManager.get_database() as db:
            data = (
                await db[self.collection_name]
                .find()
                .skip((page - 1) * limit)
                .limit(limit)
                .to_list()
            )

            total_items = await db[self.collection_name].count_documents({})
            total_pages = (total_items + limit - 1) // limit

            return {
                "data": data,
                "page": page,
                "limit": limit,
                "total_items": total_items,
                "total_pages": total_pages,
            }

    async def soft_delete(self, id: str, db: AsyncIOMotorDatabase):
        now = datetime.utcnow()
        with db[self.collection_name] as db:
            await self.collection(db).update_one(
                {"_id": ObjectId(id)},
                {"$set": {"deleted": True, "updated_at": now}},
            )
