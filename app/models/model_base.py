from bson import ObjectId
import msgspec

from datetime import datetime
from typing import ClassVar


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

    def to_dict(self):
        return msgspec.to_builtins(self)
