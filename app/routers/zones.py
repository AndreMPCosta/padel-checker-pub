from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.feed.config import all_ids
from app.feed.fetcher import Zone

router = APIRouter()


def fetch_zone(date: str, _id: int):
    dt = datetime.today()
    if datetime.strptime(date, '%Y-%m-%d') < datetime(dt.year, dt.month, dt.day):
        raise HTTPException(status_code=400, detail="The date has to be in the future")
    zone = Zone(internal_date=date, id=_id)
    zone.load_from_file()
    return zone


@router.get('/zone', summary="Fetch the available slots")
def get_zone(_id: int = Query("12", enum=all_ids),
             date: Optional[str] = datetime.today().strftime('%Y-%m-%d'),
             start_time: Optional[str] = '07:59',
             end_time: Optional[str] = '23:59',
             indoor: Optional[bool] = True,
             minutes: Optional[int] = 90):
    """
    Fetch the available slots for the zone you have picked.
    - **_id**: pick an id from these available zones:

        * #### Grande Porto: 12 ####\n
        * #### Grande Lisboa: 13 ####\n
        * #### Distrito Braga: 14 ####\n
        * #### Distrito Coimbra: 16 ####\n
        * #### Algarve: 22 ####\n
        * #### Distrito Aveiro: 23 ####\n
        * #### Alentejo: 24 ####\n
        * #### Leiria: 25 ####\n
        * #### Madeira: 26 ####\n
        * #### Distrito Vila Real: 28 ####\n
        * #### Viseu: 29 ####\n
        * #### Açores: 31 ####\n
        * #### Distrito Santarém: 32 ####\n
        * #### Viana do Castelo: 33 ####\n

    - **date**: day to search
    - **start_time**: starting time to look for slots
    - **end_time**: ending time to look for slots
    - **indoor**: if you are looking for indoor courts or not
    - **minutes**: how many minutes should be available (minimum) to play
    """

    zone = fetch_zone(date, _id=_id)
    response = zone.filter_by(start_time, end_time, indoor,
                              preferred_clubs=[], minutes_to_check=minutes)
    # 8, 26, 54, 62, 79, 93, 246, 310, 322, 372, 401, 431, 453, 462, 492

    return {'response': response}
