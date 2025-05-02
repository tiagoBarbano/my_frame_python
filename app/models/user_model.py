import msgspec
from app.models.model_base import MongoModel

class User(MongoModel):
    __collection__ = "users"

    empresa: str
    valor: int


decode = msgspec.json.Decoder(type=User).decode
encode = msgspec.json.Encoder().encode
