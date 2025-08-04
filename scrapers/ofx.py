import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

pairs = [
    ('usd', 'pkr'),  
    ('eur', 'usd'),  
    ('gbp', 'usd'),   
    ('usd', 'jpy'),   
    ('usd', 'chf'),   
    ('usd', 'cad'),   
    ('aud', 'usd'),   
    ('eur', 'gbp')    
]

def scrape(pair):
    url = f"https://www.ofx.com/en-au/exchange-rates/{pair[0]}-to-{pair[1]}/"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    rate_element = soup.select_one("div.ofx-market-chart__chart-section__controls > p")
    if rate_element:
        try:
            rate_text = rate_element.text.strip()
            rate = float(rate_text.split("=")[1].strip().split()[0])

            return {
                "provider": "Ofx",
                "from_currency": pair[0].upper(),
                "to_currency": pair[1].upper(),
                "rate": rate,
                "fee": 0.0,  # Placeholder
                "timestamp": datetime.now().isoformat()
            }
        except:
            pass

def threading():
    data = []
    with ThreadPoolExecutor(max_workers=len(pairs)) as executor:
        results = [executor.submit(scrape, pair) for pair in pairs]
        for f in as_completed(results):
            result = f.result()
            if result:
                data.append(result)
            else:
                pass
    return data
