from bs4 import BeautifulSoup
from util.rate_limiter import *
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import undetected_chromedriver as uc

# we'll probably need a file per endpoint that we want to provide since each endpoint will take a lot of work
# this scraper should just provide the generic things that are used, such as accessing a webpage, finding what it needs on that webpage, etc
# all the endpoints should then call this scraper for stuff

class HLTVScraper:
    rate_limiter: RateLimitedExecutor
    driver: uc.Chrome
    cookie_text: str = "Allow all cookies" # Pop-up for site cookies
    default_url: str = "https://www.hltv.org"

    # TODO: set a default value for calls_per_second once we figure out decent value
    def __init__(self, max_calls_per_second: int):
        self.rate_limiter = RateLimitedExecutor(max_calls_per_second, 1)

        # Browser options
        options = Options()
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-crash-reporter")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-blink-features=AutomationControlled")  # Reduces automation detection
        options.add_argument("--disable-dev-shm-usage")  # Fixes crash issues in Docker/Linux environments

        # options.add_argument("--headless") # Runs the Chrome browser without popping up. Currently doesn't work since Cloudflare will block it
        # options.add_argument(
        #     "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        # )

        # Browser
        self.driver = uc.Chrome(options=options)
        self.driver.maximize_window()

    def get_website(self, url: str, buttons_to_click: list = []) -> BeautifulSoup:
        """
        This method accesses the input URL and also hits the necessary buttons to access dynamically generated content

        url: The URL to access
        buttons_to_click: The list of buttons to click, specified by their name in the order that we want them to be clicked in

        Output is a BeautifulSoup containing the scraped content
        """
        print(f"Scraping the webpage {url}")

        # Getting the site
        self.rate_limiter.call(self.driver.get, url)

        # Waits for the initial page to fully load
        WebDriverWait(self.driver, 30).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(2) # Additional wait for JS elements to laod

        for button_text in buttons_to_click:
            try:
                # Wait for and click the button by visible text
                button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, f'//button[contains(text(), "{button_text}")]'))
                )
                button.click()
                time.sleep(2) # Wait for the DOM to update after click
            except Exception as e:
                # If button click fails, just print a message saying so
                # print(f"Failed to click button {button_text} due to error {e}")
                print(f"Failed to click button \"{button_text}\"")

        soup = BeautifulSoup(self.driver.page_source, "html.parser")

        # Printing for testing, comment this out when not needed
        with open("page_dump.html", "w", encoding="utf-8") as f:
            f.write(soup.prettify())

        print(f"Successfully scraped webpage {url}")

        return soup
    
    def end_scraping(self):
        # Quitting the driver once everything finishes
        self.driver.quit()
