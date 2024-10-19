from datetime import timedelta

from flask_pymongo import PyMongo



class Config:
    # MongoDB settings
    MONGO_URI = "mongodb://localhost:27017/healthdis"
    SECRET_KEY = 'dc21a9cb05847ffd9d5a37b67857042b'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)

    # OpenAPI documentation settings
    OPENAPI_VERSION = "3.0.2"
    OPENAPI_JSON_PATH = "api-spec.json"
    OPENAPI_URL_PREFIX = "/"
    OPENAPI_REDOC_PATH = "/redoc"
    OPENAPI_REDOC_URL = "https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"
    OPENAPI_SWAGGER_UI_PATH = "/swagger-ui"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    OPENAPI_RAPIDOC_PATH = "/rapidoc"
    OPENAPI_RAPIDOC_URL = "https://unpkg.com/rapidoc/dist/rapidoc-min.js"

    API_TITLE = "Healthdis API"
    API_VERSION = "1.0.0"  # Add this line to specify your API version

    @staticmethod
    def getSetting(key):
        return getattr(Config, key, None)