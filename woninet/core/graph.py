from pathlib import Path
from matplotlib import pyplot as plt
from woninet.database.tables import AlertEventTable

CHARTS_PATH = Path(__file__).parent.parent / "charts"


class GraphEngine:
    """
    Engine for generating graphs and visualizations of network device metrics.
    """

    def design_device_latency_events(self, ip: str, recent_device_alert_events: list[AlertEventTable]) -> None:
        """
        Generate and save a latency chart for a device.

        Creates a line plot showing latency values over time with trigger and recovery events
        marked as scatter points. The chart is saved as a PNG file.

        Args:
            ip: The IP address of the device for the chart title and filename.
            recent_device_alert_events: List of alert events containing latency metrics and event types.
        """
        times = []
        latency_values = []
        trigger_times = []
        trigger_values = []
        recover_times = []
        recover_values = []

        for event in recent_device_alert_events:
            if event.metric == "latency_ms":
                times.append(event.timestamp)
                latency_values.append(event.value)
                if event.event_type == "trigger":
                    trigger_times.append(event.timestamp)
                    trigger_values.append(event.value)
                elif event.event_type == "recover":
                    recover_times.append(event.timestamp)
                    recover_values.append(event.value)

        fig, ax = plt.subplots(figsize=(16, 8), dpi=150)

        ax.plot(times, latency_values, label="Latency")
        ax.axhline(100, linestyle="--", label="Alert Threshold")
        ax.scatter(trigger_times, trigger_values, marker="^", color="red", label="Trigger")
        ax.scatter(recover_times, recover_values, marker="v", color="blue", label="Recover")

        ax.set_title(f"{ip} - Latency")
        ax.set_xlabel("Time")
        ax.set_ylabel("Latency (ms)")
        ax.legend()
        ax.grid(True, alpha=0.3)

        fig.autofmt_xdate()
        fig.savefig(f"{CHARTS_PATH}/{ip}.png", bbox_inches="tight")
        plt.close(fig)
