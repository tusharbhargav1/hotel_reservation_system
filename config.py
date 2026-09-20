import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()


class Config:

    SECRET_KEY = os.getenv("SECRET_KEY")

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_COOKIE_HTTPONLY = True

    SESSION_COOKIE_SAMESITE = "Lax"

    SESSION_COOKIE_SECURE = (
        os.getenv(
            "SESSION_COOKIE_SECURE",
            "False"
        ).lower() == "true"
    )

    PERMANENT_SESSION_LIFETIME = timedelta(
        minutes=30
    )

    WTF_CSRF_ENABLED = True

    WTF_CSRF_TIME_LIMIT = 3600