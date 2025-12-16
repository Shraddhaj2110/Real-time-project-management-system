import logging
import json
import random
import time
import uuid
import datetime as dt

from quixstreams import Application

projects = ["P001", "P002", "P003"]
tasks = [f"T{i:03}" for i in range(1, 11)]


def generate_event():
    status = random.choice(["Not Started", "In Progress", "Completed", "Delayed"])

    # ---- PLANNING SIDE ----
    planned_hours = random.randint(40, 200)  # total planned hours for the task
    planned_cost_per_hour = round(random.uniform(50, 150), 2)

    # BAC (Budget at Completion) = total planned cost
    bac = planned_hours * planned_cost_per_hour

    # Where are we in the schedule timeline? (0 = start, 1 = end)
    schedule_fraction = random.uniform(0.0, 1.0)

    # Planned % complete as per schedule (for PV)
    if status == "Completed":
        planned_fraction_complete = 1.0
    else:
        planned_fraction_complete = schedule_fraction

    # ---- ACTUAL PROGRESS / % COMPLETE ----
    if status == "Not Started":
        percent_complete = 0.0
    elif status == "Completed":
        percent_complete = 1.0
    elif status == "Delayed":
        # behind schedule: actual % is lower than planned %
        percent_complete = max(
            planned_fraction_complete * random.uniform(0.2, 0.8),
            0.0,
        )
    else:  # "In Progress"
        # can be slightly ahead or behind
        percent_complete = planned_fraction_complete * random.uniform(0.7, 1.2)

    # keep in [0, 1]
    percent_complete = max(0.0, min(1.0, percent_complete))

    # ---- HOURS & COSTS ----
    # expected hours based on % complete
    expected_hours = planned_hours * percent_complete

    # actual hours: some noise around expected
    actual_hours = max(expected_hours * random.uniform(0.8, 1.3), 0.1)

    # actual cost = actual hours * planned rate * some cost overrun/underrun factor
    cost_factor = random.uniform(0.8, 1.3)
    actual_cost = actual_hours * planned_cost_per_hour * cost_factor

    # ---- EVM METRICS ----
    # EV = % complete * BAC
    EV = percent_complete * bac

    # PV = planned % complete (based on schedule) * BAC
    PV = planned_fraction_complete * bac

    # SPI = EV / PV
    SPI = EV / PV if PV > 0 else 0.0

    # CPI = EV / AC
    CPI = EV / actual_cost if actual_cost > 0 else 0.0

    # SV = EV - PV
    SV = EV - PV

    # CV = EV - AC
    CV = EV - actual_cost

    # ETC = (BAC - EV) / CPI   (if CPI == 0, fall back to remaining planned cost)
    if CPI > 0:
        ETC = (bac - EV) / CPI
    else:
        ETC = bac - EV

    # EAC = AC + ETC
    EAC = actual_cost + ETC

    # Simple on-track rule: schedule and cost performance >= 1
    OnTrackFlag = SPI >= 1.0 and CPI >= 1.0

    # ---- INCREMENTAL FIELDS YOU ALREADY HAD ----
    increment_hours = random.randint(1, 5)
    increment_cost = round(random.uniform(100, 500), 2)

    event = {
        "eventId": str(uuid.uuid4()),
        "timestamp": dt.datetime.utcnow().isoformat() + "Z",
        "projectId": random.choice(projects),
        "taskId": random.choice(tasks),
        "status": status,
        "incrementHours": increment_hours,
        "incrementCost": increment_cost,

        # NEW FIELDS
        "plannedHours": planned_hours,
        "actualHours": round(actual_hours, 2),
        "percentComplete": round(percent_complete, 2),
        "plannedCostPerHour": planned_cost_per_hour,
        "actualCost": round(actual_cost, 2),

        "EV": round(EV, 2),
        "PV": round(PV, 2),
        "SPI": round(SPI, 2),
        "CPI": round(CPI, 2),
        "SV": round(SV, 2),
        "CV": round(CV, 2),
        "ETC": round(ETC, 2),
        "EAC": round(EAC, 2),

        "OnTrackFlag": OnTrackFlag,
    }

    return event


def main():
    app = Application(
        broker_address="localhost:9092",
        loglevel="DEBUG",
    )

    print("Starting producer application", app)

    with app.get_producer() as producer:
        while True:
            event = generate_event()

            logging.debug("Generated event: %s", event)
            producer.produce(
                topic="event_data_demo",
                key="project_event",
                value=json.dumps(event).encode("utf-8"),
            )
            logging.info("Produced. Sleeping...")
            time.sleep(3)


if __name__ == "__main__":
    logging.basicConfig(level="DEBUG")
    main()