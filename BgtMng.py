import sqlite3
import datetime as dt
from tkinter import *
from tkinter import ttk
import tkinter.font as font
from tkinter.messagebox import showinfo

con = sqlite3.connect("DB.db")


class Budget:
    acc_balance = con.cursor().execute("SELECT amount FROM BUDGET;").fetchall()[0][0]
    prev = (
        con.cursor()
        .execute(
            "SELECT date from DATES \
        WHERE name == 'previous_launch'"
        )
        .fetchall()[0][0]
    )
    prev = dt.datetime.strptime(prev, "%d-%m-%Y").date()
    curr = dt.date.today()

    def add_to_db(self):
        con.cursor().execute(
            f"""UPDATE BUDGET SET amount = {self.acc_balance} WHERE name = 'budget';"""
        )

    butt = 0

    def budget_button(self, app):
        button_font_1 = font.Font(family="Arial", size=30)
        button_font_2 = font.Font(family="Arial", size=37, weight="bold")

        def show_bgt():
            bgt_button.configure(text=f"{self.acc_balance}", command=hide_bgt, font=button_font_2)
            self.butt = 1

        def hide_bgt():
            bgt_button.configure(
                text="Show total budget status", command=show_bgt, font=button_font_1
            )
            self.butt = 0

        if self.butt == 0:
            bgt_button = Button(
                app,
                text="Show total budget status",
                font=button_font_1,
                command=show_bgt,
                height=2,
                width=23,
                bd=2,
            )
        else:
            bgt_button = Button(
                app,
                text=f"{self.acc_balance}",
                font=button_font_2,
                command=hide_bgt,
                height=2,
                width=23,
                bd=2,
            )
        bgt_button.place(x=10, y=10, height=85, width=589)

    history = con.cursor().execute("""SELECT * FROM HISTORY;""").fetchall()[::-1]

    def history_table(self, app):
        self.history = sorted(self.history, key=lambda x: x[3], reverse=True)
        style = ttk.Style()
        style.configure("Treeview.Heading", font=(None, 12))
        style.configure("Treeview", font=("Helvetica bold", 11))
        history_table = ttk.Treeview(
            app,
            columns=("name", "category", "amount", "date"),
            show="headings",
            height=28,
        )
        history_table.column("name", width=145, minwidth=145, anchor=CENTER)
        history_table.column("category", width=145, minwidth=145, anchor=CENTER)
        history_table.column("amount", width=145, minwidth=145, anchor=CENTER)
        history_table.column("date", width=145, minwidth=145, anchor=CENTER)
        history_table.heading("name", text="name")
        history_table.heading("category", text="category")
        history_table.heading("amount", text="amount")
        history_table.heading("date", text="date")
        for record in self.history:
            history_table.insert("", END, values=record)
        history_table.place(x=16, y=140)

        scrollbar = Scrollbar(app, orient=VERTICAL, command=history_table.yview, width=16)
        history_table.configure(yscrollcommand=scrollbar.set)
        scrollbar.place(x=-1, y=140, height=587)


