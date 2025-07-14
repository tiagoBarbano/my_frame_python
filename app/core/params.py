from typing import Any
import msgspec


class BaseParams(msgspec.Struct, kw_only=True):
    """Base Params"""
    name: str
    required: bool = msgspec.field(default=False)
    type_field: str
    description: str | None = None
    example: Any = None
    deprecated: bool = False
    allow_empty_value: bool = False
    maxLength: int | None = None
    minLength: int | None = None
    enum: list[Any] | None = None
    pattern: str | None = None
    default: Any = None  # ← valor padrão adicional

    def encode_dict(self) -> dict:
        return msgspec.to_builtins(self)


class HeaderParams(BaseParams, kw_only=True):
    """Header Params"""

    _in: str = msgspec.field(default="header", name="in")


class QueryParams(BaseParams, kw_only=True):
    """Query Params"""

    _in: str = msgspec.field(default="query", name="in")


class PathParams(BaseParams, kw_only=True):
    """Path Params"""

    _in: str = msgspec.field(default="path", name="in")
    required: bool = msgspec.field(default=True)


class CookieParams(msgspec.Struct, kw_only=True):
    """Cookie Parameter"""

    _in: str = msgspec.field(default="cookie", name="in")
