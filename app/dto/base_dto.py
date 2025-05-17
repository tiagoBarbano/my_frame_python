import msgspec


class BaseDto(msgspec.Struct):
    """Data Transfer Object Base"""

    def encode_dict(self) -> dict:
        return msgspec.to_builtins(self)