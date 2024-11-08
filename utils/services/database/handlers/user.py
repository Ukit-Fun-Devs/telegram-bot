import ast
from typing import Optional

from sqlalchemy import select, update

from utils.services.database import async_session
from utils.services.database.models import User


class UserTools:

    @classmethod
    async def get(cls, tg_id: int) -> Optional[User]:
        async with async_session() as session:
            async with session.begin():
                result = await session.execute(
                    select(User).where(User.tg_id == tg_id)  # type: ignore
                )
                user = result.scalar_one_or_none()

        return user

    @classmethod
    async def get_if_reminded(cls) -> list[User]:
        async with async_session() as session:
            async with session.begin():
                result = await session.execute(
                    select(User).where(User.reminded)  # type: ignore
                )
                user = result.scalars().all()

        return user if user else []

    @classmethod
    async def update_sent(cls, tg_id: int, value: bool) -> None:
        async with async_session() as session:
            async with session.begin():
                await session.execute(
                    update(User)
                    .where(User.tg_id == tg_id)  # type: ignore
                    .values(sent=value)
                    .execution_options(synchronize_session="fetch")
                )

    @classmethod
    async def change_remind(cls, tg_id: int) -> User:
        async with async_session() as session, session.begin():
            result = await session.execute(
                update(User)
                .where(User.tg_id == tg_id)  # type: ignore
                .values(reminded=~User.reminded)
                .returning(User)
            )
            user = result.scalar_one()
        return user

    @classmethod
    async def get_groups(cls, tg_id: int) -> list[int]:
        async with async_session() as session, session.begin():
            result = await session.execute(
                select(User).where(User.tg_id == tg_id)  # type: ignore
            )
            saved_groups: list[int] = ast.literal_eval(result.scalar_one().saved_groups)

        return saved_groups[:]

    @classmethod
    async def update_groups(
            cls,
            tg_id: int,
            groups: list[int] = None,
            remove_groups: list[int] = None,
            set_group: int = None
    ) -> User:
        async with async_session() as session, session.begin():
            result = (await session.execute(
                select(User).where(User.tg_id == tg_id)  # type: ignore
            )).scalar_one()

            saved_groups: list[int] = ast.literal_eval(result.saved_groups)
            if groups:
                saved_groups.extend(groups)

            if remove_groups:
                for del_group in remove_groups:
                    saved_groups.remove(del_group)

            new = await session.execute(
                update(User)
                .where(User.tg_id == tg_id)  # type: ignore
                .values(
                    saved_groups=str(saved_groups),
                    group_id=set_group if set_group else result.group_id
                )
                .execution_options(synchronize_session="fetch")
                .returning(User)
            )

            user = new.scalar_one()
        return user

    @classmethod
    async def clean_saved_groups(cls, tg_id: int) -> User:
        async with async_session() as session, session.begin():
            new = await session.execute(
                update(User)
                .where(User.tg_id == tg_id)  # type: ignore
                .values(saved_groups="[]")
                .execution_options(synchronize_session="fetch")
                .returning(User)
            )

            user = new.scalar_one()
        return user

    @classmethod
    async def set_theme(cls, tg_id: int, theme_key: str) -> None:
        async with async_session() as session, session.begin():
            await session.execute(
                update(User)
                .where(User.tg_id == tg_id)  # type: ignore
                .values(theme=theme_key)
                .execution_options(synchronize_session="fetch")
            )
