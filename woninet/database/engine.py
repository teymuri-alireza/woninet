from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from woninet.database.base import Base


class DatabaseEngine:
    """
    Encapsulate database engine creation and initialization logic.
    """

    def __init__(self, database_path: str) -> None:
        """
        Create a SQLAlchemy engine and session factory for the given database.

        Args:
            database_path (str): Path to the SQLite database file.
        """
        self.engine = create_engine(
            f"sqlite:///{database_path}", echo=False, future=True
        )
        self.SessionLocal = sessionmaker(bind=self.engine, autoflush=False)

    def init_db(self) -> None:
        """
        Initialize the database and create missing tables.
        """
        import woninet.database.tables  # noqa: F401

        Base.metadata.create_all(bind=self.engine)

    def get_database_enigne(self) -> Engine:
        """
        Return the SQLAlchemy Engine instance.
        """
        return self.engine

    def get_session_factory(self) -> sessionmaker[Session]:
        """
        Return the SQLAlchemy session factory used to create sessions.
        """
        return self.SessionLocal
