import sqlite3
import datetime
import os
env = os.path.dirname(os.path.abspath(__file__))

# Connect to the database (it will be created if it doesn't exist)
conn = sqlite3.connect(f'{env}/bank_database.db')
c = conn.cursor()

# Function to create a new account
def create_account(customer_id, account_type, initial_balance, date_opened):
    c.execute("INSERT INTO Account (CustomerID, AccountType, Balance, DateOpened) VALUES (?, ?, ?, ?)",
              (customer_id, account_type, initial_balance, date_opened))
    conn.commit()
    print("\nAccount created successfully.")

# Function to delete an account
def delete_account(account_id):
    c.execute("DELETE FROM Account WHERE AccountID = ? AND Balance = 0", (account_id,))
    conn.commit()
    print("\nAccount deleted successfully.")

# Function to add a deposit
def add_deposit(account_id, amount):
    c.execute("UPDATE Account SET Balance = Balance + ? WHERE AccountID = ?", (amount, account_id))
    conn.commit()
    print("\nDeposit added successfully.")

# Function to find top 5 users by total account balance
def find_top_users():
    c.execute('''SELECT u.FirstName, u.LastName, SUM(a.Balance) AS TotalBalance
                 FROM User u
                 JOIN Account a ON u.UserID = a.CustomerID
                 GROUP BY u.UserID
                 ORDER BY TotalBalance DESC
                 LIMIT 5''')
    results = c.fetchall()
    print("\nTop 5 users by total account balance:")
    for row in results:
        print(f"Name: {row[0]} {row[1]}, Total Balance: {round(row[2], 2)}")

# Function to find accounts with more than 3 transactions in a specific month
def find_accounts_with_transactions(start_date):
    c.execute('''SELECT u.FirstName, u.LastName, NumberOfTransactions
                 FROM (
                     SELECT a.CustomerID, COUNT(t.TransactionID) AS NumberOfTransactions,
                            ROW_NUMBER() OVER (ORDER BY COUNT(t.TransactionID) DESC) AS RowNum
                     FROM "Transaction" t
                     JOIN Account a ON t.AccountID = a.AccountID
                     WHERE t.Date >= ?
                     GROUP BY a.CustomerID
                     HAVING COUNT(t.TransactionID) > 3
                 ) AS subquery
                 JOIN User u ON subquery.CustomerID = u.UserID
                 WHERE RowNum <= 10''', (start_date,))
    results = c.fetchall()
    print(f"\nUsers with more than 3 transactions from {start_date} to present:")
    for row in results:
        print(f"Name: {row[0]} {row[1]}, Number of Transactions: {row[2]}")

# Function to find users with above average account balances
def find_users_above_average_balance():
    c.execute('''SELECT u.FirstName, u.LastName, a.Balance
                 FROM User u
                 JOIN Account a ON u.UserID = a.CustomerID
                 WHERE a.Balance > (SELECT AVG(Balance) FROM Account)
                 ORDER BY a.Balance DESC''')
    results = c.fetchall()
    print("\nUsers with above average account balances:")
    for row in results:
        print(f"Name: {row[0]} {row[1]}, Balance: {row[2]}")


# Example usage
create_account(1, 'Checking', 0.00, '2024-02-26')
delete_account(2)
add_deposit(3, 100.00)
find_top_users()
find_accounts_with_transactions('2023-01-01')
find_users_above_average_balance()

# Close the database connection
conn.close()