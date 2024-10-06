import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton,
                             QVBoxLayout, QHBoxLayout, QListWidget, QComboBox,
                             QGridLayout, QMessageBox, QCalendarWidget, QDialog)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from bson.objectid import ObjectId
from finance_tracker import Database  # Import the Database class from finance_tracker.py


class CalendarDialog(QDialog):
    def __init__(self, title):
        super().__init__()
        self.setWindowTitle(title)
        self.calendar = QCalendarWidget(self)
        self.calendar.setGridVisible(True)
        self.calendar.setStyleSheet("""
            QCalendarWidget {
                background-color: #fff;
                color: #333;
            }
        """)
        layout = QVBoxLayout()
        layout.addWidget(self.calendar)
        self.setLayout(layout)
        self.setFixedSize(300, 300)  # Set a fixed size for the dialog


class FinanceTrackerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.database = Database("mongodb://127.0.0.1:27017/finance_tracker")

    def init_ui(self):
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

        main_layout = QVBoxLayout()

        title_label = QLabel("Personal Finance Tracker", self)
        title_label.setFont(QFont('Arial', 26, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2C3E50; margin-bottom: 30px;")

        form_layout = QGridLayout()
        form_layout.setHorizontalSpacing(20)

        self.expense_input = QLineEdit(self)
        self.amount_input = QLineEdit(self)
        self.category_input = QComboBox(self)
        self.category_input.addItems(["Food", "Transport", "Entertainment", "Other"])

        form_layout.addWidget(QLabel("Expense Name:", self), 0, 0)
        form_layout.addWidget(self.expense_input, 0, 1)
        form_layout.addWidget(QLabel("Amount (Rs):", self), 1, 0)
        form_layout.addWidget(self.amount_input, 1, 1)
        form_layout.addWidget(QLabel("Category:", self), 2, 0)
        form_layout.addWidget(self.category_input, 2, 1)

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

        search_by_date_button = QPushButton("Search by Dates", self)
        search_by_date_button.setStyleSheet("background-color: #8E44AD;")
        search_by_date_button.clicked.connect(self.open_calendar)

        buttons_layout.addWidget(add_button)
        buttons_layout.addWidget(delete_button)
        buttons_layout.addWidget(show_expenses_button)
        buttons_layout.addWidget(search_by_date_button)

        # Expense List
        self.expense_list = QListWidget(self)

        # Main layout adjustments
        main_layout.addWidget(title_label)
        main_layout.addLayout(form_layout)
        main_layout.addLayout(buttons_layout)
        main_layout.addWidget(self.expense_list)

        main_layout.addStretch()

        self.setLayout(main_layout)
        self.setGeometry(300, 200, 800, 600)

    def open_calendar(self):
        self.start_calendar = CalendarDialog("Select Start Date")
        self.start_calendar.calendar.clicked.connect(self.set_start_date)
        self.start_calendar.exec_()

    def set_start_date(self, date):
        self.start_date = date
        self.start_calendar.close()
        self.end_calendar = CalendarDialog("Select End Date")
        self.end_calendar.calendar.clicked.connect(self.set_end_date)
        self.end_calendar.exec_()

    def set_end_date(self, date):
        self.end_date = date
        self.end_calendar.close()
        self.search_by_date()

    def add_expense(self):
        expense_name = self.expense_input.text()
        amount = self.amount_input.text()
        category = self.category_input.currentText()

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
            return ObjectId(parts[0])  # ID is the first part
        return None

    def show_all_expenses(self):
        self.expense_list.clear()
        expenses = self.database.get_expenses()
        for expense in expenses:
            self.expense_list.addItem(f"{expense['expense']} - Rs {expense['amount']} - {expense['category']} ({expense['month']}/{expense['year']})")

    def search_by_date(self):
        expenses = self.database.get_expenses_by_date(self.start_date.toPyDate(), self.end_date.toPyDate())

        self.expense_list.clear()
        total_expense = 0.0  # Initialize total expense

        for expense in expenses:
            self.expense_list.addItem(f"{expense['expense']} - Rs {expense['amount']} - {expense['category']} ({expense['month']}/{expense['year']})")
            total_expense += expense['amount']  # Accumulate total expense

        # Show total expense in a popup or status bar
        if expenses:
            self.show_popup("Total Expense", f"Total Expense from {self.start_date.toPyDate()} to {self.end_date.toPyDate()} is Rs {total_expense:.2f}")
        else:
            self.show_popup("Info", "No expenses found for the selected date range.")

    def show_popup(self, title, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
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
