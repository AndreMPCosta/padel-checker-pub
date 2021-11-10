from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException

from app.feed.fetcher import Zone

router = APIRouter()


def fetch_zone(date: str, _id: int):
    dt = datetime.today()
    if datetime.strptime(date, '%Y-%m-%d') < datetime(dt.year, dt.month, dt.day):
        raise HTTPException(status_code=400, detail="The date has to be in the future")
    zone = Zone(internal_date=date, id=_id)
    zone.load_from_file()
    return zone


@router.get('/zone')
def get_zone(_id: int,
             date: Optional[str] = datetime.today().strftime('%Y-%m-%d'),
             start_time: Optional[str] = '07:59',
             end_time: Optional[str] = '23:59',
             indoor: Optional[bool] = True,
             minutes: Optional[int] = 90):
    zone = fetch_zone(date, _id=_id)
    response = zone.filter_by(start_time, end_time, indoor,
                              preferred_clubs=[], minutes_to_check=minutes)
    # 8, 26, 54, 62, 79, 93, 246, 310, 322, 372, 401, 431, 453, 462, 492

    return {'response': response}
