from datetime import datetime
from flask import Flask, jsonify, request
import mysql.connector
import yfinance as yf
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
CORS(app)

# Connect to database
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"), # Use your actual password here
        database=os.getenv("DB_NAME")
    )

# API route that fetches all the user's owned stocks and stock related data
@app.route('/api/stock_values', methods=['GET'])
def get_stock_value():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT stock_ticker, number_of_shares, purchase_price_per_share
        FROM Stocks;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    stock_values = {}
    for row in rows:
        ticker = row['stock_ticker']
        shares = row['number_of_shares']
        purchase_price = row['purchase_price_per_share']
        try:
            stock = yf.Ticker(ticker)
            current_price = stock.info['regularMarketPrice']
            stock_name = stock.info.get('shortName')
            if current_price is not None and stock_name is not None:
                stock_values[ticker] = {
                    'stock_name': stock_name,
                    'purchase_price': float(purchase_price),
                    'shares': shares,
                    'current_price': float(current_price)
                }
            else:
                stock_values[ticker] = {
                    'error': 'Price or name not available',
                    'purchase_price': float(purchase_price),
                    'shares': shares
                }
        except Exception as e:
            stock_values[ticker] = {
                'error': str(e),
                'purchase_price': float(purchase_price),
                'shares': shares
            }
    return jsonify(stock_values)

# API route that fetches the total amount of cash the user has deposited on our platform for buying/selling stocks
@app.route("/api/total_value", methods=["GET"])
def get_total_value():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_ID, total_value FROM User_portfolio")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result:
            return jsonify({"user_id": int(result[0]), "total_value": float(result[1])})
        else:
            return jsonify({"error": "User not found"}), 404
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500

# API route that fetches all the user's owned bonds and bond related data
@app.route('/api/bonds', methods=['GET'])
def get_all_bonds():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT bond_name,bond_ticker , maturity_date, bond_current_price, number_of_bonds
            FROM Bonds
        """)
        bonds = cursor.fetchall()

        result = []

        for bond in bonds:
            ticker = bond['bond_ticker']
            if ticker:
                try:
                    ticker_data = yf.Ticker(ticker)
                    hist = ticker_data.history(period="1d")
                    current_price = hist['Close'][-1] if not hist.empty else None
                except Exception:
                    current_price = None
            else:
                current_price = None

            result.append({
                "Bond Name": bond['bond_name'],
                "Maturity Date": str(bond['maturity_date']),
                "Bond Ticker" : bond['bond_ticker'],
                "Bond Amount (Purchase Price)": float(bond['bond_current_price']),
                "Number of Bonds": bond['number_of_bonds'],
                "Current Market Price": round(float(current_price), 2) if current_price else "Unavailable"
            })

        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
            return jsonify({"error": str(err)}), 500

    return jsonify(result)

# API route that fetches all the user's bank accounts and related data
@app.route("/api/bank_accounts", methods=["GET"])
def get_bank_accounts():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT bank_account_name, bank_account_type 
            FROM Bank_Account 
        """)

        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        if rows:
            accounts = [
                {"bank_account_name": name, "bank_account_type": acc_type}
                for name, acc_type in rows
            ]
            return jsonify({ "bank_accounts": accounts})
        else:
            return jsonify({"error": "No bank accounts found for this user"}), 404

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    
# API that verifies whether a stock ticker exists through yfinance
@app.route("/api/stock_value_from_ticker/<string:ticker>", methods=["GET"])
def get_stock_value_from_ticker(ticker):
    ticker = ticker.upper()

    try:
        shares = int(request.args.get("shares", 0))
    except (TypeError, ValueError):
        shares = 0

    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        stock_name = info.get("shortName")
        current_price = info.get("regularMarketPrice")

        if stock_name and current_price:
            stock_values = {}
            stock_values[ticker.replace("\n","")] = {
                'stock_name': stock_name,
                'shares': shares,
                'current_price': float(current_price)
            }
            return jsonify(stock_values)
        else:
            return jsonify({
                "ticker": ticker,
                "error": "Could not fetch stock data"
            }), 404
    except Exception as e:
        return jsonify({"ticker": ticker, "error": str(e)}), 500
    

# API to allow the user to sell a stock of their choice
@app.route("/api/sell_stock", methods=["POST"])
def sell_stock():
    data = request.get_json()
    quantity_to_sell = int(data.get("quantity", 0))
    stock_ticker = data.get("stock_ticker", "").upper()
    bank_id = int(data.get("bank_id", 0))

    if quantity_to_sell <= 0 or not stock_ticker or bank_id <= 0:
        return jsonify({"error": "Invalid input"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Get stock record from DB
        cursor.execute("""
            SELECT stock_id, number_of_shares, purchase_price_per_share, transaction_id
            FROM Stocks
            WHERE stock_ticker = %s
        """, (stock_ticker,))
        stock_row = cursor.fetchone()

        if not stock_row:
            return jsonify({"error": "Stock not found"}), 404
        if stock_row['number_of_shares'] < quantity_to_sell:
            return jsonify({"error": "Not enough shares to sell"}), 400

        # Get current market price from yfinance
        stock_data = yf.Ticker(stock_ticker)
        current_price = stock_data.info.get("regularMarketPrice")
        if not current_price:
            return jsonify({"error": "Unable to fetch current stock price"}), 500

        sale_value = quantity_to_sell * current_price

        # Update or delete stock in DB
        if stock_row['number_of_shares'] == quantity_to_sell:
            cursor.execute("DELETE FROM Stocks WHERE stock_id = %s", (stock_row['stock_id'],))
        else:
            cursor.execute("""
                UPDATE Stocks
                SET number_of_shares = number_of_shares - %s
                WHERE stock_id = %s
            """, (quantity_to_sell, stock_row['stock_id']))

        # Update bank account balance
        cursor.execute("""
            UPDATE Bank_Account
            SET current_balance = current_balance + %s
            WHERE bank_id = %s
        """, (sale_value, bank_id))

        # Update user portfolio total_value
        cursor.execute("""
            UPDATE User_portfolio
            SET total_value = total_value + %s
            WHERE user_id = (
                SELECT user_id FROM Bank_Account WHERE bank_id = %s
            )
        """, (sale_value, bank_id))

        # Insert into transaction table
        cursor.execute("""
            INSERT INTO Transaction (bank_id, date)
            VALUES (%s, %s)
        """, (bank_id, datetime.now()))
        transaction_id = cursor.lastrowid

        conn.commit()

        return jsonify({
            "message": "Stock sold successfully",
            "stock_ticker": stock_ticker,
            "quantity_sold": quantity_to_sell,
            "sale_value": sale_value,
            "transaction_id": transaction_id
        })

    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    app.run(debug=True)