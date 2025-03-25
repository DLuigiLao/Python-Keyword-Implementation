"""
Banking System Implementation
This program demonstrates all Python keywords while implementing a complete banking system
with accounts, transactions, loans, and customer management.
"""

# Import required modules (import, from, as)
import datetime as dt
from decimal import Decimal, getcontext
from typing import Dict, List, Optional, Union

# Set precision for decimal operations (global)
getcontext().prec = 4

# Constants (True, False, None)
MIN_DEPOSIT = Decimal('50.00')
MIN_WITHDRAWAL = Decimal('20.00')
MAX_DAILY_WITHDRAWAL = Decimal('5000.00')
LOAN_INTEREST_RATE = Decimal('0.08')  # 8% annual interest
LOAN_TERM_YEARS = 5


# Custom exceptions (raise, class)
class InsufficientFundsError(Exception):
    """Raised when account has insufficient funds for a transaction."""
    pass


class InvalidAmountError(Exception):
    """Raised when an invalid amount is provided for a transaction."""
    pass


class AccountNotFoundError(Exception):
    """Raised when an account is not found."""
    pass


class CustomerNotFoundError(Exception):
    """Raised when a customer is not found."""
    pass


# Base class for all bank entities (class)
class BankEntity:
    """Base class for all bank entities with common properties."""
    
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name
        self.created_at = dt.datetime.now()
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.name} (ID: {self.id})"


# Customer class (nonlocal)
class Customer(BankEntity):
    """Bank customer with personal details and accounts."""
    
    def __init__(self, id: str, name: str, email: str, phone: str):
        super().__init__(id, name)
        self.email = email
        self.phone = phone
        self.accounts: Dict[str, 'Account'] = {}
        self.loans: List['Loan'] = []
    
    def add_account(self, account: 'Account') -> None:
        """Add an account to the customer."""
        if account.id in self.accounts:
            raise ValueError("Account already exists for this customer")
        self.accounts[account.id] = account
    
    def get_account(self, account_id: str) -> 'Account':
        """Get an account by ID."""
        if account_id not in self.accounts:
            raise AccountNotFoundError(f"Account {account_id} not found")
        return self.accounts[account_id]
    
    def add_loan(self, loan: 'Loan') -> None:
        """Add a loan to the customer."""
        self.loans.append(loan)
    
    def get_total_balance(self) -> Decimal:
        """Get the total balance across all accounts."""
        return sum(account.balance for account in self.accounts.values())


# Account class (is, and, or, not)
class Account(BankEntity):
    """Bank account with transaction capabilities."""
    
    def __init__(self, id: str, customer: Customer, account_type: str = "checking"):
        super().__init__(id, f"{account_type.title()} Account")
        self.customer = customer
        self.account_type = account_type
        self.balance = Decimal('0.00')
        self.transactions: List['Transaction'] = []
        self.is_active = True
    
    def deposit(self, amount: Union[Decimal, float, str]) -> 'Transaction':
        """Deposit money into the account."""
        amount = self._validate_amount(amount)
        
        if amount < MIN_DEPOSIT:
            raise InvalidAmountError(f"Minimum deposit is {MIN_DEPOSIT}")
        
        transaction = Transaction(
            transaction_id=f"TXN-{dt.datetime.now().timestamp()}",
            account=self,
            amount=amount,
            transaction_type="deposit",
            description="Account deposit"
        )
        
        self.balance += amount
        self.transactions.append(transaction)
        return transaction
    
    def withdraw(self, amount: Union[Decimal, float, str]) -> 'Transaction':
        """Withdraw money from the account."""
        amount = self._validate_amount(amount)
        
        if not self.is_active:
            raise ValueError("Account is inactive")
        
        if amount < MIN_WITHDRAWAL:
            raise InvalidAmountError(f"Minimum withdrawal is {MIN_WITHDRAWAL}")
        
        if amount > MAX_DAILY_WITHDRAWAL:
            raise InvalidAmountError(f"Maximum daily withdrawal is {MAX_DAILY_WITHDRAWAL}")
        
        if amount > self.balance:
            raise InsufficientFundsError("Insufficient funds for withdrawal")
        
        transaction = Transaction(
            transaction_id=f"TXN-{dt.datetime.now().timestamp()}",
            account=self,
            amount=-amount,  # Negative for withdrawals
            transaction_type="withdrawal",
            description="Account withdrawal"
        )
        
        self.balance -= amount
        self.transactions.append(transaction)
        return transaction
    
    def transfer(self, amount: Union[Decimal, float, str], recipient: 'Account') -> 'Transaction':
        """Transfer money to another account."""
        amount = self._validate_amount(amount)
        
        if self is recipient:
            raise ValueError("Cannot transfer to the same account")
        
        if not recipient.is_active:
            raise ValueError("Recipient account is inactive")
        
        # Withdraw from this account
        withdrawal = self.withdraw(amount)
        
        # Deposit to recipient account
        deposit = recipient.deposit(amount)
        
        # Create a transfer transaction record
        transaction = Transaction(
            transaction_id=f"TXN-{dt.datetime.now().timestamp()}",
            account=self,
            amount=-amount,
            transaction_type="transfer",
            description=f"Transfer to account {recipient.id}"
        )
        
        self.transactions.append(transaction)
        return transaction
    
    def _validate_amount(self, amount: Union[Decimal, float, str]) -> Decimal:
        """Validate and convert amount to Decimal."""
        if isinstance(amount, Decimal):
            pass
        elif isinstance(amount, (float, str)):
            amount = Decimal(str(amount))
        else:
            raise InvalidAmountError("Amount must be a number")
        
        if amount <= Decimal('0.00'):
            raise InvalidAmountError("Amount must be positive")
        
        return amount
    
    def get_transaction_history(self, limit: Optional[int] = None) -> List['Transaction']:
        """Get transaction history with optional limit."""
        return self.transactions[-limit:] if limit is not None else self.transactions.copy()


