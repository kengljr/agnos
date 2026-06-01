# app/main.py
from fastapi import FastAPI
from datetime import datetime
import psycopg2
import os

app = FastAPI()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "dbname": os.getenv("DB_NAME", "mydb"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
}

def get_db_status():
    try:
        conn = psycopg2.connect(**DB_CONFIG, connect_timeout=3)
        conn.close()
        return "connected"
    except Exception:
        return "disconnected"

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "database": get_db_status(),
    }