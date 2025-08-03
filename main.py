from flask import Flask, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import logging

from db import get_connection, save_to_db

# Scrapers
from scrapers.wise import scrape as wise_scrape
from scrapers.remitly import scrape as remitly_scrape
from scrapers.western_union import scrape as wu_scrape

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# ─────────────────────────────────────────────
# Scheduled Job: Run all scrapers every 10 min
# ─────────────────────────────────────────────
def run_scrapers():
    for scraper in [wise_scrape, remitly_scrape, wu_scrape]:
        try:
            data = scraper()
            if data:
                save_to_db(data)
                logging.info(f"[✓] Saved data from {data['provider']}")
            else:
                logging.warning(f"[!] No data returned from {scraper.__name__}")
        except Exception as e:
            logging.error(f"[✗] Error in {scraper.__name__}: {e}")

scheduler = BackgroundScheduler()
scheduler.add_job(run_scrapers, 'interval', minutes=10)
scheduler.start()


# ─────────────────────────────
# Routes
# ─────────────────────────────

@app.route("/rates", methods=["GET"])
def get_latest_rates():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT provider, from_currency, to_currency, rate, fee, timestamp
        FROM rates
        ORDER BY timestamp DESC
        LIMIT 10
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify([
        {
            "provider": r[0],
            "from_currency": r[1],
            "to_currency": r[2],
            "rate": float(r[3]),
            "fee": float(r[4]) if r[4] is not None else None,
            "timestamp": r[5].isoformat()
        } for r in rows
    ])


@app.route("/historical", methods=["GET"])
def get_historical_rates():
    provider = request.args.get("provider")
    from_date = request.args.get("from")
    to_date = request.args.get("to")
    limit = request.args.get("limit", default=100, type=int)
    offset = request.args.get("offset", default=0, type=int)

    conn = get_connection()
    cur = conn.cursor()
    query = "SELECT provider, from_currency, to_currency, rate, fee, timestamp FROM rates WHERE 1=1"
    values = []

    if provider:
        query += " AND provider = %s"
        values.append(provider)
    if from_date:
        query += " AND DATE(timestamp) >= %s::date"
        values.append(from_date)
    if to_date:
        query += " AND DATE(timestamp) <= %s::date"
        values.append(to_date)

    query += " ORDER BY timestamp DESC LIMIT %s OFFSET %s"
    values.extend([limit, offset])

    cur.execute(query, values)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify([
        {
            "provider": r[0],
            "from_currency": r[1],
            "to_currency": r[2],
            "rate": float(r[3]),
            "fee": float(r[4]) if r[4] is not None else None,
            "timestamp": r[5].isoformat()
        } for r in rows
    ])


@app.route("/health", methods=["GET"])
def health_check():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.fetchone()
        conn.close()
        status = "connected"
    except Exception as e:
        status = f"error: {e}"

    return jsonify({
        "status": "ok",
        "time": datetime.utcnow().isoformat(),
        "db": status
    })


# ─────────────────────────────
# Start Flask app
# ─────────────────────────────
if __name__ == "__main__":
    app.run(debug=True)
