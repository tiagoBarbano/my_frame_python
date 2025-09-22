from typing import Annotated
import msgspec

from app.dto.base_dto import BaseDto


class UserRequestDto(BaseDto, kw_only=True):
    """Data Transfer Object Request for User"""

    empresa: Annotated[
        str,
        msgspec.Meta(
            description="Empresa da Porto Seguro",
            extra={"error": "O campo empresa é obrigatório e deve ser uma string"},
        ),
    ]
    valor: Annotated[
        int,
        msgspec.Meta(
            description="Valor referente ao produto",
            gt=0,
            extra={"error": "O campo valor deve ser numerico e maior que zero"},
        ),
    ]


class UserResponseDto(BaseDto, kw_only=True):
    """Data Transfer Object Response for User"""

    _id: Annotated[str, msgspec.Meta(description="ID unico do banco de dados")]
    empresa: Annotated[str, msgspec.Meta(description="Empresa da Porto Seguro")]
    cotacao_final: Annotated[float, msgspec.Meta(description="Valor da Cotacao Final")]


class UserListResponse(BaseDto, kw_only=True):
    data: list[UserResponseDto]
    page: Annotated[int, msgspec.Meta(description="Numero da pagina atual")]
    limit: Annotated[int, msgspec.Meta(description="Quantidade de registro por pagina")]
    total_items: Annotated[
        int, msgspec.Meta(description="Quantidade Total de Registros")
    ]
    total_pages: Annotated[int, msgspec.Meta(description="Quantidade Total de pagina")]
