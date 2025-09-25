import re
from urllib.parse import parse_qs
import msgspec

from jsonschema import Draft7Validator, ValidationError

from functools import lru_cache


@lru_cache(maxsize=128)
def get_validator(model_cls):
    schema = msgspec.json.schema(model_cls)
    validator = Draft7Validator(schema["$defs"][model_cls.__name__])
    return validator



async def validate_schema(body, ModelDto, return_dict=False):
    """
    Valida o body contra o schema ModelDto.
    Se return_dict=True, retorna um dict. Senão retorna instância do ModelDto.
    """
    data = (
        body
        if isinstance(body, dict)
        else (msgspec.json.decode(body) if isinstance(body, bytes) else body)
    )
    validator = get_validator(ModelDto)

    if errors := sorted(validator.iter_errors(data), key=lambda e: e.path):
        message_error = []
        for e in errors:
            campo = ".".join(str(p) for p in e.path) or e.schema_path[-1]
            # Pega a anotação do campo
            annot = ModelDto.__annotations__.get(campo)
            # Inicializa msg com a mensagem padrão do validator
            msg = e.message

            # Se for Annotated e tiver msgspec.Meta com extra["error"], sobrescreve
            if getattr(annot, "__metadata__", None):
                for meta in annot.__metadata__:
                    if isinstance(meta, msgspec.Meta):
                        extra = meta.extra or {}  # garante que extra seja dict
                        msg = extra.get("error", msg)  # usa 'error' se existir, senão a msg padrão                        
                        
            message_error.append({
                "campo": campo,
                "mensagem": msg,
                "validador": e.validator
            })

        raise ValidationError({"detalhes": message_error, "body": body})

    instance = ModelDto(**data)
    return instance.encode_dict() if return_dict else instance



@lru_cache(maxsize=256)
def compile_path_to_regex(path_template):
    """
    Convert a path template with placeholders into a regex pattern.
    This function takes a path template string (e.g., "/item/{id}")
    and converts it into a regex pattern that can be used for matching.
    The placeholders in the path template are replaced with regex groups
    that capture the corresponding values.
    For example, "/item/{id}" becomes "^/item/(?P<id>[^/]+)$".
    """

    pattern = re.sub(r"{(\w+)}", r"(?P<\1>[^/]+)", path_template)
    return re.compile(f"^{pattern}$")


def _build_headers(content_type: bytes, headers: dict[str, str] = None):
    result = [
        (k.encode("utf-8"), v.encode("utf-8")) for k, v in (headers or {}).items()
    ]
    result.append((b"content-type", content_type))
    return result


def json_response(data, status=200, headers: dict[str, str] = None):
    """
    Return a response with JSON content type.
    This function takes the response data and status code as input
    and returns a tuple containing the status code, headers, and body.
    The headers include the content type set to "application/json".
    """
    return (
        status,
        _build_headers(b"application/json", headers),
        [msgspec.json.encode(data)],
    )


def text_plain_response(data, status=200, headers=None):
    """
    Return a response with plain text content type.
    This function takes the response data and status code as input
    and returns a tuple containing the status code, headers, and body.
    The headers include the content type set to "text/plain".
    """
    return status, _build_headers(b"text/plain", headers), [data]


def text_html_response(data, status=200, headers=None):
    """
    Return a response with HTML content type.
    This function takes the response data and status code as input
    and returns a tuple containing the status code, headers, and body.
    The headers include the content type set to "text/html".
    """
    return status, _build_headers(b"text/html", headers), [data]


async def read_body(receive) -> dict:
    """
    Read the body of the request from the ASGI receive channel.
    This function handles chunked transfer encoding and concatenates
    the received chunks into a single bytes object.
    It returns the complete request body as a dictionary.
    """
    body = bytearray()
    while True:
        message = await receive()
        if message["type"] != "http.request":
            continue
        body.extend(message.get("body", b""))
        if not message.get("more_body", False):
            break
    return msgspec.json.decode(body)


async def send_response(send, response):
    """
    Send an HTTP response to the ASGI send channel.
    This function takes the ASGI send channel and a response tuple
    containing the status code, headers, and body.
    It sends the response start message and then sends the response body
    in chunks.
    """
    status, headers, body_chunks = response
    await send({"type": "http.response.start", "status": status, "headers": headers})
    for chunk in body_chunks:
        await send({"type": "http.response.body", "body": chunk})

def get_query_param(scope, name: str, default=None, cast=str):
    query = parse_qs(scope.get("query_string", b"").decode())
    value = query.get(name, [default])[0]
    return cast(value) if value is not None else default

async def response(send, data, status=200, headers=None):
    return await send_response(send, json_response(data, status=status, headers=headers))