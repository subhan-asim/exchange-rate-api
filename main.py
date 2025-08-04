from flask import Flask, request, jsonify, Response
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from functools import wraps
import os

from db import get_connection, save_to_db

# Scrapers
from scrapers.wise import threading as wise_scrape
from scrapers.remitly import threading as remitly_scrape
from scrapers.ofx import threading as ofx_scrape
from scrapers.western_union import threading as wu_scrape
from scrapers.instarem import threading as instarem_scrape
from scrapers.transfer_go import threading as tg_scrape

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# ─────────────────────────────────────────────
# Scheduled Job: Run all scrapers every 10 min
# ─────────────────────────────────────────────
def run_scrapers():
    scrapers = [tg_scrape, wu_scrape, ofx_scrape, remitly_scrape, instarem_scrape, wise_scrape]
    results = []
    with ThreadPoolExecutor(max_workers=len(scrapers)) as executor:
        future_to_scraper = {executor.submit(scraper): scraper.__name__ for scraper in scrapers}

        for future in as_completed(future_to_scraper):
            name = future_to_scraper[future]
            try:
                data = future.result()
                if data:
                    save_to_db(data)
                    logging.info(f"[✓] Saved data from {data['provider']}")
                else:
                    logging.warning(f"[!] No data returned from {name}")
            except Exception as e:
                logging.error(f"[✗] Error in {name}: {e}")



scheduler = BackgroundScheduler()
scheduler.add_job(run_scrapers, 'interval', minutes=10)
scheduler.start()


# ─────────────────────────────
# Authentication decorator
# ─────────────────────────────
def check_auth(username, password):
    return username == os.getenv("ADMIN_USERNAME") and password == os.getenv("ADMIN_PASSWORD")

def authenticate():
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials.', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


# ─────────────────────────────
# Routes
# ─────────────────────────────

@app.route("/rates", methods=["GET"])
def get_latest_rates():
    from_currency = request.args.get("from")
    to_currency = request.args.get("to")
    limit = request.args.get("limit", default=10, type=int)
    offset = request.args.get("offset", default=0, type=int)

    conn = get_connection()
    cur = conn.cursor()
    query = """
        SELECT provider, from_currency, to_currency, rate, fee, timestamp
        FROM rates
        WHERE 1=1
    """
    values = []

    if from_currency:
        query += " AND from_currency = %s"
        values.append(from_currency.upper())

    if to_currency:
        query += " AND to_currency = %s"
        values.append(to_currency.upper())

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
# /admin/scrape endpoint
# ─────────────────────────────
@app.route("/admin/scrape", methods=["POST"])
@requires_auth
def admin_scrape():
    try:
        run_scrapers()
        return jsonify({"status": "ok", "message": "Scrapers executed manually."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# ─────────────────────────────
# Start Flask app
# ─────────────────────────────
if __name__ == "__main__":
    app.run(debug=True)
