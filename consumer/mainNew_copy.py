import json
import psycopg2
from quixstreams import Application


# ---------- Postgres setup ----------
def get_pg_connection():
    """
    Create and return a PostgreSQL connection.
    Adjust dbname, user, password, host, port as needed.
    """
    conn = psycopg2.connect(
        dbname="postgres_trial",   # e.g. "postgres" or your custom DB
        user="postgres_trial",        # e.g. "datha"
        password="postgres",         # or "" if using trust/peer auth
        host="localhost",
        port=5432,
    )
    conn.autocommit = True
    return conn


def ensure_table_exists(conn):
    """
    Create the table if it does not exist.
    NOTE: If the table already exists with the old columns only,
    you will need to ALTER TABLE manually to add the new columns.
    """
    create_table_sql = """
        CREATE TABLE IF NOT EXISTS project_events (
            event_id              UUID PRIMARY KEY,
            ts                    TIMESTAMPTZ NOT NULL,
            project_id            TEXT NOT NULL,
            task_id               TEXT NOT NULL,
            status                TEXT NOT NULL,
            increment_hours       INTEGER NOT NULL,
            increment_cost        NUMERIC(10, 2) NOT NULL,

            -- NEW FIELDS
            planned_hours         NUMERIC(10, 2),
            actual_hours          NUMERIC(10, 2),
            percent_complete      NUMERIC(5, 2),
            planned_cost_per_hour NUMERIC(10, 2),
            actual_cost           NUMERIC(12, 2),

            ev                    NUMERIC(14, 2),
            pv                    NUMERIC(14, 2),
            spi                   NUMERIC(8, 4),
            cpi                   NUMERIC(8, 4),
            sv                    NUMERIC(14, 2),
            cv                    NUMERIC(14, 2),
            etc                   NUMERIC(14, 2),
            eac                   NUMERIC(14, 2),

            on_track_flag         BOOLEAN
        );
    """
    with conn.cursor() as cur:
        cur.execute(create_table_sql)


def save_event_to_postgres(conn, event: dict):
    """
    Insert a single event dict into the project_events table.

    Expects keys (from producer JSON):
      eventId, timestamp, projectId, taskId, status,
      incrementHours, incrementCost,
      plannedHours, actualHours, percentComplete,
      plannedCostPerHour, actualCost,
      EV, PV, SPI, CPI, SV, CV, ETC, EAC, OnTrackFlag
    """
    insert_sql = """
        INSERT INTO project_events (
            event_id,
            ts,
            project_id,
            task_id,
            status,
            increment_hours,
            increment_cost,
            planned_hours,
            actual_hours,
            percent_complete,
            planned_cost_per_hour,
            actual_cost,
            ev,
            pv,
            spi,
            cpi,
            sv,
            cv,
            etc,
            eac,
            on_track_flag
        ) VALUES (
            %(eventId)s,
            %(timestamp)s,
            %(projectId)s,
            %(taskId)s,
            %(status)s,
            %(incrementHours)s,
            %(incrementCost)s,
            %(plannedHours)s,
            %(actualHours)s,
            %(percentComplete)s,
            %(plannedCostPerHour)s,
            %(actualCost)s,
            %(EV)s,
            %(PV)s,
            %(SPI)s,
            %(CPI)s,
            %(SV)s,
            %(CV)s,
            %(ETC)s,
            %(EAC)s,
            %(OnTrackFlag)s
        )
        ON CONFLICT (event_id) DO NOTHING;
    """
    with conn.cursor() as cur:
        cur.execute(insert_sql, event)


# ---------- Kafka consumer + Postgres integration ----------
def main():
    # 1. Connect to Postgres and ensure table exists
    pg_conn = get_pg_connection()
    ensure_table_exists(pg_conn)

    # 2. Create the Kafka application / consumer
    app = Application(
        broker_address="localhost:9092",
        loglevel="DEBUG",
        consumer_group="project_event",
        auto_offset_reset="latest",
    )

    with app.get_consumer() as consumer:
        consumer.subscribe(["event_data_demo"])
        print("Consumer started. Listening on topic 'event_data_demo'...")

        while True:
            msg = consumer.poll(1.0)  # 1 second timeout

            if msg is None:
                print("Waiting...")
                continue

            if msg.error() is not None:
                raise Exception(msg.error())

            # Parse key/value
            key = msg.key()
            if key is not None:
                key = key.decode("utf-8")

            value_bytes = msg.value()
            try:
                event = json.loads(value_bytes)
            except json.JSONDecodeError:
                print(f"❌ Failed to decode message value as JSON: {value_bytes}")
                consumer.store_offsets(msg)
                continue

            offset = msg.offset()
            print(f"Received message at offset {offset}: key={key}, value={event}")

            # 3. Save the event into Postgres
            try:
                save_event_to_postgres(pg_conn, event)
                print(f"✅ Saved event {event.get('eventId')} to Postgres")
            except Exception as e:
                print(f"❌ Error saving event to Postgres: {e}")

            # 4. Commit offset
            consumer.store_offsets(msg)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutting down consumer...")