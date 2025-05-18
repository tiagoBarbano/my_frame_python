import pytest
import msgspec
import orjson
from jsonschema import ValidationError
from app.core.utils import (
    get_validator,
    validate_schema_dict,
    validate_schema_object,
    compile_path_to_regex,
    json_response,
    text_plain_response,
    text_html_response,
    read_body,
    send_response,
    CONTENT_TYPE_TEXT_HTML_HEADER,
    CONTENT_TYPE_TEXT_PLAIN_HEADER,
    CONTENT_TYPE_APPLICATION_JSON_HEADER,
)

class User(msgspec.Struct):
    name: str
    age: int

class Empty(msgspec.Struct):
    pass

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "body, ModelDto, expected, test_id",
    [
        # Happy path: valid dict, User model
        ({"name": "Alice", "age": 30}, User, {"name": "Alice", "age": 30}, "dict_valid_user"),
        # Happy path: valid bytes, User model
        (orjson.dumps({"name": "Bob", "age": 25}), User, {"name": "Bob", "age": 25}, "bytes_valid_user"),
        # Edge: empty struct, dict
        ({}, Empty, {}, "dict_empty_struct"),
        # Edge: empty struct, bytes
        (orjson.dumps({}), Empty, {}, "bytes_empty_struct"),
    ],
    ids=lambda x: x if isinstance(x, str) else None,
)
async def test_validate_schema_dict_valid(body, ModelDto, expected, test_id):
    # Act
    result = await validate_schema_dict(body, ModelDto)

    # Assert
    assert result == expected

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "body, ModelDto, test_id",
    [
        # Error: missing required field
        ({"name": "Alice"}, User, "dict_missing_field"),
        # Error: wrong type
        ({"name": "Alice", "age": "not_an_int"}, User, "dict_wrong_type"),
    ],
    ids=lambda x: x if isinstance(x, str) else None,
)
async def test_validate_schema_dict_invalid(body, ModelDto, test_id):
    # Act & Assert
    with pytest.raises(ValidationError) as excinfo:
        await validate_schema_dict(body, ModelDto)
    # The error message should contain 'detail' and 'body'
    assert "detail" in str(excinfo.value)
    assert "body" in str(excinfo.value)

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "body, ModelDto, expected_type, test_id",
    [
        # Happy path: valid dict, User model
        ({"name": "Alice", "age": 30}, User, User, "dict_valid_user"),
        # Happy path: valid bytes, User model
        (orjson.dumps({"name": "Bob", "age": 25}), User, User, "bytes_valid_user"),
        # Edge: empty struct, dict
        ({}, Empty, Empty, "dict_empty_struct"),
        # Edge: empty struct, bytes
        (orjson.dumps({}), Empty, Empty, "bytes_empty_struct"),
    ],
    ids=lambda x: x if isinstance(x, str) else None,
)
async def test_validate_schema_object_valid(body, ModelDto, expected_type, test_id):
    # Act
    result = await validate_schema_object(body, ModelDto)

    # Assert
    assert isinstance(result, expected_type)

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "body, ModelDto, test_id",
    [
        # Error: missing required field
        ({"name": "Alice"}, User, "dict_missing_field"),
        # Error: wrong type
        ({"name": "Alice", "age": "not_an_int"}, User, "dict_wrong_type"),
    ],
    ids=lambda x: x if isinstance(x, str) else None,
)
async def test_validate_schema_object_invalid(body, ModelDto, test_id):
    # Act & Assert
    with pytest.raises(ValidationError) as excinfo:
        await validate_schema_object(body, ModelDto)
    assert "detail" in str(excinfo.value)
    assert "body" in str(excinfo.value)

@pytest.mark.parametrize(
    "path_template, path, expected, test_id",
    [
        ("/item/{id}", "/item/123", True, "simple_path"),
        ("/user/{uid}/post/{pid}", "/user/42/post/99", True, "multi_param_path"),
        ("/static", "/static", True, "no_param_path"),
        ("/item/{id}", "/item/", False, "missing_param"),
        ("/item/{id}", "/item/123/extra", False, "extra_segment"),
    ],
    ids=lambda x: x if isinstance(x, str) else None,
)
def test_compile_path_to_regex(path_template, path, expected, test_id):
    # Act
    regex = compile_path_to_regex(path_template)
    match = regex.match(path)

    # Assert
    assert (match is not None) == expected

