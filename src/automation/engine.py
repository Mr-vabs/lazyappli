from playwright.sync_api import sync_playwright, Page, Browser
import time
import random

class BaseAutomationEngine:
    """
    Base class for Playwright-based automation with stealth elements.
    """
    def __init__(self, headless: bool = False, apply_limit: int = 50):
        self.headless = headless
        self.apply_limit = apply_limit
        self.applications_made = 0
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def check_rate_limit(self) -> bool:
        """Returns True if limit is not reached, False otherwise."""
        if self.applications_made >= self.apply_limit:
            print(f"Rate limit reached. Made {self.applications_made} applications.")
            return False
        return True

    def increment_applications(self):
        """Increments the counter."""
        self.applications_made += 1

    def start(self):
        self.playwright = sync_playwright().start()
        # Using a typical browser profile to avoid basic detection
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=["--disable-blink-features=AutomationControlled"]
        )
        self.context = self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        self.page = self.context.new_page()

        # Overwrite the webdriver property to avoid bot detection
        self.page.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

    def stop(self):
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def random_delay(self, min_seconds: float = 1.0, max_seconds: float = 4.0):
        """Human-like delay."""
        time.sleep(random.uniform(min_seconds, max_seconds))

    def human_type(self, selector: str, text: str, delay_min: int = 50, delay_max: int = 200):
        """Simulate human typing speed."""
        self.page.wait_for_selector(selector)
        element = self.page.locator(selector)
        element.click()
        self.page.keyboard.press("Control+A")
        self.page.keyboard.press("Backspace")
        for char in text:
            self.page.keyboard.type(char, delay=random.randint(delay_min, delay_max))

    def smooth_scroll(self, scroll_amount: int = 500):
        """Scroll down slightly to trigger lazy-loaded elements."""
        self.page.evaluate(f"window.scrollBy(0, {scroll_amount});")
        self.random_delay(0.5, 1.5)