class Categories:
    def __init__(self, budget):
        self.bgt = budget
        self.categories_limits = con.cursor().execute("""SELECT * FROM CATEGORIES;""").fetchall()
        self.categories_limits = self.categories_limits[1:] + [self.categories_limits[0]]
        self.categories = [i[0] for i in self.categories_limits]
        if (
            con.cursor().execute(f"""SELECT SUM("limit") FROM CATEGORIES;""").fetchall()[0][0]
            == None
        ):
            self.savings = 0
        else:
            self.savings = int(
                con.cursor().execute(f"""SELECT SUM("limit") FROM CATEGORIES;""").fetchall()[0][0]
            ) + int(
                con.cursor()
                .execute(f"""SELECT SUM(amount) FROM BUDGET WHERE name != 'budget';""")
                .fetchall()[0][0]
            )
        self.actual = (
            con.cursor().execute("SELECT * FROM BUDGET WHERE name != 'budget';").fetchall()
        )
        self.actual = self.actual[1:] + [self.actual[0]]
        if self.bgt.prev.month != self.bgt.curr.month or self.bgt.prev.year != self.bgt.curr.year:
            self.monthly_budget = 0
            for record in self.bgt.history:
                date = dt.datetime.strptime(record[3], "%d-%m-%Y").date()
                if date.month == self.bgt.prev.month and date.year == self.bgt.prev.year:
                    self.monthly_budget += record[2]
            con.cursor().execute(
                f"""INSERT INTO STATISTICS(category, date, expense, "limit")
            VALUES ('remains from limit', '{self.bgt.prev.strftime("%m-%Y")}', {self.savings},'');"""
            )
            con.cursor().execute(
                f"""INSERT INTO STATISTICS(category, date, expense, "limit")
            VALUES ('monthly budget', '{self.bgt.prev.strftime("%m-%Y")}', {self.monthly_budget},'');"""
            )
            for i in range(len(self.actual)):
                con.cursor().execute(
                    f"""INSERT INTO STATISTICS(category, date, expense, "limit")
                    VALUES ('{self.actual[len(self.actual)-1-i][0]}',
                    '{self.bgt.prev.strftime("%m-%Y")}',
                    {self.actual[len(self.actual)-1-i][1]},
                    {self.categories_limits[len(self.actual)-1-i][1]});"""
                )
                self.actual[len(self.actual) - 1 - i] = (
                    self.actual[len(self.actual) - 1 - i][0],
                    0,
                )
            con.cursor().execute(
                f"""INSERT INTO STATISTICS(category, date, expense, "limit")
            VALUES ('', '', '','');"""
            )
            con.cursor().execute(
                f"""UPDATE BUDGET
            SET amount=0 WHERE name!= 'budget';"""
            )
            self.actual = (
                con.cursor().execute("SELECT * FROM BUDGET WHERE name != 'budget';").fetchall()
            )
            self.actual = self.actual[1:] + [self.actual[0]]
            self.savings = 0

            for i in range(len(self.actual)):
                self.savings += self.categories_limits[i][1] + self.actual[i][1]
        self.monthly_budget = 0
        for record in self.bgt.history:
            date = dt.datetime.strptime(record[3], "%d-%m-%Y").date()
            if date.month == self.bgt.curr.month and date.year == self.bgt.curr.year:
                self.monthly_budget += record[2]
        self.stats = con.cursor().execute("SELECT * FROM STATISTICS;").fetchall()[3:-1][::-1]


    def add_category(self, name, limit):
        con.cursor().execute(
            f"""INSERT INTO CATEGORIES(name, "limit")
        VALUES ('{name}', {limit});"""
        )
        self.categories_limits = (
            self.categories_limits[:-1] + [(f"{name}", limit)] + [self.categories_limits[-1]]
        )
        self.categories = self.categories[:-1] + [name] + [self.categories[-1]]
        con.cursor().execute(
            f"""INSERT INTO BUDGET(name, amount)
        VALUES ('{name}', '0');"""
        )
        self.actual = self.actual[:-1] + [(f"{name}", 0)] + [self.actual[-1]]
        self.savings += int(limit)

    def del_category(self, name):
        con.cursor().execute(f"""DELETE FROM CATEGORIES WHERE name = '{name}';""")
        con.cursor().execute(f"""DELETE FROM BUDGET WHERE name = '{name}';""")
        new_amount = 0
        for i in range(len(self.actual)):
            if self.actual[i][0] == "other":
                new_amount = self.actual[i][1] + self.actual[self.categories.index(name)][1]
                self.actual = self.actual[:i] + [("other", new_amount)] + self.actual[i + 1 :]
                con.cursor().execute(
                    f"""UPDATE BUDGET SET amount = {new_amount} WHERE name = 'other';"""
                )
                break
        self.categories_limits.remove(self.categories_limits[self.categories.index(name)])
        self.actual.remove(self.actual[self.categories.index(name)])
        self.categories.remove(name)

    def category_table(self, app):
        category_table = ttk.Treeview(
            app, columns=("category", "expense", "limit"), show="headings", height=7
        )
        category_table.column("category", width=193, minwidth=193, anchor=CENTER)
        category_table.column("expense", width=193, minwidth=193, anchor=CENTER)
        category_table.column("limit", width=193, minwidth=193, anchor=CENTER)
        category_table.heading("category", text="category")
        category_table.heading("expense", text="monthly expense")
        category_table.heading("limit", text="limit")

        for record in range(len(self.actual)):
            category_table.insert(
                "",
                END,
                values=self.actual[record] + (self.categories_limits[record][1],),
            )

        category_table.place(x=16, y=780)
        scrollbar2 = Scrollbar(app, orient=VERTICAL, command=category_table.yview, width=16)
        category_table.configure(yscrollcommand=scrollbar2.set)
        scrollbar2.place(x=-1, y=780, height=168)
        self.monthly_budget_button(app)
        self.savings_button(app)

    def categories_button(self, app):
        def modify_categories():
            mod = Toplevel()
            mod.title("Modify categories")
            mod.geometry("650x150")
            mod.maxsize(650, 150)
            mod.minsize(650, 150)
            canvas = Canvas(mod)
            canvas.create_line(100, 0, 100, 200)
            canvas.place(x=230, y=-5)

            name = Entry(mod, width=20, font=(None, 10))
            name.place(x=125, y=25)
            name_label = Label(mod, text="Category name:", font=("sans-serif", 11))
            name_label.place(x=3, y=25)
            limit = Entry(mod, width=20, font=(None, 10))
            limit.place(x=125, y=65)
            limit_label = Label(mod, text="Monthly limit:", font=("sans-serif", 11))
            limit_label.place(x=15, y=65)

            def add_button():
                new_name = name.get()
                new_limit = limit.get()
                name.delete(0, END)
                limit.delete(0, END)
                if new_name in self.categories:
                    old_limit = self.categories_limits[self.categories.index(new_name)][1]
                    self.categories_limits[self.categories.index(new_name)] = (
                        new_name,
                        new_limit,
                    )
                    con.cursor().execute(
                        f"""UPDATE CATEGORIES SET "limit" = {new_limit} WHERE name = '{new_name}';"""
                    )
                    self.savings -= int(old_limit) - int(new_limit)
                else:
                    self.add_category(new_name, new_limit)
                self.category_table(app)
                del_menu()

            add_button = Button(
                mod,
                text="Add category",
                font=(None, 11),
                command=add_button,
                height=1,
                width=17,
            )
            add_button.place(x=125, y=100)

            def del_menu():
                clicked = StringVar()
                clicked.set("Select category")
                menu = OptionMenu(mod, clicked, "—————————", *self.categories)
                menu.config(width=20, font=("Helvetica bold", 11))
                menu.place(x=390, y=85)
                menu_text = mod.nametowidget(menu.menuname)
                menu_text.config(font=("TkDefaultFont", 11))

                def del_button():
                    del_name = clicked.get()
                    if (
                        del_name == "Select category"
                        or del_name == "—————————"
                        or del_name == "other"
                    ):
                        return 0
                    for i in self.categories_limits:
                        if i[0] == del_name:
                            self.savings -= int(i[1])
                            break
                    self.del_category(del_name)
                    self.category_table(app)
                    del_menu()

                del_button = Button(
                    mod,
                    text="Delete category",
                    command=del_button,
                    font=(None, 11),
                    height=1,
                    width=17,
                )
                del_button.place(x=410, y=35)

            del_menu()

        categories_button = Button(
            app,
            text="Modify categories",
            font=(None, 12),
            height=2,
            width=15,
            command=modify_categories,
        )
        categories_button.place(x=15, y=947)

    def statistics(self, app):
        stats_table = ttk.Treeview(
            app,
            columns=("category", "month", "amount", "limit"),
            show="headings",
            height=39,
        )
        stats_table.column("category", width=170, minwidth=145, anchor=CENTER)
        stats_table.column("month", width=145, minwidth=145, anchor=CENTER)
        stats_table.column("amount", width=145, minwidth=145, anchor=CENTER)
        stats_table.column("limit", width=145, minwidth=145, anchor=CENTER)
        stats_table.heading("category", text="category")
        stats_table.heading("month", text="month")
        stats_table.heading("amount", text="amount")
        stats_table.heading("limit", text="limit")
        for record in self.stats:
            stats_table.insert("", END, values=record)
        stats_table.place(x=660, y=140)

        scrollbar = Scrollbar(app, orient=VERTICAL, command=stats_table.yview, width=16)
        stats_table.configure(yscrollcommand=scrollbar.set)
        scrollbar.place(x=660, y=140, height=808)

    butt1 = 0

    def monthly_budget_button(self, app):
        button_font_1 = font.Font(family="Arial", size=30)
        button_font_2 = font.Font(family="Arial", size=37, weight="bold")

        def show_bgt():
            bgt_button.configure(
                text=f"{self.monthly_budget}", command=hide_bgt, font=button_font_2
            )
            self.butt1 = 1

        def hide_bgt():
            bgt_button.configure(
                text="Show monthly budget status", command=show_bgt, font=button_font_1
            )
            self.butt1 = 0

        if self.butt1 == 0:
            bgt_button = Button(
                app,
                text="Show monthly budget status",
                font=button_font_1,
                command=show_bgt,
                height=2,
                width=23,
                bd=2,
            )
        else:
            bgt_button = Button(
                app,
                text=f"{self.monthly_budget}",
                font=button_font_2,
                command=hide_bgt,
                height=2,
                width=23,
                bd=2,
            )
        bgt_button.place(x=663, y=10, height=85, width=604)

    butt2 = 0

    def savings_button(self, app):
        button_font_1 = font.Font(family="Arial", size=30)
        button_font_2 = font.Font(family="Arial", size=37, weight="bold")

        def show_savings():
            savings_button.configure(
                text=f"{self.savings}", command=hide_savings, font=button_font_2
            )
            self.butt2 = 1

        def hide_savings():
            savings_button.configure(
                text="Show remaining limit amount",
                command=show_savings,
                font=button_font_1,
            )
            self.butt2 = 0

        if self.butt2 == 0:
            savings_button = Button(
                app,
                text="Show remaining limit amount",
                font=button_font_1,
                command=show_savings,
                height=2,
                width=23,
                bd=2,
            )
        else:
            savings_button = Button(
                app,
                text=f"{self.savings}",
                font=button_font_2,
                command=hide_savings,
                height=2,
                width=23,
                bd=2,
            )
        savings_button.place(x=1325, y=10, height=85, width=580)