@pytest.mark.parametrize(
    "data, status, headers, expected_status, expected_headers, expected_body, test_id",
    [
        # Happy path: dict, default status, no headers
        ({"foo": "bar"}, 200, None, 200, CONTENT_TYPE_APPLICATION_JSON_HEADER, [orjson.dumps({"foo": "bar"})], "json_no_headers"),
        # Custom status and headers
        ({"foo": "bar"}, 201, {"X-Test": "1"}, 201, [(b"X-Test", b"1")] + CONTENT_TYPE_APPLICATION_JSON_HEADER, [orjson.dumps({"foo": "bar"})], "json_custom_headers"),
    ],
    ids=lambda x: x if isinstance(x, str) else None,
)
def test_json_response(data, status, headers, expected_status, expected_headers, expected_body, test_id):
    # Act
    result = json_response(data, status, headers)

    # Assert
    assert result[0] == expected_status
    assert set(result[1]) == set(expected_headers)
    assert result[2] == expected_body

@pytest.mark.parametrize(
    "data, status, headers, expected_status, expected_headers, expected_body, test_id",
    [
        # Happy path: text, default status, no headers
        (b"hello", 200, None, 200, CONTENT_TYPE_TEXT_PLAIN_HEADER, [b"hello"], "plain_no_headers"),
        # Custom status and headers
        (b"hi", 201, {"X-Test": "1"}, 201, [(b"X-Test", b"1")] + CONTENT_TYPE_TEXT_PLAIN_HEADER, [b"hi"], "plain_custom_headers"),
    ],
    ids=lambda x: x if isinstance(x, str) else None,
)
def test_text_plain_response(data, status, headers, expected_status, expected_headers, expected_body, test_id):
    # Act
    result = text_plain_response(data, status, headers)

    # Assert
    assert result[0] == expected_status
    assert set(result[1]) == set(expected_headers)
    assert result[2] == expected_body

@pytest.mark.parametrize(
    "data, status, headers, expected_status, expected_headers, expected_body, test_id",
    [
        # Happy path: html, default status, no headers
        (b"<h1>hi</h1>", 200, None, 200, CONTENT_TYPE_TEXT_HTML_HEADER, [b"<h1>hi</h1>"], "html_no_headers"),
        # Custom status and headers
        (b"<h2>ok</h2>", 201, {"X-Test": "1"}, 201, [(b"X-Test", b"1")] + CONTENT_TYPE_TEXT_HTML_HEADER, [b"<h2>ok</h2>"], "html_custom_headers"),
    ],
    ids=lambda x: x if isinstance(x, str) else None,
)
def test_text_html_response(data, status, headers, expected_status, expected_headers, expected_body, test_id):
    # Act
    result = text_html_response(data, status, headers)

    # Assert
    assert result[0] == expected_status
    assert set(result[1]) == set(expected_headers)
    assert result[2] == expected_body

@pytest.mark.asyncio
async def test_read_body_bytes():
    # Arrange
    body_bytes = orjson.dumps({"foo": "bar"})
    messages = [
        {"type": "http.request", "body": body_bytes, "more_body": False}
    ]
    async def receive():
        return messages.pop(0)

    # Act
    result = await read_body(receive)

    # Assert
    assert result == {"foo": "bar"}

@pytest.mark.asyncio
async def test_read_body_chunked():
    # Arrange
    part1 = orjson.dumps({"foo": "bar"})[:5]
    part2 = orjson.dumps({"foo": "bar"})[5:]
    messages = [
        {"type": "http.request", "body": part1, "more_body": True},
        {"type": "http.request", "body": part2, "more_body": False},
    ]
    async def receive():
        return messages.pop(0)

    # Act
    result = await read_body(receive)

    # Assert
    assert result == {"foo": "bar"}

@pytest.mark.asyncio
async def test_send_response():
    # Arrange
    sent = []
    async def send(msg):
        sent.append(msg)
    response = (200, [(b"content-type", b"text/plain")], [b"hello"])

    # Act
    await send_response(send, response)

    # Assert
    assert sent[0]["type"] == "http.response.start"
    assert sent[0]["status"] == 200
    assert sent[0]["headers"] == [(b"content-type", b"text/plain")]
    assert sent[1]["type"] == "http.response.body"
    assert sent[1]["body"] == b"hello"
