from typing import Annotated
import msgspec

from app.dto.base_dto import BaseDto
from app.models.user_model import UserModel


class UserRequestDto(BaseDto, kw_only=True):
    """Data Transfer Object Request for User"""

    empresa: Annotated[str, msgspec.Meta(description="Empresa da Porto Seguro")]
    valor: Annotated[int, msgspec.Meta(description="Valor referente ao produto", gt=0)]


class UserResponseDto(BaseDto, kw_only=True):
    """Data Transfer Object Response for User"""

    empresa: Annotated[str, msgspec.Meta(description="Empresa da Porto Seguro")]
    cotacao_final: Annotated[float, msgspec.Meta(description="Valor da Cotacao Final")]

class CotadorListResponse(BaseDto, kw_only=True):
    data: list[UserModel]
    page: int
    limit: int
    total_items: int
    total_pages: int