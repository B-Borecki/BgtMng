import sqlite3
import datetime as dt
from tkinter import *
from tkinter import ttk
import tkinter.font as font
from tkinter.messagebox import showinfo

con = sqlite3.connect('DB.db')

class Budget:
    acc_balance = con.cursor().execute("SELECT amount FROM BUDGET;").fetchall()[0][0]
    prev = con.cursor().execute("SELECT date from DATES \
        WHERE name == 'previous_launch'").fetchall()[0][0]
    prev = dt.datetime.strptime(prev, "%d-%m-%Y").date()
    curr = dt.datetime.strptime("15-07-2023", "%d-%m-%Y").date()
    def add_to_db(self):
        con.cursor().execute(f"""UPDATE BUDGET SET amount = {self.acc_balance} WHERE name = 'budget';""")
    def budget_button(self, app):
        button_font_1 = font.Font(family='Arial', size=25)
        button_font_2 = font.Font(family='Arial', size=30, weight='bold')
        def show_bgt():
            bgt_button.configure(text=f"{self.acc_balance}", command=hide_bgt, font=button_font_2)
        def hide_bgt():
            bgt_button.configure(text="Show budget status", command=show_bgt, font=button_font_1)
        bgt_button = Button(app, text = "Show budget status", font=button_font_1, command=show_bgt, height = 2, width=23, bd=2)
        bgt_button.place(x = 13, y = 6,  height=60, width=403)
    history = con.cursor().execute("""SELECT * FROM HISTORY;""").fetchall()[::-1]
    def history_table(self, app):
        history_table = ttk.Treeview(app, columns=("name", "category", "amount", "date"), show='headings', height=20)
        history_table.column("name", width=100, minwidth=100, anchor=CENTER)
        history_table.column("category", width=100, minwidth=100, anchor=CENTER)
        history_table.column("amount", width=100, minwidth=100, anchor=CENTER)
        history_table.column("date", width=100, minwidth=100, anchor=CENTER)
        history_table.heading("name", text="name")
        history_table.heading("category", text="category")
        history_table.heading("amount", text="amount")
        history_table.heading("date", text="date")
        for record in self.history:
            history_table.insert('', END, values=record)
        history_table.place(x = 14, y = 90)

        scrollbar = Scrollbar(app, orient=VERTICAL, command=history_table.yview, width = 15)
        history_table.configure(yscrollcommand=scrollbar.set)
        scrollbar.place(x = -1, y = 90, height=420)


