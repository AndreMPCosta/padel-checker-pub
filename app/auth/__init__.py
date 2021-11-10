from os import environ

from fastapi_login import LoginManager
from passlib.context import CryptContext

SECRET_KEY = environ.get('SECRET_KEY')
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

manager = LoginManager(SECRET_KEY, '/login')


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)
