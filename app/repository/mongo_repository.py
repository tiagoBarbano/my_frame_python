from typing import TypeVar, Generic, Type
from bson import ObjectId
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.model_base import MongoModel

T = TypeVar("T", bound=MongoModel)


class MongoRepository(Generic[T]):
    def __init__(self, model_cls: Type[T]):
        self.model_cls = model_cls

    def collection(self, db: AsyncIOMotorDatabase):
        return db[self.model_cls.__collection__]

    def mongo_to_model(self, doc: dict) -> T:
        doc = dict(doc)
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])
        return self.model_cls(**doc)

    async def save(self, model: T, db: AsyncIOMotorDatabase):
        return await self.collection(db).insert_one(model.to_dict())

    async def find_by_id(self, id: str, db: AsyncIOMotorDatabase) -> T | None:
        result = await self.collection(db).find_one({"_id": id})
        if not result:
            return None
        return self.mongo_to_model(result)

    async def find_all(self, db: AsyncIOMotorDatabase) -> list[T]:
        cursor = self.collection(db).find()
        return await cursor.to_list(length=None)

    async def soft_delete(self, id: str, db: AsyncIOMotorDatabase):
        now = datetime.utcnow()
        await self.collection(db).update_one(
            {"_id": ObjectId(id)},
            {"$set": {"deleted": True, "updated_at": now}},
        )
