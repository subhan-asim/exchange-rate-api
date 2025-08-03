from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def scrape():
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://www.westernunion.com/us/en/currency-converter/usd-to-pkr-rate.html")
        time.sleep(10)  # Wait for JS content

        rate_elem = driver.find_element(By.CSS_SELECTOR, "span.fx-to").text.split(" ")[0]  # adjust selector
        fee_elem = driver.find_element(By.CSS_SELECTOR, "span.fee").text.split(" ")[0]  # adjust selector
        
        rate = float(rate_elem.strip())
        fee = float(fee_elem.strip())

        return {
            "provider": "WesternUnion",
            "from_currency": "USD",
            "to_currency": "PKR",
            "rate": rate,
            "fee": fee,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        print("Error scraping Western Union:", e)
        return None
    finally:
        driver.quit()
print(scrape())