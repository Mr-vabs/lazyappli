from ..engine import BaseAutomationEngine
import time
import urllib.parse
from urllib.parse import urlencode
from ...matcher import calculate_match_score

class NaukriAutomation(BaseAutomationEngine):
    """
    Playwright automation tailored for Naukri.com.
    """
    def __init__(self, headless: bool = False, apply_limit: int = 50):
        super().__init__(headless=headless, apply_limit=apply_limit)

    def login(self, email: str, password: str) -> bool:
        """Logs into Naukri."""
        try:
            self.page.goto("https://www.naukri.com/nlogin/login")
            self.random_delay(2, 5)

            # Check if we are already logged in (maybe using cookies later)
            if self.page.url == "https://www.naukri.com/":
                print("Already logged in.")
                return True

            self.human_type("input#usernameField", email)
            self.random_delay(1, 2)
            self.human_type("input#passwordField", password)
            self.random_delay(1, 3)

            self.page.locator("button[type='submit']").click()
            self.page.wait_for_load_state('networkidle', timeout=30000)

            # Wait to ensure we bypassed login
            self.random_delay(3, 6)

            if "nlogin" not in self.page.url:
                print("Successfully logged into Naukri.")
                return True
            else:
                print("Login failed, still on login page.")
                return False

        except Exception as e:
            print(f"Error during login: {e}")
            return False

    def search_jobs(self, role: str, location: str, ctc: str):
        """
        Navigates to the search page.
        """
        try:
            # Simple Naukri URL search pattern
            base_url = "https://www.naukri.com"
            query = f"{role} jobs in {location}"
            formatted_query = query.replace(" ", "-").lower()

            # Additional params can be added here
            search_url = f"{base_url}/{formatted_query}"

            print(f"Navigating to search URL: {search_url}")
            self.page.goto(search_url)
            self.page.wait_for_load_state('networkidle')
            self.random_delay(2, 4)

            # Ensure we are on a search results page
            return "naukri.com" in self.page.url
        except Exception as e:
            print(f"Error navigating to search page: {e}")
            return False

    def next_page(self):
        """Navigates to the next page of search results."""
        try:
            # Usually pagination "Next" button has text or a specific class
            next_button = self.page.locator("a.fright.fs14.btn-secondary.br2", has_text="Next")
            if next_button.is_visible():
                next_button.click()
                self.page.wait_for_load_state('networkidle')
                self.random_delay(2, 4)
                return True
            else:
                print("Next page button not found.")
                return False
        except Exception as e:
            print(f"Error moving to next page: {e}")
            return False

    def handle_popups(self):
        """Handle common simple pop-ups."""
        try:
            # Add known selectors for pop-ups to close them
            close_selectors = [
                ".crossIcon", # General close icon
                "button:has-text('Not now')",
                "button:has-text('Close')"
            ]
            for selector in close_selectors:
                elements = self.page.locator(selector)
                if elements.count() > 0:
                    for i in range(elements.count()):
                        if elements.nth(i).is_visible():
                            elements.nth(i).click()
                            self.random_delay(1, 2)
        except Exception as e:
            print(f"Error handling popups: {e}")

    def apply_to_jobs(self, resume_text: str, match_threshold: float) -> list:
        """
        Iterates through jobs on the current page, extracts JD, scores it,
        and applies if it meets the threshold. Uses the class's rate limit.
        Returns a list of applied job details.
        """
        applied_jobs = []
        try:
            self.page.wait_for_selector(".srp-jobtuple-wrapper", timeout=10000)
            job_cards = self.page.locator(".srp-jobtuple-wrapper")
            count = job_cards.count()
            print(f"Found {count} jobs on this page.")

            for i in range(count):
                if not self.check_rate_limit():
                    break

                self.handle_popups()
                card = job_cards.nth(i)

                try:
                    # Scroll to card
                    card.scroll_into_view_if_needed()
                    self.random_delay(0.5, 1.5)

                    title_elem = card.locator("a.title")
                    job_title = title_elem.inner_text()
                    job_link = title_elem.get_attribute("href")

                    company_elem = card.locator("a.comp-name")
                    company_name = company_elem.inner_text() if company_elem.count() > 0 else "Unknown"

                    # Open job in new tab to get full JD
                    with self.context.expect_page() as new_page_info:
                        title_elem.click(modifiers=["Control"]) # Opens in new tab
                    new_page = new_page_info.value
                    new_page.wait_for_load_state('networkidle')

                    jd_text = ""
                    if new_page.locator(".dang-inner-html").count() > 0:
                        jd_text = new_page.locator(".dang-inner-html").inner_text()
                    elif new_page.locator(".job-desc").count() > 0:
                        jd_text = new_page.locator(".job-desc").inner_text()

                    score = calculate_match_score(resume_text, jd_text)
                    print(f"[{job_title} at {company_name}] Match Score: {score:.2f}%")

                    if score >= match_threshold:
                        print(f"Score {score:.2f} >= {match_threshold}. Attempting to apply...")

                        apply_button = new_page.locator("button:has-text('Apply')").first
                        if apply_button.count() > 0 and apply_button.is_visible():
                            apply_button.click()
                            self.random_delay(2, 4)

                            # Check for success or complex popups requiring answers
                            if new_page.locator("text='successfully applied'").count() > 0 or new_page.locator(".apply-message").count() > 0:
                                print(f"Successfully applied to {job_title}")
                                self.increment_applications()
                                applied_jobs.append({
                                    "Company Name": company_name,
                                    "Role": job_title,
                                    "Link to JD": job_link
                                })
                            else:
                                print(f"Could not confirm application for {job_title} (maybe custom questions). Skipping.")
                        else:
                            print("No Easy Apply button found.")
                    else:
                        print(f"Skipping {job_title} due to low score.")

                    new_page.close()
                    self.random_delay(1, 3)

                except Exception as e_card:
                    print(f"Error processing a job card: {e_card}")
                    if 'new_page' in locals() and not new_page.is_closed():
                        new_page.close()
                    continue

        except Exception as e:
            print(f"Error scanning jobs on page: {e}")

        return applied_jobs
