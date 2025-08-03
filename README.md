FX Scraper API

A finance-grade Python application that scrapes exchange rates and transaction fees from Wise, Remitly, and Western Union. Data is stored in PostgreSQL and exposed via a RESTful Flask API. Includes scheduled scraping, historical queries, and a health check.

Features

Real-time scraping from Wise, Remitly, and Western Union

PostgreSQL storage with timestamped records

REST API endpoints: /rates, /historical, /health

Scheduled scraping every 10 minutes using APScheduler

Health check endpoint to verify database and server status


Tech Stack

Python 3.11+

Flask

PostgreSQL

APScheduler

Selenium

python-dotenv


Folder Structure

fx-scraper-api/
├── main.py                  → Flask app and scheduler
├── db.py                    → PostgreSQL connection and data storage
├── scrapers/
│   ├── wise.py
│   ├── remitly.py
│   └── western_union.py
├── requirements.txt
├── .env                     → Environment variables (not committed)
└── README.md

API Endpoints

GET /rates
Returns the 10 most recent exchange rates.

GET /historical?from=2025-08-01&to=2025-08-03&provider=Wise&limit=5&offset=0
Returns historical data based on optional filters:

from (start date)

to (end date)

provider (e.g., Wise, Remitly)

limit (number of records)

offset (pagination)


GET /health
Returns database connection status and current server time.

Setup Instructions

1. Clone the repo
git clone https://github.com/yourusername/fx-scraper-api.git
cd fx-scraper-api


2. Create a virtual environment
python -m venv venv
source venv/bin/activate        (on Windows: venv\Scripts\activate)


3. Install dependencies
pip install -r requirements.txt


4. Create the .env file
Make a .env file in the root folder with these values:



DB_NAME= your db name
DB_USER= your postgres user
DB_PASSWORD= your db password
DB_HOST=localhost
DB_PORT=5432

Edit as needed for your PostgreSQL setup.

5. Set up the database
Make sure PostgreSQL is running and the fx_scraper database exists.
Then run this SQL to create the rates table:



CREATE TABLE rates (
id SERIAL PRIMARY KEY,
provider TEXT,
from_currency TEXT,
to_currency TEXT,
rate NUMERIC,
fee NUMERIC,
timestamp TIMESTAMPTZ
);

6. Run the application
python main.py



The scraper will run every 10 minutes and serve the API at: http://localhost:5000

Roadmap

Interactive dashboard (in progress)

Cloud deployment (Render, Fly.io, EC2) - DONE (https://exchange-rate-api-vrj5.onrender.com/historical)

Docker support (DONE)