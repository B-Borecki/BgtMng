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
            app, columns=("category", "expense", "limit"), show="headings", height=6
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

        category_table.place(x=16, y=776)
        scrollbar2 = Scrollbar(app, orient=VERTICAL, command=category_table.yview, width=16)
        category_table.configure(yscrollcommand=scrollbar2.set)
        scrollbar2.place(x=-1, y=776, height=145)
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
            height=38,
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
        scrollbar.place(x=660, y=140, height=788)

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
    def __init__(self, category):
        self.category = category
        pay_list = (
            con.cursor()
            .execute(f"""SELECT * FROM PAYMENTS WHERE category == '{category}';""")
            .fetchall()
        )

    def add(self, name, amount, payday):
        con.cursor().execute(
            f"""INSERT INTO PAYMENTS(name, category, amount, payday)
        VALUES ('{name}', '{self.category}', {amount}, {payday});"""
        )
        self.pay_list.append((name, f"{category}", amount, payday))

    def modify_budget(self, budget):
        for i in self.pay_list:
            payday = i[3]
            amount = i[2]
            name = i[0]
            add_day = dt.timedelta(days=1)
            it = budget.prev + add_day
            while it <= budget.curr:
                if ((it + add_day).day == 1 and payday > it.day) or it.day == payday:
                    budget.acc_balance += amount
                    budget.history.append(
                        (name, amount, it.strftime("%d-%m-%Y"), budget.acc_balance)
                    )
                it += add_day


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
            "———————————statistics———————————————————————————————————————————————"),
            font="Helvetica 15 italic",
        )
        history_label.place(x=-4, y=110)
        category_label = Label(
            self,
            text="–—————————————category—————————————————",
            font="Helvetica 15 italic",
        )
        category_label.place(x=-12, y=745)


if __name__ == "__main__":
    app = BgtMng()
    bgt = Budget()
    cat = Categories(bgt)
    pay = Transactions(bgt)
    bgt.budget_button(app)
    bgt.history_table(app)
    cat.categories_button(app)
    cat.category_table(app)
    pay.transaction_button(app, cat)
    cat.statistics(app)

    app.mainloop()

    bgt.add_to_db()
    con.cursor().execute(
        f"""UPDATE DATES SET date = '{bgt.curr.strftime("%d-%m-%Y")}' WHERE name = 'previous_launch';"""
    )
    con.commit()
    con.close()
