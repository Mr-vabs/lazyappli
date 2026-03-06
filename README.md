# OpenApply-India

OpenApply-India is a Free and Open Source (FOSS) Python-based automation tool that streamlines the job application process on major Indian job boards (currently supporting Naukri.com and Indeed.co.in). The tool intelligently matches your resume to job descriptions and automates the "Easy Apply" process for relevant roles.

## Features

*   **Web Interface (Streamlit):** Accessible via desktop or mobile devices (Android/iOS) over your local network. Allows you to build your profile, upload your resume, and track live application logs.
*   **User Input Module:** Accepts your PDF resume and input fields for Target Role, Preferred Locations, Expected CTC, Experience, and a Match Score threshold.
*   **Smart Filtering:** Uses a local, lightweight TF-IDF matching algorithm (`scikit-learn`) to calculate a "Match Score" between your resume text and the Job Description (JD). It only applies if the score exceeds your defined threshold.
*   **Platform Integration & Automation Engine:**
    *   Automated login and session management for Naukri and Indeed.
    *   Navigates search results and handles pagination.
    *   Implements stealth techniques like human-like typing delays and random mouse movements to avoid bot detection.
    *   Handles common pop-ups to ensure a smooth "Easy Apply" experience.
    *   Attempts to answer common application questions automatically based on your created profile.
*   **Rate Limiting & Reporting:** Caps applications at 50 per session to protect your account and generates an `applications_log.csv` tracking your applied jobs.

## Prerequisites

*   Python 3.10 or higher.
*   A Naukri.com account.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/openapply-india.git
    cd openapply-india
    ```

2.  **Create a virtual environment (Optional but recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Install Playwright browsers:**
    ```bash
    playwright install chromium
    ```

## Configuration

The tool requires your login credentials to apply on your behalf. **Never hardcode these.**

1.  Copy the example environment file:
    ```bash
    cp .env.example .env
    ```

2.  Open the `.env` file and add your credentials:
    ```env
    NAUKRI_EMAIL="your.email@example.com"
    NAUKRI_PASSWORD="your_secure_password"
    INDEED_EMAIL="your.email@example.com"
    INDEED_PASSWORD="your_secure_password"
    ```
    *Note: If `INDEED_*` variables are missing, the tool will attempt to use your Naukri credentials for Indeed.*

## Usage (Web UI)

OpenApply-India now uses a Streamlit Web UI.

1.  **Start the server:**
    ```bash
    streamlit run app.py
    ```

2.  **Access on Desktop:**
    Open your browser and navigate to `http://localhost:8501`.

3.  **Access on Android/Mobile Device:**
    *   Ensure your computer and mobile device are connected to the same Wi-Fi network.
    *   When you run `streamlit run app.py`, the terminal will display a **Network URL** (e.g., `http://192.168.1.5:8501`).
    *   Open your Android phone's browser (Chrome/Safari) and go to that Network URL.
    *   You can now configure your profile, upload your resume from your phone, and trigger the bot running on your computer!

## Output

After execution, the tool will update (or create) an `applications_log.csv` file in your root directory containing:
*   Company Name
*   Role
*   Date Applied
*   Link to the Job Description

## Safety & Ethics
*   Always test with `--headless=False` (default behavior) first to monitor the bot's behavior.
*   The default rate limit is set to 50 applications per session to avoid account bans.
*   Do not share your `.env` file with anyone.
