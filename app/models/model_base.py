import uuid
from bson import ObjectId
import msgspec

from datetime import datetime
from typing import ClassVar
from motor.motor_asyncio import AsyncIOMotorDatabase


class MongoModel(msgspec.Struct, kw_only=True):
    id: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted: bool = False

    __collection__: ClassVar[str] = ""

    @classmethod
    def create(cls, data: dict = None, **kwargs):
        now = datetime.utcnow()
        raw = {**(data or {}), **kwargs}
        return cls(
            id=raw.get("id", str(uuid.uuid4())),
            created_at=raw.get("created_at", now),
            updated_at=raw.get("updated_at", now),
            deleted=raw.get("deleted", False),
            **{
                k: v
                for k, v in raw.items()
                if k not in {"id", "created_at", "updated_at", "deleted"}
            },
        )

    @classmethod
    def collection(cls, db: AsyncIOMotorDatabase):
        return db[cls.__collection__]

    def to_dict(self):
        return msgspec.to_builtins(self)

    @classmethod
    async def mongo_to_model(model_cls, doc):
        doc = dict(doc)
        if "_id" in doc:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
        return model_cls(**doc)

    async def save(self, db: AsyncIOMotorDatabase):
        return await self.collection(db).insert_one(self.to_dict())

    @classmethod
    async def find_by_id(cls, id: str, db: AsyncIOMotorDatabase):
        return await cls.collection(db).find_one({"_id": ObjectId(id)})
    
    @classmethod
    async def soft_delete(cls, id: str, db: AsyncIOMotorDatabase):
        cls.deleted = True
        cls.updated_at = datetime.utcnow()
        await cls.collection(db).update_one(
            {"_id": ObjectId(id)},
            {"$set": {"deleted": True, "updated_at": cls.updated_at}},
        )
