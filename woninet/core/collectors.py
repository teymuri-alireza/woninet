import re
import logging
import subprocess
from icmplib import ping, SocketPermissionError, SocketAddressError
from concurrent.futures import ThreadPoolExecutor, as_completed
from woninet.core.models import Device, MetricRecord, HostStatus
from woninet.core.storage import StorageEngine

core_logger = logging.getLogger("core")


def get_arp_mac(ip: str) -> str | None:
    """
    Return MAC address from ARP table for the given IP, or None if not present.
    """
    try:
        # Suppress strerr to avoid clutter when ARP table is empty or limited
        output = subprocess.check_output(["arp", "-an"], stderr=subprocess.DEVNULL)
        output = output.decode()
    except Exception as e:
        core_logger.error(f"Failed to read ARP table: {e}")
        return None

    regex = rf"\({re.escape(ip)}\)\s+at\s+([0-9a-fA-F:]+)\s"
    match = re.search(regex, output)
    if match:
        return match.group(1)
    return None


def detect_host(
    ip: str,
    src_addr: str,
    timeout: float = 1.0,
    stop_event=None,
    arp_noise_limit: float = 300.0,
) -> HostStatus | None:
    """
    Combined ARP + ICMP detection for accurate device status.

    Detection_Rules:
        - ARP_FAIL and ICMP_FAIL → Host doesn't exist
        - ARP_OK and ICMP_FAIL → Host exists but is unreachable or blocks ICMP
        - ARP_OK and ICMP_OK < arp_noise_limit → Host is reachable
        - ARP_OK and ICMP_OK >= arp_noise_limit → Treat as ARP-timeout noise (unreachable)

    Args:
        ip: IP address of the host to scan.
        src_addr: Source IP address used to send packets.
        timeout: Timeout for ICMP scan.
        stop_event: Event used to control the monitoring life cycle.
        arp_noise_limit: Threshold above which ARP fluctuations are considered noise.

    Returns:
        HostStatus|None: A `HostStatus` instance if the stop event is not triggered; otherwise, None.
    """
    status = HostStatus(ip=ip)

    # Skip source ip to prevent confusion.
    if ip == src_addr:
        status.exists = False
        status.reachable = False
        status.mac = None
        status.latency = 0.0
        return status

    if stop_event and stop_event.is_set():
        return None

    # ARP check
    mac = get_arp_mac(ip=ip)
    if mac:
        status.exists = True
        status.mac = mac

    # ICMP check
    try:
        response = ping(
            source=src_addr,
            address=ip.strip(),
            timeout=timeout,
            count=2,
            privileged=True,
            interval=1,
        )
        if stop_event and stop_event.is_set():
            return None
    except (PermissionError, SocketPermissionError):
        raise
    except SocketAddressError:
        raise
    except Exception as e:
        core_logger.error(
            f"Error during ICMP ping at detect_host function, to {ip}: {e}"
        )
        response = 0

    status.latency = response.avg_rtt
    latency: float = status.latency

    # Classification logic
    if not mac and latency == 0:
        # Host is not in ARP table and doesn't respond to ICMP
        status.exists = False
        status.reachable = False
        return status

    if mac and latency == 0:
        # Device exists but doesn't respond to ICMP
        status.exists = True
        status.reachable = False
        return status

    if latency != 0:
        if arp_noise_limit == 0 or latency < arp_noise_limit:
            # Acceptable latency (reachable)
            status.exists = bool(mac)
            status.reachable = True
        else:
            # High-latency ICMP, often ARP resolution noise (unreachable)
            status.exists = bool(mac)
            status.reachable = False

    # Refresh MAC if host responded to ICMP but ARP cache was stale
    if status.reachable and mac is None:
        new_mac = get_arp_mac(ip=ip)
        if new_mac:
            status.exists = True
            status.mac = new_mac

    return status


class BaseCollector:
    """
    Abstract base class for all monitoring collectors.
    Each collector periodically gathers metrics from devices.
    """

    interval = 10

    def collect(
        self,
        devices: dict[str, Device],
        ip_addr: str,
        store_callback: StorageEngine,
        stop_event=None,
        arp_noise_limit: float = 300.0,
    ) -> list | list[MetricRecord]:
        """
        Collect metrics from devices.
        Must be implemented by subclasses.
        """
        raise NotImplementedError

    def run(
        self,
        devices: dict[str, Device],
        ip_addr,
        store_callback: StorageEngine,
        stop_event=None,
        arp_noise_limit: float = 300.0,
    ) -> None:
        """
        Main execution function for the collector.
        Send collected metrics to storage.
        """
        if stop_event and stop_event.is_set():
            return
        result = self.collect(
            devices,
            ip_addr=ip_addr,
            store_callback=store_callback,
            stop_event=stop_event,
            arp_noise_limit=arp_noise_limit,
        )
        # Store metric data
        store_callback.store_metric(result)


class PingCollector(BaseCollector):
    """
    Collector that measures ICMP latency to devices,
    enhanced with ARP-based existence detection.
    """

    interval = 5

    def collect(
        self,
        devices: dict[str, Device],
        ip_addr: str,
        store_callback: StorageEngine,
        stop_event=None,
        arp_noise_limit: float = 300.0,
    ) -> list | list[MetricRecord]:
        """
        For each device:
            - Use ARP + ICMP to determine existence and reachability.
            - Update Device fields.
            - Record latency metric only when reachable and latency is sane.
        """
        if stop_event and stop_event.is_set():
            return []

        results: list[MetricRecord] = []
        db_devices = store_callback.get_history()

        def worker(ip: str, dev: Device) -> MetricRecord:
            try:
                status = detect_host(
                    ip=ip,
                    src_addr=ip_addr,
                    timeout=1.0,
                    stop_event=stop_event,
                    arp_noise_limit=arp_noise_limit,
                )
            except (PermissionError, SocketPermissionError):
                raise
            except SocketAddressError:
                raise

            # Update device state from status
            dev.exists = status.exists
            dev.reachable = status.reachable
            if status.mac is not None:
                dev.mac = status.mac
            dev.latency = status.latency

            if status.reachable:
                # Only consider reachable hosts as recently seen
                dev.update_seen()

            # Store device to history
            is_known = any(db_device.ip == dev.ip for db_device in db_devices)
            if dev.reachable or is_known:
                store_callback.store(device=dev)

            value = status.latency if status.reachable else 0

            if dev.reachable:
                core_logger.debug(
                    f"Device {ip}: \tUP,\t MAC={dev.mac}, latency={value:.2f} ms"
                )
            elif dev.exists:
                core_logger.debug(
                    f"Device {ip}: \tDOWN,\t MAC={dev.mac}, latency=OFFLINE"
                )
            else:
                core_logger.trace(
                    f"Device {ip}: \tABSENT,\t MAC={dev.mac}, latency=OFFLINE"
                )

            return MetricRecord(ip, "latency_ms", value)

        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_ip = {
                executor.submit(worker, ip, dev): ip for ip, dev in devices.items()
            }

            for future in as_completed(future_to_ip):
                if stop_event and stop_event.is_set():
                    break
                if stop_event.is_set():
                    return results
                try:
                    metric = future.result()
                except (PermissionError, SocketPermissionError):
                    raise
                except SocketAddressError:
                    raise
                except Exception as e:
                    ip = future_to_ip[future]
                    core_logger.error(f"Error in PingCollector for {ip}: {e}")
                    continue
                else:
                    if metric.value != 0:
                        results.append(metric)

        return results
