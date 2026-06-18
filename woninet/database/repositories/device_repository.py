from datetime import datetime
from sqlalchemy.orm import Session
from woninet.database.tables import DeviceTable
from woninet.core.models import Device


class DeviceRepository:
    """
    Repository for persisting and retrieving Device entities.

    Eencapsulate ORM operations on `DeviceTable` and expose a
    simple API in terms of the domain model `Device`.

    Attributes:
        session (Session): SQLAlchemy session used for
            database operations
    """

    def __init__(self, session: Session) -> None:
        """
        Initialize the repository.

        Args:
            session (Session): SQLAlchemy session used for all database operations.
        """
        self.session: Session = session

    def upsert(self, dev: Device) -> None:
        """
        Insert or update a device into the database.

        If `dev.mac` is present, the existing record is looked up by MAC
        address, otherwise it is looked up by IP address. If the record
        is found, its IP and latency fields are updated. The `last_seen`
        timestamp is set to `dev.last_seen` or the current time, and is only
        updated when device is reachable (`dev.latency > 0`).

        All changes are committed immediatly.

        Args:
            dev (Device): Domain `Device` instance.
        """
        query = self.session.query(DeviceTable)
        if dev.mac:
            query = query.filter(DeviceTable.mac == dev.mac)
        else:
            query = query.filter(DeviceTable.ip == dev.ip)
        existing = query.first()
        now = datetime.now()

        if existing:
            existing.ip = dev.ip
            existing.latency = dev.latency
            if dev.latency > 0:
                existing.last_seen = dev.last_seen or now
            existing.packet_loss = dev.packet_loss
        else:
            existing = DeviceTable(
                ip=dev.ip,
                mac=dev.mac,
                latency=dev.latency,
                packet_loss=dev.packet_loss,
                last_seen=dev.last_seen or now,
            )
            self.session.add(existing)

    def fetch_devices(self) -> list[Device]:
        """
        Return all existing devices from the database.

        Returns:
            list[Device]: A list of `Device` instances from `DeviceTable` in the database.
        """
        rows = self.session.query(DeviceTable).all()
        result = []
        for row in rows:
            dev = Device(ip=row.ip)
            dev.mac = row.mac
            dev.latency = row.latency
            dev.packet_loss = row.packet_loss
            dev.last_seen = row.last_seen
            result.append(dev)
        return result

    def fetch_device(self, ip: str) -> Device | None:
        """
        Return a device from the database for the given IP address or
        `None` if not found.
        """
        row = self.session.query(DeviceTable).filter_by(ip=ip).one_or_none()
        if row is not None:
            device = Device(ip=row.ip)
            device.mac = row.mac
            device.latency = row.latency
            device.last_seen = row.last_seen
            device.packet_loss = row.packet_loss
            return device
        return None

    def count_devices(self) -> int:
        """
        Return the number of existing devices in the database.

        Returns:
            int: Number of devices in the database.
        """
        total = self.session.query(DeviceTable).count()
        return total
