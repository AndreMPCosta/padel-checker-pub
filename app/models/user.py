from abc import ABC

from datetime import datetime
from pprint import pprint
from typing import Optional, List

from odmantic import Model, ObjectId, Field
from pydantic import root_validator

from app.auth import get_password_hash, manager
from app.db import engine
from app.exceptions import WatcherNotFound
from app.mail import send_email
from app.models.snapshot import Snapshot


class UserModel(Model, ABC):
    first_name: str
    last_name: str
    email: str
    password: str
    phone: Optional[str] = None
    preferred_clubs: Optional[List] = Field(default_factory=list)
    snapshots: Optional[List[ObjectId]] = Field(default_factory=list)
    premium: bool = False

    class Config:
        collection = "users"

    @root_validator
    def _hash_password(cls, values):
        values['password'] = get_password_hash(values['password'])
        return values

    async def save(self):
        await engine.save(self)

    @classmethod
    async def get_by_email(cls, email: str) -> 'UserModel':
        return await engine.find_one(cls, cls.email == email)

    @classmethod
    async def get_all(cls) -> List['UserModel']:
        return await engine.find(cls)

    @classmethod
    async def get_with_watchers(cls) -> List['UserModel']:
        return await engine.find(cls, {'$expr': {'$gt': [{'$size': '$snapshots'}, 0]}})

    async def add_watcher(self, **kwargs):
        snapshot: Snapshot = Snapshot(**kwargs)
        # pprint(snapshot)
        self.snapshots.append(snapshot.id)
        await snapshot.save()
        await self.save()

    async def remove_watcher(self, _id: ObjectId):
        snapshot = await Snapshot.get_by_id(_id)
        if snapshot:
            await engine.delete(snapshot)
            self.snapshots.remove(_id)
            await self.save()
        else:
            raise WatcherNotFound

    async def check_watcher(self):
        try:
            snapshots_to_remove = []
            snapshots_to_add = []
            for snapshot_id in self.snapshots:
                snapshot = await Snapshot.get_by_id(snapshot_id)
                dt = datetime.today()
                if snapshot.target_time < datetime(dt.year, dt.month, dt.day):
                    await engine.delete(snapshot)
                    # self.snapshots.remove(snapshot_id)
                    snapshots_to_remove.append(snapshot_id)
                    continue
                temp_snap = Snapshot(
                    id=snapshot.id,
                    zone_id=snapshot.zone_id,
                    preferred_clubs=snapshot.preferred_clubs,
                    start_time=snapshot.start_time,
                    end_time=snapshot.end_time,
                    indoor=snapshot.indoor,
                    date=snapshot.date)
                new_slots = await Snapshot.check_new_slots(snapshot, temp_snap)
                # self.snapshots.remove(snapshot_id)
                snapshots_to_remove.append(snapshot_id)
                await engine.delete(snapshot)
                # self.snapshots.append(temp_snap.id)
                snapshots_to_add.append(temp_snap.id)
                # await self.save()
                await temp_snap.save()
                if new_slots and self.premium:
                    pprint(f'Sending email to {self.first_name} {self.last_name} - {datetime.now()}')
                    # await send_email(self, f'Vagas disponíveis: {new_slots}')
                    pprint(new_slots)
                else:
                    pprint(f'Checking watcher for {self.first_name} {self.last_name} at {datetime.now()}')
            for snap in snapshots_to_remove:
                self.snapshots.remove(snap)
            self.snapshots = self.snapshots + snapshots_to_add
            await self.save()
        except Exception as e:
            print(e)


@manager.user_loader()
async def get_user(email):
    return UserModel.get_by_email(email)


if __name__ == '__main__':
    import asyncio

    loop = asyncio.get_event_loop()
    u1 = UserModel(first_name='a',
                   last_name='b',
                   password='c',
                   email='d')
    print(u1)
    u = loop.run_until_complete(UserModel.get_by_email('sample_email@domain.com'))
    v = loop.run_until_complete(UserModel.get_with_watchers())
    print(v)
    # loop.run_until_complete(send_email(u, 'teste2'))
