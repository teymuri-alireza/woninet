from sqlalchemy import Integer, String, DateTime, Float
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from woninet.database.base import Base


class DeviceTable(Base):
    """
    ORM model representing a discovered network device.

    Each row stores the most recently observed state for a device,
    including IP address, MAC address, latency, and timestamp
    of the last time device was reachable.
    """
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ip: Mapped[str] = mapped_column(String, index=True)
    mac: Mapped[str | None] = mapped_column(String, index=True, nullable=True)
    latency: Mapped[float] = mapped_column(Float)
    last_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default=lambda: datetime.now(),
        index=True
    )


class MetricTable(Base):
    """
    ORM model representing a metric record of a device model.

    Each row stores the metric record of device, including IP address,
    metric name, value and timestamp of the time the metric was recorded.
    """
    __tablename__ = "metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_ip: Mapped[str] = mapped_column(String, index=True)
    metric: Mapped[str] = mapped_column(String, index=True)
    value: Mapped[float] = mapped_column(Float)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default=lambda: datetime.now(),
        index=True
    )
