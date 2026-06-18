# Keylogger Detector

A behavioral keylogger detector. It watches running processes and flags any
that combine the signs of a keylogger: reading raw keyboard input, beaconing
out to the network on a schedule, and running hidden in the background.

Detection is behavioral, not signature-based — it watches what a process *does*,
not what it looks like.
