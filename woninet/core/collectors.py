import re
from icmplib import ping, SocketPermissionError
import subprocess
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from woninet.core.models import Device, MetricRecord, HostStatus
from woninet.core.storage import StorageEngine
from woninet.utilities.logger import logger_function

rootLogger = logger_function()


def get_arp_mac(ip: str) -> Optional[str]:
    """
    Return MAC address from ARP table for the given IP, or None if not present.

    Notes:
        - Uses `arp -an` output and parses it.
        - Works on most Unix-like systems. If fails, it simply returns None and rely on ICMP only.
    """
    try:
        # Suppress strerr to avoid clutter when ARP table is empty or limited
        output = subprocess.check_output(["arp", "-an"], stderr=subprocess.DEVNULL)
        output = output.decode()
    except Exception as e:
        rootLogger.debug(f"Failed to read ARP table: {e}")
        return None

    regex = rf"\({re.escape(ip)}\)\s+at\s+([0-9a-fA-F:]+)\s"
    match = re.search(regex, output)
    if match:
        return match.group(1)
    return None


def detect_host(
    ip: str, src_addr: str, timeout: float = 1.0, stop_event=None
) -> HostStatus:
    """
    Combined ARP + ICMP detection for accurate device status.

    Rules:
        - If ARP_FAIL and ICMP_FAIL -> Host does NOT exist (exists=False, reachable=False)
        - If ARP_OK and ICMP_FAIL -> Host exists but unreachable / ICMP blocked
        - If ARP_OK and ICMP_OK < 300 ms -> Host is reachable
        - If ARP_OK and ICMP_OK >= 300 ms -> Treat as ARP-timeout noise (unreachable)
    """
    status = HostStatus(ip=ip)

    # Skip source ip to prevent confusion.
    if ip == src_addr:
        status.exists = None
        status.reachable = None
        status.mac = None
        status.latency = None
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
    except Exception as e:
        rootLogger.error(
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
        if latency < 300.0:
            # Acceptable latency (reachable)
            status.exists = bool(mac)
            status.reachable = True
        else:
            # High-latency ICMP, often ARP resolution noise (unreachable)
            status.exists = bool(mac)
            status.reachable = False

    return status


class BaseCollector:
    """
    Abstract base class for all monitoring collectors.
    Each collector periodically gathers metrics from devices.
    """

    interval = 10

    def collect(
        self,
        devices: Dict[str, Device],
        ip_addr: str,
        store_callback: StorageEngine,
        stop_event=None,
    ) -> List[MetricRecord]:
        """
        Collect metrics from devices.
        Must be implemented by subclasses.
        """
        raise NotImplementedError

    def run(
        self,
        devices: Dict[str, Device],
        ip_addr,
        store_callback: StorageEngine,
        stop_event=None,
    ):
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
        devices: Dict[str, Device],
        ip_addr: str,
        store_callback: StorageEngine,
        stop_event=None,
    ) -> List[MetricRecord]:
        """
        For each device:
            - Use ARP + ICMP to determine existence and reachability.
            - Update Device fields.
            - Record latency metric only when reachable and latency is sane.
        """
        if stop_event and stop_event.is_set():
            return []

        results: List[MetricRecord] = []

        def worker(ip: str, dev: Device) -> MetricRecord:
            try:
                status = detect_host(
                    ip=ip, src_addr=ip_addr, timeout=1.0, stop_event=stop_event
                )
            except (PermissionError, SocketPermissionError):
                raise

            # Update device state from status
            dev.exists = status.exists
            dev.reachable = status.reachable
            dev.mac = status.mac
            dev.latency = status.latency

            if status.reachable:
                # Only consider reachable hosts as recently seen
                dev.update_seen()

            # Store device to history
            if dev.latency:
                store_callback.store(device=dev)

            value = status.latency if status.reachable else 0

            if value != 0:
                rootLogger.debug(
                    f"Device {ip}: exists={dev.exists}, reachable={dev.reachable}, "
                    f"MAC={dev.mac}, latency={value:.2f} ms"
                )
            else:
                if dev.exists:
                    rootLogger.debug(
                        f"Device {ip}: exists={dev.exists}, reachable={dev.reachable}, "
                        f"MAC={dev.mac}, latency=0.0"
                    )
                else:
                    rootLogger.trace(
                        f"Device {ip}: exists={dev.exists}, reachable={dev.reachable}, "
                        f"MAC={dev.mac}, latency=0.0"
                    )
                pass

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
                except Exception as e:
                    ip = future_to_ip[future]
                    rootLogger.error(f"Error in PingCollector for {ip}: {e}")
                    continue
                else:
                    if metric.value != 0:
                        results.append(metric)

        return results
