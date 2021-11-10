from dataclasses import dataclass, field
from datetime import datetime
from json import dump, load
from os import getcwd
from os.path import join
from typing import List, Dict

from requests import get

from app.feed.config import api, sport_id, page_size, favorites
from app.utils import get_project_root


@dataclass
class Court:
    club_id: int
    id: int
    roof: int
    slots: List[Dict]
    slug: str = ''
    club_name: str = ''
    name: str = ''

    @staticmethod
    def check_time(time_1: str, time_2: str, condition: str = 'start') -> bool:
        if condition == 'start':
            return datetime.strptime(time_1, '%H:%M') <= datetime.strptime(time_2, '%H:%M')
        else:
            return datetime.strptime(time_1, '%H:%M') >= datetime.strptime(time_2, '%H:%M')

    def get_free_slots(self, minutes_to_check=90, start_time: str = '07:59', end_time: str = '23:59'):
        slots = []
        if minutes_to_check:
            for index, slot in enumerate(self.slots):
                if slot.get('status') == 'available' and index < len(self.slots) - int((minutes_to_check / 30 - 1)):
                    if 'booked' not in [d.get('status') for d in
                                        self.slots[index + 1: index + int((minutes_to_check / 30))]]:
                        if self.check_time(start_time, slot.get('start')) \
                                and self.check_time(end_time, slot.get('start'), 'end'):
                            slots.append(slot.get('start'))
            return slots
        return [d.get('start') for d in self.slots if d.get('status') == 'available']

    def filter_by(self, _field: str, _value, slots: List = None):
        if not slots:
            slots = self.slots
        return [d for d in slots if getattr(self, _field) in _value]


@dataclass
class Club:
    club_id: int
    slug: str = ''
    club_name: str = ''
    courts: List[Court] = field(default_factory=list)


@dataclass
class CourtList:
    courts: List[Court]
    clubs: List[Club] = field(default_factory=list)

    def clear(self):
        self.courts = []

    def get_by_club_id(self, _id: int):
        return [d for d in self.courts if d.club_id == _id]

    def get_by_attr(self, attr_name, attr_value):
        return [d for d in self.courts if getattr(d, attr_name) == attr_value]

    def build_clubs(self):
        for court in self.courts:
            if not [d for d in self.clubs if d.club_name == court.club_name]:
                club = Club(club_id=court.club_id, slug=court.slug, club_name=court.club_name)
                self.clubs.append(club)
            else:
                club = [d for d in self.clubs if d.club_name == court.club_name][0]
            club.courts.append(court)


@dataclass
class Zone:
    id: int
    name: str = ''
    court_list: CourtList = CourtList(courts=[])
    internal_date: str = datetime.today().strftime('%Y-%m-%d')
    days: int = 0

    def __post_init__(self):
        self.days = (datetime.strptime(self.internal_date, '%Y-%m-%d') - datetime(
            datetime.today().year, datetime.today().month, datetime.today().day)).days

    def get_all_courts(self, start_time: str = None):
        self.court_list.clear()
        results = get(api, params=(
            ('city', self.id),
            ('sport', sport_id),
            ('date', self.internal_date),
            ('start_time', '08:00' if not start_time else start_time),
            ('page', 1),
            ('page_size', page_size),
            ('favorites', favorites)
        ))
        # r = results.json().get('results')
        dumper = results.json()
        dumper['refresh_time'] = datetime.now().strftime('%H:%M:%S')

        try:
            with open(join(get_project_root(), 'app', 'feed', 'data', str(self.id), f'{self.days}.json'), 'w') as f:
                dump(dumper, f)

        except FileNotFoundError:
            with open(join(getcwd(), 'data', str(self.id), f'{self.days}.json'), 'w') as f:
                dump(dumper, f)
        self.load_court_list(dumper.get('results'))

    def load_court_list(self, r: List):
        self.court_list = CourtList(courts=[])
        for result in r:
            court = Court(
                int(result.get('club_id')),
                int(result.get('id')),
                int(result.get('roof')),
                result.get('slots'),
                slug=result.get('slug'),
                club_name=result.get('club_name'),
                name=result.get('name'),
            )
            self.court_list.courts.append(court)

    def load_from_file(self):
        with open(join(get_project_root(), 'app', 'feed', 'data', str(self.id), f'{self.days}.json')) as json_file:
            r = load(json_file).get('results')
        self.load_court_list(r)
        self.court_list.build_clubs()

    def filter_by(self, start_time, end_time, indoor, preferred_clubs: List = None, minutes_to_check: int = 90):
        response = {}
        if preferred_clubs is None:
            preferred_clubs = []
        for c in self.court_list.clubs:
            if preferred_clubs and c.club_id not in preferred_clubs:
                continue
            response[c.club_name] = {}
            for x in c.courts:
                s = x.get_free_slots(minutes_to_check=minutes_to_check, start_time=start_time, end_time=end_time)
                if s and indoor:
                    show = x.filter_by('roof', [1, 2], s)
                else:
                    show = s
                if show:
                    response[c.club_name].update({
                        x.name: show
                    })
            if not len(response.get(c.club_name).keys()):
                response.pop(c.club_name)

        return response


if __name__ == '__main__':
    print(Court.check_time('22:00', '23:00', 'end'))
