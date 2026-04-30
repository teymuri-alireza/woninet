from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from woninet.database.base import Base

engine = create_engine("sqlite:///woninet.db", echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False)


def init_db() -> None:
    """
    Initialize the database and create missing tables.
    """
    import woninet.database.tables # noqa: F401
    Base.metadata.create_all(bind=engine)
