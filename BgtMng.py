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

class Recurring_payments:
    def modify_budget(budget, pay_list):
        for i in pay_list:
            payday = i[2]
            amount = i[1]
            name = i[0]
            add_day = dt.timedelta(days=1)
            it = budget.prev + add_day
            while it <= budget.curr:
                if ((it+add_day).day == 1 and payday > it.day) or it.day == payday:
                    budget.acc_balance += s[1]
                    budget.history.append((name, amount, it.strftime("%Y-%m-%d"), budget.acc_balance))
                it += add_day

class Salary(Recurring_payments):
    def __init__(self, budget):
        self.budget = budget
    salary = con.cursor().execute("""SELECT * FROM PAYMENTS WHERE category == 'SALARY';""").fetchall()
    def add_salary(this, name, amount, payday):
        this.salary.append((name, amount, 'SALARY', payday))
    def modify_budget():
        super().modify_budget(self.budget, self.salary)

class Bills(Recurring_payments):
    def __init__(self, budget):
        self.budget = budget
    bills = con.cursor().execute("""SELECT * FROM PAYMENTS WHERE category == 'BILLS';""").fetchall()
    def add_bill(this, name, amount, payday):
        this.bills.append((name, amount, 'BILLS', payday))
    def modify_budget():
        super().modify_budget(self.budget, self.bills)

class Subscriptions:
    def __init__(self, budget):
        self.budget = budget
    subs = con.cursor().execute("""SELECT * FROM PAYMENTS WHERE category == 'SUBSCRIPTIONS';""").fetchall()
    def add_sub():
       this.subs.append((name, amount, 'SUBSCRIPTIONS', payday))
    def modify_budget():
        super().modify_budget(self.budget, self.subs)

class Payments:
    def reduce_budget(budget):
        None

class Recognitions:
    def increase_budget(budget):
        None
