import re
import logging
import subprocess
from typing import Generator, Any
from icmplib import ping, SocketPermissionError, SocketAddressError
from concurrent.futures import ThreadPoolExecutor, as_completed
from woninet.core.models import Device, MetricRecord, HostStatus

core_logger = logging.getLogger("core")


def read_arp_table() -> dict[str, str]:
    """
    Return all valid MAC addresses from the ARP table.

    Returns:
        dict[str,str]: Dictionary contaning IP addressses and the related MAC addresses.
    """
    table = {}
    try:
        # Suppress strerr to avoid clutter when ARP table is empty or limited
        output = subprocess.check_output(["arp", "-an"], stderr=subprocess.DEVNULL)
        output = output.decode()
    except Exception:
        return table

    for line in output.splitlines():
        match = re.search(r"\((.*?)\)\s+at\s+([0-9a-fA-F:]+)", line)
        if match:
            table[match.group(1)] = match.group(2)
    return table


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
    target_ip: str,
    source_ip: str,
    timeout: float = 1.0,
    stop_event=None,
    arp_noise_limit: float = 300.0,
    arp_table: dict[str, str] = None,
) -> HostStatus | None:
    """
    Combined ARP + ICMP detection for accurate device status.

    Detection_Rules:
        - ARP_FAIL and ICMP_FAIL → Host doesn't exist
        - ARP_OK and ICMP_FAIL → Host exists but is unreachable or blocks ICMP
        - ARP_OK and ICMP_OK < arp_noise_limit → Host is reachable
        - ARP_OK and ICMP_OK >= arp_noise_limit → Treat as ARP-timeout noise (unreachable)

    Args:
        target_ip: IP address of the host to scan.
        source_ip: Source IP address used to send packets.
        timeout: Timeout for ICMP scan.
        stop_event: Event used to control the monitoring life cycle.
        arp_noise_limit: Threshold above which ARP fluctuations are treated as noise.
        arp_table: Dictionary of ARP table contaning IP addressses and the related
            MAC addresses.

    Returns:
        HostStatus|None: A `HostStatus` instance if the stop event is not triggered; otherwise, None.
    """
    status = HostStatus(ip=target_ip)

    # Skip source ip to prevent confusion.
    if target_ip == source_ip:
        status.exists = False
        status.reachable = False
        status.mac = None
        status.latency = 0.0
        return status

    if stop_event and stop_event.is_set():
        return None

    # ARP check
    mac = arp_table.get(target_ip)
    if mac:
        status.exists = True
        status.mac = mac

    # ICMP check
    try:
        response = ping(
            source=source_ip,
            address=target_ip.strip(),
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
            f"Error during ICMP ping at detect_host function, to {target_ip}: {e}"
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
            status.latency = 0

    # Refresh MAC if host responded to ICMP but ARP cache was stale
    if status.reachable and mac is None:
        new_mac = get_arp_mac(ip=target_ip)
        if new_mac:
            status.exists = True
            status.mac = new_mac

    return status


class BaseCollector:
    """
    Abstract base class for all monitoring collectors.
    """

    def collect(self, *args, **kwargs) -> Any:
        raise NotImplementedError


class PingCollector(BaseCollector):
    """
    Collector that measures ICMP latency to devices,
    enhanced with ARP-based existence detection.
    """

    def collect(
        self,
        candidate_devices: dict[str, Device],
        local_ip: str,
        device_records: list[Device],
        stop_event=None,
        arp_noise_limit: float = 300.0,
        max_thread_workers: int = 4,
    ) -> Generator[tuple[()] | tuple, Any, None]:
        """
        For each device:
            - Use ARP + ICMP to determine existence and reachability.
            - Update Device fields.
            - Record latency metric only when reachable and latency is sane.
        """
        if stop_event and stop_event.is_set():
            yield ()

        arp_table = read_arp_table()

        def worker(
            ip: str, dev: Device
        ) -> tuple[Device, MetricRecord] | tuple[None, MetricRecord]:
            try:
                status = detect_host(
                    target_ip=ip,
                    source_ip=local_ip,
                    timeout=1.0,
                    stop_event=stop_event,
                    arp_noise_limit=arp_noise_limit,
                    arp_table=arp_table,
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

            if dev.reachable:
                # Only consider reachable hosts as recently seen
                dev.update_seen()

            # Check if the found device is already stored in the database.
            is_known = any(
                device_record.ip == dev.ip for device_record in device_records
            )

            if dev.reachable:
                core_logger.debug(
                    f"Device {ip}: \tUP,\t MAC={dev.mac}, latency={dev.latency:.2f} ms"
                )
            elif is_known:
                core_logger.debug(
                    f"Device {ip}: \tDOWN,\t MAC={dev.mac}, latency=OFFLINE"
                )
            else:
                core_logger.trace(
                    f"Device {ip}: \tABSENT,\t MAC={dev.mac}, latency=OFFLINE"
                )

            if dev.reachable or is_known:
                return (dev, MetricRecord(ip, "latency_ms", dev.latency))
            else:
                return (None, MetricRecord(ip, "latency_ms", dev.latency))

        with ThreadPoolExecutor(max_workers=max_thread_workers) as executor:
            future_to_ip = {
                executor.submit(worker, ip, dev): ip
                for ip, dev in candidate_devices.items()
            }

            for future in as_completed(future_to_ip):
                results = []
                if stop_event and stop_event.is_set():
                    break
                if stop_event.is_set():
                    yield ()
                try:
                    future_device, future_metric = future.result()
                    results.append(future_device)
                except (PermissionError, SocketPermissionError):
                    raise
                except SocketAddressError:
                    raise
                except Exception as e:
                    ip = future_to_ip[future]
                    core_logger.error(f"Error in PingCollector for {ip}: {e}")
                    continue
                else:
                    if future_metric.value != 0:
                        results.append(future_metric)
                    else:
                        results.append(None)
                finally:
                    yield tuple(results)

        yield ()
