class LoggerMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            print(f"👉 {scope['method']} {scope['path']}")
        await self.app(scope, receive, send)
