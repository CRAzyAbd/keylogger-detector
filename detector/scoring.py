from dataclasses import dataclass, field


# Points awarded for each signal.
KEYBOARD_ACCESS_POINTS = 40
BEACON_POINTS = 35
CORRELATION_BONUS = 50

ALERT_THRESHOLD = 70


@dataclass
class Verdict:
    """The scoring result for a single process."""
    pid: int
    name: str
    score: int = 0
    reasons: list = field(default_factory=list)

    @property
    def is_alert(self):
        return self.score >= ALERT_THRESHOLD


def score_process(signals):
    """Score one process from its collected signals."""
    verdict = Verdict(pid=signals["pid"], name=signals["name"])

    reads_keyboard = signals.get("reads_keyboard", False)
    beacon_hits = signals.get("beacon_hits", 0)
    is_beaconing = beacon_hits >= 3

    if reads_keyboard:
        verdict.score += KEYBOARD_ACCESS_POINTS
        verdict.reasons.append("reads raw keyboard input")

    if is_beaconing:
        verdict.score += BEACON_POINTS
        remote = signals.get("beacon_remote", "an external host")
        verdict.reasons.append(f"beacons to {remote} ({beacon_hits} times)")

    if reads_keyboard and is_beaconing:
        verdict.score += CORRELATION_BONUS
        verdict.reasons.append(
            "CAPTURES KEYSTROKES *and* PHONES HOME — classic keylogger pattern"
        )

    return verdict


def score_all(process_signals):
    """Score a list of processes and return verdicts sorted by score."""
    verdicts = [score_process(s) for s in process_signals]
    return sorted(verdicts, key=lambda v: v.score, reverse=True)


if __name__ == "__main__":
    # Synthetic examples to demonstrate the scoring logic (no real malware).
    examples = [
        {"pid": 3271, "name": "gnome-shell",
         "reads_keyboard": True, "beacon_hits": 0},
        {"pid": 8001, "name": "firefox",
         "reads_keyboard": False, "beacon_hits": 12, "beacon_remote": "142.250.x.x"},
        {"pid": 6666, "name": "suspicious.py",
         "reads_keyboard": True, "beacon_hits": 9, "beacon_remote": "109.74.200.23"},
    ]

    for verdict in score_all(examples):
        flag = "  >>> ALERT" if verdict.is_alert else ""
        print(f"[{verdict.pid:>6}] {verdict.name:<16} score={verdict.score:<4}{flag}")
        for reason in verdict.reasons:
            print(f"           - {reason}")
