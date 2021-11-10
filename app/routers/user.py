from fastapi import APIRouter, status, Depends
from fastapi.responses import ORJSONResponse, JSONResponse
from odmantic import ObjectId

from app.auth import manager
from app.exceptions import UserNotUnique, WatcherNotFound
from app.models.snapshot import Snapshot
from app.models.user import UserModel

router = APIRouter()


@router.post('/register', response_class=ORJSONResponse)
async def register(user: UserModel):
    db_user = await UserModel.get_by_email(user.email)
    if db_user:
        return JSONResponse(status_code=status.HTTP_409_CONFLICT,
                            content={
                                "error": UserNotUnique().message(db_user.email)
                            })
    await user.save()
    return {'message': f"User '{user.email}' created successfully"}


@router.post('/user/watcher', response_class=ORJSONResponse)
async def create_watcher(watcher: Snapshot, user=Depends(manager)):
    user = await user
    await user.add_watcher(**watcher.dict())
    return {'message': "Watcher created successfully"}


@router.delete('/user/watcher', response_class=ORJSONResponse)
async def remove_watcher(_id: ObjectId, user=Depends(manager)):
    user = await user
    try:
        await user.remove_watcher(_id)
    except WatcherNotFound:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={
                                "error": WatcherNotFound().message(_id)
                            })
    return {'message': "Watcher removed successfully"}
