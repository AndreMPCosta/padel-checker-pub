from abc import ABC
from datetime import datetime
from pprint import pprint
from typing import Optional, List, Dict

from odmantic import Model, Field
from pydantic import root_validator

from app.db import engine
from app.routers.zones import fetch_zone


class Snapshot(Model, ABC):
    zone_id: int
    preferred_clubs: Optional[List] = []
    start_time: str = '08:00'
    end_time: str = '23:30'
    indoor: bool = False
    date: str = datetime.today().strftime('%Y-%m-%d')
    creation_time: datetime = datetime.now()
    target_time: datetime = datetime.now()
    body: Optional[Dict] = Field(default_factory=dict)
    clubs: Optional[List[str]] = Field(default_factory=list)

    @root_validator
    def _init(cls, values):
        dt = datetime.today()
        if not values.get('clubs') and \
                datetime.strptime(values.get('date'), '%Y-%m-%d') >= datetime(dt.year, dt.month, dt.day):
            zone = fetch_zone(values.get('date'), values.get('zone_id'))
            values['body'] = zone.filter_by(
                values.get('start_time'),
                values.get('end_time'),
                values.get('indoor'),
                preferred_clubs=values.get('preferred_clubs')
            )
            values['creation_time'] = datetime.now()
            values['target_time'] = datetime.strptime(values.get('date'), '%Y-%m-%d')

            for k in values['body'].keys():
                values['clubs'].append(k)
        return values

    def __eq__(self, other: 'Snapshot') -> bool:
        return self.body == other.body

    @classmethod
    async def get_by_id(cls, _id) -> 'Snapshot':
        return await engine.find_one(cls, cls.id == _id)

    @classmethod
    async def check_new_slots(cls, snap1: 'Snapshot', snap2: 'Snapshot') -> Dict:
        new_slots = {}
        all_clubs = set(snap1.clubs + snap2.clubs)
        for club in all_clubs:
            new_slots[club] = {}

            if not snap1.body.get(club):
                new_slots[club] = snap2.body.get(club)
            elif not snap2.body.get(club):
                pass
            else:
                courts_1 = set(list(snap1.body.get(club).keys()))
                courts_2 = set(list(snap2.body.get(club).keys()))

                all_courts = courts_1.union(courts_2)
                for court in all_courts:
                    if not snap1.body.get(club).get(court):
                        new_slots[club].update({
                            court: snap2.body.get(club).get(court)
                        })
                    elif not snap2.body.get(club).get(court):
                        pass
                    else:
                        set_1 = set(snap1.body.get(club).get(court))
                        set_2 = set(snap2.body.get(club).get(court))
                        if len(list(set_2 - set_1)) > 0:
                            new_slots[club].update({
                                court: list(
                                    set(snap2.body.get(club).get(court)) - set(snap1.body.get(club).get(court)))
                            })

            if not len(new_slots.get(club).keys()):
                new_slots.pop(club)
        return new_slots

    class Config:
        collection = "snapshots"

    async def save(self):
        await engine.save(self)


if __name__ == '__main__':
    s1: Snapshot = Snapshot(preferred_clubs=[453, 246], start_time='17:00', end_time='21:00')
    s2: Snapshot = Snapshot(preferred_clubs=[453, 246],
                            start_time='15:00', end_time='23:00',
                            date='2021-10-28')
    print('s1')
    pprint(s1.body)
    print('s2')
    pprint(s2.body)
    pprint(Snapshot.check_new_slots(s1, s2))
