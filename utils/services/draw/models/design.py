from dataclasses import dataclass

from aiogram.types import BufferedInputFile


@dataclass
class Design:
    name: str
    key: str
    preview: BufferedInputFile