class Categories:
    categories_limits = con.cursor().execute("""SELECT * FROM CATEGORIES;""").fetchall()
    categories = [i[0] for i in categories_limits]
    if con.cursor().execute(f"""SELECT SUM("limit") FROM CATEGORIES;""").fetchall()[0][0] == None:
        savings = 0
    else:
        savings = int(con.cursor().execute(f"""SELECT SUM("limit") FROM CATEGORIES;""").fetchall()[0][0]) - int(con.cursor().execute(f"""SELECT SUM(amount) FROM BUDGET WHERE name != 'budget';""").fetchall()[0][0])
    prev = con.cursor().execute("SELECT date from DATES \
        WHERE name == 'previous_launch'").fetchall()[0][0]
    prev = dt.datetime.strptime(prev, '%d-%m-%Y').date()
    curr = dt.datetime.strptime("15-07-2023", "%d-%m-%Y").date()
    actual = con.cursor().execute("SELECT * FROM BUDGET WHERE name != 'budget';").fetchall()
    if prev.month != curr.month or prev.year != curr.year:
        con.cursor().execute(f"""INSERT INTO CATEGORY_HISTORY(category, date, expense, "limit")
        VALUES ('savings', '{prev.strftime("%m-%Y")}', {savings},'');""")
        for i in range(len(actual)):
            con.cursor().execute(f"""INSERT INTO CATEGORY_HISTORY(category, date, expense, "limit")
            VALUES ('{actual[i][0]}', '{prev.strftime("%m-%Y")}',{actual[i][1]}, {categories_limits[i][1]});""")
            actual[i] = (actual[i][0], 0)
        con.cursor().execute(f"""INSERT INTO CATEGORY_HISTORY(category, date, expense, "limit")
        VALUES ('', '', '','');""")
        savings = 0
        for i in range(len(actual)):
            savings += categories_limits[i][1] - actual[i][1]



    def add_category(self, name, limit):
        con.cursor().execute(f"""INSERT INTO CATEGORIES(name, "limit")
        VALUES ('{name}', {limit});""")
        self.categories_limits.append((f'{name}', limit))
        self.categories.append(name)
        con.cursor().execute(f"""INSERT INTO BUDGET(name, amount)
        VALUES ('{name}', '0');""")
        self.actual.append((f'{name}', 0))
        self.savings += int(limit)

    def del_category(self, name):
        con.cursor().execute(f"""DELETE FROM CATEGORIES WHERE name = '{name}';""")
        con.cursor().execute(f"""DELETE FROM BUDGET WHERE name = '{name}';""")
        self.categories_limits.remove(self.categories_limits[self.categories.index(name)])
        self.actual.remove(self.actual[self.categories.index(name)])
        self.categories.remove(name)

    def category_table(self, app):
        category_table = ttk.Treeview(app, columns=("category", "expense", "limit"), show='headings', height=5)
        category_table.column("category", width=125, minwidth=125, anchor=CENTER)
        category_table.column("expense", width=125, minwidth=125, anchor=CENTER)
        category_table.column("limit", width=125, minwidth=125, anchor=CENTER)
        category_table.heading("category", text="category")
        category_table.heading("expense", text="monthly expense")
        category_table.heading("limit", text="limit")
        i = 0
        for record in self.actual:
            category_table.insert('', END, values=record + (self.categories_limits[i][1],))
            i+=1
        category_table.place(x = 14, y = 540)
        scrollbar2 = Scrollbar(app, orient=VERTICAL, command=category_table.yview, width = 15)
        category_table.configure(yscrollcommand=scrollbar2.set)
        scrollbar2.place(x = -1, y = 540, height=120)
        savings_label = Label(app, text = f"savings:   {self.savings}", bg='#F5F5F5', width=53, anchor=W).place(x=15, y=660)

    def categories_button(self, app):
        def modify_categories():
            mod = Toplevel()
            mod.title("Modify categories")
            mod.geometry("500x100")
            mod.maxsize(500, 100)
            mod.minsize(500, 100)
            canvas = Canvas(mod)
            canvas.create_line(100, 0, 100, 120)
            canvas.place(x=155, y = -5)

            name = Entry(mod, width=17)
            name.place(x = 100, y=5)
            name_label = Label(mod, text="Category name:")
            name_label.place(x = 1, y = 5)
            limit = Entry(mod, width=17)
            limit.place(x = 100, y = 35)
            limit_label = Label(mod, text="Monthly limit:")
            limit_label.place(x = 13, y = 35)

            def add_button():
                new_name = name.get()
                new_limit = limit.get()
                name.delete(0, END)
                limit.delete(0, END)
                if new_name in self.categories:
                    return 0
                self.add_category(new_name, new_limit)
                self.category_table(app)
                del_menu()


            add_button = Button(mod, text = "Add category", command=add_button)
            add_button.place(x = 110, y = 62)

            def del_menu():
                clicked = StringVar()
                clicked.set("Select category")
                menu = OptionMenu(mod, clicked, "—————————", *self.categories)
                menu.config(width=17)
                menu.place(x = 295, y = 50)
                def del_button():
                    del_name = clicked.get()
                    if del_name == 'Select category' or del_name == "—————————":
                        return 0
                    self.del_category(del_name)
                    self.category_table(app)
                    del_menu()
                del_button = Button(mod, text = "Delete category", command = del_button)
                del_button.place(x = 315, y = 15)
            del_menu()
        categories_button = Button(app, text = "Modify categories", height=2,width=15, command=modify_categories)
        categories_button.place(x = 14, y = 680)


