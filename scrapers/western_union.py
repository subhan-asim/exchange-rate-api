from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

pairs = [
    ('usd', 'pkr'),     
    ('usd', 'chf'), ]
def scrape(pair):
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(f"https://www.westernunion.com/us/en/currency-converter/{pair[0]}-to-{pair[1]}-rate.html")
        time.sleep(10)  # Wait for JS content

        rate_elem = driver.find_element(By.CSS_SELECTOR, "span.fx-to").text.split(" ")[0]  # adjust selector
        fee_elem = driver.find_element(By.CSS_SELECTOR, "span.fee").text.split(" ")[0]  # adjust selector
        
        rate = float(rate_elem.strip())
        fee = float(fee_elem.strip())

        return {
            "provider": "WesternUnion",
            "from_currency": f"{pair[0].upper()}",
            "to_currency": f"{pair[1].upper()}",
            "rate": rate,
            "fee": fee,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print("Error scraping Western Union:", e)
        return None
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