class Recurring_payment:
    bills = (
        con.cursor()
        .execute(f"""SELECT * FROM PAYMENTS WHERE category == 'bill';""")
        .fetchall()
    )

    payouts = (
        con.cursor()
        .execute(f"""SELECT * FROM PAYMENTS WHERE category == 'payout';""")
        .fetchall()
    )

    subs = (
        con.cursor()
        .execute(f"""SELECT * FROM PAYMENTS WHERE category == 'subscription';""")
        .fetchall()
    )

    def add(self, name, category, amount, payday):
        con.cursor().execute(
            f"""INSERT INTO PAYMENTS(name, category, amount, payday)
        VALUES ('{name}', '{category}', {amount}, {payday});"""
        )
        if category == 'bill':
            self.bills.append((name, category, amount, payday))
        elif category == 'payout':
            self.payouts.append((name, category, amount, payday))
        elif category == 'subscription':
            self.subs.append((name, category, amount, payday))

    def delete(self, name, category):
        if category == 'bill':
            for i in range(len(self.bills)):
                if self.bills[i][0] == name:
                    self.bills = self.bills[:i] + self.bills[i+1:]
                    break
        elif category == 'payout':
            for i in range(len(self.payouts)):
                if self.payouts[i][0] == name:
                    self.payouts = self.payouts[:i] + self.payouts[i+1:]
                    break
        elif category == 'subscription':
            for i in range(len(self.subs)):
                if self.subs[i][0] == name:
                    self.subs = self.subs[:i] + self.subs[i+1:]
                    break

        con.cursor().execute(f"""DELETE FROM PAYMENTS WHERE name = '{name}' AND category = '{category}';""")

    def past_month(self, budget):
        def modify(pay_list):
            for record in pay_list:
                payday = record[3]
                amount = record[2]
                category = record[1]
                name = record[0]
                if payday > budget.prev.day:
                    budget.acc_balance += amount
                    budget.history = [
                        (name, category, amount, dt.date(day=payday,month=budget.prev.month,year=budget.prev.year).strftime("%d-%m-%Y"))
                    ] + budget.history

                    con.cursor().execute(
                    f"""INSERT INTO HISTORY(name, category, amount, date)
                    VALUES ('{name}', '{category}', {amount}, '{dt.date(day=payday,month=budget.prev.month,year=budget.prev.year).strftime("%d-%m-%Y")}');"""
                    )


        if budget.curr.month != budget.prev.month or budget.curr.year != budget.prev.year:
            modify(self.bills)
            modify(self.payouts)
            modify(self.subs)

    def actual_month(self, budget, cat):
        def modify(pay_list, prev):
            for record in pay_list:
                payday = record[3]
                amount = record[2]
                category = record[1]
                name = record[0]
                if payday > prev and payday <= budget.curr.day:
                    budget.acc_balance += amount
                    budget.history = [
                        (name, category, amount, dt.date(day=payday,month=budget.curr.month,year=budget.curr.year).strftime("%d-%m-%Y"))
                    ] + budget.history
                    con.cursor().execute(
                    f"""INSERT INTO HISTORY(name, category, amount, date)
                    VALUES ('{name}', '{category}', {amount}, '{dt.date(day=payday,month=budget.prev.month,year=budget.prev.year).strftime("%d-%m-%Y")}');"""
                    )
                    cat.monthly_budget += amount
        if budget.curr.month == budget.prev.month and budget.curr.year == budget.prev.year:
            modify(self.bills, budget.prev.day)
            modify(self.payouts, budget.prev.day)
            modify(self.subs, budget.prev.day)
        else:
            modify(self.bills, 0)
            modify(self.payouts, 0)
            modify(self.subs, 0)

    def bills_table(self, app):
        bills_table = ttk.Treeview(
            app, columns=("name", "amount", "payday"), show="headings", height=7
        )
        bills_table.column("name", width=187, minwidth=185, anchor=CENTER)
        bills_table.column("amount", width=188, minwidth=185, anchor=CENTER)
        bills_table.column("payday", width=187, minwidth=185, anchor=CENTER)
        bills_table.heading("name", text="name")
        bills_table.heading("amount", text="amount")
        bills_table.heading("payday", text="payday")

        for record in self.bills:
            bills_table.insert(
                "",
                END,
                values=(record[0], record[2], record[3]))

        bills_table.place(x=1340, y=140)
        scrollbar = Scrollbar(app, orient=VERTICAL, command=bills_table.yview, width=17)
        bills_table.configure(yscrollcommand=scrollbar.set)
        scrollbar.place(x=1322, y=140, height=168)

    def bills_button(self, app):
        def modify_bills():
            mod = Toplevel()
            mod.title("Modify bills")
            mod.geometry("650x150")
            mod.maxsize(650, 150)
            mod.minsize(650, 150)
            canvas = Canvas(mod)
            canvas.create_line(100, 0, 100, 200)
            canvas.place(x=230, y=-5)

            name = Entry(mod, width=20, font=(None, 10))
            name.place(x=90, y=20)
            name_label = Label(mod, text="Bill name:", font=("sans-serif", 11))
            name_label.place(x=3, y=20)
            amount = Entry(mod, width=20, font=(None, 10))
            amount.place(x=90, y=50)
            amount_label = Label(mod, text="Amount:", font=("sans-serif", 11))
            amount_label.place(x=10, y=50)
            payday = Entry(mod, width=20, font=(None, 10))
            payday.place(x=90, y=80)
            payday_label = Label(mod, text="Payday:", font=("sans-serif", 11))
            payday_label.place(x=17, y=80)

            def add_button():
                new_name = name.get()
                new_payday = payday.get()
                new_amount = -int(amount.get())
                name.delete(0, END)
                payday.delete(0, END)
                amount.delete(0, END)
                bill_names = [i[0] for i in self.bills]
                if new_name in bill_names:
                    k = 0
                    for i in range(len(self.bills)):
                        if self.bills[i][0] == new_name:
                             k = i
                             break
                    self.bills = self.bills[:k] + [(new_name, 'bill', new_amount, new_payday)]
                    con.cursor().execute(
                        f"""UPDATE PAYMENTS SET "payday" = {new_payday} WHERE name = '{new_name}';"""
                    )
                    con.cursor().execute(
                        f"""UPDATE PAYMENTS SET "amount" = {new_amount} WHERE name = '{new_name}';"""
                    )
                else:
                    self.add(new_name, 'bill', new_amount, new_payday)
                self.bills_table(app)
                del_menu()

            add_button = Button(
                mod,
                text="Add bill",
                font=(None, 11),
                command=add_button,
                height=1,
                width=17,
            )
            add_button.place(x=91, y=110)

            def del_menu():
                clicked = StringVar()
                clicked.set("Select bill")
                bills_name = []
                for i in self.bills:
                    bills_name.append(i[0])
                menu = OptionMenu(mod, clicked, "—————————", *bills_name)
                menu.config(width=20, font=("Helvetica bold", 11))
                menu.place(x=390, y=85)
                menu_text = mod.nametowidget(menu.menuname)
                menu_text.config(font=("TkDefaultFont", 11))

                def del_button():
                    del_name = clicked.get()
                    if (
                        del_name == "Select bill"
                        or del_name == "—————————"
                    ):
                        return 0

                    self.delete(del_name, 'bill')
                    self.bills_table(app)
                    del_menu()

                del_button = Button(
                    mod,
                    text="Delete bill",
                    command=del_button,
                    font=(None, 11),
                    height=1,
                    width=17,
                )
                del_button.place(x=410, y=35)

            del_menu()

        bills_button = Button(
            app,
            text="Modify bills",
            font=(None, 12),
            height=2,
            width=18,
            command=modify_bills,
        )
        bills_button.place(x=1530, y=305)

    def payouts_table(self, app):
        payouts_table = ttk.Treeview(
            app, columns=("name", "amount", "payday"), show="headings", height=7
        )
        payouts_table.column("name", width=187, minwidth=185, anchor=CENTER)
        payouts_table.column("amount", width=188, minwidth=185, anchor=CENTER)
        payouts_table.column("payday", width=187, minwidth=185, anchor=CENTER)
        payouts_table.heading("name", text="name")
        payouts_table.heading("amount", text="amount")
        payouts_table.heading("payday", text="payday")

        for record in self.payouts:
            payouts_table.insert(
                "",
                END,
                values=(record[0], record[2], record[3]))

        payouts_table.place(x=1340, y=460)
        scrollbar = Scrollbar(app, orient=VERTICAL, command=payouts_table.yview, width=17)
        payouts_table.configure(yscrollcommand=scrollbar.set)
        scrollbar.place(x=1322, y=460, height=168)

    def payouts_button(self, app):
        def modify_payouts():
            mod = Toplevel()
            mod.title("Modify payouts")
            mod.geometry("650x150")
            mod.maxsize(650, 150)
            mod.minsize(650, 150)
            canvas = Canvas(mod)
            canvas.create_line(100, 0, 100, 200)
            canvas.place(x=230, y=-5)

            name = Entry(mod, width=20, font=(None, 10))
            name.place(x=115, y=20)
            name_label = Label(mod, text="Payout name:", font=("sans-serif", 11))
            name_label.place(x=3, y=20)
            amount = Entry(mod, width=20, font=(None, 10))
            amount.place(x=115, y=50)
            amount_label = Label(mod, text="Amount:", font=("sans-serif", 11))
            amount_label.place(x=37, y=50)
            payday = Entry(mod, width=20, font=(None, 10))
            payday.place(x=115, y=80)
            payday_label = Label(mod, text="Payday:", font=("sans-serif", 11))
            payday_label.place(x=44, y=80)

            def add_button():
                new_name = name.get()
                new_payday = payday.get()
                new_amount = int(amount.get())
                name.delete(0, END)
                payday.delete(0, END)
                amount.delete(0, END)
                payout_names = [i[0] for i in self.payouts]
                if new_name in payout_names:
                    k = 0
                    for i in range(len(self.payouts)):
                        if self.payouts[i][0] == new_name:
                             k = i
                             break
                    self.payouts = self.payouts[:k] + [(new_name, 'bill', new_amount, new_payday)]
                    con.cursor().execute(
                        f"""UPDATE PAYMENTS SET "payday" = {new_payday} WHERE name = '{new_name}';"""
                    )
                    con.cursor().execute(
                        f"""UPDATE PAYMENTS SET "amount" = {new_amount} WHERE name = '{new_name}';"""
                    )
                else:
                    self.add(new_name, 'payout', new_amount, new_payday)
                self.payouts_table(app)
                del_menu()

            add_button = Button(
                mod,
                text="Add payout",
                font=(None, 11),
                command=add_button,
                height=1,
                width=17,
            )
            add_button.place(x=116, y=110)

            def del_menu():
                clicked = StringVar()
                clicked.set("Select payout")
                payouts_name = []
                for i in self.payouts:
                    payouts_name.append(i[0])
                menu = OptionMenu(mod, clicked, "—————————", *payouts_name)
                menu.config(width=20, font=("Helvetica bold", 11))
                menu.place(x=390, y=85)
                menu_text = mod.nametowidget(menu.menuname)
                menu_text.config(font=("TkDefaultFont", 11))

                def del_button():
                    del_name = clicked.get()
                    if (
                        del_name == "Select payout"
                        or del_name == "—————————"
                    ):
                        return 0

                    self.delete(del_name, 'payout')
                    self.payouts_table(app)
                    del_menu()

                del_button = Button(
                    mod,
                    text="Delete payout",
                    command=del_button,
                    font=(None, 11),
                    height=1,
                    width=17,
                )
                del_button.place(x=410, y=35)

            del_menu()

        payouts_button = Button(
            app,
            text="Modify payouts",
            font=(None, 12),
            height=2,
            width=18,
            command=modify_payouts,
        )
        payouts_button.place(x=1530, y=625)

    def subs_table(self, app):
        subs_table = ttk.Treeview(
            app, columns=("name", "amount", "payday"), show="headings", height=7
        )
        subs_table.column("name", width=187, minwidth=185, anchor=CENTER)
        subs_table.column("amount", width=188, minwidth=185, anchor=CENTER)
        subs_table.column("payday", width=187, minwidth=185, anchor=CENTER)
        subs_table.heading("name", text="name")
        subs_table.heading("amount", text="amount")
        subs_table.heading("payday", text="payday")

        for record in self.subs:
            subs_table.insert(
                "",
                END,
                values=(record[0], record[2], record[3]))

        subs_table.place(x=1340, y=780)
        scrollbar = Scrollbar(app, orient=VERTICAL, command=subs_table.yview, width=17)
        subs_table.configure(yscrollcommand=scrollbar.set)
        scrollbar.place(x=1322, y=780, height=168)

    def subs_button(self, app):
        def modify_subs():
            mod = Toplevel()
            mod.title("Modify subscriptions")
            mod.geometry("650x150")
            mod.maxsize(650, 150)
            mod.minsize(650, 150)
            canvas = Canvas(mod)
            canvas.create_line(100, 0, 100, 200)
            canvas.place(x=230, y=-5)

            name = Entry(mod, width=20, font=(None, 10))
            name.place(x=150, y=20)
            name_label = Label(mod, text="Subscription name:", font=("sans-serif", 11))
            name_label.place(x=3, y=20)
            amount = Entry(mod, width=20, font=(None, 10))
            amount.place(x=150, y=50)
            amount_label = Label(mod, text="Amount:", font=("sans-serif", 11))
            amount_label.place(x=76, y=50)
            payday = Entry(mod, width=20, font=(None, 10))
            payday.place(x=150, y=80)
            payday_label = Label(mod, text="Payday:", font=("sans-serif", 11))
            payday_label.place(x=83, y=80)

            def add_button():
                new_name = name.get()
                new_payday = payday.get()
                new_amount = -int(amount.get())
                name.delete(0, END)
                payday.delete(0, END)
                amount.delete(0, END)
                subs_names = [i[0] for i in self.payouts]
                if new_name in subs_names:
                    k = 0
                    for i in range(len(self.subs)):
                        if self.subs[i][0] == new_name:
                             k = i
                             break
                    self.subs = self.subs[:k] + [(new_name, 'subscription', new_amount, new_payday)]
                    con.cursor().execute(
                        f"""UPDATE PAYMENTS SET "payday" = {new_payday} WHERE name = '{new_name}';"""
                    )
                    con.cursor().execute(
                        f"""UPDATE PAYMENTS SET "amount" = {new_amount} WHERE name = '{new_name}';"""
                    )
                else:
                    self.add(new_name, 'subscription', new_amount, new_payday)
                self.subs_table(app)
                del_menu()

            add_button = Button(
                mod,
                text="Add subscription",
                font=(None, 11),
                command=add_button,
                height=1,
                width=17,
            )
            add_button.place(x=151, y=110)

            def del_menu():
                clicked = StringVar()
                clicked.set("Select subscription")
                subs_name = []
                for i in self.subs:
                    subs_name.append(i[0])
                menu = OptionMenu(mod, clicked, "—————————", *subs_name)
                menu.config(width=20, font=("Helvetica bold", 11))
                menu.place(x=390, y=85)
                menu_text = mod.nametowidget(menu.menuname)
                menu_text.config(font=("TkDefaultFont", 11))

                def del_button():
                    del_name = clicked.get()
                    if (
                        del_name == "Select subscription"
                        or del_name == "—————————"
                    ):
                        return 0

                    self.delete(del_name, 'subscription')
                    self.subs_table(app)
                    del_menu()

                del_button = Button(
                    mod,
                    text="Delete subscription",
                    command=del_button,
                    font=(None, 11),
                    height=1,
                    width=17,
                )
                del_button.place(x=410, y=35)

            del_menu()

        subs_button = Button(
            app,
            text="Modify subscriptions",
            font=(None, 12),
            height=2,
            width=18,
            command=modify_subs,
        )
        subs_button.place(x=1530, y=947)


