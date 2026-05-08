from sqlalchemy import Integer, String, DateTime, Float, UniqueConstraint
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
        DateTime(timezone=False), default=lambda: datetime.now(), index=True
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
        DateTime(timezone=False), default=lambda: datetime.now(), index=True
    )


class AlertStateTable(Base):
    """
    ORM model representing an alert state for a specific device.

    Each row stores the alert state of a device, including device IP address,
    metric name, last state, and last time alert triggered.
    """

    __tablename__ = "alert_state"
    __table_args__ = (
        UniqueConstraint("device_ip", "metric", name="uix_device_metric"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_ip: Mapped[str] = mapped_column(String, index=True)
    metric: Mapped[str] = mapped_column(String, index=True)
    state: Mapped[str] = mapped_column(String, default="ok", index=True)
    triggered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), index=True, nullable=True
    )


class AlertEventTable(Base):
    """
    ORM model representing an alert event occured.

    Each row stores the alert event of a device, including device IP address,
    metric name, captured value of metric, event type, and timestamp.
    """

    __tablename__ = "alert_event"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_ip: Mapped[str] = mapped_column(String, index=True)
    metric: Mapped[str] = mapped_column(String, index=True)
    value: Mapped[float] = mapped_column(Float)
    event_type: Mapped[str] = mapped_column(String, index=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, index=True, nullable=True
    )
