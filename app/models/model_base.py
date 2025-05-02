from bson import ObjectId
import msgspec

from datetime import datetime
from typing import ClassVar
from motor.motor_asyncio import AsyncIOMotorDatabase


class MongoModel(msgspec.Struct, kw_only=True):
    _id: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted: bool = False

    __collection__: ClassVar[str] = ""

    @classmethod
    def create(cls, data: dict = None, **kwargs):
        now = datetime.utcnow()
        raw = {**(data or {}), **kwargs}
        return cls(
            _id=raw.get("_id", str(ObjectId())),
            created_at=raw.get("created_at", now),
            updated_at=raw.get("updated_at", now),
            deleted=raw.get("deleted", False),
            **{
                k: v
                for k, v in raw.items()
                if k not in {"created_at", "updated_at", "deleted"}
            },
        )

    async def save(self, db: AsyncIOMotorDatabase):
        doc_dict = self.to_dict()
        return await self.collection(db).insert_one(doc_dict)

    def to_dict(self):
        return msgspec.to_builtins(self)

    @classmethod
    def collection(cls, db: AsyncIOMotorDatabase):
        return db[cls.__collection__]

    @classmethod
    def mongo_to_model(model_cls, doc):
        doc = dict(doc)
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])
        return model_cls(**doc)

    @classmethod
    async def find_by_id(cls, id: str, db: AsyncIOMotorDatabase):
        result = await cls.collection(db).find_one({"_id": id})

        if not result:
            return None

        result = cls.mongo_to_model(result)

        return result.to_dict()

    @classmethod
    async def find_all(cls, db: AsyncIOMotorDatabase):
        cursor = cls.collection(db).find()
        result = await cursor.to_list(length=None)

        if not result:
            return []

        result = [cls.mongo_to_model(res) for res in result]
        return [res.to_dict() for res in result]

    @classmethod
    async def soft_delete(cls, id: str, db: AsyncIOMotorDatabase):
        cls.deleted = True
        cls.updated_at = datetime.utcnow()
        await cls.collection(db).update_one(
            {"_id": ObjectId(id)},
            {"$set": {"deleted": True, "updated_at": cls.updated_at}},
        )
