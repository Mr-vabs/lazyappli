import pandas as pd
import os
from datetime import datetime

class Reporter:
    """
    Handles tracking applications and generating reports.
    """
    def __init__(self, log_file: str = "applications_log.csv"):
        self.log_file = log_file
        self.columns = ["Company Name", "Role", "Date Applied", "Link to JD"]

        if not os.path.exists(self.log_file):
            pd.DataFrame(columns=self.columns).to_csv(self.log_file, index=False)

    def log_application(self, company_name: str, role: str, link: str):
        """
        Logs a single application.
        """
        date_applied = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_row = {
            "Company Name": company_name,
            "Role": role,
            "Date Applied": date_applied,
            "Link to JD": link
        }

        # Append to CSV
        df = pd.DataFrame([new_row])
        df.to_csv(self.log_file, mode='a', header=not os.path.exists(self.log_file), index=False)
        print(f"Logged application for {role} at {company_name}")
