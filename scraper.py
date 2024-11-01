from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pickle
import os


class TemuScraper:
    def __init__(self):
        self.options = Options()

        # Set specific iPhone details
        mobile_emulation = {
            "deviceMetrics": {
                "width": 390,
                "height": 844,
                "pixelRatio": 3.0,
                "touch": True,
                "mobile": True
            },
            "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/122.0.6261.89 Mobile/15E148 Safari/604.1"
        }

        # Enhanced anti-detection measures
        self.options.add_argument(
            '--disable-blink-features=AutomationControlled')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--disable-notifications')
        self.options.add_argument('--disable-web-security')
        self.options.add_argument('--disable-site-isolation-trials')
        self.options.add_argument(
            '--disable-features=IsolateOrigins,site-per-process')
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('--ignore-ssl-errors')
        self.options.add_argument('--allow-running-insecure-content')

        # Add language and geolocation for Denmark
        self.options.add_argument('--lang=da-DK,da')
        self.options.add_argument('--accept-lang=da-DK')

        # Additional experimental options
        self.options.add_experimental_option(
            'mobileEmulation', mobile_emulation)
        self.options.add_experimental_option(
            'excludeSwitches', ['enable-automation', 'enable-logging'])
        self.options.add_experimental_option('useAutomationExtension', False)

        # Initialize driver
        self.driver = webdriver.Chrome(options=self.options)

        # Execute CDP commands for enhanced mobile emulation
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                Object.defineProperty(navigator, 'languages', {get: () => ['da-DK', 'da', 'en-US', 'en']});
                window.chrome = { runtime: {} };
                Object.defineProperty(navigator, 'platform', {get: () => 'iPhone'});
                Object.defineProperty(navigator, 'maxTouchPoints', {get: () => 5});
            '''
        })

        # Set geolocation to Denmark
        self.driver.execute_cdp_cmd('Emulation.setGeolocationOverride', {
            'latitude': 55.676098,  # Copenhagen coordinates
            'longitude': 12.568337,
            'accuracy': 100
        })

        # Enable touch events
        self.driver.execute_cdp_cmd('Emulation.setTouchEmulationEnabled', {
            'enabled': True,
            'maxTouchPoints': 5
        })

        # Set timezone to Denmark
        self.driver.execute_cdp_cmd('Emulation.setTimezoneOverride', {
            'timezoneId': 'Europe/Copenhagen'
        })

        # Set proper mobile user agent with modern Chrome version
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            'userAgent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/122.0.6261.89 Mobile/15E148 Safari/604.1',
            'platform': 'iPhone',
            'mobile': True,
            'acceptLanguage': 'da-DK'
        })

    def handle_popups(self):
        """Handle any initial popups (lottery, etc)"""
        try:
            # Wait for and close lottery popup if it appears
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, '_1vzn_3SE'))
            ).click()
            print("✅ Closed initial popup")
        except:
            print("No popup found or already closed")

    def handle_verification(self):
        """Handle the slider verification"""
        try:
            # Wait for verification iframe
            iframe = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'iframe[title="Verification challenge"]'))
            )

            # Get iframe dimensions and position
            iframe_location = iframe.location
            iframe_size = iframe.size

            # Scroll to make sure the iframe is in the middle of the viewport
            scroll_y = iframe_location['y'] - \
                (self.driver.execute_script("return window.innerHeight") / 2)
            self.driver.execute_script(f"window.scrollTo(0, {scroll_y});")

            # Switch to iframe
            self.driver.switch_to.frame(iframe)

            print("\n⭐ Slider verification detected!")
            print("Please:")
            print("1. Slide the button to complete the puzzle")
            print("2. Wait for the green checkmark")
            input("3. Press Enter once verification is complete...\n")

            # Switch back to main content
            self.driver.switch_to.default_content()

            # Add a small delay after verification
            time.sleep(2)
            return True

        except Exception as e:
            print("No verification needed or already completed")
            return False

    def save_cookies(self):
        """Save cookies after manual login"""
        print("🔐 Please login manually to TEMU...")
        self.driver.get("https://www.temu.com/dk")

        # Wait for manual login
        input("\nPress Enter after you have logged in...\n")

        # Save cookies
        cookies = self.driver.get_cookies()
        with open('temu_cookies.pkl', 'wb') as f:
            pickle.dump(cookies, f)
        print("✅ Cookies saved successfully!")

    def load_cookies(self):
        """Load saved cookies"""
        try:
            with open('temu_cookies.pkl', 'rb') as f:
                cookies = pickle.load(f)

            # Visit the site first
            self.driver.get("https://www.temu.com/dk")

            # Add the cookies
            for cookie in cookies:
                self.driver.add_cookie(cookie)

            print("✅ Cookies loaded successfully!")
            return True
        except Exception as e:
            print(f"❌ Error loading cookies: {e}")
            return False

    def scrape_page(self):
        """Main scraping function"""
        try:
            print("🌐 Loading TEMU with saved cookies...")

            # Try to load cookies
            if self.load_cookies():
                # Refresh page with cookies
                self.driver.get("https://www.temu.com/dk")

                # Handle popups
                # self.handle_popups()

                # Handle verification if needed
                # self.handle_verification()

                print("\n1. Navigate to desired page if needed")
                input("2. Press Enter when ready to scrape...\n")

                try:
                    # Look for elements with class text-2XEN6
                    elements = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_all_elements_located(
                            (By.CLASS_NAME, 'text-2XEN6'))
                    )

                    print(f"\n📱 Found {len(elements)} text elements:")
                    for i, element in enumerate(elements, 1):
                        try:
                            text = element.text.strip()
                            if text:  # Only print non-empty texts
                                print(f"{i}. {text}")
                        except:
                            continue

                except Exception as e:
                    print(f"❌ Error: {e}")
                    self.driver.save_screenshot("error.png")

            else:
                print("❌ Failed to load cookies. Please run save_cookies() first.")

        except Exception as e:
            print(f"❌ Error during scraping: {e}")

        finally:
            input("\nPress Enter to close the browser...")
            self.driver.quit()


if __name__ == "__main__":
    scraper = TemuScraper()

    # Check if cookie file exists
    if not os.path.exists('temu_cookies.pkl'):
        print("No saved cookies found. Starting cookie saving process...")
        scraper.save_cookies()
        scraper.driver.quit()
        print("\nPlease run the script again to use saved cookies.")
    else:
        scraper.scrape_page()
