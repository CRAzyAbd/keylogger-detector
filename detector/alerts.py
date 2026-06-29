import json
import urllib.request
import urllib.error


BACKEND_URL = "http://localhost:4000/api/alerts"
REQUEST_TIMEOUT = 3


def send_alert(verdict):
    """POST a single verdict to the reporting backend. Returns True on success."""
    payload = json.dumps({
        "pid": verdict.pid,
        "name": verdict.name,
        "score": verdict.score,
        "reasons": verdict.reasons,
    }).encode("utf-8")

    request = urllib.request.Request(
        BACKEND_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
            return response.status in (200, 201)
    except (urllib.error.URLError, OSError):
        return False
