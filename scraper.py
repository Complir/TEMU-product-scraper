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
        # Oxylabs proxy configuration
        PROXY_HOST = "pr.oxylabs.io"  # Your Oxylabs proxy host
        PROXY_PORT = "7777"  # Your Oxylabs port
        PROXY_USER = "YOUR_USERNAME"  # Your Oxylabs username
        PROXY_PASS = "YOUR_PASSWORD"  # Your Oxylabs password
        
        proxy = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"
        
        # Add proxy to Chrome options
        self.options.add_argument(f'--proxy-server={proxy}')
        
        # Enhanced anti-detection measures
        self.options.add_argument(
            '--disable-blink-features=AutomationControlled')
        self.options.add_argument('--start-maximized')
        self.options.add_argument('--disable-infobars')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--lang=da-DK,da')  # Danish language
        self.options.add_argument(
            f'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')

        # Add window size to mimic real browser
        self.options.add_argument('--window-size=1920,1080')

        # Add more realistic user agent
        self.options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')

        # Disable automation flags
        self.options.add_experimental_option(
            'excludeSwitches', ['enable-automation', 'enable-logging'])
        self.options.add_experimental_option('useAutomationExtension', False)

        # Add additional preferences
        self.options.add_experimental_option('prefs', {
            'profile.default_content_setting_values.notifications': 2,
            'profile.default_content_settings.popups': 0,
            'download.default_directory': "/dev/null",
            'profile.default_content_setting_values.automatic_downloads': 1,
            'credentials_enable_service': False,
            'profile.password_manager_enabled': False,
        })

        self.driver = webdriver.Chrome(options=self.options)

        # Execute CDP commands to mask automation
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            "platform": "Windows",
        })

        # Additional stealth measures
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['da-DK', 'da', 'en-US', 'en']
                });
                window.chrome = {
                    runtime: {}
                };
            '''
        })

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
        print(f"🌐 Opening URL: {url}")
        self.driver.get(url)

        # Handle verification first
        self.wait_for_manual_verification()

        try:
            print("🔍 Looking for text elements...")
            elements = WebDriverWait(self.driver, 20).until(
                EC.presence_of_all_elements_located(
                    (By.CLASS_NAME, 'text-2XEN6'))
            )

            if elements:
                print(f"\n📝 Found {len(elements)} text elements:")
                for i, element in enumerate(elements, 1):
                    try:
                        text = element.text.strip()
                        if text:  # Only print non-empty texts
                            print(f"{i}. {text}")
                        if i % 3 == 0:  # Add small delays every 3 items
                            self.add_random_delay(0.2, 0.5)
                    except Exception as e:
                        continue

                print(f"\nTotal elements found: {len(elements)}")
            else:
                print("❌ No text elements found")

        except Exception as e:
            print(f" Error: {e}")
            self.driver.save_screenshot("error.png")

        finally:
            input("\nPress Enter to close the browser...")
            self.driver.quit()

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
        print("\n🤖 Checking for verification...")
        try:
            # Wait for either the verification iframe or puzzle element
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR,
                    'iframe[title="Verification challenge"], .verify-wrap'
                ))
            )
            print("⚠️ Verification detected! Please:")
            print("1. Complete the puzzle/verification")
            print("2. Wait for the page to load")
            input("3. Press Enter once you see the makeup products...\n")

            # Add delay after verification
            self.add_random_delay(3, 5)
            return True
        except:
            print("✅ No verification needed")
            return True

    def verify_stealth(self):
        """Verify that our anti-detection measures are working"""
        print("\n🕵️ Checking stealth measures...")

        # Test webdriver property
        webdriver_present = self.driver.execute_script(
            'return navigator.webdriver')
        print(f"Webdriver detected: {webdriver_present == True}")

        # Test Chrome property
        chrome_present = self.driver.execute_script(
            'return window.chrome !== undefined')
        print(f"Chrome runtime present: {chrome_present}")

        # Test plugins
        plugins = self.driver.execute_script('return navigator.plugins.length')
        print(f"Number of plugins: {plugins}")

        # Test languages
        languages = self.driver.execute_script('return navigator.languages')
        print(f"Languages: {languages}")


if __name__ == "__main__":
    scraper = TemuScraper()
    scraper.verify_stealth()  # Check our stealth measures

    if scraper.start_session_with_cookies():
        try:
            scraper.scrape_makeup_category()
        except Exception as e:
            print(f"❌ Error during scraping: {e}")
            scraper.driver.save_screenshot("error.png")
    else:
        print("Failed to load cookies. Please run save_cookies() first.")
