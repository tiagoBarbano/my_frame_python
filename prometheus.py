from prometheus_client import Counter, Histogram
import time

REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests", ["method", "path", "status"])
REQUEST_LATENCY = Histogram("http_request_duration_seconds", "Request latency", ["method", "path"])

class PrometheusMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope["path"] == "/metrics":
            return await self.app(scope, receive, send)

        method = scope["method"]
        path = scope["path"]
        status_holder = {}

        start_time = time.perf_counter()

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                status = message["status"]
                status_holder["status"] = status
            await send(message)

        await self.app(scope, receive, send_wrapper)

        duration = time.perf_counter() - start_time
        status = str(status_holder.get("status", 500))

        REQUEST_COUNT.labels(method, path, status).inc()
        REQUEST_LATENCY.labels(method, path).observe(duration)
        
