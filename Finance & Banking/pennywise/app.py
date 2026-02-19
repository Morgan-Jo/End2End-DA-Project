import os
from datetime import datetime, date

from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request,
    session,
    flash,
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SECRET_KEY"] = "change-this-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///" + os.path.join(BASE_DIR, "instance", "pennywise.db")
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

os.makedirs(os.path.join(BASE_DIR, "instance"), exist_ok=True)

db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    expenses = db.relationship("Expense", backref="user", lazy=True)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    description = db.Column(db.Text)

# Utility functions
def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return User.query.get(user_id)

def login_required(view_func):
    from functools import wraps

    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not current_user():
            flash("Please log in first.")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)

    return wrapper

# Routes
@app.route("/")
def index():
    if current_user():
        return redirect(url_for("dashboard"))
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username").strip()
        email = request.form.get("email").strip().lower()
        password = request.form.get("password")
        confirm = request.form.get("confirm")

        if not username or not email or not password:
            flash("All fields are required.")
            return redirect(url_for("register"))

        if password != confirm:
            flash("Passwords do not match.")
            return redirect(url_for("register"))

        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash("Username or email already exists.")
            return redirect(url_for("register"))

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Registration successful. Please log in.")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email").strip().lower()
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session["user_id"] = user.id
            flash("Logged in.")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password.")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Logged out.")
    return redirect(url_for("index"))

@app.route("/expenses", methods=["GET", "POST"])
@login_required
def expenses():
    user = current_user()

    if request.method == "POST":
        try:
            amount = float(request.form.get("amount"))
        except (TypeError, ValueError):
            flash("Amount must be a number.")
            return redirect(url_for("expenses"))

        category = request.form.get("category").strip()
        description = request.form.get("description") or ""
        date_str = request.form.get("date")

        try:
            if date_str:
                expense_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            else:
                expense_date = date.today()
        except ValueError:
            flash("Invalid date format.")
            return redirect(url_for("expenses"))

        if not category:
            flash("Category is required.")
            return redirect(url_for("expenses"))

        exp = Expense(
            user_id=user.id,
            amount=amount,
            category=category,
            date=expense_date,
            description=description,
        )
        db.session.add(exp)
        db.session.commit()
        flash("Expense added.")
        return redirect(url_for("expenses"))

    category_filter = request.args.get("category")
    month = request.args.get("month")
    year = request.args.get("year")

    query = Expense.query.filter_by(user_id=user.id)

    if category_filter:
        query = query.filter_by(category=category_filter)

    if month and year:
        try:
            month = int(month)
            year = int(year)
            query = query.filter(
                db.extract("month", Expense.date) == month,
                db.extract("year", Expense.date) == year,
            )
        except ValueError:
            flash("Invalid month or year filter.")

    expenses_list = query.order_by(Expense.date.desc()).all()

    categories = (
        db.session.query(Expense.category)
        .filter_by(user_id=user.id)
        .distinct()
        .all()
    )
    categories = [c[0] for c in categories]

    return render_template(
        "expenses.html",
        expenses=expenses_list,
        categories=categories,
        selected_category=category_filter or "",
        selected_month=str(month or ""),
        selected_year=str(year or ""),
    )

@app.route("/expenses/<int:expense_id>/edit", methods=["GET", "POST"])
@login_required
def edit_expense(expense_id):
    user = current_user()
    expense = Expense.query.filter_by(id=expense_id, user_id=user.id).first_or_404()

    if request.method == "POST":
        try:
            expense.amount = float(request.form.get("amount"))
        except (TypeError, ValueError):
            flash("Amount must be a number.")
            return redirect(url_for("edit_expense", expense_id=expense.id))

        expense.category = request.form.get("category").strip()
        expense.description = request.form.get("description") or ""
        date_str = request.form.get("date")

        try:
            if date_str:
                expense.date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid date format.")
            return redirect(url_for("edit_expense", expense_id=expense.id))

        db.session.commit()
        flash("Expense updated.")
        return redirect(url_for("expenses"))

    return render_template("edit_expense.html", expense=expense)

@app.route("/expenses/<int:expense_id>/delete", methods=["POST"])
@login_required
def delete_expense(expense_id):
    user = current_user()
    expense = Expense.query.filter_by(id=expense_id, user_id=user.id).first_or_404()
    db.session.delete(expense)
    db.session.commit()
    flash("Expense deleted.")
    return redirect(url_for("expenses"))

@app.route("/dashboard")
@login_required
def dashboard():
    user = current_user()

    month = request.args.get("month")
    year = request.args.get("year")

    today = date.today()
    try:
        month_int = int(month) if month else today.month
        year_int = int(year) if year else today.year
    except ValueError:
        month_int, year_int = today.month, today.year

    expenses = (
        Expense.query.filter_by(user_id=user.id)
        .filter(
            db.extract("month", Expense.date) == month_int,
            db.extract("year", Expense.date) == year_int,
        )
        .all()
    )

    totals_by_category = {}
    total_monthly = 0.0
    for exp in expenses:
        totals_by_category[exp.category] = totals_by_category.get(exp.category, 0) + exp.amount
        total_monthly += exp.amount

    labels = list(totals_by_category.keys())
    values = list(totals_by_category.values())

    return render_template(
        "dashboard.html",
        labels=labels,
        values=values,
        total_monthly=total_monthly,
        month=month_int,
        year=year_int,
    )

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)