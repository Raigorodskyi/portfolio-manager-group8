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

    def _create_indexes(self, cursor):
        """Create database indexes for performance"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_bank_account_user ON Bank_Account(User_id)",
            "CREATE INDEX IF NOT EXISTS idx_stocks_user ON Stocks(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_bonds_user ON Bonds(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_transaction_bank ON Transaction(Bank_id)",
            "CREATE INDEX IF NOT EXISTS idx_transaction_stock ON Transaction(Stock_id)",
            "CREATE INDEX IF NOT EXISTS idx_transaction_bond ON Transaction(Bond_id)",
            "CREATE INDEX IF NOT EXISTS idx_transaction_date ON Transaction(transaction_date)",
            "CREATE INDEX IF NOT EXISTS idx_stocks_symbol ON Stocks(stock_symbol)"
        ]

        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
            except Error as e:
                logger.warning(f"Index creation warning: {e}")

    def _create_triggers(self, cursor):
        """Create database triggers"""
        # Note: Triggers are complex and may need to be created separately
        # This is a simplified version
        pass

    # CRUD Operations
    def create_user_portfolio(self, currency='USD') -> Optional[int]:
        """Create a new user portfolio"""
        cursor = self.connection.cursor()
        try:
            query = "INSERT INTO User_portfolio (currency) VALUES (%s)"
            cursor.execute(query, (currency,))
            user_id = cursor.lastrowid
            logger.info(f"Created user portfolio with ID: {user_id}")
            return user_id
        except Error as e:
            logger.error(f"Error creating user portfolio: {e}")
            return None
        finally:
            cursor.close()

    def add_bank_account(self, user_id: int, account_name: str, account_type: str,
                         date_created: date, current_balance: Decimal,
                         first_balance: Decimal) -> Optional[int]:
        """Add a bank account to user portfolio"""
        cursor = self.connection.cursor()
        try:
            query = """
                INSERT INTO Bank_Account 
                (Bank_Account_Name, Bank_account_type, Bank_account_date_created, 
                 Current_balance, Very_first_balance, User_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (account_name, account_type, date_created,
                                   current_balance, first_balance, user_id))
            bank_id = cursor.lastrowid
            logger.info(f"Added bank account with ID: {bank_id}")
            return bank_id
        except Error as e:
            logger.error(f"Error adding bank account: {e}")
            return None
        finally:
            cursor.close()

    def add_stock_holding(self, user_id: int, symbol: str, company_name: str,
                          shares: Decimal, purchase_price: Decimal,
                          purchase_date: date, current_price: Optional[Decimal] = None) -> Optional[int]:
        """Add a stock holding to user portfolio"""
        cursor = self.connection.cursor()
        try:
            query = """
                INSERT INTO Stocks 
                (user_id, stock_symbol, company_name, Number_of_shares, 
                 Purchase_price_per_share, current_price_per_share, Purchase_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (user_id, symbol, company_name, shares,
                                   purchase_price, current_price, purchase_date))
            stock_id = cursor.lastrowid
            logger.info(f"Added stock holding with ID: {stock_id}")
            return stock_id
        except Error as e:
            logger.error(f"Error adding stock holding: {e}")
            return None
        finally:
            cursor.close()

    def add_bond_holding(self, user_id: int, bond_name: str, purchase_date: date,
                         bond_amount: Decimal, coupon_rate: Decimal,
                         num_bonds: int, maturity_date: date) -> Optional[int]:
        """Add a bond holding to user portfolio"""
        cursor = self.connection.cursor()
        try:
            query = """
                INSERT INTO Bonds 
                (user_id, bond_name, purchase_date, Bond_amount, 
                 Coupon_rate, number_of_bonds, maturity_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (user_id, bond_name, purchase_date, bond_amount,
                                   coupon_rate, num_bonds, maturity_date))
            bond_id = cursor.lastrowid
            logger.info(f"Added bond holding with ID: {bond_id}")
            return bond_id
        except Error as e:
            logger.error(f"Error adding bond holding: {e}")
            return None
        finally:
            cursor.close()

    def add_transaction(self, transaction_type: str, amount: Decimal,
                        description: str = "", bank_id: Optional[int] = None,
                        stock_id: Optional[int] = None, bond_id: Optional[int] = None) -> Optional[int]:
        """Add a transaction record"""
        cursor = self.connection.cursor()
        try:
            query = """
                INSERT INTO Transaction 
                (transaction_type, transaction_amount, description, Bank_id, Stock_id, Bond_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (transaction_type, amount, description,
                                   bank_id, stock_id, bond_id))
            transaction_id = cursor.lastrowid
            logger.info(f"Added transaction with ID: {transaction_id}")
            return transaction_id
        except Error as e:
            logger.error(f"Error adding transaction: {e}")
            return None
        finally:
            cursor.close()

    def get_user_portfolio_summary(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get complete portfolio summary for a user"""
        cursor = self.connection.cursor(dictionary=True)
        try:
            # Get portfolio info
            cursor.execute("SELECT * FROM User_portfolio WHERE User_id = %s", (user_id,))
            portfolio = cursor.fetchone()

            if not portfolio:
                return None

            # Get bank accounts
            cursor.execute("SELECT * FROM Bank_Account WHERE User_id = %s", (user_id,))
            bank_accounts = cursor.fetchall()

            # Get stocks
            cursor.execute("SELECT * FROM Stocks WHERE user_id = %s", (user_id,))
            stocks = cursor.fetchall()

            # Get bonds
            cursor.execute("SELECT * FROM Bonds WHERE user_id = %s", (user_id,))
            bonds = cursor.fetchall()

            return {
                'portfolio': portfolio,
                'bank_accounts': bank_accounts,
                'stocks': stocks,
                'bonds': bonds
            }

        except Error as e:
            logger.error(f"Error getting portfolio summary: {e}")
            return None
        finally:
            cursor.close()

    def update_stock_price(self, stock_id: int, new_price: Decimal) -> bool:
        """Update current stock price"""
        cursor = self.connection.cursor()
        try:
            query = "UPDATE Stocks SET current_price_per_share = %s WHERE stock_id = %s"
            cursor.execute(query, (new_price, stock_id))
            logger.info(f"Updated stock {stock_id} price to {new_price}")
            return True
        except Error as e:
            logger.error(f"Error updating stock price: {e}")
            return False
        finally:
            cursor.close()

    def get_portfolio_value(self, user_id: int) -> Optional[Decimal]:
        """Calculate total portfolio value"""
        cursor = self.connection.cursor()
        try:
            query = """
                SELECT 
                    COALESCE(SUM(ba.Current_balance), 0) as bank_total,
                    COALESCE(SUM(s.Number_of_shares * COALESCE(s.current_price_per_share, s.Purchase_price_per_share)), 0) as stock_total,
                    COALESCE(SUM(b.Bond_amount * b.number_of_bonds), 0) as bond_total
                FROM User_portfolio up
                LEFT JOIN Bank_Account ba ON up.User_id = ba.User_id
                LEFT JOIN Stocks s ON up.User_id = s.user_id
                LEFT JOIN Bonds b ON up.User_id = b.user_id
                WHERE up.User_id = %s
                GROUP BY up.User_id
            """
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()

            if result:
                total_value = sum(result)
                return Decimal(str(total_value))
            return Decimal('0.00')

        except Error as e:
            logger.error(f"Error calculating portfolio value: {e}")
            return None
        finally:
            cursor.close()


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

        # Example usage
        print("\n--- Example Usage ---")

        # Create a user portfolio
        user_id = db.create_user_portfolio('USD')
        if user_id:
            print(f"Created user portfolio: {user_id}")

            # Add a bank account
            bank_id = db.add_bank_account(
                user_id=user_id,
                account_name="Main Checking",
                account_type="Checking",
                date_created=date.today(),
                current_balance=Decimal('5000.00'),
                first_balance=Decimal('1000.00')
            )

            # Add a stock holding
            stock_id = db.add_stock_holding(
                user_id=user_id,
                symbol="AAPL",
                company_name="Apple Inc.",
                shares=Decimal('100.0000'),
                purchase_price=Decimal('150.25'),
                purchase_date=date.today(),
                current_price=Decimal('165.80')
            )

            # Add a transaction
            if bank_id:
                db.add_transaction(
                    transaction_type="Deposit",
                    amount=Decimal('5000.00'),
                    description="Initial deposit",
                    bank_id=bank_id
                )

            # Get portfolio summary
            summary = db.get_user_portfolio_summary(user_id)
            if summary:
                print(f"\nPortfolio Summary for User {user_id}:")
                print(f"Bank Accounts: {len(summary['bank_accounts'])}")
                print(f"Stock Holdings: {len(summary['stocks'])}")
                print(f"Bond Holdings: {len(summary['bonds'])}")

                # Calculate total value
                total_value = db.get_portfolio_value(user_id)
                print(f"Total Portfolio Value: ${total_value}")

    finally:
        # Always disconnect
        db.disconnect()


if __name__ == "__main__":
    main()