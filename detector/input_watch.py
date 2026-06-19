import os
import pwd


INPUT_DEVICE_DIR = "/dev/input"


def get_process_name(pid):
    """Return the process's command name from /proc/<pid>/comm."""
    try:
        with open(f"/proc/{pid}/comm") as f:
            return f.read().strip()
    except (FileNotFoundError, PermissionError):
        return "unknown"


def get_process_owner(pid):
    """Return the username that owns the given process."""
    try:
        uid = os.stat(f"/proc/{pid}").st_uid
        return pwd.getpwuid(uid).pw_name
    except (FileNotFoundError, PermissionError, KeyError):
        return "unknown"


def get_open_input_devices(pid):
    """Return the input device paths that the given process has open."""
    fd_dir = f"/proc/{pid}/fd"
    open_inputs = []
    try:
        for fd in os.listdir(fd_dir):
            fd_path = os.path.join(fd_dir, fd)
            try:
                target = os.readlink(fd_path)
            except OSError:
                continue
            if target.startswith(INPUT_DEVICE_DIR):
                open_inputs.append(target)
    except (FileNotFoundError, PermissionError):
        pass
    return open_inputs


def find_input_readers():
    """Return info on every process holding raw input devices open."""
    readers = []
    for entry in os.listdir("/proc"):
        if not entry.isdigit():
            continue
        pid = int(entry)
        devices = get_open_input_devices(pid)
        if devices:
            readers.append({
                "pid": pid,
                "name": get_process_name(pid),
                "user": get_process_owner(pid),
                "devices": sorted(set(devices)),
            })
    return readers


if __name__ == "__main__":
    found = find_input_readers()
    if not found:
        print("No processes reading raw input devices were found.")
        print("Tip: run it with sudo to inspect every process:")
        print("    sudo python3 detector/input_watch.py")
    for r in found:
        print(f"[{r['pid']:>6}] {r['user']:<12} {r['name']:<20} "
              f"{len(r['devices'])} device(s): {', '.join(r['devices'])}")
