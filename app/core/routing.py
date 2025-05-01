from app.config import Settings

settings = Settings()
routes = {}
openapi_spec = {
    "openapi": "3.0.0",
    "info": {"title": settings.app_name, "version": "1.0.0"},
    "paths": {},
}


def route(method: str, path: str, summary: str = ""):
    def decorator(func):
        if settings.enable_swagger:
            openapi_spec["paths"].setdefault(path, {})[method] = {
                "summary": summary,
                "responses": {"200": {"description": "Sucesso"}},
            }

        routes[(path, method.upper())] = func
        return func

    return decorator


get = lambda path, summary: route("get", path, summary)  # noqa: E731
post = lambda path, summary: route("post", path, summary)  # noqa: E731
