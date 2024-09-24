# Configurations like database URI, secret keys etc.


class Config:
    DEBUG = True
    SECRET_KEY = "quizquickie_secret_key"
    LANGUAGES = ["en", "fr", "ar"]
    UNPROTECTED_ROUTES = [
        "/apidocs",
        "/apidocs/*",
        "/api/v1/status/",
        "/api/v1/auth/signup/",
        "/api/v1/auth/login/",
    ]
    SQLALCHEMY_DATABASE_URI = "sqlite:///quizquickie.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    JSONIFY_PRETTYPRINT_REGULAR = False
    SWAGGER = {"title": "QuizQuickie Restful API", "uiversion": 3}
    CACHE_DEFAULT_TIMEOUT = 300


class DevelopmentConfig(Config):
    FLASK_ENV = "development"


class ProductionConfig(Config):
    DEBUG = False
    CACHE_TYPE = "SimpleCache"
    FLASK_ENV = "production"


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
