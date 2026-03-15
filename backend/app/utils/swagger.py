"""
OpenAPI/Swagger Documentation for PED Majevica API
"""

from flask import Flask, jsonify, render_template_string
import logging

logger = logging.getLogger(__name__)


def create_swagger_ui(
    app: Flask, title: str = "PED Majevica API", api_url: str = "/api"
):
    """
    Create and register Swagger UI for Flask app

    Args:
        app: Flask application instance
        title: API title
        api_url: URL where OpenAPI spec is available
    """

    # OpenAPI Specification
    openapi_spec = {
        "openapi": "3.0.0",
        "info": {
            "title": title,
            "description": """
## PED Majevica 1988 - Planinarski Elektornski Dnevnik

Ovo je API za upravljanje sadržajem sajta Planinarskog društva "Majevica 1988".

### Funkcionalnosti:
- **Blog postovi** - Kreiranje, uređivanje i brisanje postova
- **Događaji** - Upravljanje planinarskim događajima
- **Staze** - Informacije o planinarskim stazama
- **Galerija** - Upravljanje slikama
- **Korisnici** - Autentifikacija i autorizacija

### Autentifikacija:
API koristi session-based autentifikaciju. Za zaštićene endpoint-e,
potrebno je biti prijavljen na sajtu.
            """,
            "version": "1.0.0",
            "contact": {"name": "PED Majevica 1988", "email": "info@pedmajevica.org"},
        },
        "servers": [{"url": api_url, "description": "Production server"}],
        "paths": {
            # Posts endpoints
            "/posts": {
                "get": {
                    "summary": "Get all blog posts",
                    "description": "Returns paginated list of published blog posts",
                    "parameters": [
                        {
                            "name": "page",
                            "in": "query",
                            "schema": {"type": "integer", "default": 1},
                            "description": "Page number",
                        },
                        {
                            "name": "per_page",
                            "in": "query",
                            "schema": {"type": "integer", "default": 10},
                            "description": "Items per page (max 50)",
                        },
                        {
                            "name": "category",
                            "in": "query",
                            "schema": {"type": "string"},
                            "description": "Filter by category",
                        },
                    ],
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "success": {"type": "boolean"},
                                            "data": {
                                                "type": "object",
                                                "properties": {
                                                    "posts": {"type": "array"},
                                                    "pagination": {"type": "object"},
                                                },
                                            },
                                        },
                                    }
                                }
                            },
                        }
                    },
                },
                "post": {
                    "summary": "Create new blog post",
                    "security": [{"sessionAuth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["title", "content"],
                                    "properties": {
                                        "title": {"type": "string"},
                                        "slug": {"type": "string"},
                                        "content": {"type": "string"},
                                        "content_html": {"type": "string"},
                                        "preview": {"type": "string"},
                                        "category": {"type": "string"},
                                        "published": {"type": "boolean"},
                                    },
                                }
                            }
                        },
                    },
                    "responses": {
                        "201": {"description": "Post created"},
                        "401": {"description": "Unauthorized"},
                        "403": {"description": "Forbidden"},
                    },
                },
            },
            "/posts/{post_id}": {
                "get": {
                    "summary": "Get single blog post",
                    "parameters": [
                        {
                            "name": "post_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "responses": {
                        "200": {"description": "Successful response"},
                        "404": {"description": "Post not found"},
                    },
                },
                "put": {
                    "summary": "Update blog post",
                    "security": [{"sessionAuth": []}],
                    "parameters": [
                        {
                            "name": "post_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "responses": {
                        "200": {"description": "Post updated"},
                        "401": {"description": "Unauthorized"},
                        "404": {"description": "Post not found"},
                    },
                },
                "delete": {
                    "summary": "Delete blog post",
                    "security": [{"sessionAuth": []}],
                    "parameters": [
                        {
                            "name": "post_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "responses": {
                        "200": {"description": "Post deleted"},
                        "401": {"description": "Unauthorized"},
                        "404": {"description": "Post not found"},
                    },
                },
            },
            "/posts/{post_id}/like": {
                "post": {
                    "summary": "Like a blog post",
                    "security": [{"sessionAuth": []}],
                    "parameters": [
                        {
                            "name": "post_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "responses": {
                        "200": {"description": "Post liked"},
                        "401": {"description": "Login required"},
                    },
                },
                "delete": {
                    "summary": "Unlike a blog post",
                    "security": [{"sessionAuth": []}],
                    "parameters": [
                        {
                            "name": "post_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "responses": {
                        "200": {"description": "Post unliked"},
                        "401": {"description": "Login required"},
                    },
                },
            },
            # Events endpoints
            "/events": {
                "get": {
                    "summary": "Get all events",
                    "parameters": [
                        {
                            "name": "page",
                            "in": "query",
                            "schema": {"type": "integer", "default": 1},
                        },
                        {
                            "name": "per_page",
                            "in": "query",
                            "schema": {"type": "integer", "default": 10},
                        },
                    ],
                    "responses": {"200": {"description": "Successful response"}},
                },
                "post": {
                    "summary": "Create new event",
                    "security": [{"sessionAuth": []}],
                    "responses": {
                        "201": {"description": "Event created"},
                        "401": {"description": "Unauthorized"},
                    },
                },
            },
            "/events/{event_id}": {
                "get": {
                    "summary": "Get single event",
                    "parameters": [
                        {
                            "name": "event_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "responses": {
                        "200": {"description": "Successful response"},
                        "404": {"description": "Event not found"},
                    },
                }
            },
            # Trails endpoints
            "/trails": {
                "get": {
                    "summary": "Get all trails",
                    "parameters": [
                        {
                            "name": "page",
                            "in": "query",
                            "schema": {"type": "integer", "default": 1},
                        },
                        {
                            "name": "per_page",
                            "in": "query",
                            "schema": {"type": "integer", "default": 10},
                        },
                    ],
                    "responses": {"200": {"description": "Successful response"}},
                }
            },
            "/trails/{trail_id}": {
                "get": {
                    "summary": "Get single trail",
                    "parameters": [
                        {
                            "name": "trail_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "responses": {
                        "200": {"description": "Successful response"},
                        "404": {"description": "Trail not found"},
                    },
                }
            },
            # Auth endpoints
            "/auth/login": {
                "post": {
                    "summary": "User login",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["username", "password"],
                                    "properties": {
                                        "username": {"type": "string"},
                                        "password": {
                                            "type": "string",
                                            "format": "password",
                                        },
                                    },
                                }
                            }
                        },
                    },
                    "responses": {
                        "200": {"description": "Login successful"},
                        "401": {"description": "Invalid credentials"},
                    },
                }
            },
            "/auth/logout": {
                "post": {
                    "summary": "User logout",
                    "responses": {"200": {"description": "Logout successful"}},
                }
            },
        },
        "components": {
            "securitySchemes": {
                "sessionAuth": {"type": "apiKey", "in": "cookie", "name": "session"}
            }
        },
    }

    # Register OpenAPI JSON endpoint
    @app.route("/api/openapi.json")
    def get_openapi_spec():
        return jsonify(openapi_spec)

    # Register Swagger UI
    swagger_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>{{ title }}</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css" />
        <style>
            body { margin: 0; padding: 0; }
            .swagger-ui .topbar { display: none; }
        </style>
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
        <script>
            window.onload = function() {
                window.ui = SwaggerUIBundle({
                    url: "/api/openapi.json",
                    dom_id: "#swagger-ui",
                    deepLinking: true,
                    presets: [
                        SwaggerUIBundle.presets.apis,
                        SwaggerUIBundle.SwaggerUIStandalonePreset
                    ],
                    layout: "StandaloneLayout"
                });
            };
        </script>
    </body>
    </html>
    """

    @app.route("/api/docs")
    def swagger_ui():
        return render_template_string(swagger_html, title=title)

    @app.route("/api/redoc")
    def redoc_ui():
        redoc_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>{{ title }} - ReDoc</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link href="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js" rel="stylesheet">
        </head>
        <body>
            <redoc spec-url="/api/openapi.json"></redoc>
            <script src="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"></script>
        </body>
        </html>
        """
        return render_template_string(redoc_html, title=title)

    logger.info("✅ Swagger UI initialized at /api/docs")
    logger.info("✅ ReDoc initialized at /api/redoc")

    return openapi_spec
