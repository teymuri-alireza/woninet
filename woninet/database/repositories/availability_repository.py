from datetime import date, datetime
from sqlalchemy import func, select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import Session
from woninet.database.tables import AvailabilityTable


class AvailabilityRepository:
    """
    Repository for persisting device's availability.

    Attributes:
        session (Session): SQLAlchemy sessions used for
            database operations.
    """

    def __init__(self, session: Session) -> None:
        """
        Initialize the repository.

        Args:
            session (Session): SQLAlchemy session used for all database operations
        """
        self.session: Session = session

    def record_checks(
        self, checks: list[tuple[str, bool]], hour_start: datetime
    ) -> None:
        """
        Add one check per device to the counters of the given hour (atomic upsert).
        """
        if not checks:
            return

        rows = [
            {
                "device_ip": ip,
                "hour_start": hour_start,
                "checks": 1,
                "up_checks": 1 if reachable else 0,
            }
            for ip, reachable in checks
        ]

        stmt = insert(AvailabilityTable)
        stmt = stmt.on_conflict_do_update(
            index_elements=["device_ip", "hour_start"],
            set_={
                "checks": AvailabilityTable.checks + stmt.excluded.checks,
                "up_checks": AvailabilityTable.up_checks + stmt.excluded.up_checks,
            },
        )
        self.session.execute(stmt, rows)

    def fetch_daily(self, ip: str, since: datetime) -> dict[date, tuple[int, int]]:
        """
        Return hourly records into daily statistics.

        Args:
            ip (str): IP address of device.
            since: (datetime): Datetime from which records are retrieved.
        """
        day = func.date(AvailabilityTable.hour_start)
        stmt = (
            select(
                day,
                func.sum(AvailabilityTable.checks),
                func.sum(AvailabilityTable.up_checks),
            )
            .where(
                AvailabilityTable.device_ip == ip,
                AvailabilityTable.hour_start >= since,
            )
            .group_by(day)
        )
        return {
            date.fromisoformat(d): (int(checks), int(up_checks))
            for d, checks, up_checks in self.session.execute(stmt)
        }

    def fetch_hourly(self, ip: str, since: datetime) -> dict[datetime, tuple[int, int]]:
        """
        Return hourly records.

        Args:
            ip (str): IP address of device.
            since: (datetime): Datetime from which records are retrieved.
        """
        stmt = select(
            AvailabilityTable.hour_start,
            AvailabilityTable.checks,
            AvailabilityTable.up_checks,
        ).where(
            AvailabilityTable.device_ip == ip,
            AvailabilityTable.hour_start >= since,
        )
        return {
            hour_start: (checks, up_checks)
            for hour_start, checks, up_checks in self.session.execute(stmt)
        }

    def delete_older_than(self, cutoff: datetime) -> int:
        """
        Delete records older than the given datetime.

        Args:
            cutoff (datetime): DateTime provided from which records are deleted
        """
        return (
            self.session.query(AvailabilityTable)
            .filter(AvailabilityTable.hour_start < cutoff)
            .delete(synchronize_session=False)
        )
