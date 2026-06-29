import time
import signal

from detector import input_watch
from detector import netwatch
from detector import scoring
from detector import alerts
from detector.logger import get_logger

log = get_logger()

# How long each network-watch window lasts, and how often we re-scan.
NETWORK_WINDOW = 15
NETWORK_INTERVAL = 1

_running = True


def _handle_stop(signum, frame):
    """Flip the run flag so the main loop can exit cleanly."""
    global _running
    _running = False
    log.info("Shutdown requested — finishing current cycle and stopping.")


def collect_signals():
    """Run both detectors and merge their findings per process (by PID)."""
    signals = {}

    # Signal 1: processes reading raw keyboard/input devices.
    for reader in input_watch.find_input_readers():
        pid = reader["pid"]
        signals[pid] = {
            "pid": pid,
            "name": reader["name"],
            "reads_keyboard": True,
            "beacon_hits": 0,
        }

    # Signal 2: processes beaconing to external hosts.
    observations = netwatch.watch_for_beacons(
        duration=NETWORK_WINDOW, interval=NETWORK_INTERVAL
    )
    beacons = netwatch.find_beacons(observations)
    for beacon in beacons:
        pid = beacon["pid"]
        if pid not in signals:
            signals[pid] = {
                "pid": pid,
                "name": netwatch.process_name(pid),
                "reads_keyboard": False,
                "beacon_hits": 0,
            }
        signals[pid]["beacon_hits"] = beacon["hits"]
        signals[pid]["beacon_remote"] = beacon["remote_ip"]

    return list(signals.values())


def run_once():
    """Perform one full detection cycle: collect, score, log."""
    log.debug("Starting detection cycle.")
    process_signals = collect_signals()
    verdicts = scoring.score_all(process_signals)

    for verdict in verdicts:
        if verdict.is_alert:
            log.critical(
                "ALERT pid=%s name=%s score=%s :: %s",
                verdict.pid, verdict.name, verdict.score,
                "; ".join(verdict.reasons),
            )
            if alerts.send_alert(verdict):
                log.debug("Alert for pid=%s sent to backend.", verdict.pid)
            else:
                log.warning("Could not reach backend for pid=%s alert.", verdict.pid)
        elif verdict.score > 0:
            log.info(
                "watch pid=%s name=%s score=%s :: %s",
                verdict.pid, verdict.name, verdict.score,
                "; ".join(verdict.reasons),
            )

    log.debug("Cycle complete: %s processes scored.", len(verdicts))


def main():
    signal.signal(signal.SIGINT, _handle_stop)
    signal.signal(signal.SIGTERM, _handle_stop)

    log.info("Keylogger detector started. Press Ctrl+C to stop.")
    while _running:
        run_once()
    log.info("Keylogger detector stopped.")


if __name__ == "__main__":
    main()
