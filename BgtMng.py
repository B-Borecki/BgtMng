import sqlite3
import datetime as dt
con = sqlite3.connect('DB.db')

class Budget:
    acc_balance = con.cursor().execute("SELECT amount FROM BUDGET;").fetchall()[0][0]
    history = con.cursor().execute("""SELECT * FROM HISTORY;""").fetchall()
    prev = con.cursor().execute("SELECT date from DATES \
        WHERE name == 'previous_launch'").fetchall()[0][0]
    prev = dt.datetime.strptime(prev, '%d.%m.%Y').date()
    curr = dt.date.today()

class Remuneration:
    salary
    def add_salary():
        None
    def modify_budget(budget):
        None

class Charges:
    bills
    def add_bill():
        None
    def modify_budget(budget):
        None

class Subscriptions:
    subs
    def add_sub():
        None

class Payments:
    def reduce_budget(budget):
        None

class Recognitions:
    def increase_budget(budget):
        None

con.close()
