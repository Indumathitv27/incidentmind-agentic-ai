import time
import random
from datetime import datetime, timezone
from pathlib import Path

LOG_PATH = Path(__file__).resolve().parents[1] / "data" / "live_logs" / "orders-api.log"
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

ERRORS = [
    'TimeoutError: DB connection timed out',
    'psycopg2.OperationalError: connection pool exhausted',
    'HTTP 500 Internal Server Error',
]
WARNS = [
    'Slow query detected duration_ms=1540',
    'Slow query detected duration_ms=1622',
]
INFOS = [
    'GET /health 200',
    'Retry succeeded',
]

def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def write_line(level, msg, request_id):
    line = f'{now_iso()} level={level} service=orders-api request_id={request_id} msg="{msg}"\n'
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line)

def main():
    i = 1000
    print(f"Writing live logs to: {LOG_PATH}")
    while True:
        i += 1
        request_id = f"req-{i}"
        p = random.random()

        if p < 0.20:
            write_line("ERROR", random.choice(ERRORS), request_id)
        elif p < 0.35:
            write_line("WARN", random.choice(WARNS), request_id)
        else:
            write_line("INFO", random.choice(INFOS), request_id)

        time.sleep(1)

if __name__ == "__main__":
    main()
