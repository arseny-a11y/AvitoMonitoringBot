from database.models import CollectedData
from database.database import async_session_factory
from sqlalchemy import select

#функция для записи собранных данный в БД
async def save_items(items: list[dict]):
    if not items:
        return 

    items_id = [item.get("id") for item in items if item.get("id") is not None]

    if not items_id:
        return
    
    async with async_session_factory() as session:
        items_in_db = (await session.scalars(select(CollectedData).where(CollectedData.item_id.in_(items_id)))).all()

        ids_in_db = {item.item_id for item in items_in_db}

        new_data = []
        for item in items:
            item_id = item.get("id")

            if item_id is None or item_id in ids_in_db:
                continue

            new_data.append(
                CollectedData(
                    item_id=item.get("id"),
                    title=item.get("title"),
                    price=item.get("price"),
                    description=item.get("description"),
                    url=item.get("url")
                )
            )

        if not new_data:
            return

        async with session.begin():
            session.add_all(new_data)

        return new_data
