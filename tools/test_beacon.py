"""
BENIGN TEST FIXTURE — this is NOT malware.

It makes a harmless outbound TCP connection to a public host on a fixed
schedule, purely so the detector has a 'beacon' timing pattern to catch.
It reads nothing, captures no keystrokes, and sends no data. It only mimics
the *network timing* of a beacon. Stop it any time with Ctrl+C.
"""
import socket
import time

TARGET_HOST = "1.1.1.1"   # Cloudflare's public IP — an external address
TARGET_PORT = 443
INTERVAL = 5              # seconds between connections

print(f"Test beacon: connecting to {TARGET_HOST}:{TARGET_PORT} every "
      f"~{INTERVAL}s. Ctrl+C to stop.")

while True:
    try:
        sock = socket.create_connection((TARGET_HOST, TARGET_PORT), timeout=5)
        print(f"[{time.strftime('%H:%M:%S')}] connected")
        time.sleep(2)        # hold briefly so a sampler can observe it
        sock.close()
    except OSError as error:
        print(f"connection failed: {error}")
    time.sleep(INTERVAL)