# Transaction class (yield)
class Transaction:
    """Financial transaction record."""
    
    def __init__(self, transaction_id: str, account: Account, amount: Decimal, 
                 transaction_type: str, description: str):
        self.id = transaction_id
        self.account = account
        self.amount = amount
        self.type = transaction_type
        self.description = description
        self.timestamp = dt.datetime.now()
        self.status = "completed"
    
    def __str__(self) -> str:
        return (f"Transaction {self.id}: {self.type} of {abs(self.amount):.2f} "
                f"on {self.timestamp:%Y-%m-%d %H:%M:%S}")
    
    def reverse(self) -> 'Transaction':
        """Reverse this transaction."""
        if self.status != "completed":
            raise ValueError("Cannot reverse a non-completed transaction")
        
        # Create a reversal transaction
        reversal = Transaction(
            transaction_id=f"RVSL-{self.id}",
            account=self.account,
            amount=-self.amount,
            transaction_type="reversal",
            description=f"Reversal of {self.id}"
        )
        
        # Update account balance
        self.account.balance += self.amount
        self.account.transactions.append(reversal)
        self.status = "reversed"
        
        return reversal


# Loan class (assert)
class Loan(BankEntity):
    """Bank loan with amortization schedule."""
    
    def __init__(self, id: str, customer: Customer, amount: Decimal, 
                 interest_rate: Decimal = LOAN_INTEREST_RATE, 
                 term_years: int = LOAN_TERM_YEARS):
        super().__init__(id, f"Loan #{id[-6:]}")
        self.customer = customer
        self.original_amount = amount
        self.remaining_amount = amount
        self.interest_rate = interest_rate
        self.term_months = term_years * 12
        self.start_date = dt.datetime.now().date()
        self.payments: List['LoanPayment'] = []
        self.is_active = True
        
        # Validate loan parameters
        assert amount > Decimal('0'), "Loan amount must be positive"
        assert interest_rate > Decimal('0'), "Interest rate must be positive"
        assert term_years > 0, "Loan term must be at least 1 year"
    
    def calculate_monthly_payment(self) -> Decimal:
        """Calculate monthly payment using amortization formula."""
        monthly_rate = self.interest_rate / Decimal('12')
        factor = (Decimal('1') + monthly_rate) ** self.term_months
        payment = (self.original_amount * monthly_rate * factor) / (factor - Decimal('1'))
        return payment.quantize(Decimal('0.01'))
    
    def make_payment(self, amount: Decimal, payment_date: Optional[dt.date] = None) -> 'LoanPayment':
        """Make a payment toward the loan."""
        if not self.is_active:
            raise ValueError("Loan is not active")
        
        if amount <= Decimal('0'):
            raise InvalidAmountError("Payment amount must be positive")
        
        if amount > self.remaining_amount:
            amount = self.remaining_amount  # Accept partial payment to close loan
        
        payment_date = payment_date or dt.datetime.now().date()
        
        # Calculate interest and principal portions
        interest = self.remaining_amount * (self.interest_rate / Decimal('12'))
        if amount <= interest:
            principal = Decimal('0')
            interest = amount
        else:
            principal = amount - interest
        
        payment = LoanPayment(
            payment_id=f"PMT-{dt.datetime.now().timestamp()}",
            loan=self,
            amount=amount,
            principal=principal,
            interest=interest,
            payment_date=payment_date
        )
        
        self.remaining_amount -= principal
        self.payments.append(payment)
        
        if self.remaining_amount <= Decimal('0'):
            self.is_active = False
        
        return payment
    
    def generate_amortization_schedule(self) -> List[Dict]:
        """Generate full amortization schedule for the loan."""
        schedule = []
        balance = self.original_amount
        monthly_payment = self.calculate_monthly_payment()
        monthly_rate = self.interest_rate / Decimal('12')
        
        for month in range(1, self.term_months + 1):
            interest = balance * monthly_rate
            principal = monthly_payment - interest
            
            if month == self.term_months:  # Last payment adjustment
                principal = balance
                monthly_payment = principal + interest
            
            balance -= principal
            
            schedule.append({
                'month': month,
                'payment': monthly_payment,
                'principal': principal,
                'interest': interest,
                'balance': max(balance, Decimal('0'))  # Ensure balance doesn't go negative
            })
            
            if balance <= Decimal('0'):
                break
        
        return schedule
    
    def get_remaining_payments(self) -> List[Dict]:
        """Get remaining payments based on actual payments made."""
        amortization = self.generate_amortization_schedule()
        payments_made = len(self.payments)
        
        if payments_made >= len(amortization):
            return []
        
        return amortization[payments_made:]


