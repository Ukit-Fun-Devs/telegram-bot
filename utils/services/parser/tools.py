from collections import defaultdict
from typing import Optional

from aiohttp import ClientSession

from .models import Day, GroupInfo
from ...basic.time import now


class MgutmTools:
    session: Optional[ClientSession] = None

    @classmethod
    def _load_session(cls) -> None:
        if not cls.session:
            cls.session = ClientSession()

    @classmethod
    async def get_schedule(cls, group_id: int, sdate: Optional[str] = None) -> list[Day]:
        cls._load_session()

        data: defaultdict = defaultdict(list)
        async with cls.session.get(
                f"https://dec.mgutm.ru/api/Rasp",
                data={
                    "idGroup": str(group_id),
                    "sdate": sdate if sdate else now().strftime("%Y-%m-%d")
                }
        ) as response:
            if response.status != 200:
                return []

            json = await response.json()
            if json.get("data") and (schedule := json.get("data", {}).get("rasp")):
                for day in schedule:
                    data[day["дата"]].append(day)

        return [
            Day(
                data=day,
                start_date=json.get("data", {}).get("info", {}).get("date"),
                next_date=json.get("data", {}).get("info", {}).get("lastDate"),
                changed_date=json.get("data", {}).get("info", {}).get("dateUploadingRasp")
            )
            for day in data.values()
        ]

    @classmethod
    async def get_info(cls, group_id: int) -> Optional[GroupInfo]:
        cls._load_session()

        async with cls.session.get(
                f"https://dec.mgutm.ru/api/UserInfo/GroupInfo",
                params={"groupID": str(group_id)}
        ) as response:
            if response.status != 200:
                return None

            json = await response.json()
            if json.get("data"):
                return GroupInfo(json)
