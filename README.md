# Mindful Tracker 🌱

Welcome to **Mindful Tracker**! This is your personal companion for building better habits, achieving your goals, and practicing daily gratitude.

## What is this?

Mindful Tracker is a simple, intuitive web application designed to help you stay consistent and positive. Whether you're trying to drink more water, read every day, or just want a place to reflect on your day, this tool is for you.

## Key Features ✨

*   **📊 Personal Dashboard:** Get a clear overview of your progress with visual charts and stats.
*   **✅ Habit Tracking:** Create and track daily habits. See your streaks and consistency over time.
*   **🎯 Goal Setting:** Set meaningful goals with deadlines and track your journey towards completing them.
*   **📝 Daily Journal:** A dedicated space to log your sleep and write down what you're grateful for each day.
*   **🚀 Onboarding:** A smooth start to help you set up your profile and initial preferences.

## How to Run Locally 🏃‍♂️

1.  **Clone the repository** to your local machine.
2.  **Set up the environment:**
    It's recommended to use a virtual environment.
    ```bash
    python3 -m venv env
    source env/bin/activate  # On Windows use `env\Scripts\activate`
    ```
3.  **Install Dependencies:**
    Make sure you have Django and other necessary packages installed.
    ```bash
    pip install django psycopg2-binary
    ```
4.  **Run Migrations:**
    Set up your database.
    ```bash
    cd core
    python manage.py migrate
    ```
5.  **Start the Server:**
    ```bash
    python manage.py runserver
    ```
6.  **Open in Browser:**
    Go to `http://127.0.0.1:8000/` and start your mindful journey!

## Tech Stack 🛠

*   **Backend:** Django (Python)
*   **Database:** SQLite / PostgreSQL
*   **Frontend:** HTML, CSS, JavaScript

---

*Stay mindful, stay consistent.* 🧘‍♀️

Created by **Anmol Rajput**