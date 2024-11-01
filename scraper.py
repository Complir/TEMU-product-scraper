from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import json
import pandas as pd
import pickle


class TemuScraper:
    def __init__(self):
        self.options = Options()
        # Add anti-detection measures
        self.options.add_argument(
            '--disable-blink-features=AutomationControlled')
        self.options.add_argument('--start-maximized')
        self.options.add_experimental_option(
            "excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        self.driver = webdriver.Chrome(options=self.options)

        # Modify navigator.webdriver flag to prevent detection
        self.driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    def add_random_delay(self, min_delay=1, max_delay=3):
        time.sleep(random.uniform(min_delay, max_delay))

    def scroll_page(self):
        """Smooth scroll to simulate human behavior"""
        last_height = self.driver.execute_script(
            "return document.body.scrollHeight")
        while True:
            # Scroll down in smaller increments
            for i in range(10):
                self.driver.execute_script(
                    f"window.scrollTo(0, {(i+1) * last_height/10});")
                self.add_random_delay(0.1, 0.3)

            new_height = self.driver.execute_script(
                "return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def click_see_more(self):
        try:
            see_more_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, '_2ugbvrpI'))
            )
            see_more_button.click()
            self.add_random_delay()
            return True
        except:
            return False

    def extract_product_data(self):
        products = []
        # Updated selector for product cards
        product_cards = self.driver.find_elements(
            By.CLASS_NAME, '_2KkHWtYf')  # This is TEMU's product card class

        for card in product_cards:
            try:
                product = {
                    # Product title class
                    'title': card.find_element(By.CLASS_NAME, '_3n5ZQDD0').text,
                    # Price class
                    'price': card.find_element(By.CLASS_NAME, '_2fNrPpGV').text,
                    'url': card.find_element(By.TAG_NAME, 'a').get_attribute('href')
                }
                products.append(product)
            except Exception as e:
                continue

        return products

    def scrape_makeup_category(self):
        url = "https://www.temu.com/dk/makeup-o3-26.html"
        self.driver.get(url)

        # Wait for manual verification if needed
        if not self.wait_for_manual_verification():
            print("Failed to handle verification")
            return []

        self.add_random_delay(3, 5)  # Initial longer delay for page load

        products = []

        # Keep clicking "See More" and collecting products
        while True:
            self.scroll_page()
            current_products = self.extract_product_data()
            products.extend(current_products)

            if not self.click_see_more():
                break

        # Save results
        df = pd.DataFrame(products)
        df.to_csv('temu_makeup_products.csv', index=False)

        with open('temu_makeup_products.json', 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)

        self.driver.quit()
        return products

    def start_session_with_cookies(self):
        """Start a new session using saved cookies"""
        self.driver = webdriver.Chrome(options=self.options)

        # First access the site
        self.driver.get("https://www.temu.com/dk")

        # Load saved cookies
        try:
            with open('temu_cookies.pkl', 'rb') as f:
                cookies = pickle.load(f)

            # Add cookies to session
            for cookie in cookies:
                self.driver.add_cookie(cookie)

            # Refresh page with cookies
            self.driver.refresh()
            return True
        except Exception as e:
            print(f"Error loading cookies: {e}")
            return False

    def wait_for_manual_verification(self):
        """Wait for manual verification if needed"""
        while True:
            try:
                # Check for verification elements (adjust selectors as needed)
                verification_element = self.driver.find_element(
                    By.CLASS_NAME, 'verification-class')
                print("Verification detected! Please complete it manually...")
                input("Press Enter once verification is complete...")
                time.sleep(2)

                # Check if verification is still present
                try:
                    verification_element = self.driver.find_element(
                        By.CLASS_NAME, 'verification-class')
                except:
                    print("Verification completed successfully!")
                    return True

            except:
                print("No verification detected, continuing...")
                return True


if __name__ == "__main__":
    scraper = TemuScraper()
    if scraper.start_session_with_cookies():
        scraper.scrape_makeup_category()
    else:
        print("Failed to load cookies. Please run save_cookies() first.")
