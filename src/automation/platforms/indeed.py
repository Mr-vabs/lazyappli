from ..engine import BaseAutomationEngine
import time
import urllib.parse
from urllib.parse import urlencode
from ...matcher import calculate_match_score

class IndeedAutomation(BaseAutomationEngine):
    """
    Playwright automation tailored for Indeed.co.in.
    """
    def __init__(self, headless: bool = False, apply_limit: int = 50):
        super().__init__(headless=headless, apply_limit=apply_limit)

    def login(self, email: str, password: str) -> bool:
        """Logs into Indeed."""
        try:
            self.page.goto("https://in.indeed.com/")
            self.random_delay(2, 5)

            # Check if we are already logged in
            if self.page.locator("a[href*='/account']").count() > 0:
                print("Already logged in.")
                return True

            sign_in_link = self.page.locator("a:has-text('Sign in')")
            if sign_in_link.count() > 0:
                sign_in_link.first.click()
                self.random_delay(2, 4)

                self.human_type("input#ifl-InputFormField-3", email)
                self.random_delay(1, 2)
                self.page.locator("button[type='submit']").click()

                # Wait for password field to appear
                self.page.wait_for_selector("input[type='password']", timeout=10000)
                self.human_type("input[type='password']", password)
                self.random_delay(1, 3)

                self.page.locator("button[type='submit']").click()
                self.page.wait_for_load_state('networkidle', timeout=30000)

                self.random_delay(3, 6)

                if "account" in self.page.url or self.page.url == "https://in.indeed.com/":
                    print("Successfully logged into Indeed.")
                    return True
                else:
                    print("Login failed, still on login page.")
                    return False
            else:
                print("Sign in link not found.")
                return False

        except Exception as e:
            print(f"Error during login: {e}")
            return False

    def search_jobs(self, role: str, location: str, ctc: str):
        """
        Navigates to the search page.
        """
        try:
            # Construct Indeed URL
            base_url = "https://in.indeed.com/jobs"
            params = {
                'q': role,
                'l': location,
            }
            # Note: Indeed doesn't easily filter by expected CTC in URL reliably, ignoring it here
            search_url = f"{base_url}?{urllib.parse.urlencode(params)}"

            print(f"Navigating to search URL: {search_url}")
            self.page.goto(search_url)
            self.page.wait_for_load_state('networkidle')
            self.random_delay(2, 4)

            # Ensure we are on a search results page
            return "indeed.com/jobs" in self.page.url
        except Exception as e:
            print(f"Error navigating to search page: {e}")
            return False

    def next_page(self):
        """Navigates to the next page of search results."""
        try:
            # Indeed pagination usually has a button with aria-label containing "Next Page" or "Next"
            next_button = self.page.locator("a[data-testid='pagination-page-next']")
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
        """Handle common simple pop-ups on Indeed."""
        try:
            # Close known modals (e.g., job alert prompts)
            close_selectors = [
                "button[aria-label='close']",
                "button[aria-label='Close']",
                ".popover-x-button-close"
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

    def apply_to_jobs(self, resume_text: str, match_threshold: float, user_profile: dict = None) -> list:
        """
        Iterates through Indeed jobs, extracts JD, scores it,
        and applies using Easily Apply if threshold is met.
        """
        applied_jobs = []
        try:
            # Wait for job list
            self.page.wait_for_selector("div.job_seen_beacon", timeout=10000)
            job_cards = self.page.locator("div.job_seen_beacon")
            count = job_cards.count()
            print(f"Found {count} jobs on this page.")

            for i in range(count):
                if not self.check_rate_limit():
                    break

                self.handle_popups()
                card = job_cards.nth(i)

                try:
                    card.scroll_into_view_if_needed()
                    self.random_delay(0.5, 1.5)

                    title_elem = card.locator("h2.jobTitle span").first
                    job_title = title_elem.inner_text() if title_elem.count() > 0 else "Unknown Title"

                    company_elem = card.locator("span[data-testid='company-name']")
                    company_name = company_elem.inner_text() if company_elem.count() > 0 else "Unknown Company"

                    # Instead of opening new tabs, Indeed loads JDs in a side panel
                    card.click()
                    self.page.wait_for_selector("#jobsearch-ViewjobPaneWrapper", timeout=5000)
                    self.random_delay(1, 2)

                    jd_elem = self.page.locator("#jobDescriptionText")
                    jd_text = jd_elem.inner_text() if jd_elem.count() > 0 else ""

                    score = calculate_match_score(resume_text, jd_text)
                    print(f"[{job_title} at {company_name}] Match Score: {score:.2f}%")

                    if score >= match_threshold:
                        print(f"Score {score:.2f} >= {match_threshold}. Checking for Indeed Apply...")

                        # Look for "Apply now" button (Easily apply)
                        apply_button = self.page.locator("#ia-ApplyButton button")
                        if apply_button.count() > 0 and apply_button.is_visible():
                            # Extract the job URL directly from the card to save in logs
                            job_link_elem = card.locator("a.jcs-JobTitle")
                            job_link = job_link_elem.get_attribute("href")
                            if job_link and not job_link.startswith("http"):
                                job_link = "https://in.indeed.com" + job_link

                            apply_button.click()
                            self.random_delay(2, 4)

                            # Note: To handle Indeed's iframe application we'd need more complex logic.
                            # For MVP Phase, we will attempt to close the modal after "applying".
                            print(f"Attempted to apply to {job_title}")
                            self.increment_applications()
                            applied_jobs.append({
                                "Company Name": company_name,
                                "Role": job_title,
                                "Link to JD": job_link or "N/A"
                            })

                            # Attempt to exit modal if we can't complete it
                            exit_btn = self.page.locator("button[aria-label='Close']")
                            if exit_btn.count() > 0 and exit_btn.is_visible():
                                exit_btn.click()
                                self.random_delay(1, 2)
                                confirm_exit = self.page.locator("button:has-text('Exit')")
                                if confirm_exit.count() > 0:
                                    confirm_exit.click()
                        else:
                            print("No Easy Apply button found. Skipping.")
                    else:
                        print(f"Skipping {job_title} due to low score.")

                    self.random_delay(1, 3)

                except Exception as e_card:
                    print(f"Error processing a job card: {e_card}")
                    continue

        except Exception as e:
            print(f"Error scanning jobs on page: {e}")

        return applied_jobs
