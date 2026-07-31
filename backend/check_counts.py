import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import select, text
from app.models.universe import Universe

async def check():
    engine = create_async_engine('sqlite+aiosqlite:///loreweave.db')
    async with AsyncSession(engine) as session:
        result = await session.execute(select(Universe).order_by(Universe.created_at.desc()).limit(1))
        u = result.scalar_one_or_none()
        if not u:
            print('No universes found')
            return
        print(f'Checking universe {u.id} {u.name}')
        tables = ['characters', 'locations', 'organizations', 'world_objects', 'world_rules', 'relationships', 'timeline_events']
        for t in tables:
            r = await session.execute(text(f"SELECT COUNT(*) FROM {t} WHERE universe_id = '{u.id}' AND deleted_at IS NULL"))
            c = r.scalar()
            if c > 0:
                print(f'{t} count: {c}')

asyncio.run(check())
