from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def scrape():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://www.remitly.com/us/en/currency-converter/usd-to-pkr-rate")
        time.sleep(5)  # Let the JS load

        # Find exchange rate
        rate_elem = driver.find_element(By.XPATH, "/html/body/div[4]/div/div[1]/div/div[2]/div/div[3]/div/div/div[2]")
        rate_text = rate_elem.text.strip().split("=")[1].strip().split(" ")[0]  # "1 USD = 280.50 PKR" → 280.50
        rate = float(rate_text)

        # Find fee
        fee_elem = driver.find_element(By.XPATH, '//*[@id="send-recv-calc-container"]/div[4]/div[1]/div[2]')
        fee_text = fee_elem.text.strip().replace(" USD", "")
        fee = float(fee_text)

        return {
            "provider": "Remitly",
            "from_currency": "USD",
            "to_currency": "PKR",
            "rate": rate,
            "fee": fee,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        print("Error scraping Remitly:", e)
        return None

    finally:
        driver.quit()
    