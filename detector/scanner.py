import psutil


def scan_processes():
    """Return a list of running processes with their basic metadata."""
    processes = []
    for proc in psutil.process_iter(["pid", "name", "username", "status", "cmdline"]):
        try:
            info = proc.info
            processes.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return processes


def format_process(info):
    """Return a single readable line describing one process."""
    pid = info["pid"]
    name = info["name"] or "unknown"
    user = info["username"] or "unknown"
    status = info["status"] or "unknown"
    cmdline = info["cmdline"]
    command = " ".join(cmdline) if cmdline else name
    return f"[{pid:>6}] {status:<10} {user:<15} {name:<25} {command}"


if __name__ == "__main__":
    for p in scan_processes():
        print(format_process(p))
