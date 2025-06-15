import asyncio
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.base_class import Base
from app.db.models.user import User

# Create async engine
engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    echo=False,
    future=True,
    poolclass=NullPool,
)

# Create async session factory
async_session_factory = async_sessionmaker(
    engine, expire_on_commit=False, autoflush=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async DB session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def create_tables() -> None:
    """Create database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def init_db() -> None:
    """Initialize the database with initial data."""
    async with async_session_factory() as session:
        # Create first superuser if it doesn't exist
        superuser = await session.get(User, 1)
        if not superuser:
            superuser = User(
                email=settings.FIRST_SUPERUSER_EMAIL,
                hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
                full_name="Administrator",
                role="admin",
                is_superuser=True,
            )
            session.add(superuser)
            await session.commit()


async def main() -> None:
    """Main function to initialize the database."""
    await create_tables()
    await init_db()


if __name__ == "__main__":
    asyncio.run(main())