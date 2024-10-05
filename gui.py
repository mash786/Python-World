import sys
import sqlite3
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton,
                             QVBoxLayout, QHBoxLayout, QListWidget, QComboBox,
                             QGridLayout, QMessageBox)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


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

    def close_connection(self):
        self.connection.close()


class FinanceTrackerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.database = Database("finance_tracker.db")

    def init_ui(self):
        # Set Window properties
        self.setWindowTitle("Personal Finance Tracker")
        self.setStyleSheet("""
            QWidget {
                background-color: #F0F4F8;
            }
            QLabel {
                font-size: 16px;
                color: #333;
            }
            QLineEdit, QComboBox {
                font-size: 14px;
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 8px;
                background-color: #fff;
            }
            QPushButton {
                font-size: 14px;
                padding: 12px 20px;
                border-radius: 8px;
                background-color: #3498DB;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
            QListWidget {
                font-size: 14px;
                border: 1px solid #ccc;
                background-color: #fff;
                border-radius: 8px;
                padding: 10px;
            }
        """)

        # Main layout as a grid for balance and responsiveness
        main_layout = QVBoxLayout()

        # Title Label
        title_label = QLabel("Personal Finance Tracker", self)
        title_label.setFont(QFont('Arial', 26, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2C3E50; margin-bottom: 30px;")

        # Form layout for input fields
        form_layout = QGridLayout()
        form_layout.setHorizontalSpacing(20)

        # Create input fields
        self.expense_input = QLineEdit(self)
        self.amount_input = QLineEdit(self)
        self.category_input = QComboBox(self)
        self.category_input.addItems(["Food", "Transport", "Entertainment", "Other"])

        # Add to grid layout with labels
        form_layout.addWidget(QLabel("Expense Name:", self), 0, 0)
        form_layout.addWidget(self.expense_input, 0, 1)
        form_layout.addWidget(QLabel("Amount (Rs):", self), 1, 0)
        form_layout.addWidget(self.amount_input, 1, 1)
        form_layout.addWidget(QLabel("Category:", self), 2, 0)
        form_layout.addWidget(self.category_input, 2, 1)

        # Buttons layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)

        add_button = QPushButton("Add Expense", self)
        add_button.setStyleSheet("background-color: #27AE60;")
        add_button.clicked.connect(self.add_expense)

        delete_button = QPushButton("Delete Expense", self)
        delete_button.setStyleSheet("background-color: #E74C3C;")
        delete_button.clicked.connect(self.delete_expense)

        show_expenses_button = QPushButton("Show All Expenses", self)
        show_expenses_button.setStyleSheet("background-color: #F39C12;")
        show_expenses_button.clicked.connect(self.show_all_expenses)

        buttons_layout.addWidget(add_button)
        buttons_layout.addWidget(delete_button)
        buttons_layout.addWidget(show_expenses_button)

        # Expense List
        self.expense_list = QListWidget(self)

        # Add widgets to the main layout
        main_layout.addWidget(title_label)
        main_layout.addLayout(form_layout)
        main_layout.addLayout(buttons_layout)
        main_layout.addWidget(self.expense_list)

        main_layout.addStretch()

        self.setLayout(main_layout)
        self.setGeometry(300, 200, 800, 600)

    def add_expense(self):
        expense_name = self.expense_input.text()
        amount = self.amount_input.text()
        category = self.category_input.currentText()

        # Validation checks
        if not expense_name:
            self.show_popup("Error", "Expense name cannot be empty!")
        elif not amount.isdigit():
            self.show_popup("Error", "Amount must be a number!")
        else:
            self.database.add_expense(expense_name, float(amount), category)
            self.expense_list.addItem(f"{expense_name} - Rs {amount} ({category})")
            self.expense_input.clear()
            self.amount_input.clear()

    def delete_expense(self):
        selected_items = self.expense_list.selectedItems()
        if selected_items:
            for item in selected_items:
                expense_id = self.get_expense_id(item.text())
                if expense_id:
                    self.database.delete_expense(expense_id)
                self.expense_list.takeItem(self.expense_list.row(item))
        else:
            self.show_popup("Error", "No item selected to delete!")

    def get_expense_id(self, item_text):
        parts = item_text.split(" - ")
        if parts:
            return int(parts[0])  # ID is the first part
        return None

    def show_all_expenses(self):
        self.expense_list.clear()
        expenses = self.database.get_expenses()
        for expense in expenses:
            self.expense_list.addItem(f"{expense[0]}: {expense[1]} - Rs {expense[2]} - {expense[3]} ({expense[4]}/{expense[5]})")

    def show_popup(self, title, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def closeEvent(self, event):
        self.database.close_connection()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FinanceTrackerApp()
    window.show()
    sys.exit(app.exec_())
