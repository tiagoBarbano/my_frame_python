import msgspec
from app.models.model_base import MongoModel


class UserDto(msgspec.Struct, kw_only=True):
    empresa: str
    valor: int


class User(MongoModel):
    __collection__ = "users"

    empresa: str
    cotacao_final: float


decode = msgspec.json.Decoder().decode
encode = msgspec.json.Encoder().encode
