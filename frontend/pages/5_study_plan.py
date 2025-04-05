import os
import json
import hashlib
import random
import datetime
import streamlit as st

# --- Configuration Constants ---
# Inline learning material (used instead of reading from "context.txt")
context_data = """
Getting Started with Git
-------------------------
This chapter covers the basics of Git. You will learn about version control, installing Git, and getting started with managing your source code.

About Version Control
---------------------
Version control records changes to files over time, allowing you to recall specific versions later. It is essential for collaboration and recovering previous states.

Local and Centralized VCS
-------------------------
Local VCS methods (like copying files) can be error prone, while centralized systems (like CVS or Subversion) manage changes on a single server, which can be a single point of failure.

Distributed Version Control Systems
-------------------------------------
Distributed systems such as Git give each user a full copy of the repository, increasing reliability and flexibility.

A Short History of Git
----------------------
Git was created by Linus Torvalds in 2005 for the Linux kernel project. It is fast, efficient, and offers robust branching capabilities.

Git Fundamentals
----------------
- Snapshots, Not Differences: Git stores snapshots of your files.
- Local Operations: Most operations occur locally, ensuring speed.
- Data Integrity: Git uses SHA-1 hashing to verify data.
- Three States: Files can be Modified, Staged, or Committed.

Basic Git Workflow
------------------
1. Modify files in your working directory.
2. Stage the changes you want to include.
3. Commit the staged changes to record a snapshot.
"""

STUDY_PLAN_DIR = "/home/study_plans"  # Directory for study plan files

# Ensure the study plan directory exists.
os.makedirs(STUDY_PLAN_DIR, exist_ok=True)

# --- Utility Functions ---

def read_context(dummy_path: str) -> str:
    """
    Returns the inline learning material.
    """
    return context_data.strip()

def compute_hash(data: list) -> str:
    """
    Compute an MD5 hash of the provided data (JSON dumped with sorted keys).
    """
    json_str = json.dumps(data, sort_keys=True)
    return hashlib.md5(json_str.encode('utf-8')).hexdigest()

def save_study_plan(plan: list, directory: str = STUDY_PLAN_DIR) -> str:
    """
    Save the study plan (a list of daily study strings) as JSON to a file
    with a hash-based filename: study_plan_[hash].json.
    Returns the file path.
    """
    json_str = json.dumps(plan, sort_keys=True, indent=2)
    md5_hash = compute_hash(plan)
    filename = f"study_plan_{md5_hash}.json"
    filepath = os.path.join(directory, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(json_str)
    return filepath

# --- Gemini API Stub Functions ---

def generate_study_plan(context: str, total_days: int, daily_time: int) -> list:
    """
    Simulate a Gemini API call that divides the context into smaller portions.
    Each day's plan includes a portion of the material plus a note for rehearsal
    and a mock test.
    
    Args:
        context: The full text material.
        total_days: Total days available.
        daily_time: Daily study time in minutes.
    
    Returns:
        A list of strings with the plan for each day.
    """
    # For demonstration, we split the context into sentences.
    sentences = context.split('.')
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # Determine approximate number of sentences per day.
    portion_length = max(1, len(sentences) // total_days)
    plan = []
    
    for day in range(1, total_days + 1):
        start_idx = (day - 1) * portion_length
        end_idx = start_idx + portion_length
        portion = sentences[start_idx:end_idx]
        day_plan = f"Day {day}: Cover " + ", ".join(portion)
        day_plan += " | Rehearsal: Review key concepts | Mock Test: Short quiz"
        plan.append(day_plan)
    
    return plan

def generate_notification_calendar(plan: list) -> list:
    """
    Simulate a Gemini API call to create a notification calendar.
    Each entry contains a date (starting tomorrow), a fixed time (12:00),
    and a notification message based on the day's study plan.
    
    Returns:
        A list of dicts with 'date', 'time', and 'message' keys.
    """
    calendar = []
    today = datetime.date.today()
    for idx, day_plan in enumerate(plan):
        notify_date = today + datetime.timedelta(days=idx + 1)
        entry = {
            "date": notify_date.strftime("%Y-%m-%d"),
            "time": "12:00",
            "message": f"Reminder: {day_plan}"
        }
        calendar.append(entry)
    return calendar

# --- UI Functions ---

def display_study_plan_ui(plan: list):
    """
    Display the study plan with a bullet point list.
    Each day has a checkbox to mark it as completed.
    Also, show a gamified progress bar.
    """
    st.markdown("## Your Study Plan")
    
    completed_days = 0
    total_days = len(plan)
    
    for idx, day_plan in enumerate(plan):
        key = f"day_{idx+1}"
        if key not in st.session_state:
            st.session_state[key] = False
        if st.checkbox(day_plan, key=key):
            completed_days += 1

    # Display gamified progress bar
    progress = completed_days / total_days if total_days > 0 else 0
    st.progress(progress)
    st.markdown(f"**Progress:** {completed_days}/{total_days} days completed!")
    
    if completed_days == total_days:
        st.success("Great job! You've completed your study plan!")

def display_notification_calendar(calendar: list):
    """
    Display the notification calendar as a bullet list.
    In a real app, you might integrate a scheduler library to send notifications.
    """
    st.markdown("## Notification Calendar")
    for entry in calendar:
        st.markdown(f"- **{entry['date']} at {entry['time']}**: {entry['message']}")

# --- Main Pipeline ---

def run_study_plan_pipeline():
    """
    Main pipeline:
      1. Get user input (total days and daily study time).
      2. Retrieve the learning material from the inline string.
      3. Generate the study plan via a Gemini API stub.
      4. Save the study plan (with a hash-based filename).
      5. Display the plan with checkboxes and a progress bar.
      6. Generate and display a notification calendar.
    """
    st.markdown("### Enter your study details")
    
    total_days = st.number_input("How many days do you have to learn the material?", 
                                 min_value=1, max_value=365, value=7, step=1)
    daily_time = st.number_input("How many minutes per day would you like to study?", 
                                 min_value=1, max_value=1440, value=60, step=5)
    
    if st.button("Generate Study Plan"):
        # Retrieve the inline context.
        context = read_context("dummy_path_not_used")
        
        # Generate study plan.
        study_plan = generate_study_plan(context, total_days, daily_time)
        # Save plan to a file.
        saved_file = save_study_plan(study_plan)
        st.info(f"Study plan generated and saved to: {saved_file}")
        
        # Store the plan in session_state for persistence.
        st.session_state["study_plan"] = study_plan
        
        # Display the study plan UI.
        display_study_plan_ui(study_plan)
        
        # Generate notification calendar.
        notification_calendar = generate_notification_calendar(study_plan)
        display_notification_calendar(notification_calendar)

# --- Main Application ---

st.set_page_config(page_title="Study Plan Generator", page_icon="🎓", layout="wide")
st.title("Dynamic Study Plan Application - Metoda tancerki")
st.markdown(
    """
    This gamified app helps you plan your study sessions by breaking your learning material 
    (stored inline) into daily portions with rehearsals and mock tests.
    """
)

# If a study plan is already generated, display it; otherwise, prompt for a new one.
if "study_plan" in st.session_state:
    st.markdown("## Your Current Study Plan")
    display_study_plan_ui(st.session_state["study_plan"])
else:
    run_study_plan_pipeline()

st.markdown(
    """
    **Note:** Actual daily notifications at 12:00 would require integration with an external scheduler 
    (e.g., APScheduler, cron jobs, or a push notification service). This example simulates the notification calendar.
    """
)
