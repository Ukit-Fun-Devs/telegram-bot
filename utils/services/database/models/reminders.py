from sqlalchemy import Column, Integer, BigInteger, Boolean

from ._base import Base


class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tg_id = Column(BigInteger)

    start_event = Column(Boolean, default=False)
    couple_start = Column(Boolean, default=False)
    launch_start = Column(Boolean, default=False)
