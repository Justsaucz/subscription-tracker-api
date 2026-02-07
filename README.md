# 📊 SubTrack API (Subscription Tracker)

A RESTful API built with **Python** and **Flask** to help users track recurring expenses, manage subscriptions, and calculate monthly spending. This project demonstrates modular software architecture using Flask Blueprints and SQLAlchemy.

## 🚀 Features

* **CRUD Operations:** Create, Read, Update, and Delete subscriptions.
* **Smart Categorization:** Automatically creates new categories if they don't exist when adding a subscription.
* **Filtering:** Filter subscriptions by category (e.g., `GET /subscriptions?category=Gaming`).
* **Data Validation:** Enforces strict Enum types for Frequencies and Statuses to ensure data integrity.
* **Modular Design:** Code is split into Blueprints (`routes/`, `models.py`) for scalability.

---

## 📂 Project Structure

```text
/subscription-tracker
│
├── run.py                 # Entry Point (Run this to start server)
├── seed.py                # Database Seeder (Run this to reset data)
├── test_app.py            # Unit Test Suite
├── config.py              # Configuration settings
├── requirements.txt       # Dependencies
├── .gitignore             # Git ignore rules
│
├── instance/              # Local Data Folder (Ignored by Git)
│   └── subscriptions.db   # SQLite Database File
│
└── app/                   # Main Application Package
    ├── __init__.py        # App Factory & Initialization
    ├── models.py          # Database Models & Enums
    └── routes/            # API Route Blueprints
        ├── __init__.py
        ├── category_routes.py
        └── subscription_routes.py


