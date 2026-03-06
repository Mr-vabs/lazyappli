import typer
import os
from dotenv import load_dotenv

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.parser import parse_resume
from src.matcher import calculate_match_score

app = typer.Typer(help="OpenApply-India - Automating FOSS Lazy Apply.")

@app.command()
def apply(
    resume: str = typer.Option(..., "--resume", "-r", help="Path to your PDF resume."),
    role: str = typer.Option(..., "--role", "-t", help="Target role (e.g., 'Software Engineer')."),
    location: str = typer.Option("India", "--location", "-l", help="Preferred location."),
    ctc: str = typer.Option(..., "--ctc", "-c", help="Expected CTC (e.g., '10-15 LPA')."),
    match_threshold: float = typer.Option(70.0, "--threshold", "-m", help="Match threshold (0-100) to apply."),
    headless: bool = typer.Option(False, "--headless", help="Run in headless mode.")
):
    """
    Main entry point for automating the application process.
    """
    load_dotenv()

    naukri_email = os.getenv("NAUKRI_EMAIL")
    naukri_password = os.getenv("NAUKRI_PASSWORD")

    if not naukri_email or not naukri_password:
        typer.secho("Error: NAUKRI_EMAIL and NAUKRI_PASSWORD must be set in the .env file.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    typer.secho(f"Parsing resume: {resume}", fg=typer.colors.CYAN)

    try:
        resume_text = parse_resume(resume)
        typer.secho(f"Parsed {len(resume_text)} characters from resume.", fg=typer.colors.GREEN)
    except Exception as e:
        typer.secho(f"Failed to parse resume: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    typer.secho(f"Target Role: {role}", fg=typer.colors.YELLOW)
    typer.secho(f"Location: {location}", fg=typer.colors.YELLOW)
    typer.secho(f"Expected CTC: {ctc}", fg=typer.colors.YELLOW)
    typer.secho(f"Match Threshold: {match_threshold}%", fg=typer.colors.YELLOW)
    typer.secho(f"Headless Mode: {headless}", fg=typer.colors.YELLOW)

    from src.automation.platforms.naukri import NaukriAutomation
    from src.reporting import Reporter

    reporter = Reporter()
    engine = NaukriAutomation(headless=headless, apply_limit=50)

    try:
        engine.start()
        if not engine.login(naukri_email, naukri_password):
            typer.secho("Failed to login to Naukri. Exiting.", fg=typer.colors.RED)
            raise typer.Exit(code=1)

        typer.secho("Successfully logged in. Searching for jobs...", fg=typer.colors.GREEN)
        if not engine.search_jobs(role, location, ctc):
            typer.secho("Failed to navigate to search results. Exiting.", fg=typer.colors.RED)
            raise typer.Exit(code=1)

        pages_to_scan = 5 # Set a limit for pages
        for page_num in range(pages_to_scan):
            typer.secho(f"Scanning page {page_num + 1}...", fg=typer.colors.CYAN)

            applied_jobs = engine.apply_to_jobs(resume_text, match_threshold)
            for job in applied_jobs:
                reporter.log_application(job["Company Name"], job["Role"], job["Link to JD"])

            if not engine.check_rate_limit():
                break

            if not engine.next_page():
                typer.secho("No more pages found or failed to navigate. Finishing up.", fg=typer.colors.YELLOW)
                break

    except Exception as e:
        typer.secho(f"An error occurred during automation: {e}", fg=typer.colors.RED)
    finally:
        engine.stop()
        typer.secho(f"Automation finished. Made {engine.applications_made} applications.", fg=typer.colors.GREEN)


if __name__ == "__main__":
    app()
