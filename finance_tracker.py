import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime

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
        now = datetime.now()
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

    def view_all_expenses(self):
        query = "SELECT * FROM expenses"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def close_connection(self):
        self.connection.close()
