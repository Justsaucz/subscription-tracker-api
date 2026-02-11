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

```

---

## ⚡ Getting Started

Follow these steps to set up the project locally.

### 1. Clone the Repository

```bash
git clone https://github.com/Justsaucz/subscription-tracker-api
cd subscription-tracker-api

```

### 2. Set up Virtual Environment

It is recommended to use a virtual environment to manage dependencies.

```bash
# Mac/Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate

```

### 3. Install Dependencies

```bash
pip install -r requirements.txt

```

### 4. Initialize the Database

Run the seed script to create the database tables and populate them with sample data (e.g., Netflix, Spotify).

```bash
python seed.py

```

*> Expected Output: "✅ Database seeded!"*

### 5. Run the Server

```bash
python run.py

```


---

## 📡 API Endpoints

### 1. Subscriptions

| Method | Endpoint | Description |
| --- | --- | --- |
| **GET** | `/subscriptions` | Retrieve all subscriptions. |
| **GET** | `/subscriptions?category=Name` | **Filter:** Retrieve subscriptions by category (e.g., `?category=Gaming`). Case-insensitive. |
| **GET** | `/subscriptions/<id>` | Retrieve a single subscription by ID. |
| **POST** | `/subscriptions` | Create a new subscription. |
| **PUT** | `/subscriptions/<id>` | Update an existing subscription. |
| **DELETE** | `/subscriptions/<id>` | Delete a subscription. |

**📝 POST Request Example (Create):**

```json
{
  "name": "Netflix",
  "price": 15.99,
  "frequency": "Monthly",
  "category": "Entertainment",
  "status": "Active"
}

```

**📝 PUT Request Example (Update):**

```json
{
  "price": 19.99,
  "status": "Cancelled"
}

```

### 2. Categories

| Method | Endpoint | Description |
| --- | --- | --- |
| **GET** | `/categories` | List all available categories. |
| **POST** | `/categories` | Manually create a new category. |

---

### 3. Summarize prices (Per month)

| Method | Endpoint | Description |
| --- | --- | --- |
| **Total** | `/analytics` | List total prices that are Active. |


