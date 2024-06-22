import locale
import string
import random
from abc import ABC, abstractclassmethod
from datetime import timedelta

from flask import Flask, flash, redirect, render_template, request, session, url_for


class Slab(ABC):
    @abstractclassmethod
    def is_current_slab(self, income):
        raise NotImplementedError


class Slab1(Slab):
    min_income = 0
    max_income = 250000

    def __init__(self):
        self.rate = 0

    @classmethod
    def is_current_slab(cls, income):
        if income > cls.min_income and income <= cls.max_income:
            return True
        return False

    def __str__(self):
        return f"{self.rate*100}%"


class Slab2(Slab):
    min_income = 250001
    max_income = 500000

    def __init__(self):
        self.rate = 0.05

    @classmethod
    def is_current_slab(cls, income):
        if income >= cls.min_income and income <= cls.max_income:
            return True
        return False

    def __str__(self):
        return f"{self.rate*100}%"


class Slab3(Slab):
    min_income = 500001
    max_income = 1000000

    def __init__(self):
        self.rate = 0.2

    @classmethod
    def is_current_slab(cls, income):
        if income >= cls.min_income and income <= cls.max_income:
            return True
        return False

    def __str__(self):
        return f"{self.rate*100}%"


class Slab4(Slab):
    min_income = 1000001

    def __init__(self):
        self.rate = 0.3

    @classmethod
    def is_current_slab(cls, income):
        if income >= cls.min_income:
            return True
        return False

    def __str__(self):
        return f"{self.rate*100}%"


class IncomeTaxCalculator:
    def __init__(self, income):
        self.original_income = income
        self.income = income

    def add_exemption(self, exemption):
        if exemption >= self.income:
            raise ValueError("Exemption cannot be greater than or equal to income")
        self.income = self.income - exemption

    def compute_income_tax(self):
        slab = None
        for cls in Slab.__subclasses__():
            if cls.is_current_slab(self.income):
                slab = cls()

        if slab is None:
            print("No Slab is applicable to this income")
            return 1

        income_tax = self.income * slab.rate
        income_upon_tax = self.income - income_tax

        amount_saved = (self.original_income * slab.rate) - income_tax

        locale.setlocale(locale.LC_MONETARY, "en_IN")
        rupees = lambda amt: locale.currency(amt, grouping=True)

        result = {
            "original_income": rupees(self.original_income),
            "taxable_income": rupees(self.income),
            "income_tax": rupees(income_tax),
            "income_upon_tax": rupees(income_upon_tax),
            "amount_saved": rupees(amount_saved),
            "slab": str(slab),
        }
        return result


app = Flask(__name__)
key = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
app.secret_key = key.encode()
app.permanent_session_lifetime = timedelta(seconds=30)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/submit", methods=["POST", "GET"])
def compute():
    if request.method == "GET":
        return redirect(url_for("home"))
    try:
        income = float(request.form.get("income", None))
    except Exception as exc:
        flash("Income should be a number",category="error")
        return redirect(url_for("home"))

    exemption = request.form.get("exemption", None)
    if exemption == "":
        exemption = 0.0
    else:
        try:
            exemption = float(exemption)
        except Exception as exc:
            flash("Exemption should be a number", category="error")
            return redirect(url_for("home"))
    ic = IncomeTaxCalculator(income)
    try:
        ic.add_exemption(exemption)
    except Exception as exc:
        flash(str(exc), category="warning")
        return redirect(url_for("home"))
    result = ic.compute_income_tax()
    return render_template("result.html", response="success", result=result)


# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
