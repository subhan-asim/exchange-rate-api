import requests
from bs4 import BeautifulSoup
from datetime import datetime


def scrape():
    url = "https://wise.com/gb/currency-converter/usd-to-pkr-rate"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    # Try to extract the exchange rate
    rate_element = soup.find("span", string=lambda text: text and "1 USD =" in text)
    if rate_element:
        rate_text = rate_element.text.strip()
        rate = float(rate_text.split("=")[1].strip().split()[0])
    else:
        rate = None

    return {
        "provider": "Wise",
        "from_currency": "USD",
        "to_currency": "PKR",
        "rate": rate,
        "fee": 0.5,  # We’ll do fees later
        "timestamp": datetime.now().isoformat()
    }
