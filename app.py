"""
StudyTrack - a simple student study planner built with Streamlit.

This file is organized into a few sections:
1. Setup & constants
2. Data helper functions (load/save/calculate)
3. Small styling (custom CSS)
4. Page renderers (homepage, input page, dashboard, scheduler)
5. Main app logic (decides which page to show)
"""

import json
import os
from datetime import datetime, date

import streamlit as st

# ----------------------------------------------------------------------
# 1. SETUP & CONSTANTS
# ----------------------------------------------------------------------

DATA_FILE = "data.json"

STUDY_HOUR_OPTIONS = ["1 hour", "2 hours", "3 hours", "4 hours", "5+ hours"]
TASK_TYPES = ["Exam", "Test", "Quiz", "Assignment", "Project", "Revision", "Study Task", "Other"]

# A small, fixed color system for task cards (no random / rotating colors).
COLOR_NORMAL = "#EAF1FF"       # very light blue
COLOR_HIGHLIGHT = "#F1EBFF"    # very light lavender (used for today's items)
COLOR_COMPLETED = "#F0F1F3"    # very light grey (completed items)

st.set_page_config(page_title="StudyTrack", page_icon="✨", layout="wide")


# ----------------------------------------------------------------------
# 2. DATA HELPER FUNCTIONS
# ----------------------------------------------------------------------

def default_data():
    """Return an empty StudyTrack data structure."""
    return {
        "name": "",
        "subjects": [],
        "exam_date": "",
        "study_hours": "",
        "improve_subject": "",
        "setup_complete": False,
        "tasks": [],       # dashboard "What's next" tasks
        "schedule": [],    # scheduler agenda items
        "next_task_id": 1,
        "next_event_id": 1,
    }


def load_data():
    """Load StudyTrack data from the local JSON file, or start fresh."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return default_data()
    return default_data()


def save_data():
    """Save the current session data to the local JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(st.session_state.data, f, indent=2)


def calculate_progress(tasks):
    """Return the percentage of completed tasks (0-100)."""
    if not tasks:
        return 0
    completed = sum(1 for t in tasks if t["completed"])
    return round((completed / len(tasks)) * 100)


def get_days_remaining(target_date_str):
    """Return the number of whole days remaining until target_date_str (YYYY-MM-DD)."""
    if not target_date_str:
        return None
    try:
        target = datetime.strptime(target_date_str, "%Y-%m-%d").date()
    except ValueError:
        return None
    delta = (target - date.today()).days
    return delta


def days_remaining_label(days):
    """Turn a day count into a friendly countdown label."""
    if days is None:
        return "No date set"
    if days < 0:
        return "Completed"
    if days == 0:
        return "Today"
    if days == 1:
        return "1 day to go"
    return f"{days} days to go"


def add_task(name, subject):
    task = {
        "id": st.session_state.data["next_task_id"],
        "name": name,
        "subject": subject,
        "completed": False,
    }
    st.session_state.data["tasks"].append(task)
    st.session_state.data["next_task_id"] += 1
    save_data()


def toggle_task(task_id):
    for t in st.session_state.data["tasks"]:
        if t["id"] == task_id:
            t["completed"] = not t["completed"]
    save_data()


def delete_task(task_id):
    st.session_state.data["tasks"] = [
        t for t in st.session_state.data["tasks"] if t["id"] != task_id
    ]
    save_data()


def clear_completed_tasks():
    st.session_state.data["tasks"] = [
        t for t in st.session_state.data["tasks"] if not t["completed"]
    ]
    save_data()


def add_schedule_item(name, task_type, subject, event_date, event_time, completed=False):
    item = {
        "id": st.session_state.data["next_event_id"],
        "name": name,
        "type": task_type,
        "subject": subject,
        "date": event_date,
        "time": event_time,
        "completed": completed,
    }
    st.session_state.data["schedule"].append(item)
    st.session_state.data["next_event_id"] += 1
    save_data()


def toggle_schedule_item(item_id):
    for item in st.session_state.data["schedule"]:
        if item["id"] == item_id:
            item["completed"] = not item["completed"]
    save_data()


