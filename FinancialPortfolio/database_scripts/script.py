#!/usr/bin/env python3
"""
Financial Portfolio Database Management System
A Python script to create and manage a financial portfolio database using MySQL.
"""

import mysql.connector
from mysql.connector import Error
from datetime import datetime, date
from decimal import Decimal
import logging
from typing import Optional, List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class FinancialPortfolioDB:
    def __init__(self, host='localhost', user='root', password='', database='financial_portfolio'):
        """Initialize database connection parameters"""
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                autocommit=True
            )
            logger.info("Successfully connected to MySQL database")
            return True
        except Error as e:
            logger.error(f"Error connecting to MySQL: {e}")
            return False

    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("MySQL connection closed")

    def create_database_and_tables(self):
        """Create the database and all tables"""
        if not self.connection:
            logger.error("No database connection")
            return False

        cursor = self.connection.cursor()

        try:
            # Create database
            cursor.execute("CREATE DATABASE IF NOT EXISTS financial_portfolio")
            cursor.execute("USE financial_portfolio")
            logger.info("Database 'financial_portfolio' created/selected")

            # Update connection to use the database
            self.connection.database = 'financial_portfolio'

            # Create tables
            tables = self._get_table_definitions()

            for table_name, table_sql in tables.items():
                cursor.execute(table_sql)
                logger.info(f"Table '{table_name}' created successfully")

            # Create indexes
            self._create_indexes(cursor)

            # Create triggers
            self._create_triggers(cursor)

            return True

        except Error as e:
            logger.error(f"Error creating database/tables: {e}")
            return False
        finally:
            cursor.close()

    def _get_table_definitions(self) -> Dict[str, str]:
        """Return dictionary of table creation SQL statements"""
        return {
            'User_portfolio': """
                CREATE TABLE IF NOT EXISTS User_portfolio (
                    User_id INT PRIMARY KEY AUTO_INCREMENT,
                    Total_value DECIMAL(15, 2) NOT NULL DEFAULT 0.00,
                    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
                    Created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    Updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """,

            'Bank_Account': """
                CREATE TABLE IF NOT EXISTS Bank_Account (
                    Bank_id INT PRIMARY KEY AUTO_INCREMENT,
                    Bank_Account_Name VARCHAR(100) NOT NULL,
                    Bank_account_type ENUM('Checking', 'Savings', 'Money Market', 'CD', 'Investment') NOT NULL,
                    Bank_account_date_created DATE NOT NULL,
                    Bank_account_last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    Current_balance DECIMAL(15, 2) NOT NULL DEFAULT 0.00,
                    Very_first_balance DECIMAL(15, 2) NOT NULL DEFAULT 0.00,
                    User_id INT NOT NULL,
                    FOREIGN KEY (User_id) REFERENCES User_portfolio(User_id) ON DELETE CASCADE
                )
            """,

            'Stocks': """
                CREATE TABLE IF NOT EXISTS Stocks (
                    stock_id INT PRIMARY KEY AUTO_INCREMENT,
                    user_id INT NOT NULL,
                    Updated_at_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    Number_of_shares DECIMAL(10, 4) NOT NULL DEFAULT 0,
                    Purchase_price_per_share DECIMAL(10, 4) NOT NULL,
                    current_price_per_share DECIMAL(10, 4),
                    Purchase_date DATE NOT NULL,
                    stock_symbol VARCHAR(10) NOT NULL,
                    company_name VARCHAR(100),
                    FOREIGN KEY (user_id) REFERENCES User_portfolio(User_id) ON DELETE CASCADE
                )
            """,

            'Bonds': """
                CREATE TABLE IF NOT EXISTS Bonds (
                    bond_id INT PRIMARY KEY AUTO_INCREMENT,
                    bond_name VARCHAR(100) NOT NULL,
                    purchase_date DATE NOT NULL,
                    Bond_amount DECIMAL(15, 2) NOT NULL,
                    Coupon_rate DECIMAL(5, 4) NOT NULL,
                    number_of_bonds INT NOT NULL DEFAULT 1,
                    maturity_date DATE NOT NULL,
                    user_id INT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES User_portfolio(User_id) ON DELETE CASCADE
                )
            """,

            'Transaction': """
                CREATE TABLE IF NOT EXISTS Transaction (
                    Transaction_id INT PRIMARY KEY AUTO_INCREMENT,
                    Bank_id INT,
                    Stock_id INT,
                    Bond_id INT,
                    transaction_type ENUM('Buy', 'Sell', 'Deposit', 'Withdrawal', 'Dividend', 'Interest') NOT NULL,
                    transaction_amount DECIMAL(15, 2) NOT NULL,
                    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    description TEXT,
                    FOREIGN KEY (Bank_id) REFERENCES Bank_Account(Bank_id) ON DELETE SET NULL,
                    FOREIGN KEY (Stock_id) REFERENCES Stocks(stock_id) ON DELETE SET NULL,
                    FOREIGN KEY (Bond_id) REFERENCES Bonds(bond_id) ON DELETE SET NULL
                )
            """
        }

def main():
    """Main function to demonstrate database usage"""
    # Database connection parameters - modify as needed
    db = FinancialPortfolioDB(
        host='localhost',
        user='root',  # Change to your MySQL username
        password='n3u3da!',  # Change to your MySQL password
        database='financial_portfolio'
    )

    # Connect to database
    if not db.connect():
        return

    try:
        # Create database and tables
        print("Creating database and tables...")
        if db.create_database_and_tables():
            print("Database setup completed successfully!")

        # # Example usage
        # print("\n--- Example Usage ---")

        # # Create a user portfolio
        # user_id = db.create_user_portfolio('USD')
        # if user_id:
        #     print(f"Created user portfolio: {user_id}")

        #     # Add a bank account
        #     bank_id = db.add_bank_account(
        #         user_id=user_id,
        #         account_name="Main Checking",
        #         account_type="Checking",
        #         date_created=date.today(),
        #         current_balance=Decimal('5000.00'),
        #         first_balance=Decimal('1000.00')
        #     )

        #     # Add a stock holding
        #     stock_id = db.add_stock_holding(
        #         user_id=user_id,
        #         symbol="AAPL",
        #         company_name="Apple Inc.",
        #         shares=Decimal('100.0000'),
        #         purchase_price=Decimal('150.25'),
        #         purchase_date=date.today(),
        #         current_price=Decimal('165.80')
        #     )

        #     # Add a transaction
        #     if bank_id:
        #         db.add_transaction(
        #             transaction_type="Deposit",
        #             amount=Decimal('5000.00'),
        #             description="Initial deposit",
        #             bank_id=bank_id
        #         )

        #     # Get portfolio summary
        #     summary = db.get_user_portfolio_summary(user_id)
        #     if summary:
        #         print(f"\nPortfolio Summary for User {user_id}:")
        #         print(f"Bank Accounts: {len(summary['bank_accounts'])}")
        #         print(f"Stock Holdings: {len(summary['stocks'])}")
        #         print(f"Bond Holdings: {len(summary['bonds'])}")

        #         # Calculate total value
        #         total_value = db.get_portfolio_value(user_id)
        #         print(f"Total Portfolio Value: ${total_value}")

    finally:
        # Always disconnect
        db.disconnect()

if __name__ == "__main__":
    main()