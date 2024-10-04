import datetime
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk


class GUI:
    def __init__(self):
        self.tracker = Tracker("finance_tracker.db")

    def create_widgets(self):
        self.window = tk.Tk()
        self.window.title("Personal Finance Management")

        # Load and display the background image
        background_image = Image.open("background.jpg")
        background_photo = ImageTk.PhotoImage(background_image)
        background_label = tk.Label(self.window, image=background_photo)
        background_label.image = background_photo  # Keep a reference to the image
        background_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Rest of the code remains the same...


        # Create and configure your GUI widgets here
        style = ttk.Style()
        style.configure("TLabel", background="#f2f2f2", font=("Arial", 12))
        style.configure("TButton", font=("Arial", 12))
        style.configure("TEntry", font=("Arial", 12))

        self.expense_label = ttk.Label(self.window, text="Expense:")
        self.expense_label.grid(row=0, column=0, padx=10, pady=5)
        self.expense_entry = ttk.Entry(self.window)
        self.expense_entry.grid(row=0, column=1, padx=10, pady=5)

        self.amount_label = ttk.Label(self.window, text="Amount:")
        self.amount_label.grid(row=1, column=0, padx=10, pady=5)
        self.amount_entry = ttk.Entry(self.window)
        self.amount_entry.grid(row=1, column=1, padx=10, pady=5)

        self.category_label = ttk.Label(self.window, text="Category:")
        self.category_label.grid(row=2, column=0, padx=10, pady=5)
        self.category_entry = ttk.Entry(self.window)
        self.category_entry.grid(row=2, column=1, padx=10, pady=5)

        self.add_button = ttk.Button(self.window, text="Add Expense", command=self.add_expense)
        self.add_button.grid(row=3, column=0, columnspan=2, padx=10, pady=5)

        self.expense_listbox = tk.Listbox(self.window, width=50, font=("Arial", 12))
        self.expense_listbox.grid(row=4, column=0, columnspan=2, padx=10, pady=5)

        self.delete_button = ttk.Button(self.window, text="Delete Expense", command=self.delete_expense)
        self.delete_button.grid(row=5, column=0, columnspan=2, padx=10, pady=5)

        self.filter_label = ttk.Label(self.window, text="Filter (Month/Year):")
        self.filter_label.grid(row=6, column=0, padx=10, pady=5)
        self.filter_entry = ttk.Entry(self.window)
        self.filter_entry.grid(row=6, column=1, padx=10, pady=5)
        self.filter_button = ttk.Button(self.window, text="Filter", command=self.filter_expenses)
        self.filter_button.grid(row=7, column=0, columnspan=2, padx=10, pady=5)

        self.view_all_button = ttk.Button(self.window, text="View All", command=self.view_all_expenses)
        self.view_all_button.grid(row=8, column=0, columnspan=2, padx=10, pady=5)

        self.refresh_button = ttk.Button(self.window, text="Refresh", command=self.clear_all_fields)
        self.refresh_button.grid(row=9, column=0, columnspan=2, padx=10, pady=5)

    # Rest of the code remains the same...



    def add_expense(self):
        # Retrieve expense, amount, and category from the entry fields
        expense = self.expense_entry.get()
        amount = float(self.amount_entry.get())
        category = self.category_entry.get()

        # Add the expense using the Tracker class
        self.tracker.add_expense(expense, amount, category)

        # Refresh the expense list and clear the entry fields
        self.refresh_expense_list()
        self.clear_entry_fields()

    def delete_expense(self):
        selected_index = self.expense_listbox.curselection()
        if selected_index:
            expense_info = self.expense_listbox.get(selected_index)
            expense_id = int(expense_info.split(":")[0])

            # Delete the expense using the Tracker class
            self.tracker.delete_expense(expense_id)

            # Refresh the expense list
            self.refresh_expense_list()
        else:
            messagebox.showinfo("Delete Expense", "Please select an expense to delete.")

    def filter_expenses(self):
        filter_value = self.filter_entry.get()
        if filter_value:
            try:
                month, year = map(int, filter_value.split("/"))
                expenses = self.tracker.get_expenses_by_month_year(month, year)
                self.display_expenses(expenses)
            except ValueError:
                messagebox.showinfo("Filter Expenses", "Invalid filter value. Please provide month/year (e.g., 5/2023).")
        else:
            messagebox.showinfo("Filter Expenses", "Please provide a filter value.")

    def view_all_expenses(self):
        # Refresh the expense list to display all expenses
        self.refresh_expense_list()

    def refresh_expense_list(self):
        # Clear the expense listbox
        self.expense_listbox.delete(0, tk.END)

        expenses = self.tracker.get_expenses()
        self.display_expenses(expenses)

    def display_expenses(self, expenses):
        for expense in expenses:
            expense_info = f"{expense[0]}:  Expenses {expense[1]} - Rs {expense[2]} - {expense[3]} ({expense[4]}/{expense[5]})"
            self.expense_listbox.insert(tk.END, expense_info)

    def clear_entry_fields(self):
        self.expense_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)
        self.filter_entry.delete(0, tk.END)

    def clear_all_fields(self):
        self.clear_entry_fields()
        self.expense_listbox.delete(0, tk.END)

    def run(self):
        self.create_widgets()
        self.window.mainloop()


class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()
        self.create_expenses_table()

    def create_expenses_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            expense TEXT,
            amount REAL,
            category TEXT,
            month INTEGER,
            year INTEGER
        )
        """
        self.cursor.execute(query)
        self.connection.commit()

    def add_expense(self, expense, amount, category):
        now = datetime.datetime.now()
        month = now.month
        year = now.year
        query = "INSERT INTO expenses (expense, amount, category, month, year) VALUES (?, ?, ?, ?, ?)"
        self.cursor.execute(query, (expense, amount, category, month, year))
        self.connection.commit()

    def delete_expense(self, expense_id):
        query = "DELETE FROM expenses WHERE id = ?"
        self.cursor.execute(query, (expense_id,))
        self.connection.commit()

    def get_expenses(self):
        query = "SELECT * FROM expenses"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_expenses_by_month_year(self, month, year):
        query = "SELECT * FROM expenses WHERE month = ? AND year = ?"
        self.cursor.execute(query, (month, year))
        return self.cursor.fetchall()

    def close_connection(self):
        self.connection.close()


class Tracker:
    def __init__(self, db_file):
        self.database = Database(db_file)

    def add_expense(self, expense, amount, category):
        self.database.add_expense(expense, amount, category)

    def delete_expense(self, expense_id):
        self.database.delete_expense(expense_id)

    def get_expenses(self):
        return self.database.get_expenses()

    def get_expenses_by_month_year(self, month, year):
        return self.database.get_expenses_by_month_year(month, year)

    def close_connection(self):
        self.database.close_connection()


if __name__ == "__main__":
    gui = GUI()
    gui.run()

