# Bank System using Python Keywords

# Import necessary modules
import math  # ' is used to include external modules for mathematical operations yeah

# Defining a simple BankAccount class
class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner  # Account owner's name
        self.balance = balance  # Initial balance

    def deposit(self, amount):
        assert amount > 0, "Deposit amount must be greater than zero"  # assert ensures valid deposit
        self.balance += amount
        return self.balance

    def withdraw(self, amount):
        try:  # try block to catch errors
            assert amount > 0, "Withdrawal amount must be greater than zero"
            if amount > self.balance:
                raise ValueError("Insufficient funds")  # raise triggers an error
            self.balance -= amount
        except AssertionError as e:  # except handles assertion errors
            print(e)
        except ValueError as e:
            print(e)
        finally:  # 'finally' ensures execution of this block
            return self.balance

# Global variable to track bank's total balance
global total_bank_balance

total_bank_balance = 0  # global keyword to modify global variable

def update_total_balance(account):
    global total_bank_balance
    total_bank_balance += account.balance

# Function to check account status
def check_account_status(account):
    if account.balance is None:  # is checks if balance is None
        return "Account balance is unavailable"
    elif account.balance == 0:
        return False  # False represents empty account
    else:
        return True  # 'True' represents active account

# Lambda function to calculate interest
calculate_interest = lambda balance, rate: balance * rate  # lambda defines an anonymous function

# Function demonstrating for loop and 'continue' statement
def display_transactions(transactions):
    for transaction in transactions:
        if transaction["amount"] <= 0:
            continue  # 'continue' skips invalid transactions
        print(transaction["type"], "-", transaction["amount"])

# Function demonstrating while'loop and 'break' statement
def countdown(n):
    while n > 0:  # Runs while n is greater than 0
        print(n, end=" ")
        n -= 1
        if n == 2:
            break  # break exits the loop when n equals 2
    print()

# Using with statement for file handling
def save_balance(account):
    with open("balance.txt", "w") as file:  # with ensures the file closes properly
        file.write(f"{account.owner}: {account.balance}")

# Demonstrating 'nonlocal' keyword
def outer_function():
    account_type = "Savings"
    
    def inner_function():
        nonlocal account_type  # nonlocal modifies variable from outer function
        account_type = "Current"
        print("Inner Account Type:", account_type)
    
    inner_function()
    print("Outer Account Type:", account_type)

# Generator function using yield
def generate_transactions():
    transactions = [100, -50, 200]
    for amount in transactions:
        yield amount  # yield returns values one at a time

# Main Execution
if __name__ == "__main__":
    account = BankAccount("John Doe", 1000)
    print("Deposit:", account.deposit(500))
    print("Withdraw:", account.withdraw(200))
    print("Account Status:", check_account_status(account))
    print("Interest on Balance:", calculate_interest(account.balance, 0.05))
    print("Transactions:")
    display_transactions([{ "type": "Deposit", "amount": 500 }, { "type": "Withdraw", "amount": -200 }])
    print("Countdown Example:")
    countdown(5)
    save_balance(account)
    outer_function()
    print("Generated Transactions:")
    for transaction in generate_transactions():
        print(transaction, end=" ")
    print()

    try:
        raise ValueError("Bank system error")
    except ValueError as e:
        print("Caught Exception:", e)
