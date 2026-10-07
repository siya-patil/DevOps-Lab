import os
import random
import time

from prometheus_client import Gauge, Summary, start_http_server


total_deliveries = Gauge("total_deliveries", "Total number of deliveries")
pending_deliveries = Gauge("pending_deliveries", "Number of pending deliveries")
on_the_way_deliveries = Gauge(
    "on_the_way_deliveries", "Number of deliveries on the way"
)
average_delivery_time = Summary(
    "average_delivery_time", "Observed delivery time in seconds"
)


def simulate_delivery(high_load: bool = False) -> None:
    if high_load:
        pending = random.randint(50, 100)
        delivery_time = random.uniform(35, 45)
    else:
        pending = random.randint(2, 8)
        delivery_time = random.uniform(15, 28)

    on_the_way = random.randint(5, 20)
    delivered = random.randint(30, 70)
    total = pending + on_the_way + delivered

    total_deliveries.set(total)
    pending_deliveries.set(pending)
    on_the_way_deliveries.set(on_the_way)
    average_delivery_time.observe(delivery_time)

    print(
        f"[METRIC] total={total} pending={pending} on_the_way={on_the_way} "
        f"delivery_time={delivery_time:.2f}s scenario={'high' if high_load else 'normal'}",
        flush=True,
    )


if __name__ == "__main__":
    high_load = os.getenv("DELIVERY_SCENARIO", "normal").lower() == "high"
    print("[INFO] Starting Prometheus metrics server on 0.0.0.0:8000", flush=True)
    start_http_server(8000, addr="0.0.0.0")
    print(f"[INFO] Simulating delivery scenario: {'high' if high_load else 'normal'}", flush=True)

    while True:
        simulate_delivery(high_load)
        time.sleep(1)