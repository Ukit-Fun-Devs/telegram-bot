from __future__ import annotations

import base64
from io import BytesIO
from typing import Optional, TYPE_CHECKING

from aiogram.types import BufferedInputFile
from aiohttp import ClientSession

from utils.services.draw.models import Design

if TYPE_CHECKING:
    from utils.services.parser.models import Day, Couple
    from utils.services.database.models import User


class DrawService:
    URL: str = "http://localhost:2333"

    session: Optional[ClientSession] = None

    @classmethod
    def _load_session(cls) -> None:
        if not cls.session:
            cls.session = ClientSession()

    @staticmethod
    def _get_buffered_input_file(_s: str, name: str) -> BufferedInputFile:
        buffer = BytesIO(base64.b64decode(_s))
        buffer.seek(0)

        return BufferedInputFile(buffer.read(), filename=name)

    @classmethod
    async def draw_schedule(cls, day: Day, user: User) -> BufferedInputFile:
        cls._load_session()
        theme, theme_color = tuple(user.theme.split("."))

        async with cls.session.get(
                url=cls.URL + '/v1/draw',
                params={
                    "name": "schedule",
                    "theme_color": theme_color,
                    "theme": theme
                },
                json=day.deserialize(),
                timeout=3
        ) as response:
            json = await response.json()
            if response.status != 200:
                raise ValueError(json.get("message", "Failed to draw schedule"))

            return cls._get_buffered_input_file(json.get("encode"), "schedule.png")

    @classmethod
    async def draw_couple(cls, couple: Couple, user: User) -> BufferedInputFile:
        cls._load_session()
        theme, theme_color = tuple(user.theme.split("."))

        async with cls.session.get(
                url=cls.URL + '/v1/draw',
                params={
                    "name": "couple",
                    "theme_color": theme_color,
                    "theme": theme
                },
                json=couple.deserialize(),
                timeout=3
        ) as response:
            json = await response.json()
            if response.status != 200:
                raise ValueError(json.get("message", "Failed to draw couple"))

            return cls._get_buffered_input_file(json.get("encode"), "couple.png")

    @classmethod
    async def get_designs(cls) -> list[Design]:
        cls._load_session()

        async with cls.session.get(url=cls.URL + "/v1/designs") as response:
            if response.status != 200:
                raise ValueError(response.text())

            return [
                Design(
                    name=d["name"],
                    key=d["key"],
                    preview=cls._get_buffered_input_file(d["preview"], "design.png")
                )
                for d in (await response.json())["response"]
            ]
