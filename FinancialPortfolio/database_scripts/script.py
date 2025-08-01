import mysql.connector

# First, connect WITHOUT specifying a database to create it
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="n3u3da!"
    # No database parameter here initially
)

cursor = conn.cursor()

# Create the database
cursor.execute("CREATE DATABASE IF NOT EXISTS finance_portfolio;")

# Now switch to using the database
cursor.execute("USE finance_portfolio;")

# Alternatively, you can close and reconnect with the database specified:
# cursor.close()
# conn.close()
#
# conn = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     password="n3u3da!",
#     database="finance_portfolio"
# )
# cursor = conn.cursor()

# Create User_portfolio table
cursor.execute("""
CREATE TABLE IF NOT EXISTS User_portfolio (
    user_ID INT PRIMARY KEY,
    total_value DECIMAL(15, 2),
    currency VARCHAR(10),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
""")

# Create Bank_Account table
cursor.execute("""
CREATE TABLE IF NOT EXISTS Bank_Account (
    bank_ID INT PRIMARY KEY AUTO_INCREMENT,
    bank_account_name VARCHAR(100),
    bank_account_type VARCHAR(50),
    bank_account_date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    bank_account_last_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    current_balance DECIMAL(15, 2),
    user_ID INT,
    FOREIGN KEY (user_ID) REFERENCES User_portfolio(user_ID)
);
""")

# Create Transaction table
cursor.execute("""
CREATE TABLE IF NOT EXISTS Transaction (
    transaction_ID INT PRIMARY KEY AUTO_INCREMENT,
    bank_ID INT,
    date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bank_ID) REFERENCES Bank_Account(bank_ID)
);
""")

# Create Stocks table
cursor.execute("""
CREATE TABLE IF NOT EXISTS Stocks (
    stock_ID INT PRIMARY KEY AUTO_INCREMENT,
    transaction_ID INT,
    updated_at_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    number_of_shares INT,
    purchase_price_per_share DECIMAL(10, 2),
    current_price_per_share DECIMAL(10, 2),
    purchase_date DATE,
    FOREIGN KEY (transaction_ID) REFERENCES Transaction(transaction_ID)
);
""")

# Create Bonds table
cursor.execute("""
CREATE TABLE IF NOT EXISTS Bonds (
    bond_id INT PRIMARY KEY AUTO_INCREMENT,
    bond_name VARCHAR(100),
    bond_amount DECIMAL(15, 2),
    coupon_rate DECIMAL(5, 2),
    number_of_bonds INT,
    maturity_date DATE,
    transaction_ID INT,
    FOREIGN KEY (transaction_ID) REFERENCES Transaction(transaction_ID)
);
""")

conn.commit()
cursor.close()
conn.close()

print("Database and tables created successfully!")