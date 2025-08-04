from datetime import datetime
from flask import Flask, jsonify, request
from flask import Flask, jsonify, request
import mysql.connector
import yfinance as yf
from flask_cors import CORS
from dotenv import load_dotenv
import os
from datetime import datetime


load_dotenv()
app = Flask(__name__)
CORS(app)

# Connect to database
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
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


@app.route('/api/buy_bond', methods=['POST'])
def buy_bond():
    data = request.get_json()

    bond_ticker = data.get('bond_ticker')
    bond_name = data.get('bond_name')
    coupon_rate = data.get('coupon_rate')
    number_of_bonds = data.get('number_of_bonds')
    maturity_date = data.get('maturity_date')
    bank_ID = data.get('bank_ID')
    user_ID = data.get('user_ID')
    if not all([bond_ticker, bond_name, coupon_rate, number_of_bonds, maturity_date, bank_ID, user_ID]):
        return jsonify({"error": "Missing fields"}), 400
    try:
            bond_info = yf.Ticker(bond_ticker)
            bond_current_price = bond_info.history(period="1d")['Close'].iloc[-1]
    except Exception as e:
            return jsonify({"error": f"Failed to fetch bond price: {str(e)}"}), 500
    total_cost = bond_current_price * number_of_bonds
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
       
        now = datetime.now()
        cursor.execute("""
            INSERT INTO Transaction (bank_ID, date)
            VALUES (%s, %s)
        """, (bank_ID, now))
        transaction_ID = cursor.lastrowid

    
        cursor.execute("SELECT * FROM Bonds WHERE bond_ticker = %s", (bond_ticker,))
        existing_bond = cursor.fetchone()

        if existing_bond:
            new_total = existing_bond['number_of_bonds'] + number_of_bonds

            cursor.execute("""
                UPDATE Bonds
                SET number_of_bonds = %s,
                    bond_current_price = %s,
                    transaction_ID = %s
                WHERE bond_ticker = %s
            """, (new_total, bond_current_price, transaction_ID, bond_ticker))

        else:
            
            cursor.execute("""
                INSERT INTO Bonds (bond_name, bond_ticker, bond_current_price, coupon_rate, number_of_bonds, maturity_date, transaction_ID)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (bond_name, bond_ticker, bond_current_price, coupon_rate, number_of_bonds, maturity_date, transaction_ID))
        cursor.execute("SELECT total_value FROM User_portfolio WHERE user_ID = %s", (user_ID,))
        user_portfolio = cursor.fetchone()

        if not user_portfolio:
            return jsonify({"error": "User not found"}), 404

        new_value = float(user_portfolio['total_value']) - float(total_cost)

        cursor.execute("""
            UPDATE User_portfolio
            SET total_value = %s,
                updated_at = %s
            WHERE user_ID = %s
        """, (new_value, now, user_ID))
        cursor.execute("SELECT current_balance FROM Bank_Account WHERE bank_ID = %s", (bank_ID,))
        bank_account = cursor.fetchone()

        if not bank_account:
            return jsonify({"error": "Bank account not found"}), 404

        new_bank_balance = float(bank_account['current_balance']) - total_cost

        cursor.execute("""
            UPDATE Bank_Account
            SET current_balance = %s,
                bank_account_last_updated = %s
            WHERE bank_ID = %s
        """, (new_bank_balance, now, bank_ID))

        conn.commit()
        return jsonify({"message": "Bond purchased and portfolio updated"}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

@app.route('/api/buy_stock', methods=['POST'])
def buy_stock():
    data = request.get_json()
    stock_ticker = data.get('stock_ticker')
    number_of_shares = data.get('number_of_shares')
    purchase_date = data.get('purchase_date')
    bank_ID = data.get('bank_ID')
    user_ID = data.get('user_ID')
    if not all([stock_ticker, number_of_shares, purchase_date, bank_ID, user_ID]):
        return jsonify({'error': 'Missing required fields'}), 400
    try:
        ticker = yf.Ticker(stock_ticker)
        stock_current_price = ticker.history(period="1d")['Close'].iloc[-1]
    except Exception as e:
        return jsonify({"error": f"Failed to fetch stock price: {str(e)}"}), 500

    total_cost = stock_current_price * number_of_shares

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        now = datetime.now()
        cursor.execute("""
            INSERT INTO Transaction (bank_ID, date)
            VALUES (%s, %s)
        """, (bank_ID, now))
        transaction_ID = cursor.lastrowid
       
        cursor.execute("SELECT * FROM Stocks WHERE stock_ticker = %s", (stock_ticker,))
        existing_stock = cursor.fetchone()

        if existing_stock:
            new_total = (existing_stock['number_of_shares'] + number_of_shares) 
            total_cost = stock_current_price *  (existing_stock['number_of_shares'] + number_of_shares) 
            avg_price = total_cost / new_total
            cursor.execute("""
                UPDATE Stocks
                SET number_of_shares = %s,
                    purchase_price_per_share = %s,
                    current_price_per_share = %s,
                    updated_at_date = %s
                WHERE stock_ticker = %s
            """, (new_total, round(avg_price, 2), stock_current_price , now, stock_ticker))
        else:
        
            cursor.execute("""
                INSERT INTO Stocks (
                    transaction_ID,
                    number_of_shares,
                    purchase_price_per_share,
                    current_price_per_share,
                    purchase_date,
                    stock_ticker
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                transaction_ID,
                number_of_shares,
                stock_current_price ,
                stock_current_price ,
                purchase_date,
                stock_ticker
            ))

        
        cursor.execute("SELECT total_value FROM User_portfolio WHERE user_ID = %s", (user_ID,))
        user_portfolio = cursor.fetchone()

        if not user_portfolio:
            return jsonify({"error": "User not found"}), 404

        new_total_value = float(user_portfolio['total_value']) - float(total_cost)

        cursor.execute("""
            UPDATE User_portfolio
            SET total_value = %s,
                updated_at = %s
            WHERE user_ID = %s
        """, (new_total_value, now, user_ID))
        cursor.execute("SELECT current_balance FROM Bank_Account WHERE bank_ID = %s", (bank_ID,))
        bank_account = cursor.fetchone()

        if not bank_account:
            return jsonify({"error": "Bank account not found"}), 404

        new_bank_balance = float(bank_account['current_balance']) - total_cost

        cursor.execute("""
            UPDATE Bank_Account
            SET current_balance = %s,
                bank_account_last_updated = %s
            WHERE bank_ID = %s
        """, (new_bank_balance, now, bank_ID))

        conn.commit()
        return jsonify({"message": "Stock purchase recorded, bank account and portfolio updated"}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500

    finally:
        cursor.close()
        conn.close()
        
        
if __name__ == "__main__":
    app.run(debug=True)