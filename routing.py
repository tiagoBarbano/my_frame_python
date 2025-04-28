# router.py
routes = {}

def route(method: str, path: str):
    def decorator(func):
        routes[(path, method.upper())] = func
        return func
    return decorator

get = lambda path: route("GET", path)  # noqa: E731
post = lambda path: route("POST", path)  # noqa: E731
