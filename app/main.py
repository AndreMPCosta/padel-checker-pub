from asyncio import get_event_loop
from os import mkdir
from os.path import exists, join

from fastapi import FastAPI

from app.feed.celery_worker import cycle_days
from fastapi_utils.tasks import repeat_every

from app.feed.config import cities
from app.models.user import UserModel
from app.routers import zones, auth, user
from app.utils import get_project_root

app = FastAPI(title='Padel Checker')

app.include_router(zones.router)
app.include_router(auth.router)
app.include_router(user.router)


@app.on_event("startup")
@repeat_every(seconds=60)  # 1 minute
async def fetch_data() -> None:
    result = cycle_days.delay()
    result.get()
    users = await UserModel.get_with_watchers()
    # tasks = gather(*[r.check_watcher() for r in users])
    for u in users:
        await u.check_watcher()


@app.on_event("startup")
async def startup_event():
    if not exists(join(get_project_root(), 'app', 'feed', 'data')):
        mkdir(join(get_project_root(), 'app', 'feed', 'data'))
    for x in cities.values():
        if not exists(join(get_project_root(), 'app', 'feed', 'data', str(x))):
            mkdir(join(get_project_root(), 'app', 'feed', 'data', str(x)))


@app.get("/")
async def root():
    return {"message": "Padel-Checker API"}


@app.get("/force-refresh")
def force_refresh():
    cycle_days.delay()
    # result_output = result.get()
    return {"message": "Task added"}


if __name__ == "__main__":
    import uvicorn

    loop = get_event_loop()
    config = uvicorn.Config(app="app.main:app", host="0.0.0.0", port=8000, reload=True, workers=2, loop="asyncio")
    server = uvicorn.Server(config)
    loop.run_until_complete(server.serve())

    # config = {
    #     'host': "0.0.0.0",
    #     'port': 8000,
    #     'reload': True,
    #     'workers': 2,
    # }
    # uvicorn.run("app.main:app", **config)
