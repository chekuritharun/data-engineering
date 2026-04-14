import requests
import psycopg2
import logging
from models import MarketData
from collections import defaultdict
import time
import os

logging.basicConfig(level=logging.INFO)

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

def fetch_data():
    try:
        res = requests.get("http://api:8000/v1/market-data", timeout=5)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        logging.error(f"API error: {e}")
        return []

def process():
    data = fetch_data()
    valid_records = []

    for record in data:
        try:
            validated = MarketData(**record)
            valid_records.append(validated)
        except:
            logging.warning("Invalid record dropped")

    # VWAP Calculation
    vwap = defaultdict(lambda: {"total_price_volume": 0, "total_volume": 0})

    for r in valid_records:
        vwap[r.instrument_id]["total_price_volume"] += r.price * r.volume
        vwap[r.instrument_id]["total_volume"] += r.volume

    vwap_result = {
        k: v["total_price_volume"] / v["total_volume"]
        for k, v in vwap.items()
    }

    conn = get_connection()
    cur = conn.cursor()

    for r in valid_records:
        avg_price = vwap_result[r.instrument_id]

        # Outlier detection
        if abs(r.price - avg_price) / avg_price > 0.15:
            continue

        try:
            cur.execute("""
                INSERT INTO market_data (instrument_id, price, volume, timestamp)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (instrument_id, timestamp) DO NOTHING
            """, (r.instrument_id, r.price, r.volume, r.timestamp))
        except Exception as e:
            logging.error(e)

    conn.commit()
    cur.close()
    conn.close()

    logging.info(f"Processed: {len(valid_records)}")

if __name__ == "__main__":
    while True:
        process()
        time.sleep(10)
