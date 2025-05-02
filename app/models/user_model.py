import msgspec
from app.models.model_base import MongoModel


class UserDto(msgspec.Struct, kw_only=True):
    empresa: str
    valor: int


class UserModel(MongoModel):
    __collection__ = "users"

    empresa: str
    cotacao_final: float

