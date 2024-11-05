from sqlalchemy import Column, Integer, Text, Boolean, BigInteger

from ._base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    active = Column(Boolean, default=False)
    tg_id = Column(BigInteger)
    group_id = Column(Integer)
    reminded = Column(Boolean, default=False)
    saved_groups = Column(Text, default="[]")
    theme = Column(Text, default="black.purple")

    first_name = Column(Text)
    second_name = Column(Text)
    third_name = Column(Text)

    def __repr__(self) -> str:
        return (
            f"<User("
            f"id={self.id}, "
            f"group_id={self.group_id}, "
            f"first_name={self.first_name}, "
            f"second_name={self.second_name}, "
            f"third_name={self.third_name})"
            f">"
        )
