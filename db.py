import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os

load_dotenv()  # Load variables from .env

DB_CONFIG = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT')
}
def get_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Auto-create table if it doesn't exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS rates (
            id SERIAL PRIMARY KEY,
            provider VARCHAR(100),
            from_currency VARCHAR(10),
            to_currency VARCHAR(10),
            rate NUMERIC,
            fee NUMERIC,
            timestamp TIMESTAMPTZ
        )
    """)
    conn.commit()
    cur.close()
    return conn

def save_to_db(data):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO rates (provider, from_currency, to_currency, rate, fee, timestamp)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        data['provider'],
        data['from_currency'],
        data['to_currency'],
        data['rate'],
        data['fee'],
        data['timestamp'] if isinstance(data['timestamp'], str) else data['timestamp'].isoformat()
    ))
    conn.commit()
    cur.close()
    conn.close()
