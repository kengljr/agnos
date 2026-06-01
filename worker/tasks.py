# worker/tasks.py
from celery import Celery
from celery.schedules import crontab
from celery.utils.log import get_task_logger
import psycopg2
from datetime import date, datetime
import os

BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
BACKEND_URL = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

app = Celery("worker", broker=BROKER_URL, backend=BACKEND_URL)
logger = get_task_logger(__name__)

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "dbname": os.getenv("DB_NAME", "mydb"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
}

# --- Beat Schedule ---
app.conf.beat_schedule = {
    "update-today-timestamp": {
        "task": "tasks.update_today_timestamp",
        "schedule": crontab(minute="*/5"),  # ทุก 5 นาที (ปรับได้)
    }
}
app.conf.timezone = "UTC"

# --- Task ---
@app.task(bind=True, max_retries=3, default_retry_delay=30)
def update_today_timestamp(self):
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        today = date.today()
        now = datetime.utcnow()

        cursor.execute(
            """
            UPDATE records
            SET updated_at = %s
            WHERE DATE(created_at) = %s
            """,
            (now, today),
        )

        affected = cursor.rowcount
        conn.commit()
        logger.info(f"[update_today_timestamp] updated {affected} rows for {today}")
        return {"status": "success", "updated_rows": affected, "date": str(today)}

    except Exception as exc:
        if conn:
            conn.rollback()
        logger.error(f"[update_today_timestamp] failed: {exc}")
        raise self.retry(exc=exc)

    finally:
        if conn:
            conn.close()