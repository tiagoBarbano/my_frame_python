from typing import Annotated
import msgspec


class BaseDto(msgspec.Struct):
    """Data Transfer Object Base"""

    def encode_dict(self) -> dict:
        return msgspec.to_builtins(self)


class UserRequestDto(BaseDto, kw_only=True):
    """Data Transfer Object Request for User"""

    empresa: Annotated[str, msgspec.Meta(description="Empresa da Porto Seguro")]
    valor: Annotated[int, msgspec.Meta(description="Valor referente ao produto", gt=0)]


class UserResponseDto(BaseDto, kw_only=True):
    """Data Transfer Object Response for User"""

    empresa: Annotated[str, msgspec.Meta(description="Empresa da Porto Seguro")]
    cotacao_final: Annotated[float, msgspec.Meta(description="Valor da Cotacao Final")]
