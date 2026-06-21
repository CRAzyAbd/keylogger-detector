import ipaddress
import time
from collections import defaultdict

import psutil


def is_external(ip):
    """Return True if the IP is a public (non-local) address."""
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return False
    return not (addr.is_private or addr.is_loopback or addr.is_link_local)


def sample_outbound():
    """Return the set of (pid, remote_ip) pairs currently connected outbound."""
    seen = set()
    for conn in psutil.net_connections(kind="inet"):
        if conn.status != psutil.CONN_ESTABLISHED:
            continue
        if not conn.raddr or conn.pid is None:
            continue
        if not is_external(conn.raddr.ip):
            continue
        seen.add((conn.pid, conn.raddr.ip))
    return seen


def watch_for_beacons(duration=20, interval=1):
    """Sample outbound connections over time, recording when each is seen."""
    observations = defaultdict(list)
    samples = duration // interval
    for _ in range(samples):
        now = time.time()
        for pid, remote_ip in sample_outbound():
            observations[(pid, remote_ip)].append(now)
        time.sleep(interval)
    return observations


def find_beacons(observations, min_hits=3):
    """Flag (pid, remote) endpoints observed repeatedly — possible beacons."""
    beacons = []
    for (pid, remote_ip), times in observations.items():
        if len(times) >= min_hits:
            beacons.append({
                "pid": pid,
                "remote_ip": remote_ip,
                "hits": len(times),
                "span_seconds": round(times[-1] - times[0], 1),
            })
    return beacons


def process_name(pid):
    """Return a process's name, or 'unknown' if unavailable."""
    try:
        return psutil.Process(pid).name()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return "unknown"


if __name__ == "__main__":
    print("Watching outbound connections for 20 seconds...")
    observations = watch_for_beacons(duration=20, interval=1)
    beacons = find_beacons(observations)
    if not beacons:
        print("No repeated outbound connections detected.")
        print("Tip: run as root via the venv's Python:")
        print("    sudo venv/bin/python detector/netwatch.py")
    for b in sorted(beacons, key=lambda x: x["hits"], reverse=True):
        name = process_name(b["pid"])
        print(f"[{b['pid']:>6}] {name:<20} -> {b['remote_ip']:<18} "
              f"seen {b['hits']}x over {b['span_seconds']}s")