# LoanPayment class (try, except, finally)
class LoanPayment:
    """Record of a loan payment."""
    
    def __init__(self, payment_id: str, loan: Loan, amount: Decimal, 
                 principal: Decimal, interest: Decimal, payment_date: dt.date):
        self.id = payment_id
        self.loan = loan
        self.amount = amount
        self.principal = principal
        self.interest = interest
        self.payment_date = payment_date
        
        # Validate payment amounts
        try:
            assert abs((principal + interest) - amount) < Decimal('0.01'), "Payment amounts don't add up"
        except AssertionError as e:
            raise ValueError(f"Invalid payment amounts: {e}")


# Bank class (with, del, lambda)
class Bank:
    """The main banking system that manages customers, accounts, and loans."""
    
    def __init__(self, name: str):
        self.name = name
        self.customers: Dict[str, Customer] = {}
        self.accounts: Dict[str, Account] = {}
        self.loans: Dict[str, Loan] = {}
        self.transactions: List[Transaction] = []
        
        # Initialize with some test data
        self._initialize_test_data()
    
    def _initialize_test_data(self) -> None:
        """Initialize the bank with some test data."""
        # Add some customers
        customers = [
            ("CUST-1001", "John Doe", "john.doe@example.com", "555-0101"),
            ("CUST-1002", "Jane Smith", "jane.smith@example.com", "555-0102"),
            ("CUST-1003", "Robert Johnson", "robert.j@example.com", "555-0103"),
        ]
        
        for cust_id, name, email, phone in customers:
            self.add_customer(Customer(cust_id, name, email, phone))
        
        # Add some accounts
        accounts = [
            ("ACC-2001", "CUST-1001", "checking"),
            ("ACC-2002", "CUST-1001", "savings"),
            ("ACC-2003", "CUST-1002", "checking"),
            ("ACC-2004", "CUST-1003", "savings"),
        ]
        
        for acc_id, cust_id, acc_type in accounts:
            customer = self.get_customer(cust_id)
            account = Account(acc_id, customer, acc_type)
            self.add_account(account)
        
        # Make some initial deposits
        initial_deposits = [
            ("ACC-2001", "1000.00"),
            ("ACC-2002", "5000.00"),
            ("ACC-2003", "2500.00"),
            ("ACC-2004", "3000.00"),
        ]
        
        for acc_id, amount in initial_deposits:
            account = self.get_account(acc_id)
            account.deposit(Decimal(amount))
    
    def add_customer(self, customer: Customer) -> None:
        """Add a customer to the bank."""
        if customer.id in self.customers:
            raise ValueError(f"Customer with ID {customer.id} already exists")
        self.customers[customer.id] = customer
    
    def get_customer(self, customer_id: str) -> Customer:
        """Get a customer by ID."""
        if customer_id not in self.customers:
            raise CustomerNotFoundError(f"Customer {customer_id} not found")
        return self.customers[customer_id]
    
    def add_account(self, account: Account) -> None:
        """Add an account to the bank."""
        if account.id in self.accounts:
            raise ValueError(f"Account with ID {account.id} already exists")
        
        self.accounts[account.id] = account
        account.customer.add_account(account)
    
    def get_account(self, account_id: str) -> Account:
        """Get an account by ID."""
        if account_id not in self.accounts:
            raise AccountNotFoundError(f"Account {account_id} not found")
        return self.accounts[account_id]
    
    def close_account(self, account_id: str) -> None:
        """Close a bank account."""
        account = self.get_account(account_id)
        
        if account.balance != Decimal('0'):
            raise ValueError("Cannot close account with non-zero balance")
        
        account.is_active = False
        del self.accounts[account_id]  # Remove from bank's account registry
    
    def transfer_funds(self, from_account_id: str, to_account_id: str, amount: Decimal) -> Transaction:
        """Transfer funds between accounts."""
        from_account = self.get_account(from_account_id)
        to_account = self.get_account(to_account_id)
        return from_account.transfer(amount, to_account)
    
    def create_loan(self, customer_id: str, amount: Decimal) -> Loan:
        """Create a new loan for a customer."""
        customer = self.get_customer(customer_id)
        
        # Simple credit check - must have at least one account with sufficient balance
        if customer.get_total_balance() < amount * Decimal('0.1'):
            raise ValueError("Insufficient creditworthiness for this loan amount")
        
        loan_id = f"LOAN-{dt.datetime.now().timestamp()}"
        loan = Loan(loan_id, customer, amount)
        
        self.loans[loan.id] = loan
        customer.add_loan(loan)
        
        # Disburse loan amount to customer's primary account (first account)
        primary_account = next(iter(customer.accounts.values()))
        primary_account.deposit(amount)
        
        return loan
    
    def get_loan(self, loan_id: str) -> Loan:
        """Get a loan by ID."""
        if loan_id not in self.loans:
            raise ValueError(f"Loan {loan_id} not found")
        return self.loans[loan_id]
    
    def process_loan_payment(self, loan_id: str, amount: Decimal) -> LoanPayment:
        """Process a payment toward a loan."""
        loan = self.get_loan(loan_id)
        return loan.make_payment(amount)
    
    def get_customer_summary(self, customer_id: str) -> Dict:
        """Get a summary of a customer's accounts and loans."""
        customer = self.get_customer(customer_id)
        
        return {
            'customer': {
                'id': customer.id,
                'name': customer.name,
                'email': customer.email,
                'phone': customer.phone
            },
            'accounts': [
                {
                    'id': acc.id,
                    'type': acc.account_type,
                    'balance': float(acc.balance),
                    'is_active': acc.is_active
                }
                for acc in customer.accounts.values()
            ],
            'loans': [
                {
                    'id': loan.id,
                    'original_amount': float(loan.original_amount),
                    'remaining_amount': float(loan.remaining_amount),
                    'interest_rate': float(loan.interest_rate),
                    'is_active': loan.is_active
                }
                for loan in customer.loans
            ],
            'total_balance': float(customer.get_total_balance())
        }
    
    def generate_report(self) -> Dict:
        """Generate a summary report of the bank's status."""
        total_deposits = sum(acc.balance for acc in self.accounts.values())
        total_loans = sum(loan.remaining_amount for loan in self.loans.values())
        
        return {
            'bank_name': self.name,
            'total_customers': len(self.customers),
            'total_accounts': len(self.accounts),
            'active_accounts': sum(1 for acc in self.accounts.values() if acc.is_active),
            'total_deposits': float(total_deposits),
            'total_loans': float(total_loans),
            'loan_to_deposit_ratio': float(total_loans / total_deposits) if total_deposits > 0 else 0.0
        }
    
    def find_high_value_customers(self, threshold: Decimal = Decimal('10000.00')) -> List[Dict]:
        """Find customers with total balances above a threshold."""
        high_value = []
        
        for customer in self.customers.values():
            total = customer.get_total_balance()
            if total >= threshold:
                high_value.append({
                    'customer_id': customer.id,
                    'name': customer.name,
                    'total_balance': float(total),
                    'account_count': len(customer.accounts)
                })
        
        # Sort by total balance descending
        return sorted(high_value, key=lambda x: x['total_balance'], reverse=True)


