import msgspec
from typing import ClassVar, Type
from motor.motor_asyncio import AsyncIOMotorDatabase
from objectid_type import OID

class MongoModel(msgspec.Struct, kw_only=True):
    id: OID

    __collection__: ClassVar[str] = ""

    @classmethod
    def collection(cls, db: AsyncIOMotorDatabase):
        return db[cls.__collection__]

    def to_dict(self):
        d = msgspec.to_builtins(self)
        d["_id"] = self.id.to_bson()
        d.pop("id", None)
        return d

    @classmethod
    def from_mongo(cls: Type["MongoModel"], data: dict) -> "MongoModel":
        data["id"] = OID(data["_id"])
        data.pop("_id", None)
        return cls(**data)

    async def save(self, db: AsyncIOMotorDatabase):
        await self.collection(db).insert_one(self.to_dict())

    @classmethod
    async def find_by_id(cls, db: AsyncIOMotorDatabase, oid: OID) -> "MongoModel | None":
        doc = await cls.collection(db).find_one({"_id": oid.to_bson()})
        return cls.from_mongo(doc) if doc else None
