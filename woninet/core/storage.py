from datetime import date, datetime
from woninet.core.models import Device, MetricRecord
from woninet.database.tables import AlertStateTable, AlertEventTable
from woninet.database.repositories.device_repository import DeviceRepository
from woninet.database.repositories.metric_repository import MetricRepository
from woninet.database.repositories.alert_state_repository import AlertStateRepository
from woninet.database.repositories.alert_event_repository import AlertEventRepository
from woninet.database.repositories.availability_repository import AvailabilityRepository


class StorageEngine:
    """
    Provide a high-level API for storing, updating, and
    retrieving data from the database.

    Also manage database sessions and delegate persistence
    operations to repository classes.

    Attributes:
        session_factory (SessionLocal): Factory responsible for
            creating SQLAlchemy sessions.
    """

    def __init__(self, session_factory) -> None:
        """
        Initialize the storage engine.

        Args:
            session_factory (SessionLocal): Factory responsible for
                creating SQLAlchemy sessions.
        """
        self.session_factory = session_factory

    def store_device(self, device: Device) -> None:
        """
        Insert or update a collected device.

        Args:
            device (Device): Device instance to be persisted.
        """
        with self.session_factory() as session:
            repo = DeviceRepository(session)
            repo.upsert(device)
            session.commit()

    def delete_device(self, device: Device) -> None:
        """
        Delete a stored device from the database.

        Args:
            device (Device): Device instance to be removed.
        """
        with self.session_factory() as session:
            repo = DeviceRepository(session)
            repo.delete(device)
            session.commit()

    def list_device_history(self) -> list[Device]:
        """
        Return all stored devices in the database.

        Returns:
            list[Device]: list devices retrieved from the database.
        """
        with self.session_factory() as session:
            repo = DeviceRepository(session)
            return repo.fetch_devices()

    def fetch_device_info(self, ip) -> Device | None:
        """
        Return a device from the database for the given IP address or
        `None` if not found.
        """
        with self.session_factory() as session:
            repo = DeviceRepository(session)
            return repo.fetch_device(ip)

    def count_devices_and_metrics(self) -> tuple[int, int]:
        """
        Return number of devices and metrics in the database.

        Returns:
            tuple[int,int]: Number of devices and metrics in the database.
        """
        with self.session_factory() as session:
            device_repo = DeviceRepository(session)
            metric_repo = MetricRepository(session)
            return (
                device_repo.count_devices(),
                metric_repo.count_metrics(),
            )

    def store_metric(self, metric: MetricRecord) -> None:
        """
        Persist newly collected metric record.

        Args:
            metric (MetricRecord): A metric record captured during a scan cycle.
        """
        with self.session_factory() as session:
            repo = MetricRepository(session)
            repo.insert(metric)
            session.commit()

    def list_metric_history(self) -> list[MetricRecord]:
        """
        Return stored metric history.

        Returns:
            list[MetricRecord]: Metric records retrieved from the database.
        """
        with self.session_factory() as session:
            repo = MetricRepository(session)
            return repo.fetch_metrics()

    def get_or_create_alert_state(
        self, ip: str, metric: str, consecutive_checks: int
    ) -> AlertStateTable:
        """
        Return the alert state for a given IP address and metric.

        Returns:
            AlertStateTable: The found alert state.
        """
        with self.session_factory() as session:
            repo = AlertStateRepository(session=session)
            return repo.fetch_or_create_alert_state(
                ip=ip, metric=metric, consecutive_checks=consecutive_checks
            )

    def list_alert_states(self) -> list[AlertStateTable]:
        """
        Return a list of all alert states in the history.
        """
        with self.session_factory() as session:
            repo = AlertStateRepository(session=session)
            return repo.fetch_alert_states()

    def update_alert_state(self, state: AlertStateTable) -> None:
        """
        Update an alert state.

        Args:
            state (AlertStateTable): The updated instance of AlertStateTable class.
        """
        with self.session_factory() as session:
            repo = AlertStateRepository(session=session)
            repo.update(state=state)
            session.commit()

    def get_device_alert_state(self, ip: str) -> dict[str, str] | None:
        """
        Return alert state of a device for a given IP address.
        """
        with self.session_factory() as session:
            repo = AlertStateRepository(session)
            return repo.fetch_alert_state(ip=ip)

    def delete_alert_state(self, state: AlertStateTable) -> None:
        """
        Delete a stored alert state from the database.

        Args:
            state: AlertStateTable instance to be removed.
        """
        with self.session_factory() as session:
            repo = AlertStateRepository(session=session)
            repo.delete(state=state)
            session.commit()

    def store_alert_event(self, event: AlertEventTable) -> None:
        """
        Store the new alert event.

        Args:
            event (AlertEvent): Instance of the AlertEventTable class.
        """
        with self.session_factory() as session:
            repo = AlertEventRepository(session=session)
            repo.insert(event=event)
            session.commit()

    def get_recent_alert_events(
        self, limit: int = 10, offset: int = 0
    ) -> list[AlertEventTable]:
        """
        Return recent alert events of all devices.
        """
        with self.session_factory() as session:
            repo = AlertEventRepository(session)
            return repo.fetch_recent_alert_events(limit=limit, offset=offset)

    def get_recent_device_alert_events(self, ip: str) -> list[AlertEventTable]:
        """
        Return recent alert events of a device for a given IP address.
        """
        with self.session_factory() as session:
            repo = AlertEventRepository(session=session)
            return repo.fetch_recent_device_alert_events(ip=ip)

    def count_alert_events(self) -> int:
        """
        Return a count of alert events of all devices.
        """
        with self.session_factory() as session:
            repo = AlertEventRepository(session=session)
            return repo.count_alert_events()

    def record_availability(
        self, checks: list[tuple[str, bool]], hour_start: datetime
    ) -> None:
        """
        Store availability check results for an hour.

        Args:
            checks: IP addresses and their availability results.
            hour_start: Start of the hour the checks belong to.
        """
        with self.session_factory() as session:
            repo = AvailabilityRepository(session)
            repo.record_checks(checks, hour_start)
            session.commit()

    def delete_old_availability(self, cutoff: datetime) -> int:
        """
        Delete availability records older than the cutoff.

        Args:
            cutoff: Records before this datetime are deleted.

        Returns:
            int: The number of deleted records.
        """
        with self.session_factory() as session:
            repo = AvailabilityRepository(session)
            deleted = repo.delete_older_than(cutoff)
            session.commit()
            return deleted

    def get_daily_availability(
        self, ip: str, since: datetime
    ) -> dict[date, tuple[int, int]]:
        """
        Fetch daily availability totals for a device since a datetime.

        Args:
            ip: IP address of the device.
            since: Earliest datetime to include.
        """
        with self.session_factory() as session:
            return AvailabilityRepository(session).fetch_daily(ip, since)

    def get_hourly_availability(
        self, ip: str, since: datetime
    ) -> dict[datetime, tuple[int, int]]:
        """
        Fetch hourly availability totals for a device since a datetime.

        Args:
            ip: IP address of the device.
            since: Earliest datetime to include.
        """
        with self.session_factory() as session:
            return AvailabilityRepository(session).fetch_hourly(ip, since)
