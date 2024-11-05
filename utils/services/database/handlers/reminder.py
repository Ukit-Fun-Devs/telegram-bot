from sqlalchemy import insert, select, update, text

from utils.services.database import async_session
from utils.services.database.models import Reminder


class RemindersTools:

    @classmethod
    async def get_reminders(
            cls, tg_id: int
    ) -> Reminder:
        async with async_session() as session:
            async with session.begin():
                result = await session.execute(
                    select(Reminder).where(Reminder.tg_id == tg_id)  # type: ignore
                )

                if not (reminder := result.scalar_one_or_none()):
                    await cls.update_reminders(tg_id)

                    return (await session.execute(
                        select(Reminder).where(Reminder.tg_id == tg_id)  # type: ignore
                    )).scalar_one_or_none()

                return reminder

    @classmethod
    async def update_reminders(
            cls,
            tg_id: int,
            **kwargs: any
    ) -> None:
        async with async_session() as session:
            async with session.begin():
                result = await session.execute(
                    select(Reminder).where(Reminder.tg_id == tg_id)  # type: ignore
                )

                if result.scalar_one_or_none():
                    await session.execute(
                        update(Reminder)
                        .where(Reminder.tg_id == tg_id)  # type: ignore
                        .values(**kwargs)
                        .execution_options(synchronize_session="fetch")
                    )
                else:
                    await session.execute(
                        insert(Reminder).values(tg_id=tg_id, **kwargs)
                        .execution_options(synchronize_session="fetch")
                    )

    @classmethod
    async def truncate_reminders(cls) -> None:
        async with async_session() as session, session.begin():
            await session.execute(text(
                "TRUNCATE TABLE reminders RESTART IDENTITY"
            ))
