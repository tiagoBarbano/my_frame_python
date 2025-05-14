"""Swagger UI for AGSI API."""

async def serve_swagger_ui():
    html = """<!DOCTYPE html>
<html>
<head>
    <title>Swagger UI</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.11.0/swagger-ui.min.css" />
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.11.0/swagger-ui-bundle.min.js"></script>
    <script>
    window.onload = () => {
        SwaggerUIBundle({
            url: '/openapi.json',
            dom_id: '#swagger-ui',
        });
    };
    </script>
</body>
</html>"""
    return html.encode("utf-8")