class Transactions:
    def __init__(self, budget):
        self.budget = budget

    def modify_budget(self, name, category, amount, app, cat):
        cat.monthly_budget += amount
        cat.monthly_budget_button(app)
        self.budget.acc_balance += amount
        self.budget.history = [
            ((name, category, amount, self.budget.curr.strftime("%d-%m-%Y")))
        ] + self.budget.history
        self.budget.budget_button(app)
        con.cursor().execute(
            f"""INSERT INTO HISTORY(name, category, amount, date)
        VALUES ('{name}', '{category}', {amount}, '{self.budget.curr.strftime("%d-%m-%Y")}');"""
        )

    def transaction_button(self, app, cat):
        def trans():
            pay = Toplevel(app)
            pay.title("Add payment")
            pay.geometry("650x150")
            pay.maxsize(650, 150)
            pay.minsize(650, 150)
            name_label = Label(pay, text="Name:", font=("sans-serif", 11)).place(x=18, y=30)
            name = Entry(pay, width=20, font=(None, 10))
            name.place(x=75, y=30)
            amount_label = Label(pay, text="Amount:", font=("sans-serif", 11)).place(x=3, y=67)
            amount = Entry(pay, width=20, font=(None, 10))
            amount.place(x=75, y=67)

            sign = IntVar(pay, -1)
            Radiobutton(
                pay, text="outgoing –", font="TkDefaultFont 12", variable=sign, value=-1
            ).place(x=270, y=30)
            Radiobutton(
                pay, text="incoming +", font="TkDefaultFont 12", variable=sign, value=1
            ).place(x=270, y=65)

            clicked = StringVar()
            clicked.set("Select category")
            menu = OptionMenu(pay, clicked, "—————————", *cat.categories)
            menu.config(width=20, font=("Helvetica bold", 11))
            menu.place(x=425, y=45)
            menu_text = pay.nametowidget(menu.menuname)
            menu_text.config(font=("TkDefaultFont", 11))

            def add():
                new_name = name.get()
                new_amount = amount.get()
                new_sign = sign.get()
                new_category = clicked.get()
                name.delete(0, END)
                amount.delete(0, END)
                clicked.set("Select category")
                if (
                    new_name != None
                    and (new_category == "—————————"
                    or new_category == "Select category")
                    and new_sign == 1
                ):
                    self.modify_budget(new_name, "+", int(new_amount), app, cat)
                    self.budget.history_table(app)
                    cat.category_table(app)
                if (
                    new_name == None
                    or new_amount == None
                    or new_category == "—————————"
                    or new_category == "Select category"
                ):
                    return 0
                new_amount = new_sign * int(new_amount)
                self.modify_budget(new_name, new_category, new_amount, app, cat)
                self.budget.history_table(app)
                cat.savings += new_amount
                for i in range(len(cat.actual)):
                    if cat.actual[i][0] == new_category:
                        new_amount = cat.actual[i][1] + new_amount
                        cat.actual = (
                            cat.actual[:i] + [(new_category, new_amount)] + cat.actual[i + 1 :]
                        )
                        break
                con.cursor().execute(
                    f"""UPDATE BUDGET SET amount = {new_amount} WHERE name = '{new_category}';"""
                )
                cat.category_table(app)

            add = Button(
                pay,
                text="Add payment",
                command=add,
                font=(None, 11),
                height=1,
                width=17,
            ).place(x=255, y=105)

        trans = Button(
            app, text="Payment", command=trans, font=(None, 12), height=2, width=15
        ).place(x=177, y=947)



