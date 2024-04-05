import sqlite3
import os
from datetime import date

env = os.path.dirname(os.path.abspath(__file__))
# Connect to the database
conn = sqlite3.connect(f'{env}/bank_database.db')
c = conn.cursor()

# Function to create a new account
def create_account():
    first_name = input("Enter customer's first name: ")
    last_name = input("Enter customer's last name: ")
    
    # Find the user based on the provided first and last name
    c.execute("SELECT UserID FROM User WHERE FirstName = ? AND LastName = ?", (first_name, last_name))
    result = c.fetchone()
    
    if result:
        customer_id = result[0]
        
        print("Account Types:")
        print("1. Savings")
        print("2. Checking")
        account_type_choice = input("Enter account type choice (1 or 2): ")
        
        if account_type_choice == '1':
            account_type = 'Savings'
        elif account_type_choice == '2':
            account_type = 'Checking'
        else:
            print("Invalid account type choice.")
            return
        
        initial_balance = float(input("Enter initial balance: "))
        
        # Get today's date
        today = date.today()
        date_opened = today.strftime("%Y-%m-%d")
        
        # Insert the new account into the database
        c.execute("INSERT INTO Account (CustomerID, AccountType, Balance, DateOpened) VALUES (?, ?, ?, ?)", (customer_id, account_type, initial_balance, date_opened))
        conn.commit()
        
        # Get the automatically generated account ID
        account_id = c.lastrowid
        
        print("\nAccount created successfully.")
        print(f"Account ID: {account_id}")
        print(f"Customer: {first_name} {last_name}")
        print(f"Account Type: {account_type}")
        print(f"Initial Balance: {initial_balance}")
        print(f"Date Opened: {date_opened}")
    
    else:
        print("Customer not found.")

# Function to delete an account
def delete_account():
    account_id = int(input("Enter account ID: "))

    # Check if the account exists and has a balance of 0
    c.execute("SELECT Balance FROM Account WHERE AccountID = ?", (account_id,))
    result = c.fetchone()

    if result:
        balance = result[0]

        if balance == 0:
            # Delete the account if it has a balance of 0
            c.execute("DELETE FROM Account WHERE AccountID = ?", (account_id,))
            conn.commit()
            print("\nAccount deleted successfully.")
        else:
            print("Cannot delete account. The account balance is not 0.")
    else:
        print("Account not found.")

# Function to add a deposit
def add_deposit():
    account_id = int(input("Enter account ID: "))
    amount = float(input("Enter deposit amount: "))

    if amount <= 0:
        print("Deposit amount must be a positive value.")
        return

    # Retrieve the current balance before the deposit
    c.execute("SELECT Balance FROM Account WHERE AccountID = ?", (account_id,))
    result = c.fetchone()

    if result:
        current_balance = result[0]
        print(f"Current balance: {current_balance}")

        # Update the balance by adding the deposit amount
        c.execute("UPDATE Account SET Balance = Balance + ? WHERE AccountID = ?", (amount, account_id))
        conn.commit()

        # Retrieve the updated balance after the deposit
        c.execute("SELECT Balance FROM Account WHERE AccountID = ?", (account_id,))
        updated_balance = c.fetchone()[0]

        print("\nDeposit added successfully.")
        print(f"Previous balance: {current_balance}")
        print(f"Deposit amount: {amount}")
        print(f"Updated balance: {updated_balance}")
    else:
        print("Account not found.")

# Function to find top users by total account balance
def find_top_users():
    num_top_users = int(input("Enter the number of top users you want to see: "))
    c.execute('''SELECT u.FirstName, u.LastName, SUM(a.Balance) AS TotalBalance
                 FROM User u
                 JOIN Account a ON u.UserID = a.CustomerID
                 GROUP BY u.UserID
                 ORDER BY TotalBalance DESC
                 LIMIT ?''', (num_top_users,))
    results = c.fetchall()
    print(f"\nTop {num_top_users} users by total account balance:")
    for row in results:
        print(f"Name: {row[0]} {row[1]}, Total Balance: {round(row[2], 2)}")

# Function to find accounts with more than a specified number of transactions in a specific month
def find_accounts_with_transactions():
    start_date = input("Enter start date (YYYY-MM-DD): ")
    transaction_limit = int(input("Enter the transaction limit: "))
    c.execute('''SELECT u.FirstName, u.LastName, NumberOfTransactions
                 FROM (
                     SELECT a.CustomerID, COUNT(t.TransactionID) AS NumberOfTransactions,
                            ROW_NUMBER() OVER (ORDER BY COUNT(t.TransactionID) DESC) AS RowNum
                     FROM "Transaction" t
                     JOIN Account a ON t.AccountID = a.AccountID
                     WHERE t.Date >= ?
                     GROUP BY a.CustomerID
                     HAVING COUNT(t.TransactionID) > ?
                 ) AS subquery
                 JOIN User u ON subquery.CustomerID = u.UserID
                 WHERE RowNum <= 10''', (start_date, transaction_limit))
    results = c.fetchall()
    print(f"\nUsers with more than {transaction_limit} transactions from {start_date} to present:")
    for row in results:
        print(f"Name: {row[0]} {row[1]}, Number of Transactions: {row[2]}")

