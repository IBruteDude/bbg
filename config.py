# Configurations like database URI, secret keys etc.


class Config:
    SECRET_KEY = "quiz_quickie_secret_key"
    LANGUAGES = ["en", "fr", "ar"]
    SQLALCHEMY_DATABASE_URI = "sqlite:///quizquickie.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSONIFY_PRETTYPRINT_REGULAR = False
    SWAGGER = {"title": "QuizQuickie Restful API", "uiversion": 3}
