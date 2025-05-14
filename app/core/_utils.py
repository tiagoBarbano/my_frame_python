import re
import msgspec
import orjson

from jsonschema import Draft7Validator, ValidationError


from functools import lru_cache


@lru_cache(maxsize=128)
def get_validator(model_cls):
    schema = msgspec.json.schema(model_cls)
    validator = Draft7Validator(schema["$defs"][model_cls.__name__])
    return validator


async def validate_schema_dict(body, ModelDto):
    data = orjson.loads(body) if isinstance(body, bytes) else body
    validator = get_validator(ModelDto)

    erros = sorted(validator.iter_errors(data), key=lambda e: e.path)
    if erros:
        message_error = [e.args[0] for e in erros]
        raise ValidationError(message=message_error)

    return ModelDto(**data).encode_dict()


async def validate_schema_object(body, ModelDto):
    data = orjson.loads(body) if isinstance(body, bytes) else body
    validator = get_validator(ModelDto)

    erros = sorted(validator.iter_errors(data), key=lambda e: e.path)
    if erros:
        message_error = [e.args[0] for e in erros]
        raise ValidationError(message=message_error)

    return ModelDto(**data)

def compile_path_to_regex(path_template):
    # Converte /item/{id} → ^/item/(?P<id>[^/]+)$
    pattern = re.sub(r"{(\w+)}", r"(?P<\1>[^/]+)", path_template)
    return re.compile(f"^{pattern}$")