class Recurring_payment:
    def __init__(self, category):
        self.category = category
        pay_list = con.cursor().execute(f"""SELECT * FROM PAYMENTS WHERE category == '{category}';""").fetchall()

    def add(self, name, amount, payday):
        con.cursor().execute(f"""INSERT INTO PAYMENTS(name, category, amount, payday)
        VALUES ('{name}', '{self.category}', {amount}, {payday});""")
        self.pay_list.append((name, f'{category}', amount, payday))

    def modify_budget(self, budget):
        for i in self.pay_list:
            payday = i[3]
            amount = i[2]
            name = i[0]
            add_day = dt.timedelta(days=1)
            it = budget.prev + add_day
            while it <= budget.curr:
                if ((it+add_day).day == 1 and payday > it.day) or it.day == payday:
                    budget.acc_balance += amount
                    budget.history.append((name, amount, it.strftime("%d-%m-%Y"), budget.acc_balance))
                it += add_day


class Transactions:
    def __init__(self, budget):
        self.budget = budget

    def modify_budget(self, name, category, amount):
        self.budget.acc_balance += amount
        self.budget.history = [((name, category, amount, self.budget.curr.strftime("%d-%m-%Y")))] + self.budget.history
        con.cursor().execute(f"""INSERT INTO HISTORY(name, category, amount, date)
        VALUES ('{name}', '{category}', {amount}, '{self.budget.curr.strftime("%d-%m-%Y")}');""")

    def transaction_button(self, app, cat):
        def trans():
            pay = Toplevel(app)
            pay.title("Add payment")
            pay.geometry("500x115")
            pay.maxsize(500, 115)
            pay.minsize(500, 115)
            name_label = Label(pay, text="Name:").place(x=16, y=20)
            name = Entry(pay, width=17)
            name.place(x = 60, y=20)
            amount_label = Label(pay, text="Amount:").place(x=3, y=50)
            amount = Entry(pay, width=17)
            amount.place(x = 60, y=50)


            sign = IntVar(pay, -1)
            Radiobutton(pay, text="outgoing –", font="TkDefaultFont 10", variable=sign, value=-1).place(x = 195, y = 20)
            Radiobutton(pay, text="incoming +", font="TkDefaultFont 10", variable=sign, value=1).place(x = 195, y = 50)

            clicked = StringVar()
            clicked.set("Select category")
            menu = OptionMenu(pay, clicked, "————————", *cat.categories)
            menu.config(width=17)
            menu.place(x = 320, y = 30)

            def add():
                new_name = name.get()
                new_amount = amount.get()
                new_sign = sign.get()
                new_category = clicked.get()
                name.delete(0, END)
                amount.delete(0, END)
                clicked.set("Select category")
                if new_name == None or new_amount == None or new_category == "————————" or new_category == "Select category":
                    return 0
                new_amount = new_sign * int(new_amount)
                self.modify_budget(new_name, new_category, new_amount)
                self.budget.history_table(app)
                cat.savings += new_amount
                for i in range (len(cat.actual)):
                    if cat.actual[i][0] == new_category:
                        new_amount = cat.actual[i][1] - new_amount
                        cat.actual = cat.actual[:i] + [(new_category, new_amount)] + cat.actual[i+1:]
                        break
                con.cursor().execute(f"""UPDATE BUDGET SET amount = {new_amount} WHERE name = '{new_category}';""")
                cat.category_table(app)

            add = Button(pay, text="Add payment", command=add).place(x=200, y=80)
        trans = Button(app, text="Payment", command=trans, height=2,width=15).place(x = 146, y = 680)


class BgtMng(Tk):
    def __init__(self):
        super().__init__()
        self.title("BgtMng")
        width=self.winfo_screenwidth()
        height= self.winfo_screenheight()
        self.geometry(f"{width}x{height}")
        history_label = Label(self, text= "—————————————history——————————", font="Helvetica 12 italic")
        history_label.place(x = -4, y = 68)
        category_label = Label(self, text= "–—————————————category—————————", font="Helvetica 12 italic")
        category_label.place(x = -10, y = 517)

if __name__ == "__main__":
    app = BgtMng()
    bgt = Budget()
    cat = Categories()
    pay = Transactions(bgt)
    bgt.budget_button(app)
    bgt.history_table(app)
    cat.categories_button(app)
    cat.category_table(app)
    pay.transaction_button(app, cat)

    app.mainloop()

    con.cursor().execute(f"""UPDATE DATES SET date = '{bgt.curr.strftime("%d-%m-%Y")}' WHERE name = 'previous_launch';""")
    con.commit()
    con.close()
