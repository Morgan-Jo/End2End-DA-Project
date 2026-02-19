# Real-Time FX Insight Hub: Currency Converter & Trend Dashboard

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)
![Tableau](https://img.shields.io/badge/Tableau-Public-E97627?logo=tableau&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-WebApp-000000?logo=flask&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-Markup-E34F26?logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-Styling-1572B6?logo=css3&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Completed-green)

This project is a full-stack FX analytics showcase. It combines a real-time currency converter, a data pipeline that stores FX rates in SQL, Python-based EDA, and a Tableau dashboard for visualising volatility and trends.


## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Tableau Dashboard](#before-building-the-tableau-dashboard)
- [Setup and Installaion](#setup-and-installaion)
- [Author](#author)
- [LICENSE](#license)
- [Disclaimer](#disclaimer)


## Features

- **Real-time FX data** from the OpenExchangeRates API.
- **SQLite database** for historical storage of FX rates.
- **Exports to CSV and XLSX** for portability and reporting.
- **EDA in Python**:
  - Daily average rates per currency.
  - Daily percentage changes.
  - Rolling 7-day volatility.
- **Flask web app**:
  - Currency converter using latest rates.
  - Table of latest FX rates.
- **Tableau dashboard**:
  - FX volatility.
  - Daily trend lines.
  - Historical pattern views.


## Project structure

```text
real-time-fx-insight-hub/
│
├─ app.py                 # Flask web app (converter UI)
├─ fetch_fx.py            # Fetch FX data and store in DB + CSV/XLSX
├─ eda_fx.py              # EDA + exports for Tableau
├─ fx_database.py         # Database helpers (SQLite)
├─ README.md              # You are here
├─ requirements.txt
├─ LICENSE
│
├─ data/
│   ├─ fx_rates.db        # SQLite DB
│   ├─ fx_rates_full.csv  # All historical rows
│   ├─ fx_rates_full.xlsx
│   ├─ fx_rates_daily.csv # Aggregated daily data for Tableau
│   └─ fx_rates_daily.xlsx
│
├─ tableau/
│   └─ FX Volatility Overview.twb
|
├─ templates/
│   └─ index.html         # Converter UI
│
└─ static/
    └─ styles.css         # Basic styling
``` 


## Before building the Tableau dashboard

To get accurate trend analysis and usable volatility metrics, you need enough historical data.
Follow these steps:
  1. Run fetch_fx.py daily (or multiple times across several days) to collect exchange rate snapshots into the SQLite database.
      - Aim for at least 7 days of data so rolling volatility and percentage changes populate correctly.
  2. After you have a week (or more) of the data, run: python eda_fx.py


## Setup and Installaion

1. Clone the Repository the Whole 

Open your terminal or VS Code and run:

```bash
git https://github.com/Morgan-Jo/End2End-DA-Project.git
cd End2End-DA-Proejct/Finance-Banking/real-time-fx-insight-hub
```
### ***OR***

> **Mono-repo note:** This project lives inside the `finance&banking/` section of the
> [End2End-DA-Project](https://github.com/Morgan-Jo/End2End-DA-Project) repository at the path:
> ```
> End2End-DA-Project/
> └── Finance & Banking/
>     └── real-time-fx-insight-hub/   ← this project
> ```
> You do **not** need to clone the entire repository. Pick any of the three methods below.

 ---
### Get just this project (choose one method)

#### Option A — Sparse Checkout *(recommended — keeps full git history)*

```bash
# 1. Create a local folder and initialise git
mkdir 
cd 
git init

# 2. Add the remote
git remote add origin https://github.com/Morgan-Jo/End2End-DA-Project.git

# 3. Enable sparse checkout
git sparse-checkout init --cone

# 4. Point to the exact subfolder inside the repo
git sparse-checkout set Finance-Banking/real-time-fx-insight-hub

# 5. Pull only that folder — nothing else downloads
git pull origin main

# 6. Move into the project folder
cd Finance-Banking/real-time-fx-insight-hub
```

#### Option B — degit *(fastest — no git history, just the files)*

```bash
npx degit github:/End2End-DA-Project/Finance-Banking/real-time-fx-insight-hub
```

#### Option C — DownGit *(browser download, no terminal needed)*


1. Go to [https://minhaskamal.github.io/DownGit](https://minhaskamal.github.io/DownGit)
2. Paste this URL:
   ```
   https://github.com/Morgan-Jo/End2End-DA-Project/tree/main/Finance%20%26%Banking/real-time-fx-insight-hub
   ```
3. Click **Download** — you'll get a ZIP of just this project
 ---


2. Create and activate a virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Add your API key

```bash
Create a .env file in the project root:

OPENEXCHANGERATES_APP_ID=your_api_key_here
BASE_CURRENCY=USD
```

## Author

Morgan J. Tonner 


## LICENSE

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.


## Disclaimer

This End-to-End Data Analysis project is used for portfolio, leanring and experience.

The dataset open soucre generated form ***OpenExchangeRates API***.
