# PennyWise – Personal Finance Tracker

PennyWise is a simple personal finance tracker built with Flask.  
It lets you register an account, log in, add your daily expenses, and view a monthly dashboard with charts.

## Features

- User registration and login
- Add, edit, and delete expenses
- Categorise expenses (for example: Food, Travel, Bills)
- Filter by category and month
- Monthly dashboard with charts using Chart.js
- Uses SQLite with SQLAlchemy ORM

## Tech Stack

- Python 3.10+
- Flask
- SQLAlchemy
- HTML, CSS, Jinja2 templates
- Chart.js for charts
- SQLite for storage

## Project Structure

```text
pennywise/
│
├─ app.py
├─ requirements.txt
├─ instance/
│   └─ pennywise.db           # created at runtime
├─ templates/
│   ├─ base.html
│   ├─ index.html
│   ├─ login.html
│   ├─ register.html
│   ├─ expenses.html
│   └─ dashboard.html
└─ static/
    └─ styles.css