def delete_schedule_item(item_id):
    st.session_state.data["schedule"] = [
        i for i in st.session_state.data["schedule"] if i["id"] != item_id
    ]
    save_data()


def go_to(page_name):
    st.session_state.page = page_name


def subject_progress(tasks, subjects):
    """
    Return a list of (subject, percent_complete, total_count) for each subject,
    based on the student's task list. Used for the simple progress rows on the
    dashboard (no charting library needed).
    """
    rows = []
    for subject in subjects:
        subject_tasks = [t for t in tasks if t["subject"] == subject]
        if subject_tasks:
            percent = calculate_progress(subject_tasks)
        else:
            percent = 0
        rows.append((subject, percent, len(subject_tasks)))
    return rows


def render_bar_html(percent, color="linear-gradient(90deg,#6C5CE7,#4E7CFF)", height="8px"):
    """Return a small HTML progress bar. Kept simple - no charting library needed."""
    return (
        f'<div style="background-color:#EDEFF5; border-radius:8px; height:{height}; '
        f'margin:0.3rem 0;">'
        f'<div style="background:{color}; width:{percent}%; height:{height}; '
        f'border-radius:8px;"></div></div>'
    )


# ----------------------------------------------------------------------
# 3. STYLING
# ----------------------------------------------------------------------

