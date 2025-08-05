import mysql.connector
from datetime import datetime, date, timedelta
import random
from dotenv import load_dotenv
import os

load_dotenv()

# Connect to the database
conn = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)

cursor = conn.cursor()

# User data
user_id = 1
total_portfolio_value = 125750.50
currency = "USD"

# Insert User_portfolio
cursor.execute("""
INSERT INTO User_portfolio (user_ID, total_value, currency, created_at, updated_at)
VALUES (%s, %s, %s, %s, %s)
""", (user_id, total_portfolio_value, currency, datetime.now(), datetime.now()))

# Bank accounts data
bank_accounts = [
    {
        'name': 'Chase Checking',
        'type': 'Checking',
        'balance': 15230.75
    },
    {
        'name': 'Wells Fargo Savings',
        'type': 'Savings',
        'balance': 45500.25
    },
    {
        'name': 'Investment Account',
        'type': 'Investment',
        'balance': 64019.50
    }
]

bank_ids = []
for account in bank_accounts:
    cursor.execute("""
    INSERT INTO Bank_Account (bank_account_name, bank_account_type, current_balance, user_ID)
    VALUES (%s, %s, %s, %s)
    """, (account['name'], account['type'], account['balance'], user_id))

    bank_ids.append(cursor.lastrowid)

# Transactions data
transactions_data = [
    {'bank_id': bank_ids[0], 'date': datetime.now() - timedelta(days=30)},  # Chase checking
    {'bank_id': bank_ids[0], 'date': datetime.now() - timedelta(days=25)},
    {'bank_id': bank_ids[1], 'date': datetime.now() - timedelta(days=45)},  # Wells Fargo savings
    {'bank_id': bank_ids[2], 'date': datetime.now() - timedelta(days=60)},  # Investment account
    {'bank_id': bank_ids[2], 'date': datetime.now() - timedelta(days=35)},
    {'bank_id': bank_ids[2], 'date': datetime.now() - timedelta(days=20)},
    {'bank_id': bank_ids[2], 'date': datetime.now() - timedelta(days=10)},
]

transaction_ids = []
for trans in transactions_data:
    cursor.execute("""
    INSERT INTO Transaction (bank_ID, date)
    VALUES (%s, %s)
    """, (trans['bank_id'], trans['date']))

    transaction_ids.append(cursor.lastrowid)

# Stock data (for investment account transactions)
stocks_data = [
    {
        'transaction_id': transaction_ids[3],  # First investment transaction
        'shares': 50,
        'purchase_price': 150.25,
        'current_price': 165.80,
        'purchase_date': date.today() - timedelta(days=60),
        'stock_ticker': 'AMZN'
    },
    {
        'transaction_id': transaction_ids[4],  # Second investment transaction
        'shares': 25,
        'purchase_price': 89.50,
        'current_price': 92.75,
        'purchase_date': date.today() - timedelta(days=35),
        'stock_ticker': 'COIN'
    },
    {
        'transaction_id': transaction_ids[5],  # Third investment transaction
        'shares': 100,
        'purchase_price': 45.30,
        'current_price': 48.90,
        'purchase_date': date.today() - timedelta(days=20),
        'stock_ticker': 'RDDT'
    },
    {
        'transaction_id': transaction_ids[6],  # Fourth investment transaction
        'shares': 30,
        'purchase_price': 220.00,
        'current_price': 215.50,
        'purchase_date': date.today() - timedelta(days=10),
        'stock_ticker': 'FLR'
    }
]

for stock in stocks_data:
    cursor.execute("""
        INSERT INTO Stocks (transaction_ID, number_of_shares, purchase_price_per_share, 
                            current_price_per_share, purchase_date, updated_at_date, stock_ticker)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        stock['transaction_id'],
        stock['shares'],
        stock['purchase_price'],
        stock['current_price'],
        stock['purchase_date'],
        datetime.now(),
        stock['stock_ticker']
    ))

# Bonds data
bonds_data = [
    {
        'transaction_id': transaction_ids[2],
        'name': 'iShares iBoxx $ Investment Grade Corporate Bond ETF',
        'ticker': 'LQD',
        'purchase_price_per_bond': 52.64,
        'bond_yield': 4.25,
        'num_bonds': 10,
        'dividend_frequency': 'Monthly'
    },
    {
        'transaction_id': transaction_ids[3],
        'name': 'iShares 1-3 Year Treasury Bond ETF',
        'ticker': 'SHY',
        'purchase_price_per_bond': 70.12,
        'bond_yield': 3.85,
        'num_bonds': 5,
        'dividend_frequency': 'Monthly'
    }
]

for bond in bonds_data:
    cursor.execute("""
    INSERT INTO Bonds (bond_name, bond_ticker, purchase_price_per_bond, bond_yield, 
                       number_of_bonds, dividend_frequency, last_updated, transaction_ID)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        bond['name'],
        bond['ticker'],
        bond['purchase_price_per_bond'],
        bond['bond_yield'],
        bond['num_bonds'],
        bond['dividend_frequency'],
        datetime.now(),
        bond['transaction_id']
    ))

# Commit changes
conn.commit()

# Display summary of inserted data
print("Mock data inserted successfully!")
print(f"\nSummary for User ID {user_id}:")
print(f"Total Portfolio Value: ${total_portfolio_value:,.2f}")
print(f"Currency: {currency}")

print(f"\nBank Accounts ({len(bank_accounts)}):")
for i, account in enumerate(bank_accounts):
    print(f"  {i + 1}. {account['name']} ({account['type']}): ${account['balance']:,.2f}")

print(f"\nTransactions: {len(transactions_data)} total")
print(f"Stock positions: {len(stocks_data)} total")
print(f"Bond positions: {len(bonds_data)} total")

# Calculate total stock value
total_stock_value = sum(stock['shares'] * stock['current_price'] for stock in stocks_data)
total_bond_value = sum(bond['price_per_bond'] for bond in bonds_data)
total_cash = sum(account['balance'] for account in bank_accounts)

print(f"\nPortfolio Breakdown:")
print(f"  Cash: ${total_cash:,.2f}")
print(f"  Stocks: ${total_stock_value:,.2f}")
print(f"  Bonds: ${total_bond_value:,.2f}")
print(f"  Total: ${total_cash + total_stock_value + total_bond_value:,.2f}")

cursor.close()
conn.close()