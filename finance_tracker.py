import sys
import sqlite3
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QListWidget, QMessageBox, QFormLayout)
from PyQt5.QtCore import Qt

class Database:
    def __init__(self, db_file):
        try:
            self.connection = sqlite3.connect(db_file)
            self.cursor = self.connection.cursor()
            self.create_expenses_table()
        except sqlite3.Error as e:
            self.show_error("Database Connection Error", f"Failed to connect to the database: {e}")

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

    def close_connection(self):
        self.connection.close()

    def show_error(self, title, message):
        error_message = QMessageBox()
        error_message.setIcon(QMessageBox.Critical)
        error_message.setWindowTitle(title)
        error_message.setText(message)
        error_message.exec_()

class ExpenseTracker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Expense Tracker")
        self.setGeometry(100, 100, 800, 600)
        
        self.database = Database("finance_tracker.db")
        
        self.initUI()
    
    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        self.expense_entry = QLineEdit()
        self.amount_entry = QLineEdit()
        self.category_entry = QLineEdit()
        
        form_layout.addRow(QLabel("Expense:"), self.expense_entry)
        form_layout.addRow(QLabel("Amount:"), self.amount_entry)
        form_layout.addRow(QLabel("Category:"), self.category_entry)
        
        layout.addLayout(form_layout)
        
        button_layout = QHBoxLayout()
        
        add_button = QPushButton("Add Expense")
        add_button.clicked.connect(self.add_expense)
        button_layout.addWidget(add_button)
        
        delete_button = QPushButton("Delete Selected Expense")
        delete_button.clicked.connect(self.delete_expense)
        button_layout.addWidget(delete_button)
        
        layout.addLayout(button_layout)

        self.expense_list = QListWidget()
        layout.addWidget(self.expense_list)
        
        central_widget.setLayout(layout)
        self.refresh_expense_list()
        
    def add_expense(self):
        expense = self.expense_entry.text()
        amount = self.amount_entry.text()
        category = self.category_entry.text()
        
        if not expense or not category or not amount.isnumeric():
            self.show_error("Invalid Input", "Please enter valid data for all fields.")
            return
        
        amount = float(amount)
        self.database.add_expense(expense, amount, category)
        self.refresh_expense_list()
        self.clear_fields()

    def delete_expense(self):
        selected_items = self.expense_list.selectedItems()
        if not selected_items:
            self.show_error("Delete Error", "Please select an expense to delete.")
            return
        
        for item in selected_items:
            expense_id = int(item.text().split(":")[0])
            self.database.delete_expense(expense_id)
        
        self.refresh_expense_list()
        
    def refresh_expense_list(self):
        self.expense_list.clear()
        expenses = self.database.get_expenses()
        for expense in expenses:
            self.expense_list.addItem(f"{expense[0]}: {expense[1]} - Rs {expense[2]} - {expense[3]} ({expense[4]}/{expense[5]})")

    def clear_fields(self):
        self.expense_entry.clear()
        self.amount_entry.clear()
        self.category_entry.clear()

    def show_error(self, title, message):
        error_message = QMessageBox()
        error_message.setIcon(QMessageBox.Critical)
        error_message.setWindowTitle(title)
        error_message.setText(message)
        error_message.exec_()

    def closeEvent(self, event):
        self.database.close_connection()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExpenseTracker()
    window.show()
    sys.exit(app.exec_())
