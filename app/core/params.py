import msgspec

from enum import Enum


class ParamTypes(Enum):
    query = "query"
    header = "header"
    path = "path"
    cookie = "cookie"

class Types(Enum):
    string = "string"
    float = "float"
    integer = "integer"


class HeaderParams(msgspec.Struct, kw_only=True):
    """Header Params"""

    name: str
    _in: str = msgspec.field(default="header", name="in")
    required: bool = msgspec.field(default=True)
    type_field: str
    description: str | None = None
    

class QueryParams(msgspec.Struct, kw_only=True):
    """Query Params"""

    name: str
    _in: str = msgspec.field(default="query", name="in")
    required: bool = msgspec.field(default=True)
    type_field: str
    description: str | None = None
    

class PathParams(msgspec.Struct, kw_only=True):
    """Path Params"""

    name: str
    _in: str = msgspec.field(default="path", name="in")
    required: bool = msgspec.field(default=True)
    type_field: str
    description: str | None = None
    