def inject_css():
    st.markdown(
        """
        <style>
        /* ----- overall page ----- */
        .stApp {
            background-color: #F7F8FC;
        }
        .block-container {
            padding-top: 2rem;
            max-width: 1200px;
        }

        /* ----- typography ----- */
        h1, h2, h3 {
            color: #16213E;
        }
        p, li, span, label {
            color: #33374D;
        }
        .st-heading-eyebrow {
            color: #6C5CE7;
            font-weight: 600;
            letter-spacing: 1.5px;
            font-size: 0.8rem;
            text-transform: uppercase;
        }
        .st-support-text {
            color: #6B7280;
            font-size: 0.95rem;
        }

        /* ----- text inputs & text areas ----- */
        .stTextInput input, .stTextArea textarea, .stNumberInput input {
            background-color: #F1F3F5 !important;
            color: #23273A !important;
            border: 1px solid #DCE0E6 !important;
            border-radius: 10px !important;
            font-weight: 400 !important;
            padding: 0.55rem 0.8rem !important;
        }
        .stTextInput input:focus, .stTextArea textarea:focus {
            border: 1px solid #7C6CF0 !important;
            box-shadow: 0 0 0 2px rgba(124,108,240,0.15) !important;
        }

        /* ----- selectbox / dropdown ----- */
        .stSelectbox div[data-baseweb="select"] > div {
            background-color: #F1F3F5 !important;
            color: #23273A !important;
            border: 1px solid #DCE0E6 !important;
            border-radius: 10px !important;
            font-weight: 400 !important;
        }
        div[data-baseweb="popover"] li {
            background-color: #FBFBFD !important;
            color: #23273A !important;
        }

        /* ----- date input ----- */
        .stDateInput input {
            background-color: #F1F3F5 !important;
            color: #23273A !important;
            border-radius: 10px !important;
            border: 1px solid #DCE0E6 !important;
        }

        /* ----- buttons ----- */
        .stButton button {
            background: linear-gradient(90deg, #6C5CE7, #4E7CFF);
            color: #FFFFFF !important;
            border: none;
            border-radius: 10px;
            padding: 0.55rem 1.3rem;
            font-weight: 600;
            transition: opacity 0.15s ease-in-out;
        }
        .stButton button:hover {
            opacity: 0.88;
        }

        /* ----- checkboxes ----- */
        .stCheckbox label {
            color: #23273A;
        }

        /* ----- generic card ----- */
        .st-card {
            background-color: #FFFFFF;
            border-radius: 16px;
            padding: 1.3rem 1.5rem;
            box-shadow: 0 4px 18px rgba(23, 29, 60, 0.06);
            margin-bottom: 1rem;
        }
        .st-card-title {
            font-size: 1rem;
            font-weight: 700;
            color: #16213E;
            margin-bottom: 0.4rem;
        }
        .st-metric-value {
            font-size: 1.9rem;
            font-weight: 800;
            color: #16213E;
        }
        .st-metric-label {
            color: #6B7280;
            font-size: 0.85rem;
        }

        /* ----- task card variants ----- */
        .task-card {
            border-radius: 12px;
            padding: 0.8rem 1rem;
            margin-bottom: 0.6rem;
        }
        .task-card-normal { background-color: #EAF1FF; }
        .task-card-highlight { background-color: #F1EBFF; }
        .task-card-completed { background-color: #F0F1F3; }
        .task-title {
            font-weight: 700;
            color: #16213E;
            font-size: 0.98rem;
        }
        .task-meta {
            color: #6B7280;
            font-size: 0.82rem;
        }
        .date-rail-day {
            font-weight: 700;
            color: #16213E;
            font-size: 0.85rem;
        }
        .date-rail-date {
            color: #6B7280;
            font-size: 0.8rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ----------------------------------------------------------------------
# 4. PAGE RENDERERS
# ----------------------------------------------------------------------

def render_homepage():
    # ---- header ----
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("### ✨ StudyTrack")
    with col2:
        if st.button("Open dashboard →"):
            go_to("dashboard")

    st.write("")

    # ---- hero ----
    left, right = st.columns([3, 2])
    with left:
        st.markdown('<div class="st-heading-eyebrow">YOUR PERSONAL STUDY SPACE</div>', unsafe_allow_html=True)
        st.markdown(
            "<h1 style='font-size:2.6rem; margin-top:0.3rem;'>Plan smarter.<br>"
            "<span style='color:#6C5CE7;'>Study better.</span></h1>",
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p class="st-support-text">Turn your syllabus into small, focused wins — '
            "then see your progress grow every day.</p>",
            unsafe_allow_html=True,
        )
        if st.button("Create my study plan →"):
            go_to("input")

    with right:
        data = st.session_state.data
        progress = calculate_progress(data["tasks"])
        total = len(data["tasks"])
        done = sum(1 for t in data["tasks"] if t["completed"])
        st.markdown(
            f"""
            <div class="st-card">
                <div class="st-card-title">Today's focus</div>
                <div class="st-support-text">{done} of {total if total else 5} tasks complete</div>
                <div style="background-color:#EDEFF5; border-radius:8px; height:10px; margin:0.6rem 0;">
                    <div style="background: linear-gradient(90deg,#6C5CE7,#4E7CFF); width:{progress}%;
                                height:10px; border-radius:8px;"></div>
                </div>
                <div class="st-metric-label">{progress}% complete</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    st.write("")

    # ---- feature strip ----
    f1, f2, f3, f4 = st.columns(4)
    features = [
        ("📚", "Organize subjects"),
        ("✅", "Finish tasks"),
        ("📈", "Watch progress"),
        ("🗓️", "Build a study plan"),
    ]
    for col, (icon, text) in zip([f1, f2, f3, f4], features):
        with col:
            st.markdown(
                f'<div class="st-card" style="text-align:center;">'
                f'<div style="font-size:1.6rem;">{icon}</div>'
                f'<div class="st-support-text">{text}</div></div>',
                unsafe_allow_html=True,
            )


def render_input_page():
    top_left, _ = st.columns([1, 5])
    with top_left:
        if st.button("← StudyTrack"):
            go_to("home")

    st.markdown('<div class="st-heading-eyebrow">STEP 1 OF 1</div>', unsafe_allow_html=True)
    st.markdown(
        "<h2>Let's make your <span style='color:#6C5CE7;'>study space.</span></h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="st-support-text">Tell us a little about your goals. You can update these anytime.</p>',
        unsafe_allow_html=True,
    )

    data = st.session_state.data

    name = st.text_input("Your name", value=data["name"])

    st.markdown("**Subjects**")
    st.caption("Type a subject and press Enter to add it.")

    # Using a form means pressing Enter inside the text input submits it
    # immediately - the student doesn't have to click "+ Add".
    with st.form("add_subject_form", clear_on_submit=True):
        subj_col, btn_col = st.columns([5, 1])
        with subj_col:
            new_subject = st.text_input(
                "Add a subject", label_visibility="collapsed", placeholder="e.g. Mathematics"
            )
        with btn_col:
            add_submitted = st.form_submit_button("+ Add")

        if add_submitted:
            cleaned = new_subject.strip()
            if not cleaned:
                st.warning("Type a subject name before adding it.")
            elif cleaned in data["subjects"]:
                st.warning(f'"{cleaned}" is already in your subject list.')
            else:
                data["subjects"].append(cleaned)
                save_data()
                st.rerun()

    if data["subjects"]:
        chip_html = "".join(
            f'<span style="background-color:#EAF1FF; color:#16213E; padding:0.3rem 0.7rem; '
            f'border-radius:20px; margin-right:0.4rem; font-size:0.85rem; display:inline-block; '
            f'margin-bottom:0.4rem;">{s}</span>'
            for s in data["subjects"]
        )
        st.markdown(chip_html, unsafe_allow_html=True)
        remove_choice = st.selectbox(
            "Remove a subject (optional)", ["-- none --"] + data["subjects"]
        )
        if remove_choice != "-- none --":
            if st.button("Remove selected subject"):
                data["subjects"].remove(remove_choice)
                save_data()
                st.rerun()
    else:
        st.caption("No subjects added yet.")

    existing_date = date.today()
    if data["exam_date"]:
        try:
            existing_date = datetime.strptime(data["exam_date"], "%Y-%m-%d").date()
        except ValueError:
            pass
    exam_date = st.date_input("Exam date", value=existing_date)

    study_hours = st.selectbox(
        "Study hours per day",
        STUDY_HOUR_OPTIONS,
        index=STUDY_HOUR_OPTIONS.index(data["study_hours"]) if data["study_hours"] in STUDY_HOUR_OPTIONS else 0,
    )

    if data["subjects"]:
        improve_subject = st.selectbox(
            "Subject you want to improve",
            data["subjects"],
            index=data["subjects"].index(data["improve_subject"]) if data["improve_subject"] in data["subjects"] else 0,
        )
    else:
        improve_subject = ""
        st.caption("Add at least one subject to choose one to improve.")

    st.write("")
    if st.button("Generate my dashboard →"):
        if not name.strip():
            st.error("Please enter your name.")
        elif not data["subjects"]:
            st.error("Please add at least one subject.")
        else:
            data["name"] = name.strip()
            data["exam_date"] = exam_date.strftime("%Y-%m-%d")
            data["study_hours"] = study_hours
            data["improve_subject"] = improve_subject
            data["setup_complete"] = True
            save_data()
            go_to("dashboard")


def render_dashboard():
    data = st.session_state.data

    top1, top2 = st.columns([4, 2])
    with top1:
        st.markdown("### ✨ StudyTrack")
    with top2:
        st.markdown(
            f"<div style='text-align:right; font-weight:600; color:#16213E;'>{data['name'] or 'Student'}</div>",
            unsafe_allow_html=True,
        )

    st.markdown('<div class="st-heading-eyebrow">YOUR DASHBOARD</div>', unsafe_allow_html=True)
    st.markdown(f"<h2>Good to see you, {data['name'] or 'there'}!</h2>", unsafe_allow_html=True)

    days = get_days_remaining(data["exam_date"])
    st.markdown(
        f'<p class="st-support-text">{days_remaining_label(days)} until your exam.</p>',
        unsafe_allow_html=True,
    )

    # ---- summary cards ----
    progress = calculate_progress(data["tasks"])
    tasks_left = sum(1 for t in data["tasks"] if not t["completed"])

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f"""<div class="st-card">
                <div class="st-metric-label">OVERALL PROGRESS</div>
                <div class="st-metric-value">{progress}%</div>
                <div style="background-color:#EDEFF5; border-radius:8px; height:8px; margin-top:0.4rem;">
                    <div style="background: linear-gradient(90deg,#6C5CE7,#4E7CFF); width:{progress}%;
                                height:8px; border-radius:8px;"></div>
                </div>
            </div>""",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""<div class="st-card">
                <div class="st-metric-label">TASKS LEFT</div>
                <div class="st-metric-value">{tasks_left}</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"""<div class="st-card">
                <div class="st-metric-label">STUDY TIME</div>
                <div class="st-metric-value">{data['study_hours'] or '-'}</div>
            </div>""",
            unsafe_allow_html=True,
        )

    st.write("")
    left, right = st.columns([3, 2])

    # ---- LEFT: task planner ----
    with left:
        st.markdown("#### What's next?")

        with st.form("add_task_form", clear_on_submit=True):
            tcol1, tcol2, tcol3 = st.columns([3, 2, 1])
            with tcol1:
                task_name = st.text_input("Task name", label_visibility="collapsed",
                                           placeholder="e.g. Complete Python loops")
            with tcol2:
                subject_options = data["subjects"] if data["subjects"] else ["General"]
                task_subject = st.selectbox("Subject", subject_options, label_visibility="collapsed")
            with tcol3:
                submitted = st.form_submit_button("+ Add task")
            if submitted:
                if task_name.strip():
                    add_task(task_name.strip(), task_subject)
                else:
                    st.warning("Please enter a task name.")

        if not data["tasks"]:
            st.caption("No tasks yet — you're all caught up!")
        else:
            for task in data["tasks"]:
                card_class = "task-card-completed" if task["completed"] else "task-card-normal"
                col_a, col_b = st.columns([5, 1])
                with col_a:
                    checked = st.checkbox(
                        f"{task['name']}  ·  {task['subject']}",
                        value=task["completed"],
                        key=f"task_{task['id']}",
                    )
                    if checked != task["completed"]:
                        toggle_task(task["id"])
                        st.rerun()
                with col_b:
                    if st.button("🗑️", key=f"del_task_{task['id']}"):
                        delete_task(task["id"])
                        st.rerun()

            if st.button("Clear completed tasks"):
                clear_completed_tasks()
                st.rerun()

        st.write("")
        if st.button("Open Scheduler →"):
            go_to("scheduler")

    # ---- RIGHT: progress (simple Streamlit/CSS visuals, no charting library) ----
    with right:
        st.markdown("#### Your progress")

        st.markdown('<div class="st-card">', unsafe_allow_html=True)
        st.markdown('<div class="st-card-title">Tasks by subject</div>', unsafe_allow_html=True)
        if data["subjects"] and data["tasks"]:
            for subject, percent, count in subject_progress(data["tasks"], data["subjects"]):
                if count == 0:
                    continue
                st.markdown(
                    f'<div style="display:flex; justify-content:space-between;">'
                    f'<span class="task-meta">{subject}</span>'
                    f'<span class="task-meta">{percent}%</span></div>',
                    unsafe_allow_html=True,
                )
                st.markdown(render_bar_html(percent), unsafe_allow_html=True)
        else:
            st.caption("Add your first task to see subject progress.")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="st-card">', unsafe_allow_html=True)
        st.markdown('<div class="st-card-title">Completion score</div>', unsafe_allow_html=True)
        done_count = sum(1 for t in data["tasks"] if t["completed"])
        remaining_count = len(data["tasks"]) - done_count
        if data["tasks"]:
            completed_percent = round((done_count / len(data["tasks"])) * 100)
        else:
            completed_percent = 0
        st.markdown(
            f'<div style="display:flex; justify-content:space-between;">'
            f'<span class="task-meta">Completed ({done_count})</span>'
            f'<span class="task-meta">Remaining ({remaining_count})</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown(render_bar_html(completed_percent, height="14px"), unsafe_allow_html=True)
        if not data["tasks"]:
            st.caption("No tasks yet — you're all caught up!")
        st.markdown("</div>", unsafe_allow_html=True)


def render_scheduler():
    data = st.session_state.data

    top1, top2 = st.columns([4, 2])
    with top1:
        if st.button("← Back to Dashboard"):
            go_to("dashboard")
    with top2:
        st.markdown(
            "<div style='text-align:right; font-weight:700; color:#16213E;'>Scheduler</div>",
            unsafe_allow_html=True,
        )

    st.markdown(f"<h3>{datetime.now().strftime('%B %Y')}</h3>", unsafe_allow_html=True)
    st.markdown(
        '<p class="st-support-text">Your academic agenda — exams, tests, assignments and study sessions.</p>',
        unsafe_allow_html=True,
    )

    with st.expander("+ Add to schedule"):
        with st.form("add_schedule_form", clear_on_submit=True):
            name = st.text_input("Task name", placeholder="e.g. Mathematics Test")
            colA, colB = st.columns(2)
            with colA:
                task_type = st.selectbox("Type", TASK_TYPES)
                subject_options = data["subjects"] if data["subjects"] else ["General"]
                subject = st.selectbox("Subject (optional)", ["-- none --"] + subject_options)
            with colB:
                event_date = st.date_input("Date", value=date.today())
                event_time = st.text_input("Time (optional)", placeholder="e.g. 10:00 AM")
            completed = st.checkbox("Already completed")
            submitted = st.form_submit_button("Add to schedule")
            if submitted:
                if name.strip():
                    add_schedule_item(
                        name.strip(),
                        task_type,
                        "" if subject == "-- none --" else subject,
                        event_date.strftime("%Y-%m-%d"),
                        event_time.strip(),
                        completed,
                    )
                    st.success("Added to your schedule.")
                else:
                    st.warning("Please enter a task name.")

    st.write("")

    if not data["schedule"]:
        st.caption("No scheduler events yet — add your first exam, test or assignment above.")
        return

    # Group schedule items by date, sorted chronologically.
    items_by_date = {}
    for item in data["schedule"]:
        items_by_date.setdefault(item["date"], []).append(item)

    sorted_dates = sorted(items_by_date.keys())
    today_str = date.today().strftime("%Y-%m-%d")

    for date_str in sorted_dates:
        try:
            parsed = datetime.strptime(date_str, "%Y-%m-%d")
            date_label = parsed.strftime("%d %b").upper()
            weekday_label = parsed.strftime("%a").upper()
        except ValueError:
            date_label = date_str
            weekday_label = ""

        rail_col, cards_col = st.columns([1, 5])
        with rail_col:
            st.markdown(
                f'<div class="date-rail-day">{weekday_label}</div>'
                f'<div class="date-rail-date">{date_label}</div>',
                unsafe_allow_html=True,
            )
        with cards_col:
            for item in items_by_date[date_str]:
                if item["completed"]:
                    card_class = "task-card-completed"
                elif date_str == today_str:
                    card_class = "task-card-highlight"
                else:
                    card_class = "task-card-normal"

                meta_parts = [item["type"]]
                if item["subject"]:
                    meta_parts.append(item["subject"])
                if item["time"]:
                    meta_parts.append(item["time"])
                meta_line = " · ".join(meta_parts)

                card_col, action_col1, action_col2 = st.columns([6, 1, 1])
                with card_col:
                    st.markdown(
                        f'<div class="task-card {card_class}">'
                        f'<div class="task-title">{item["name"]}</div>'
                        f'<div class="task-meta">{meta_line}</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                with action_col1:
                    if st.button("✓" if not item["completed"] else "↺", key=f"toggle_{item['id']}"):
                        toggle_schedule_item(item["id"])
                        st.rerun()
                with action_col2:
                    if st.button("🗑️", key=f"del_event_{item['id']}"):
                        delete_schedule_item(item["id"])
                        st.rerun()


# ----------------------------------------------------------------------
# 5. MAIN APP LOGIC
# ----------------------------------------------------------------------

def main():
    if "data" not in st.session_state:
        st.session_state.data = load_data()
    if "page" not in st.session_state:
        st.session_state.page = "home" if not st.session_state.data.get("setup_complete") else "dashboard"

    inject_css()

    page = st.session_state.page
    if page == "home":
        render_homepage()
    elif page == "input":
        render_input_page()
    elif page == "dashboard":
        render_dashboard()
    elif page == "scheduler":
        render_scheduler()
    else:
        render_homepage()


if __name__ == "__main__":
    main()
