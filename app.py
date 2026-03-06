import streamlit as st
import os
import tempfile
import threading
from dotenv import load_dotenv

from src.parser import parse_resume
from src.automation.platforms.naukri import NaukriAutomation
from src.reporting import Reporter
from streamlit.runtime.scriptrunner import add_script_run_ctx
import time

st.set_page_config(page_title="OpenApply-India", page_icon="🚀", layout="wide")

st.title("🚀 OpenApply-India")
st.markdown("Automate your job applications on Indian job boards.")

# State management for automation logs
if "logs" not in st.session_state:
    st.session_state.logs = []
if "is_running" not in st.session_state:
    st.session_state.is_running = False

def add_log(message):
    st.session_state.logs.append(message)

# Profile Section
st.header("1. Create Your Profile")
col1, col2 = st.columns(2)

with col1:
    role = st.text_input("Target Role", placeholder="e.g., Software Engineer")
    location = st.text_input("Preferred Location", value="India")
    ctc = st.text_input("Expected CTC", placeholder="e.g., 10-15 LPA")
    experience = st.number_input("Total Years of Experience", min_value=0, max_value=50, value=2)

with col2:
    resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    platform = st.selectbox("Select Job Board", ["Naukri.com", "Indeed.co.in"])
    match_threshold = st.slider("Match Score Threshold (%)", min_value=0, max_value=100, value=70)
    headless = st.checkbox("Run in Background (Headless)", value=True, help="Uncheck to see the browser running on the host machine.")

def run_automation_task(profile_data, resume_path):
    load_dotenv()

    platform = profile_data["platform"]
    if platform == "Naukri.com":
        email = os.getenv("NAUKRI_EMAIL")
        password = os.getenv("NAUKRI_PASSWORD")
        if not email or not password:
            add_log("Error: NAUKRI_EMAIL and NAUKRI_PASSWORD must be set in the .env file.")
            st.session_state.is_running = False
            return

        try:
            resume_text = parse_resume(resume_path)
            add_log(f"Parsed {len(resume_text)} characters from resume.")
        except Exception as e:
            add_log(f"Failed to parse resume: {e}")
            st.session_state.is_running = False
            return

        reporter = Reporter()
        engine = NaukriAutomation(headless=profile_data["headless"], apply_limit=50)

        try:
            add_log("Starting browser...")
            engine.start()

            add_log("Logging into Naukri...")
            if not engine.login(email, password):
                add_log("Failed to login to Naukri. Exiting.")
                return

            add_log(f"Searching for '{profile_data['role']}' in '{profile_data['location']}'...")
            if not engine.search_jobs(profile_data['role'], profile_data['location'], profile_data['ctc']):
                add_log("Failed to navigate to search results. Exiting.")
                return

            pages_to_scan = 2 # Limit for demo purposes
            for page_num in range(pages_to_scan):
                add_log(f"Scanning page {page_num + 1}...")

                # We will update apply_to_jobs to take user_profile dict for question handling
                applied_jobs = engine.apply_to_jobs(resume_text, profile_data['match_threshold'], user_profile=profile_data)

                for job in applied_jobs:
                    reporter.log_application(job["Company Name"], job["Role"], job["Link to JD"])
                    add_log(f"✅ Applied: {job['Role']} at {job['Company Name']}")

                if not engine.check_rate_limit():
                    add_log("Rate limit reached.")
                    break

                if not engine.next_page():
                    add_log("No more pages found or failed to navigate.")
                    break

        except Exception as e:
            add_log(f"An error occurred during automation: {e}")
        finally:
            engine.stop()
            add_log(f"Automation finished. Made {engine.applications_made} applications.")
            st.session_state.is_running = False

    elif platform == "Indeed.co.in":
        add_log("Indeed integration is starting...")
        from src.automation.platforms.indeed import IndeedAutomation

        email = os.getenv("INDEED_EMAIL", os.getenv("NAUKRI_EMAIL"))
        password = os.getenv("INDEED_PASSWORD", os.getenv("NAUKRI_PASSWORD"))

        if not email or not password:
            add_log("Error: INDEED_EMAIL and INDEED_PASSWORD must be set in the .env file.")
            st.session_state.is_running = False
            return

        try:
            resume_text = parse_resume(resume_path)
        except Exception as e:
            add_log(f"Failed to parse resume: {e}")
            st.session_state.is_running = False
            return

        reporter = Reporter()
        engine = IndeedAutomation(headless=profile_data["headless"], apply_limit=50)

        try:
            add_log("Starting browser...")
            engine.start()

            add_log("Logging into Indeed...")
            if not engine.login(email, password):
                add_log("Failed to login to Indeed. Exiting.")
                return

            add_log(f"Searching for '{profile_data['role']}' in '{profile_data['location']}'...")
            if not engine.search_jobs(profile_data['role'], profile_data['location'], profile_data['ctc']):
                add_log("Failed to navigate to search results. Exiting.")
                return

            pages_to_scan = 2 # Limit for demo purposes
            for page_num in range(pages_to_scan):
                add_log(f"Scanning page {page_num + 1}...")

                applied_jobs = engine.apply_to_jobs(resume_text, profile_data['match_threshold'], user_profile=profile_data)

                for job in applied_jobs:
                    reporter.log_application(job["Company Name"], job["Role"], job["Link to JD"])
                    add_log(f"✅ Applied/Attempted: {job['Role']} at {job['Company Name']}")

                if not engine.check_rate_limit():
                    add_log("Rate limit reached.")
                    break

                if not engine.next_page():
                    add_log("No more pages found or failed to navigate.")
                    break

        except Exception as e:
            add_log(f"An error occurred during Indeed automation: {e}")
        finally:
            engine.stop()
            add_log(f"Indeed automation finished. Made {engine.applications_made} applications.")
            st.session_state.is_running = False

st.header("2. Start Automation")
start_btn = st.button("Start Applying", disabled=st.session_state.is_running)

if start_btn:
    if not role or not ctc or not resume_file:
        st.error("Please fill in Role, CTC, and upload a resume.")
    else:
        st.session_state.is_running = True
        st.session_state.logs = ["Automation started..."]

        # Save uploaded file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(resume_file.getbuffer())
            tmp_resume_path = tmp.name

        profile_data = {
            "role": role,
            "location": location,
            "ctc": ctc,
            "experience": str(experience),
            "match_threshold": match_threshold,
            "headless": headless,
            "platform": platform
        }

        # Run in a separate thread so UI doesn't block
        thread = threading.Thread(target=run_automation_task, args=(profile_data, tmp_resume_path))
        add_script_run_ctx(thread)
        thread.start()

st.header("Execution Logs")
log_container = st.empty()

# Render logs
with log_container.container():
    for log in st.session_state.logs:
        st.text(log)

if st.session_state.is_running:
    with st.spinner("Automation is running in the background..."):
        time.sleep(2)
        st.rerun()
