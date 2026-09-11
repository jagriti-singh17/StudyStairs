# StudyTrack

A calm, clean study planner for students — built as a beginner-friendly Streamlit hackathon prototype.

## 1. What is StudyTrack?

StudyTrack is a simple digital study space. It helps a student see, in one place:

- What subjects they're studying
- What tasks they need to finish
- How many days are left until their exam
- How much progress they've made
- What's coming up next in their agenda

## 2. Problem statement

Students juggle multiple subjects, assignments, tests and deadlines at once. It's easy to lose
track of what needs attention and when. StudyTrack solves this by combining **planning, task
tracking, academic scheduling, and progress visualization** into one simple, uncluttered workspace.

StudyTrack doesn't tell students how to study — it just puts everything they need to remember
in one place.

## 3. Features

- **Homepage** — introduces StudyTrack and its purpose.
- **Input / Setup page** — collects name, subjects, exam date, study hours, and the subject to
  improve. Subjects are added as chips; typing a subject and pressing **Enter** adds it right
  away (a secondary "+ Add" button also works).
- **Dashboard** — shows a countdown to the exam, overall progress, tasks left, study time, a
  task list ("What's next?"), and simple progress rows (tasks by subject, completed vs
  remaining) built with plain Streamlit/CSS — no charting library involved.
- **Scheduler** — an agenda-style list (not a full calendar) with a date rail and stacked task
  cards for exams, tests, quizzes, assignments, projects and revision sessions.
- **Local persistence** — all data is saved to `data.json` so refreshing the app doesn't lose
  your information.

StudyTrack intentionally does **not** include AI features, smart analytics, gamification,
streaks, badges, or a rotating multi-color task system — it stays focused on planning and
tracking.

## 4. Technologies used

- Python (functions, basic data structures, file handling)
- Streamlit (all pages, interactivity, and progress bars)
- JSON (local data persistence)
- `datetime` (countdowns and date handling)
- A small amount of custom HTML/CSS (via `st.markdown(..., unsafe_allow_html=True)`) for cards,
  chips, and progress bars

No database, backend framework, JavaScript framework, or charting library (e.g. Matplotlib) is
used. Progress is shown with plain Streamlit/CSS bars instead.

## 5. Project structure

```
StudyTrack/
│
├── app.py             # the entire application (all pages + helper functions)
├── data.json           # created automatically the first time you save data
├── requirements.txt
└── README.md
```

## 6. How to install dependencies

Make sure you have Python 3.9+ installed, then run:

```bash
pip install -r requirements.txt
```

## 7. How to run the application

From inside the `StudyTrack` folder, run:

```bash
streamlit run app.py
```

Streamlit will open the app in your browser (usually at `http://localhost:8501`).

## 8. How data persistence works

- All of the student's information (name, subjects, tasks, exam date, study hours, and
  scheduler events) is kept in `st.session_state` while the app is running.
- Every time something changes (a task is added, completed, or deleted; a scheduler event is
  added or updated), the app calls `save_data()`, which writes everything to `data.json`.
- When the app starts, `load_data()` reads `data.json` back in, so your information is still
  there after a refresh or restart.
- If `data.json` doesn't exist yet (first run), the app just starts with empty/default data.

## 9. How the Scheduler works

- Every scheduler item has a task name, a type (Exam, Test, Quiz, Assignment, Project,
  Revision, Study Task, or Other), and a date. Subject and time are optional.
- Items are grouped by date and displayed with a narrow "date rail" on the left (weekday +
  date) and stacked task cards on the right — similar to a simple agenda/list view.
- You can mark an item complete (✓), undo that (↺), or delete it (🗑️). Completed cards turn a
  quiet light-grey color instead of disappearing.
- Card colors are intentionally limited to three fixed, readable colors: light blue for normal
  items, light lavender for today's items, and light grey for completed items — there's no
  random or rotating color system.

## 10. How the dashboard works

- The greeting and exam countdown are calculated live using `get_days_remaining()`, based on
  the exam date you entered in the setup page.
- The three summary cards (Overall progress, Tasks left, Study time) are calculated from your
  current task list using `calculate_progress()`.
- The "What's next?" list lets you add a task (with a subject), check it off, or delete it.
  Completed tasks can be cleared in bulk with "Clear completed tasks".
- The progress rows update automatically whenever your task list changes:
  - **Tasks by subject** — for each subject, a percentage and a simple CSS bar showing how many
    of that subject's tasks are complete.
  - **Completion score** — a percentage and bar comparing completed vs remaining tasks overall.

## 11. How to modify the application

Everything lives in `app.py`, organized into five clearly commented sections:

1. Setup & constants (colors, options, file paths)
2. Data helper functions (`load_data`, `save_data`, `calculate_progress`, `get_days_remaining`,
   `add_task`, `add_schedule_item`, etc.)
3. Custom CSS (`inject_css`) — change colors, spacing, or fonts here
4. Page renderers (`render_homepage`, `render_input_page`, `render_dashboard`,
   `render_scheduler`) — change what each page shows here
5. Main app logic (`main`) — decides which page to display

To add a new field or page, start by adding it to `default_data()`, then build a new
`render_...()` function, and add it to the `if/elif` chain in `main()`.

## 12. How to deploy it later

StudyTrack is a plain Streamlit app, so it can be deployed for free on
[Streamlit Community Cloud](https://streamlit.io/cloud):

1. Push this folder to a GitHub repository.
2. Sign in to Streamlit Community Cloud with GitHub.
3. Point it at your repository and select `app.py` as the entry file.
4. Deploy — Streamlit Cloud will install `requirements.txt` automatically.

Note: on most free hosting platforms the local filesystem isn't permanent between deploys, so
`data.json` may reset when the app redeploys. For a hackathon demo this is not a problem, but
for long-term use you'd eventually want a small database instead.