# Main banking application (if, elif, else, while, for, break, continue, pass, def)
def main():
    """Main banking application interface."""
    print("Initializing Banking System...\n")
    bank = Bank("Python Savings & Loan")
    
    # Customer menu (while)
    while True:
        print("\n=== Banking System Menu ===")
        print("1. Customer Services")
        print("2. Account Services")
        print("3. Loan Services")
        print("4. Reports")
        print("5. Exit")
        
        choice = input("Enter your choice: ")
        
        if choice == "1":
            # Customer services
            while True:
                print("\nCustomer Services:")
                print("1. Add Customer")
                print("2. View Customer")
                print("3. List All Customers")
                print("4. Back to Main Menu")
                
                sub_choice = input("Enter choice: ")
                
                if sub_choice == "1":
                    # Add customer
                    try:
                        cust_id = f"CUST-{int(dt.datetime.now().timestamp())}"
                        name = input("Customer name: ")
                        email = input("Email: ")
                        phone = input("Phone: ")
                        
                        customer = Customer(cust_id, name, email, phone)
                        bank.add_customer(customer)
                        print(f"Added new customer: {customer}")
                    except Exception as e:
                        print(f"Error: {e}")
                
                elif sub_choice == "2":
                    # View customer
                    cust_id = input("Enter customer ID: ")
                    try:
                        customer = bank.get_customer(cust_id)
                        summary = bank.get_customer_summary(cust_id)
                        
                        print(f"\nCustomer: {customer.name} (ID: {customer.id})")
                        print(f"Contact: {customer.email} | {customer.phone}")
                        print(f"Total Balance: ${summary['total_balance']:.2f}")
                        
                        print("\nAccounts:")
                        for acc in summary['accounts']:
                            status = "Active" if acc['is_active'] else "Inactive"
                            print(f"- {acc['type'].title()}: ${acc['balance']:.2f} ({status})")
                        
                        if summary['loans']:
                            print("\nLoans:")
                            for loan in summary['loans']:
                                status = "Active" if loan['is_active'] else "Paid"
                                print(f"- Loan {loan['id'][-6:]}: "
                                      f"Original ${loan['original_amount']:.2f}, "
                                      f"Remaining ${loan['remaining_amount']:.2f} ({status})")
                    except Exception as e:
                        print(f"Error: {e}")
                
                elif sub_choice == "3":
                    # List all customers
                    print("\nAll Customers:")
                    for customer in bank.customers.values():
                        print(f"- {customer.id}: {customer.name} ({len(customer.accounts)} accounts)")
                
                elif sub_choice == "4":
                    break
                else:
                    print("Invalid choice, please try again")
        
        elif choice == "2":
            # Account services
            while True:
                print("\nAccount Services:")
                print("1. Open Account")
                print("2. Close Account")
                print("3. Deposit")
                print("4. Withdraw")
                print("5. Transfer")
                print("6. View Transactions")
                print("7. Back to Main Menu")
                
                sub_choice = input("Enter choice: ")
                
                if sub_choice == "1":
                    # Open account
                    try:
                        cust_id = input("Customer ID: ")
                        account_type = input("Account type (checking/savings): ")
                        
                        if account_type.lower() not in ("checking", "savings"):
                            print("Account type must be 'checking' or 'savings'")
                            continue
                        
                        acc_id = f"ACC-{int(dt.datetime.now().timestamp())}"
                        customer = bank.get_customer(cust_id)
                        account = Account(acc_id, customer, account_type)
                        bank.add_account(account)
                        
                        # Initial deposit
                        amount = input("Initial deposit amount: ")
                        account.deposit(Decimal(amount))
                        
                        print(f"Opened new {account_type} account {acc_id} for {customer.name}")
                        print(f"Initial deposit of ${amount} received. New balance: ${account.balance:.2f}")
                    except Exception as e:
                        print(f"Error: {e}")
                
                elif sub_choice == "2":
                    # Close account
                    try:
                        acc_id = input("Account ID to close: ")
                        bank.close_account(acc_id)
                        print(f"Account {acc_id} has been closed")
                    except Exception as e:
                        print(f"Error: {e}")
                
                elif sub_choice == "3":
                    # Deposit
                    try:
                        acc_id = input("Account ID: ")
                        amount = Decimal(input("Amount to deposit: "))
                        
                        account = bank.get_account(acc_id)
                        transaction = account.deposit(amount)
                        
                        print(f"Deposited ${amount:.2f} to account {acc_id}")
                        print(f"New balance: ${account.balance:.2f}")
                    except Exception as e:
                        print(f"Error: {e}")
                
                elif sub_choice == "4":
                    # Withdraw
                    try:
                        acc_id = input("Account ID: ")
                        amount = Decimal(input("Amount to withdraw: "))
                        
                        account = bank.get_account(acc_id)
                        transaction = account.withdraw(amount)
                        
                        print(f"Withdrew ${amount:.2f} from account {acc_id}")
                        print(f"New balance: ${account.balance:.2f}")
                    except Exception as e:
                        print(f"Error: {e}")
                
                elif sub_choice == "5":
                    # Transfer
                    try:
                        from_acc = input("From Account ID: ")
                        to_acc = input("To Account ID: ")
                        amount = Decimal(input("Amount to transfer: "))
                        
                        transaction = bank.transfer_funds(from_acc, to_acc, amount)
                        
                        print(f"Transferred ${amount:.2f} from {from_acc} to {to_acc}")
                        print(f"From account new balance: ${bank.get_account(from_acc).balance:.2f}")
                        print(f"To account new balance: ${bank.get_account(to_acc).balance:.2f}")
                    except Exception as e:
                        print(f"Error: {e}")
                
                elif sub_choice == "6":
                    # View transactions
                    try:
                        acc_id = input("Account ID: ")
                        limit = input("Number of transactions to show (blank for all): ")
                        limit = int(limit) if limit.strip() else None
                        
                        account = bank.get_account(acc_id)
                        transactions = account.get_transaction_history(limit)
                        
                        print(f"\nTransaction history for account {acc_id}:")
                        for txn in reversed(transactions):
                            amount = f"+${txn.amount:.2f}" if txn.amount > 0 else f"-${abs(txn.amount):.2f}"
                            print(f"{txn.timestamp:%Y-%m-%d %H:%M} {txn.type:10} {amount:>10} - {txn.description}")
                    except Exception as e:
                        print(f"Error: {e}")
                
                elif sub_choice == "7":
                    break
                else:
                    print("Invalid choice, please try again")
        
        elif choice == "3":
            # Loan services
            while True:
                print("\nLoan Services:")
                print("1. Apply for Loan")
                print("2. Make Loan Payment")
                print("3. View Loan Details")
                print("4. View Amortization Schedule")
                print("5. Back to Main Menu")
                
                sub_choice = input("Enter choice: ")
                
                if sub_choice == "1":
                    # Apply for loan
                    try:
                        cust_id = input("Customer ID: ")
                        amount = Decimal(input("Loan amount: "))
                        
                        loan = bank.create_loan(cust_id, amount)
                        monthly_payment = loan.calculate_monthly_payment()
                        
                        print(f"\nLoan {loan.id} approved for {loan.customer.name}")
                        print(f"Amount: ${loan.original_amount:.2f}")
                        print(f"Interest Rate: {loan.interest_rate * 100:.2f}%")
                        print(f"Term: {loan.term_months} months")
                        print(f"Monthly Payment: ${monthly_payment:.2f}")
                        print(f"Loan amount has been deposited to customer's primary account")
                    except Exception as e:
                        print(f"Error: {e}")
                
                elif sub_choice == "2":
                    # Make loan payment
                    try:
                        loan_id = input("Loan ID: ")
                        amount = Decimal(input("Payment amount: "))
                        
                        payment = bank.process_loan_payment(loan_id, amount)
                        loan = bank.get_loan(loan_id)
                        
                        print(f"\nPayment of ${amount:.2f} received for loan {loan_id}")
                        print(f"Principal: ${payment.principal:.2f}")
                        print(f"Interest: ${payment.interest:.2f}")
                        print(f"Remaining Balance: ${loan.remaining_amount:.2f}")
                        
                        if not loan.is_active:
                            print("\nCongratulations! This loan has been fully paid off!")
                    except Exception as e:
                        print(f"Error: {e}")
                
                elif sub_choice == "3":
                    # View loan details
                    try:
                        loan_id = input("Loan ID: ")
                        loan = bank.get_loan(loan_id)
                        
                        print(f"\nLoan Details for {loan_id}:")
                        print(f"Customer: {loan.customer.name}")
                        print(f"Original Amount: ${loan.original_amount:.2f}")
                        print(f"Remaining Balance: ${loan.remaining_amount:.2f}")
                        print(f"Interest Rate: {loan.interest_rate * 100:.2f}%")
                        print(f"Term: {loan.term_months} months")
                        print(f"Monthly Payment: ${loan.calculate_monthly_payment():.2f}")
                        print(f"Status: {'Active' if loan.is_active else 'Paid off'}")
                        print(f"Payments made: {len(loan.payments)}")
                    except Exception as e:
                        print(f"Error: {e}")
                
                elif sub_choice == "4":
                    # View amortization schedule
                    try:
                        loan_id = input("Loan ID: ")
                        loan = bank.get_loan(loan_id)
                        
                        print(f"\nAmortization Schedule for Loan {loan_id}:")
                        print("Month  Payment    Principal  Interest   Balance")
                        print("----------------------------------------------")
                        
                        schedule = loan.generate_amortization_schedule()
                        for pmt in schedule[:12]:  # Show first 12 months
                            print(f"{pmt['month']:5}  {pmt['payment']:8.2f}  {pmt['principal']:8.2f}  "
                                  f"{pmt['interest']:8.2f}  {pmt['balance']:8.2f}")
                        
                        if len(schedule) > 12:
                            print("... (showing first 12 months)")
                    except Exception as e:
                        print(f"Error: {e}")
                
                elif sub_choice == "5":
                    break
                else:
                    print("Invalid choice, please try again")
        
        elif choice == "4":
            # Reports
            while True:
                print("\nReports:")
                print("1. Bank Summary")
                print("2. High Value Customers")
                print("3. Back to Main Menu")
                
                sub_choice = input("Enter choice: ")
                
                if sub_choice == "1":
                    # Bank summary
                    report = bank.generate_report()
                    
                    print("\nBank Summary Report:")
                    print(f"Bank Name: {report['bank_name']}")
                    print(f"Total Customers: {report['total_customers']}")
                    print(f"Total Accounts: {report['total_accounts']} ({report['active_accounts']} active)")
                    print(f"Total Deposits: ${report['total_deposits']:,.2f}")
                    print(f"Total Loans: ${report['total_loans']:,.2f}")
                    print(f"Loan-to-Deposit Ratio: {report['loan_to_deposit_ratio']:.2f}")
                
                elif sub_choice == "2":
                    # High value customers
                    threshold = Decimal(input("Enter balance threshold (default $10,000): ") or "10000")
                    high_value = bank.find_high_value_customers(threshold)
                    
                    print(f"\nHigh Value Customers (Balance ≥ ${threshold:,.2f}):")
                    if not high_value:
                        print("No customers meet this threshold")
                    else:
                        for cust in high_value:
                            print(f"- {cust['name']}: ${cust['total_balance']:,.2f} "
                                  f"({cust['account_count']} accounts)")
                
                elif sub_choice == "3":
                    break
                else:
                    print("Invalid choice, please try again")
        
        elif choice == "5":
            print("\nThank you for using the Banking System. Goodbye!")
            break
        else:
            print("Invalid choice, please try again")


# Run the main application (if __name__ == ...)
if __name__ == "__main__":
    main()