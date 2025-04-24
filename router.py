# router.py
routes = {}

def route(method: str, path: str):
    def decorator(func):
        routes[(path, method.upper())] = func
        return func
    return decorator

get = lambda path: route("GET", path)
post = lambda path: route("POST", path)
