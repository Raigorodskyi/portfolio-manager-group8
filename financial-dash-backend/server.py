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
    
# API route that returns the list of user's transactions
@app.route('/api/transactions', methods=['POST'])
def get_all_transactions():
    try:
        data = request.get_json()
        bank_id = data.get('bank_id')  # Default to bank ID 1 if not provided
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT transaction_ID, date, amount
            FROM Transaction
            WHERE bank_ID = %s
            ORDER BY date DESC
        """, (bank_id,))
        transactions = cursor.fetchall()

        result = []
        for tx in transactions:
            result.append({
                "Transaction ID": tx['transaction_ID'],
                "Date": tx['date'].strftime("%Y-%m-%d %H:%M:%S"),
                "Amount": tx['amount']
            })

        cursor.close()
        conn.close()

        return jsonify(result)

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500   
    
# API route that fetches all the user's owned bonds and bond related data
@app.route('/api/bonds', methods=['GET'])
def get_all_bonds():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT bond_name, bond_ticker, purchase_price_per_bond, bond_yield, number_of_bonds
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
                "Bond Ticker": bond['bond_ticker'],
                "Purchase Price per Bond": float(bond['purchase_price_per_bond']),
                "Bond Yield (%)": float(bond['bond_yield']),
                "Number of Bonds": bond['number_of_bonds'],
                "Current Market Price (from YFinance)": round(float(current_price), 2) if current_price else "Unavailable"
            })

        cursor.close()
        conn.close()

        return jsonify(result)

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500

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

# Function that handles user's action to view a stock
def view_stock_action(data):
    ticker = data.get("stock_ticker", "").upper()
    shares = int(data.get("number_of_shares", 0))

    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        stock_name = info.get("shortName")
        current_price = info.get("regularMarketPrice")
        
        if stock_name and current_price:
            return {
                "stock_ticker": ticker,
                "stock_name": stock_name,
                "current_price": float(current_price)
            }
        else:
            return {"error": "Could not fetch stock data"}, 404
    except Exception as e:
        return {"error": str(e)}, 500

# Function that handles a user's request to sell a stock
def sell_stock_action(data):
    stock_ticker = data.get("stock_ticker", "").upper()
    quantity_to_sell = int(data.get("number_of_shares", 0))
    bank_id = int(data.get("bank_ID", 0))
    purchase_price = float(data.get("purchase_price_per_share", 0))

    if quantity_to_sell <= 0 or not stock_ticker or bank_id <= 0:
        return {"error": "Invalid input"}, 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT stock_id, number_of_shares, purchase_price_per_share
            FROM Stocks
            WHERE stock_ticker = %s and purchase_price_per_share = %s
        """, (stock_ticker, purchase_price))
        stock_row = cursor.fetchone()

        if not stock_row:
            return {"error": "Stock not found"}, 404
        if stock_row['number_of_shares'] < quantity_to_sell:
            return {"error": "Not enough shares to sell"}, 400

        stock_data = yf.Ticker(stock_ticker)
        current_price = stock_data.info.get("regularMarketPrice")
        if not current_price:
            return {"error": "Unable to fetch stock price"}, 500

        sale_value = quantity_to_sell * current_price

        # Update Stocks table
        if stock_row['number_of_shares'] == quantity_to_sell:
            cursor.execute("DELETE FROM Stocks WHERE stock_id = %s", (stock_row['stock_id'],))
        else:
            cursor.execute("""
                UPDATE Stocks SET number_of_shares = number_of_shares - %s
                WHERE stock_id = %s
            """, (quantity_to_sell, stock_row['stock_id']))

        # Update Bank and Portfolio
        cursor.execute("""
            UPDATE Bank_Account SET current_balance = current_balance + %s
            WHERE bank_id = %s
        """, (sale_value, bank_id))

        cursor.execute("""
            UPDATE User_portfolio SET total_value = total_value + %s
            WHERE user_id = (SELECT user_id FROM Bank_Account WHERE bank_id = %s)
        """, (sale_value, bank_id))

        # Record transaction
        cursor.execute("""
            INSERT INTO Transaction (bank_id, date, amount)
            VALUES (%s, %s, %s)
        """, (bank_id, datetime.now(), sale_value))
        transaction_id = cursor.lastrowid

        conn.commit()
        return {
            "message": "Stock sold successfully",
            "stock_ticker": stock_ticker,
            "quantity_sold": quantity_to_sell,
            "sale_value": sale_value,
            "transaction_id": transaction_id
        }, 200

    except mysql.connector.Error as err:
        conn.rollback()
        return {"error": str(err)}, 500
    finally:
        cursor.close()
        conn.close()

