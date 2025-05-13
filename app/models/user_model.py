from typing import Annotated
import msgspec

from app.models.model_base import MongoModel

def validate_all_fields(data: dict, ModelDTO) -> dict:
    errors = {}

    for field in ModelDTO.__struct_fields__:
        field_type = ModelDTO.__annotations__[field]
        value = data.get(field)

        try:
            msgspec.convert(value, type=field_type)
        except msgspec.ValidationError as e:
            errors[field] = str(e)

    if errors:
        raise ValueError(errors)

    return data


class UserDto(msgspec.Struct, kw_only=True):
    """Data Transfer Object for User"""
    empresa: Annotated[str, msgspec.Meta(description="Empresa da Porto Seguro")]
    valor: Annotated[int, msgspec.Meta(description="Valor referente ao produto", gt=0)]
    index: float | None = None
    cotacao: float | None = None
    

class UserModel(MongoModel):
    __collection__ = "users"

    empresa: str
    cotacao_final: float