# Function to find users with above average account balances
def find_users_above_average_balance():
    num_users = int(input("Enter the number of users you want to see: "))
    c.execute('''SELECT u.FirstName, u.LastName, a.Balance
                 FROM User u
                 JOIN Account a ON u.UserID = a.CustomerID
                 WHERE a.Balance > (SELECT AVG(Balance) FROM Account)
                 ORDER BY a.Balance DESC
                 LIMIT ?''', (num_users,))
    results = c.fetchall()
    print(f"\nTop {num_users} users with above average account balances:")
    for row in results:
        print(f"Name: {row[0]} {row[1]}, Balance: {row[2]}")


def send_money_to_branch_accounts():
    branch_id = int(input("Enter branch ID: "))
    amount = float(input("Enter amount to send: "))

    # Retrieve all account IDs associated with the specified branch
    c.execute("SELECT AccountID FROM Account WHERE BranchID = ?", (branch_id,))
    account_ids = c.fetchall()

    if account_ids:
        # Update the balance of each account in the branch
        c.executemany("UPDATE Account SET Balance = Balance + ? WHERE AccountID = ?", [(amount, account_id[0]) for account_id in account_ids])
        conn.commit()

        print(f"\nSent {amount} to all accounts in branch {branch_id} successfully.")
    else:
        print("No accounts found in the specified branch.")

def remove_account_from_branch():
    account_id = int(input("Enter account ID: "))

    # Update the BranchID to NULL for the specified account
    c.execute("UPDATE Account SET BranchID = NULL WHERE AccountID = ?", (account_id,))
    conn.commit()

    print(f"\nRemoved account {account_id} from its branch successfully.")



def transfer_money():
    source_account_id = int(input("Enter source account ID: "))
    target_account_id = int(input("Enter target account ID: "))
    amount = float(input("Enter transfer amount: "))

    if amount <= 0:
        print("Transfer amount must be a positive value.")
        return

    # Retrieve the current balance of the source account
    c.execute("SELECT Balance FROM Account WHERE AccountID = ?", (source_account_id,))
    result = c.fetchone()

    if result:
        source_balance = result[0]

        if source_balance >= amount:
            # Update the balance of the source account
            c.execute("UPDATE Account SET Balance = Balance - ? WHERE AccountID = ?", (amount, source_account_id))

            # Update the balance of the target account
            c.execute("UPDATE Account SET Balance = Balance + ? WHERE AccountID = ?", (amount, target_account_id))

            # Record the transaction in the "Transaction" table for the source account
            c.execute("INSERT INTO \"Transaction\" (AccountID, Type, Amount, Date) VALUES (?, ?, ?, date('now'))",
                      (source_account_id, 'Withdrawal', -amount))

            # Record the transaction in the "Transaction" table for the target account
            c.execute("INSERT INTO \"Transaction\" (AccountID, Type, Amount, Date) VALUES (?, ?, ?, date('now'))",
                      (target_account_id, 'Deposit', amount))

            conn.commit()

            print("\nMoney transfer successful.")
        else:
            print("Insufficient balance in the source account.")
    else:
        print("Source account not found.")

# Main program loop
while True:
    print("\n--- Bank Database Management ---")
    print("1. Create a new account")
    print("2. Delete an account")
    print("3. Add a deposit")
    print("4. Find top users by total account balance")
    print("5. Find accounts with the most transactions from a specific month")
    print("6. Find users with above average account balances")
    print("7. Send money to all accounts in a branch")
    print("8. Remove an account from its branch")
    print("9. Transfer money between accounts")
    print("10. Exit")

    choice = input("Enter your choice (1-10): ")

    if choice == '1':
        create_account()
    elif choice == '2':
        delete_account()
    elif choice == '3':
        add_deposit()
    elif choice == '4':
        find_top_users()
    elif choice == '5':
        find_accounts_with_transactions()
    elif choice == '6':
        find_users_above_average_balance()
    elif choice == '7':
        send_money_to_branch_accounts()
    elif choice == '8':
        remove_account_from_branch()
    elif choice == '9':
        transfer_money()
    elif choice == '10':
        break
    else:
        print("Invalid choice. Please try again.")
        
# Close the database connection
conn.close()