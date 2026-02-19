import os
import sqlite3
from pathlib import Path
from flask import Flask, render_template, request
from fx_database import DB_PATH

app = Flask(__name__)

def get_latest_rates():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # For each currency pick the latest timestamp
    cur.execute(
        """
        SELECT r.currency, r.rate
        FROM fx_rates r
        JOIN (
            SELECT currency, MAX(timestamp_utc) AS max_ts
            FROM fx_rates
            GROUP BY currency
        ) latest
        ON r.currency = latest.currency AND r.timestamp_utc = latest.max_ts
        ORDER BY r.currency
        """
    )
    rows = cur.fetchall()
    conn.close()

    rates = {currency: rate for currency, rate in rows}
    return rates

@app.route("/", methods=["GET", "POST"])
def index():
    rates = get_latest_rates()
    currencies = sorted(rates.keys())

    converted_amount = None
    conversion_info = None
    error = None

    if request.method == "POST":
        try:
            amount = float(request.form.get("amount", "0"))
            from_cur = request.form.get("from_currency")
            to_cur = request.form.get("to_currency")

            if from_cur not in rates or to_cur not in rates:
                error = "Invalid currency selection."
            else:
                # OpenExchangeRates uses USD as base
                rate_from = rates[from_cur]
                rate_to = rates[to_cur]

                # Convert amount to USD then to target
                amount_in_usd = amount / rate_from
                converted_amount = amount_in_usd * rate_to

                conversion_info = {
                    "amount": amount,
                    "from": from_cur,
                    "to": to_cur,
                    "converted": converted_amount,
                }
        except ValueError:
            error = "Please enter a valid numeric amount."

    # Show only a subset of currencies in the table if there are many
    preview_rates = dict(list(rates.items())[:15])

    return render_template(
        "index.html",
        currencies=currencies,
        preview_rates=preview_rates,
        conversion_info=conversion_info,
        error=error,
    )

if __name__ == "__main__":
    # Running directly with python app.py (optional).
    app.run(debug=True)