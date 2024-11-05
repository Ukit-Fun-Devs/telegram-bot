from sqlalchemy import Column, Integer, String, Date

from ._base import Base


class Statistic(Base):
    __tablename__ = "statistics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    text = Column(String)
    date = Column(Date)
