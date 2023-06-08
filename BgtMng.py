import sqlite3
import datetime as dt
con = sqlite3.connect('DB.db')

class Budget:
    acc_balance = con.cursor().execute("SELECT amount FROM BUDGET;").fetchall()[0][0]
    history = con.cursor().execute("""SELECT * FROM HISTORY;""").fetchall()
    prev = con.cursor().execute("SELECT date from DATES \
        WHERE name == 'previous_launch'").fetchall()[0][0]
    prev = dt.datetime.strptime(prev, '%d-%m-%Y').date()
    curr = dt.date.today()

class Remuneration:
    salary = con.cursor().execute("""SELECT * FROM SALARY;""").fetchall()
    def add_salary(this, name, amount, payday):
        this.salary.append((name, amount, payday))
    def modify_budget(this, budget):
        for s in this.salary:
            payday = s[2]
            amount = s[1]
            name = s[0]
            add_day = dt.timedelta(days=1)
            it = budget.prev + add_day
            while it <= budget.curr:
                if ((it+add_day).day == 1 and payday > it.day) or it.day == payday:
                    budget.acc_balance += s[1]
                    budget.history.append((name, amount, it.strftime("%Y-%m-%d"), budget.acc_balance))
                it += add_day


class Charges:
    bills = con.cursor().execute("""SELECT * FROM BILLS;""").fetchall()
    def add_bill(this, name, amount, payday):
        this.bills.append((name, amount, payday))
    def modify_budget(this, budget):
        for b in this.bills:
            payment_day = s[2]
            amount = s[1]
            name = s[0]
            add_day = dt.timedelta(days=1)
            it = budget.prev + add_day
            while it <= budget.curr:
                if ((it+add_day).day == 1 and payment_day > it.day) or it.day == payment_day:
                    budget.acc_balance += s[1]
                    budget.history.append((name, amount, it.strftime("%Y-%m-%d"), budget.acc_balance))SSS
                it += add_day

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
