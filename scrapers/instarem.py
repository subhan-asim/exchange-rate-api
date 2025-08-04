from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

pairs = [
    ('usd', 'pkr'),  
    ('eur', 'usd'),  
    ('gbp', 'usd'),   
    ('usd', 'jpy'),   
    ('usd', 'chf'),   
    ('usd', 'cad'),   
    ('aud', 'usd'),   
    ('eur', 'gbp')    ]
def scrape(pair):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=options)
    try:
        url = f"https://www.instarem.com/en/currency-conversion/{pair[0]}-to-{pair[1]}/"
        driver.get(url)
        time.sleep(5)  # Let the JS load

        # Find exchange rate
        rate_elem = driver.find_element(By.CLASS_NAME, "exchange-rate")
        rate_text = rate_elem.text.strip()
        rate = float(rate_text)


        return {
            "provider": "Instarem",
            "from_currency": f"{pair[0].upper()}",
            "to_currency": f"{pair[1].upper()}",
            "rate": rate,
            "fee": 0,
            "timestamp": datetime.now().isoformat()
        }
    except:
        pass
    finally:
        driver.quit()

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
