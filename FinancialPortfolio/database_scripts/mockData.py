import mysql.connector
from mysql.connector import Error

# Establishing the connection to MySQL
def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',        
            user='root',             
            password='n3u3da!',     
            database='financial_portfolio'  
        )
        if connection.is_connected():
            print("Connected to MySQL database")
            return connection
    except Error as e:
        print(f"Error: {e}")
        return None

# Inserting mock data for a single user
def insert_mock_data(connection):
    cursor = connection.cursor()

    # User Portfolio - This creates the user (User_id will be auto-generated)
    user_portfolio_query = """
    INSERT INTO User_portfolio (Total_value, currency) 
    VALUES 
    (50000.00, 'USD');
    """
    


    # Transactions
    transactions_query = """
    INSERT INTO Transaction (Bank_id, Stock_id, Bond_id, transaction_type, transaction_amount, transaction_date, description)
    VALUES
    (1, NULL, NULL, 'Deposit', 20000.00, '2023-07-15', 'Initial deposit to Checking account'),
    (2, NULL, NULL, 'Deposit', 15000.00, '2023-07-16', 'Initial deposit to Savings account'),
    (3, 1, NULL, 'Buy', 6000.00, '2023-07-17', 'Bought 50 shares of AAPL at $120/share'),
    (3, 2, NULL, 'Buy', 3550.00, '2023-07-18', 'Bought 100 shares of TSLA at $35.50/share'),
    (3, NULL, 1, 'Buy', 5000.00, '2023-07-19', 'Bought 5 units of US Treasury Bond ($1000 each)'),
    (3, 3, NULL, 'Buy', 3000.00, '2023-07-20', 'Bought 200 shares of AMZN at $15/share');
    """

    try:
        # First insert the User_portfolio record (this creates the user)
        print("Inserting User_portfolio record...")
        cursor.execute(user_portfolio_query)
        
        # Get the auto-generated User_id
        user_id = cursor.lastrowid
        print(f"Created user with ID: {user_id}")

        # Inserting mock data into Bank_Account
        print("Inserting mock data into Bank_Account...")
        bank_account_query = """
        INSERT INTO Bank_Account (Bank_Account_Name, Bank_account_type, Bank_account_date_created, Current_balance, Very_first_balance, User_id)
        VALUES
        ('Main Checking', 'Checking', '2020-01-01', 20000.00, 20000.00, %s),
        ('High Yield Savings', 'Savings', '2021-01-01', 15000.00, 15000.00, %s),
        ('Investment Fund', 'Investment', '2023-05-01', 5000.00, 5000.00, %s);
        """
        cursor.execute(bank_account_query, (user_id, user_id, user_id))
        
        # Get the Bank_ids (they will be consecutive starting from the first inserted ID)
        first_bank_id = cursor.lastrowid
        bank_ids = [first_bank_id, first_bank_id + 1, first_bank_id + 2]
        print(f"Created bank accounts with IDs: {bank_ids}")

        # Inserting mock data into Stocks
        print("Inserting mock data into Stocks...")
        stocks_query = """
        INSERT INTO Stocks (user_id, Number_of_shares, Purchase_price_per_share, current_price_per_share, Purchase_date, stock_symbol, company_name)
        VALUES
        (%s, 50, 120.00, 130.00, '2021-06-15', 'AAPL', 'Apple Inc.'),
        (%s, 100, 35.50, 40.00, '2022-03-10', 'TSLA', 'Tesla Inc.'),
        (%s, 200, 15.00, 18.00, '2023-01-01', 'AMZN', 'Amazon.com Inc.');
        """
        cursor.execute(stocks_query, (user_id, user_id, user_id))
        
        # Get the Stock_ids
        first_stock_id = cursor.lastrowid
        stock_ids = [first_stock_id, first_stock_id + 1, first_stock_id + 2]
        print(f"Created stocks with IDs: {stock_ids}")

        # Inserting mock data into Bonds
        print("Inserting mock data into Bonds...")
        bonds_query = """
        INSERT INTO Bonds (bond_name, purchase_date, Bond_amount, Coupon_rate, number_of_bonds, maturity_date, user_id)
        VALUES
        ('US Treasury Bond', '2022-04-01', 1000.00, 0.03, 5, '2032-04-01', %s),
        ('Corporate Bond - Google', '2021-07-15', 5000.00, 0.05, 10, '2026-07-15', %s),
        ('Municipal Bond - NY', '2020-08-01', 3000.00, 0.02, 3, '2030-08-01', %s);
        """
        cursor.execute(bonds_query, (user_id, user_id, user_id))
        
        # Get the Bond_ids
        first_bond_id = cursor.lastrowid
        bond_ids = [first_bond_id, first_bond_id + 1, first_bond_id + 2]
        print(f"Created bonds with IDs: {bond_ids}")

        # Inserting mock data into Transaction
        print("Inserting mock data into Transaction...")
        transactions_query = """
        INSERT INTO Transaction (Bank_id, Stock_id, Bond_id, transaction_type, transaction_amount, transaction_date, description)
        VALUES
        (%s, NULL, NULL, 'Deposit', 20000.00, '2023-07-15', 'Initial deposit to Checking account'),
        (%s, NULL, NULL, 'Deposit', 15000.00, '2023-07-16', 'Initial deposit to Savings account'),
        (%s, %s, NULL, 'Buy', 6000.00, '2023-07-17', 'Bought 50 shares of AAPL at $120/share'),
        (%s, %s, NULL, 'Buy', 3550.00, '2023-07-18', 'Bought 100 shares of TSLA at $35.50/share'),
        (%s, NULL, %s, 'Buy', 5000.00, '2023-07-19', 'Bought 5 units of US Treasury Bond ($1000 each)'),
        (%s, %s, NULL, 'Buy', 3000.00, '2023-07-20', 'Bought 200 shares of AMZN at $15/share');
        """
        cursor.execute(transactions_query, (
            bank_ids[0],  # Main Checking
            bank_ids[1],  # High Yield Savings
            bank_ids[2], stock_ids[0],  # Investment Fund, AAPL stock
            bank_ids[2], stock_ids[1],  # Investment Fund, TSLA stock
            bank_ids[2], bond_ids[0],   # Investment Fund, US Treasury Bond
            bank_ids[2], stock_ids[2]   # Investment Fund, AMZN stock
        ))

        # Commit all changes
        connection.commit()
        print("Mock data inserted successfully!")
    except Error as e:
        print(f"Error inserting data: {e}")
        # Rollback in case of error
        connection.rollback()

# Main function to run the script
def main():
    connection = create_connection()

    if connection:
        insert_mock_data(connection)
        connection.close()

if __name__ == "__main__":
    main()