# Function that handles a user's request to buy a stock
def buy_stock_action(data):
    stock_ticker = data.get('stock_ticker')
    number_of_shares = int(data.get('number_of_shares', 0))
    bank_ID = int(data.get('bank_ID', 0))

    if not all([stock_ticker, number_of_shares, bank_ID]):
        return {'error': 'Missing required fields'}, 400

    try:
        ticker = yf.Ticker(stock_ticker)
        stock_current_price = ticker.history(period="1d")['Close'].iloc[-1]
    except Exception as e:
        return {"error": f"Failed to fetch stock price: {str(e)}"}, 500

    total_cost = stock_current_price * number_of_shares
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        now = datetime.now()
        cursor.execute("""
            INSERT INTO Transaction (bank_ID, date, amount)
            VALUES (%s, %s, %s)
        """, (bank_ID, now, total_cost))
        transaction_ID = cursor.lastrowid

        cursor.execute("""
            INSERT INTO Stocks (
                transaction_ID, number_of_shares, purchase_price_per_share,
                current_price_per_share, purchase_date, stock_ticker
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            transaction_ID, number_of_shares, stock_current_price,
            stock_current_price, now, stock_ticker
        ))

        cursor.execute("SELECT total_value FROM User_portfolio")
        user_portfolio = cursor.fetchone()
        if not user_portfolio:
            return {"error": "User not found"}, 404

        new_total_value = float(user_portfolio['total_value']) - float(total_cost)

        cursor.execute("SELECT current_balance FROM Bank_Account WHERE bank_ID = %s", (bank_ID,))
        bank_account = cursor.fetchone()
        if not bank_account:
            return {"error": "Bank account not found"}, 404
        new_bank_balance = float(bank_account['current_balance']) - total_cost

        if new_bank_balance < 0:
            cursor.execute("SELECT bank_account_name FROM Bank_Account WHERE bank_id = %s", (bank_ID,))
            error_bank_name = cursor.fetchone()
            return {"error": f"Not enough cash in {error_bank_name['bank_account_name']}"}, 400

        cursor.execute("""
            UPDATE User_portfolio
            SET total_value = %s, updated_at = %s
        """, (new_total_value, now))

        cursor.execute("""
            UPDATE Bank_Account
            SET current_balance = %s, bank_account_last_updated = %s
            WHERE bank_ID = %s
        """, (new_bank_balance, now, bank_ID))

        conn.commit()
        return {
            "message": "Stock purchased successfully",
            "stock_ticker": stock_ticker,
            "quantity_sold": number_of_shares,
            "sale_value": total_cost,
            "transaction_id": transaction_ID
        }, 200

    except Exception as e:
        conn.rollback()
        return {'error': str(e)}, 500
    finally:
        cursor.close()
        conn.close()

# API route that lets a user either buy/sell/view a stock based on action 
@app.route("/api/stock_action", methods=["POST"])
def stock_action():
    data = request.get_json()
    action = data.get("action", "").lower()

    if action == "buy":
        result = buy_stock_action(data)
    elif action == "sell":
        result = sell_stock_action(data)
    elif action == "view":
        result = view_stock_action(data)
    else:
        return jsonify({"error": "Invalid action"}), 400

    if isinstance(result, tuple):
        return jsonify(result[0]), result[1]
    else:
        return jsonify(result)

# Function that processes a user's sell request
def sell_bond(bond_ticker, quantity_to_sell, bank_id, purchase_price):
    if quantity_to_sell <= 0 or not bond_ticker or bank_id <= 0:
        return jsonify({"error": "Invalid input"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT bond_ID, bond_name, bond_ticker, purchase_price_per_bond, bond_yield, 
                   number_of_bonds, dividend_frequency, transaction_ID
            FROM Bonds
            WHERE bond_ticker = %s and purchase_price_per_bond = %s
        """, (bond_ticker, purchase_price))
        bond_row = cursor.fetchone()

        if not bond_row:
            return jsonify({"error": "Bond not found"}), 404
        if bond_row['number_of_bonds'] < quantity_to_sell:
            return jsonify({"error": "Not enough bonds to sell"}), 400
        
        bond_data = yf.Ticker(bond_ticker)
        current_price = bond_data.info.get("regularMarketPrice", bond_row['purchase_price_per_bond'])
        if not current_price:
            return jsonify({"error": "Unable to fetch current bond price"}), 500
      
        sale_value = round((quantity_to_sell * current_price), 2)

        if bond_row['number_of_bonds'] == quantity_to_sell:
            cursor.execute("DELETE FROM Bonds WHERE bond_ID = %s", (bond_row['bond_ID'],))
        else:
            cursor.execute("""
                UPDATE Bonds
                SET number_of_bonds = number_of_bonds - %s
                WHERE bond_ID = %s
            """, (quantity_to_sell, bond_row['bond_ID']))
      
        cursor.execute("""
            UPDATE Bank_Account
            SET current_balance = current_balance + %s
            WHERE bank_id = %s
        """, (sale_value, bank_id))

        cursor.execute("""
            UPDATE User_portfolio
            SET total_value = total_value + %s
            WHERE user_id = (
                SELECT user_id FROM Bank_Account WHERE bank_id = %s
            )
        """, (sale_value, bank_id))

        cursor.execute("""
            INSERT INTO Transaction (bank_id, date, amount)
            VALUES (%s, %s, %s)
        """, (bank_id, datetime.now(), sale_value))
        transaction_id = cursor.lastrowid

        conn.commit()

        return jsonify({
            "message": "Bond sold successfully",
            "bond_ticker": bond_ticker,
            "quantity_sold": quantity_to_sell,
            "market_value": quantity_to_sell * current_price,
            "sale_value": sale_value,
            "transaction_id": transaction_id
        })

    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()
        
