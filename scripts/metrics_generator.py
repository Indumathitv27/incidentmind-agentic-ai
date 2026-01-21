import json
import time
import random
from datetime import datetime, timezone
from pathlib import Path

OUT_PATH = Path(__file__).resolve().parents[1] / "data" / "live_metrics" / "orders-api.jsonl"
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def clamp(x, lo, hi):
    return max(lo, min(hi, x))

def main():
    print(f"Writing live metrics to: {OUT_PATH}")

    # Baselines
    cpu = 35.0
    mem = 55.0
    latency_p95 = 250.0
    error_rate = 0.01
    db_wait = 50.0
    queue_depth = 10.0

    i = 0
    while True:
        i += 1

        # Normal small noise
        cpu = clamp(cpu + random.uniform(-2, 2), 5, 95)
        mem = clamp(mem + random.uniform(-1.5, 1.5), 10, 95)
        latency_p95 = clamp(latency_p95 + random.uniform(-30, 30), 80, 2000)
        db_wait = clamp(db_wait + random.uniform(-10, 10), 0, 1500)
        queue_depth = clamp(queue_depth + random.uniform(-2, 2), 0, 500)

        # Occasionally inject an "incident" burst
        # Every ~40 ticks we create a spike for 10-15 ticks
        if i % 40 == 0:
            burst_type = random.choice(["db", "latency", "error"])
            burst_len = random.randint(10, 15)
            for _ in range(burst_len):
                if burst_type == "db":
                    db_wait = clamp(db_wait + random.uniform(80, 180), 0, 1500)
                    error_rate = clamp(error_rate + random.uniform(0.01, 0.03), 0, 1)
                    latency_p95 = clamp(latency_p95 + random.uniform(50, 120), 80, 2000)
                elif burst_type == "latency":
                    latency_p95 = clamp(latency_p95 + random.uniform(120, 260), 80, 2000)
                    cpu = clamp(cpu + random.uniform(5, 12), 5, 95)
                else:  # error burst
                    error_rate = clamp(error_rate + random.uniform(0.02, 0.06), 0, 1)
                    queue_depth = clamp(queue_depth + random.uniform(10, 30), 0, 500)

                row = {
                    "ts": now_iso(),
                    "service": "orders-api",
                    "metrics": {
                        "cpu_pct": round(cpu, 2),
                        "memory_pct": round(mem, 2),
                        "latency_p95_ms": round(latency_p95, 2),
                        "error_rate": round(error_rate, 4),
                        "db_wait_time_ms": round(db_wait, 2),
                        "queue_depth": round(queue_depth, 2),
                    }
                }
                with open(OUT_PATH, "a", encoding="utf-8") as f:
                    f.write(json.dumps(row) + "\n")
                time.sleep(1)

        # Slowly decay error rate back toward baseline
        error_rate = clamp(error_rate * 0.95 + 0.01 * 0.05, 0, 1)

        row = {
            "ts": now_iso(),
            "service": "orders-api",
            "metrics": {
                "cpu_pct": round(cpu, 2),
                "memory_pct": round(mem, 2),
                "latency_p95_ms": round(latency_p95, 2),
                "error_rate": round(error_rate, 4),
                "db_wait_time_ms": round(db_wait, 2),
                "queue_depth": round(queue_depth, 2),
            }
        }
        with open(OUT_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")

        time.sleep(1)

if __name__ == "__main__":
    main()
