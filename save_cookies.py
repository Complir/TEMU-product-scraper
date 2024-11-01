from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle
import time


def setup_driver():
    options = Options()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--start-maximized')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(options=options)
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver


def accept_cookies_popup(driver):
    """Handle the cookie consent popup"""
    try:
        cookie_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, '_1vzn_3SE'))
        )
        cookie_button.click()
        print("✅ Accepted cookies popup")
        return True
    except Exception as e:
        print(f"❌ Could not find cookie accept button: {e}")
        return False


def save_cookies():
    driver = setup_driver()
    driver.get("https://www.temu.com/dk")

    # Handle cookie popup first
    accept_cookies_popup(driver)

    print("\n1. Complete the puzzle verification if it appears")
    print("2. Log in to your account if needed")
    input("\nPress Enter once you're done...")

    # Save cookies
    cookies = driver.get_cookies()
    with open('temu_cookies.pkl', 'wb') as f:
        pickle.dump(cookies, f)

    driver.quit()
    print("\n✅ Cookies saved successfully to temu_cookies.pkl!")


if __name__ == "__main__":
    save_cookies()