# Function that processes a user buy request for a bond
def buy_bond(bond_ticker, number_of_bonds, bank_id):
    if not bond_ticker or number_of_bonds <= 0 or bank_id <= 0:
        return jsonify({"error": "Invalid input"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        bond_data = yf.Ticker(bond_ticker)
        current_price = bond_data.info.get("regularMarketPrice")
        if not current_price:
            return jsonify({"error": "Unable to fetch bond price"}), 500

        bond_name = bond_data.info.get("shortName", bond_ticker)
        bond_yield = bond_data.info.get("yield", 3.0)
        dividend_frequency = bond_data.info.get("dividendFrequency", "Annual")

        total_cost = round(current_price * number_of_bonds, 2)
      
        cursor.execute("""
            SELECT current_balance FROM Bank_Account
            WHERE bank_ID = %s
        """, (bank_id,))
        bank = cursor.fetchone()

        if not bank:
            return jsonify({"error": "Bank account not found"}), 404
        if bank['current_balance'] < total_cost:
            return jsonify({"error": "Insufficient bank balance"}), 400
        
        cursor.execute("""
            INSERT INTO Transaction (bank_ID, date, amount)
            VALUES (%s, %s, %s)
        """, (bank_id, datetime.now(), total_cost))
        transaction_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO Bonds (
                bond_name, bond_ticker, purchase_price_per_bond, bond_yield,
                number_of_bonds, dividend_frequency, last_updated, transaction_ID
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            bond_name,
            bond_ticker,
            current_price,
            bond_yield,
            number_of_bonds,
            dividend_frequency,
            datetime.now(),
            transaction_id
        ))

        cursor.execute("""
            UPDATE Bank_Account
            SET current_balance = current_balance - %s
            WHERE bank_ID = %s
        """, (total_cost, bank_id))

        cursor.execute("""
            UPDATE User_portfolio
            SET total_value = total_value - %s
        """, (total_cost,))

        conn.commit()

        return jsonify({
            "message": "Bond purchased successfully",
            "bond_ticker": bond_ticker,
            "quantity_bought": number_of_bonds,
            "purchase_price": current_price,
            "total_cost": total_cost,
            "transaction_id": transaction_id
        })

    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

# Function that deals with user's request to a view a particular bond
def view_bond(ticker):
    ticker = ticker.upper()

    try:
        num_bonds = int(request.args.get("number_of_bonds", 0))
    except (TypeError, ValueError):
        num_bonds = 0

    try:       
        try:
            purchase_price = float(request.args.get("purchase_price_per_bond", 0))
        except (TypeError, ValueError):
            purchase_price = 0
       
        bond = yf.Ticker(ticker)
        info = bond.info

        bond_name = info.get("shortName", "").replace("\n", "").strip()
        current_price = info.get("regularMarketPrice")
        bond_yield = info.get("yield")  

        if bond_name and current_price:
            bond_values = {}
            bond_values[ticker] = {
                'bond_ticker': ticker,
                'bond_name': bond_name,
                'current_price': round(float(current_price), 2),
                'bond_yield': round(float(bond_yield), 2) if bond_yield else None
            }
            return jsonify(bond_values)
        else:
            return jsonify({
                "ticker": ticker,
                "error": "Could not fetch bond data"
            }), 404
    except Exception as e:
        return jsonify({"ticker": ticker, "error": str(e)}), 500
    
# API route that deals with bond actions where an action can be either buying, selling, or viewing a bond
@app.route("/api/bond_action", methods=["POST"])
def bond_action():
    data = request.get_json()
    action = data['action']
    ticker = data['bond_ticker']
    quantity = data['number_of_bonds']
    bank_id = data['bank_ID']
    purchase_price = data['purchase_price_per_bond']
    
    if action == 'buy':
        return buy_bond(ticker, quantity, bank_id)
    elif action == 'sell':
        return sell_bond(ticker, quantity, bank_id, purchase_price)
    elif action == 'view':
        return view_bond(ticker)
    else:
        return jsonify({
                "ticker": ticker,
                "error": "Invalid action: must be one of 'buy', 'sell', or 'view'"
            }), 400

if __name__ == "__main__":
    app.run(debug=True)