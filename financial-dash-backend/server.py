from flask import Flask, jsonify
import mysql.connector
import yfinance as yf
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Connect to database
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="n3u3da!",
        database="finance_portfolio"
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


if __name__ == "__main__":
    app.run(debug=True)