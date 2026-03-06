# OpenApply-India

OpenApply-India is a Free and Open Source (FOSS) Python-based automation tool that streamlines the job application process on major Indian job boards (currently supporting Naukri.com). The tool intelligently matches your resume to job descriptions and automates the "Easy Apply" process for relevant roles.

## Features

*   **User Input Module:** Accepts your PDF resume and input fields for Target Role, Preferred Locations, Expected CTC, and a Match Score threshold.
*   **Smart Filtering:** Uses a local, lightweight TF-IDF matching algorithm (`scikit-learn`) to calculate a "Match Score" between your resume text and the Job Description (JD). It only applies if the score exceeds your defined threshold.
*   **Platform Integration & Automation Engine:**
    *   Automated login and session management.
    *   Navigates search results and handles pagination.
    *   Implements stealth techniques like human-like typing delays and random mouse movements to avoid bot detection.
    *   Handles common pop-ups to ensure a smooth "Easy Apply" experience.
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

2.  Open the `.env` file and add your Naukri credentials:
    ```env
    NAUKRI_EMAIL="your.email@example.com"
    NAUKRI_PASSWORD="your_secure_password"
    ```

## Usage

You can run the tool from your command line using the `cli.py` entry point.

**Basic Application Run:**

```bash
python src/cli.py --resume path/to/your/resume.pdf --role "Software Engineer" --ctc "15-20 LPA"
```

**Advanced Run (with location, custom threshold, and supervised mode):**

By default, the automation runs in the background. If you want to supervise the first few applications to ensure everything works smoothly, you can disable headless mode using the `--headless` flag (wait, Typer makes it a boolean flag. Omit `--headless` to see the browser, add it to run silently... Actually, based on the Typer setup, you provide `--headless` to run headlessly, otherwise it defaults to showing the browser so you can supervise).

```bash
python src/cli.py \
  --resume my_resume.pdf \
  --role "Data Scientist" \
  --location "Bangalore" \
  --ctc "20 LPA" \
  --threshold 75.0 \
  --headless
```

### CLI Arguments

| Argument | Short | Description | Default |
| :--- | :--- | :--- | :--- |
| `--resume` | `-r` | Path to your PDF resume. | **Required** |
| `--role` | `-t` | Target role (e.g., 'Software Engineer'). | **Required** |
| `--ctc` | `-c` | Expected CTC (e.g., '10-15 LPA'). | **Required** |
| `--location` | `-l` | Preferred location. | `"India"` |
| `--threshold` | `-m` | Match threshold percentage (0-100) to apply. | `70.0` |
| `--headless` | | Run the browser in the background without a UI. | `False` |

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
