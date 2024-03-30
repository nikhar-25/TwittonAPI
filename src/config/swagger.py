template = {
    "swagger": "2.0",
    "info": {
        "title": "Twitton API",
        "description": "API for Twitter Clone",
        "contact": {
            "responsibleOrganization": "Nikhar Corp",
            "responsibleDeveloper": "Nikhar Mahendra Singh",
            "email": "nikharms2500@gmail.com",
            "url": "https://18301732.wixsite.com/portfolio",
        },
        "termsOfService": "https://www.termsfeed.com/live/4388cdf7-9fda-470d-86c9-c2b238a3811c",
        "version": "1.0"
    },
    "basePath": "/api/v1",  # base path for blueprint registration
    "schemes": [
        "http",
        "https"
    ],
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example: \"Authorization: Bearer {token}\""
        }
    },
}

swagger_config = {
    "headers": [
    ],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in 
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/"  # changed from "/" to "/swagger/"
}
