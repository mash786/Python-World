from pymongo import MongoClient
from datetime import datetime

class Database:
    def __init__(self, uri):
        self.client = MongoClient(uri)
        self.db = self.client['finance_tracker']
        self.collection = self.db['expenses']

    def add_expense(self, expense, amount, category):
        # Assume you have a method to get current month and year
        month = datetime.now().month
        year = datetime.now().year
        self.collection.insert_one({
            'expense': expense,
            'amount': amount,
            'category': category,
            'month': month,
            'year': year,
            'date': datetime.now()  # Store the date of the expense
        })

    def get_expenses(self):
        return list(self.collection.find())

    def delete_expense(self, expense_id):
        self.collection.delete_one({'_id': expense_id})

    def close_connection(self):
        self.client.close()

    def get_expenses_by_date(self, start_date, end_date):
        # Convert the dates to datetime objects
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())

        return list(self.collection.find({
            'date': {
                '$gte': start_datetime,
                '$lte': end_datetime
            }
        }))
