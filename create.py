import sqlite3
import random
import string
import datetime
import os
env = os.path.dirname(os.path.abspath(__file__))

# Check if the database file exists, and if so, delete it
if os.path.exists(f'{env}/bank_database.db'):
    os.remove(f'{env}/bank_database.db')

# Connect to the database (it will be created if it doesn't exist)
conn = sqlite3.connect(f'{env}/bank_database.db')
c = conn.cursor()

# Create User table
c.execute('''CREATE TABLE IF NOT EXISTS User
             (UserID INTEGER PRIMARY KEY,
             FirstName TEXT,
             LastName TEXT,
             SSN TEXT,
             Email TEXT,
             Phone TEXT)''')

# Create Account table
c.execute('''CREATE TABLE IF NOT EXISTS Account
             (AccountID INTEGER PRIMARY KEY,
             CustomerID INTEGER,
             BranchID INTEGER,
             AccountType TEXT,
             Balance REAL,
             DateOpened TEXT,
             FOREIGN KEY (CustomerID) REFERENCES User(UserID),
             FOREIGN KEY (BranchID) REFERENCES Branch(BranchID))''')

# Create Transaction table
c.execute('''CREATE TABLE IF NOT EXISTS "Transaction"
             (TransactionID INTEGER PRIMARY KEY,
             AccountID INTEGER,
             Type TEXT,
             Amount REAL,
             Date TEXT,
             FOREIGN KEY (AccountID) REFERENCES Account(AccountID))''')

# Create Loan table
c.execute('''CREATE TABLE IF NOT EXISTS Loan
             (LoanID INTEGER PRIMARY KEY,
             CustomerID INTEGER,
             AmountDue REAL,
             InterestRate REAL,
             StartDate TEXT,
             EndDate TEXT,
             FOREIGN KEY (CustomerID) REFERENCES User(UserID))''')

# Create Branch table
c.execute('''CREATE TABLE IF NOT EXISTS Branch
             (BranchID INTEGER PRIMARY KEY,
             BranchName TEXT,
             State TEXT,
             Address TEXT,
             ZipCode TEXT,
             UserID INTEGER,
             FOREIGN KEY (UserID) REFERENCES User(UserID))''')

# Generate random data
first_names = ['John', 'Emma', 'Michael', 'Olivia', 'William', 'Ava', 'James', 'Isabella', 'Benjamin', 'Sophia']
last_names = ['Smith', 'Johnson', 'Brown', 'Taylor', 'Miller', 'Anderson', 'Wilson', 'Davis', 'Clark', 'hall']
states = ['CA', 'NY', 'TX', 'FL', 'IL', 'PA', 'OH', 'GA', 'NC', 'MI']
account_types = ['Checking', 'Savings']
transaction_types = ['Deposit', 'Withdrawal']

# Generate random users
for i in range(20):
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    ssn = ''.join(random.choices(string.digits, k=9))
    email = f"{first_name.lower()}.{last_name.lower()}@example.com"
    phone = ''.join(random.choices(string.digits, k=10))
    c.execute("INSERT INTO User (FirstName, LastName, SSN, Email, Phone) VALUES (?, ?, ?, ?, ?)",
              (first_name, last_name, ssn, email, phone))

# Generate random branches
for i in range(5):
    branch_name = f"Branch {i+1}"
    state = random.choice(states)
    address = f"{random.randint(100, 999)} {random.choice(['Main', 'Oak', 'Elm', 'Maple'])} St"
    zip_code = ''.join(random.choices(string.digits, k=5))
    user_id = random.randint(1, 20)
    c.execute("INSERT INTO Branch (BranchName, State, Address, ZipCode, UserID) VALUES (?, ?, ?, ?, ?)",
              (branch_name, state, address, zip_code, user_id))

# Generate random accounts
for i in range(50):
    customer_id = random.randint(1, 20)
    branch_id = None
    if random.random() < 0.2:  # 20% chance of assigning to a random branch
        branch_id = random.randint(1, 5)
    account_type = random.choice(account_types)
    balance = round(random.uniform(1000, 100000), 2)
    date_opened = datetime.date(random.randint(2020, 2023), random.randint(1, 12), random.randint(1, 28)).isoformat()
    c.execute("INSERT INTO Account (CustomerID, BranchID, AccountType, Balance, DateOpened) VALUES (?, ?, ?, ?, ?)",
              (customer_id, branch_id, account_type, balance, date_opened))

# Generate random transactions
for i in range(400):
    account_id = random.randint(1, 50)
    transaction_type = random.choice(transaction_types)
    amount = round(random.uniform(100, 5000), 2)
    date = datetime.date(random.randint(2020, 2023), random.randint(1, 12), random.randint(1, 28)).isoformat()
    c.execute("INSERT INTO \"Transaction\" (AccountID, Type, Amount, Date) VALUES (?, ?, ?, ?)",
              (account_id, transaction_type, amount, date))

# Generate random loans
for i in range(10):
    customer_id = random.randint(1, 20)
    amount_due = round(random.uniform(5000, 50000), 2)
    interest_rate = round(random.uniform(0.05, 0.15), 2)
    start_date = datetime.date(random.randint(2020, 2023), random.randint(1, 12), random.randint(1, 28)).isoformat()
    end_date = (datetime.date.fromisoformat(start_date) + datetime.timedelta(days=365)).isoformat()
    c.execute("INSERT INTO Loan (CustomerID, AmountDue, InterestRate, StartDate, EndDate) VALUES (?, ?, ?, ?, ?)",
              (customer_id, amount_due, interest_rate, start_date, end_date))



# Commit the changes and close the connection
conn.commit()
conn.close()


print("Created Database")