import msgspec


class User(msgspec.Struct):
    empresa: str
    valor: int


decode = msgspec.json.Decoder(type=User).decode
encode = msgspec.json.Encoder().encode
