from datetime import timedelta

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from fastapi_login.exceptions import InvalidCredentialsException

from app.auth import verify_password, manager
from app.models.user import UserModel

router = APIRouter()


@router.post('/login')
async def login(data: OAuth2PasswordRequestForm = Depends()):
    email = data.username
    password = data.password

    user = await UserModel.get_by_email(email)
    if not user:
        raise InvalidCredentialsException
    elif verify_password(password, user.password):
        raise InvalidCredentialsException

    access_token = manager.create_access_token(
        data={'sub': email}, expires=timedelta(days=365)
    )
    return {'token': access_token}