class BgtMng(Tk):
    def __init__(self):
        super().__init__()
        self.title("BgtMng")
        width = self.winfo_screenwidth()
        height = self.winfo_screenheight()
        self.geometry(f"{width}x{height}")
        history_label = Label(
            self,
            text=("—————————————history———————————————————"
            "———————————statistics———————————————————————————————bills——————————————"),
            font="Helvetica 15 italic",
        )
        history_label.place(x=-4, y=110)
        category_label = Label(
            self,
            text="–—————————————category—————————————————"
            "—————————————————————————————————————————————subscriptions————————————————",
            font="Helvetica 15 italic",
        )
        category_label.place(x=-12, y=749)
        payout_label = Label(
            self,
            text="————————————————————payouts—————————————",
            font="Helvetica 15 italic",
            )
        payout_label.place(x=1200, y=428)


if __name__ == "__main__":
    app = BgtMng()
    bgt = Budget()
    pay = Transactions(bgt)
    rec = Recurring_payment()
    rec.past_month(bgt)
    cat = Categories(bgt)
    rec.actual_month(bgt, cat)
    bgt.budget_button(app)
    bgt.history_table(app)
    cat.categories_button(app)
    cat.category_table(app)
    pay.transaction_button(app, cat)
    cat.statistics(app)
    rec.bills_table(app)
    rec.bills_button(app)
    rec.payouts_table(app)
    rec.payouts_button(app)
    rec.subs_table(app)
    rec.subs_button(app)
    app.mainloop()

    bgt.add_to_db()
    con.cursor().execute(
        f"""UPDATE DATES SET date = '{bgt.curr.strftime("%d-%m-%Y")}' WHERE name = 'previous_launch';"""
    )
    con.commit()
    con.close()
