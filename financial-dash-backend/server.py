from flask import Flask, jsonify
import mysql.connector
import yfinance as yf

app = Flask(__name__)

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="n3u3da!",
        database="finance_portfolio"
    )

@app.route('/api/stock_values', methods=['GET'])
def get_stock_value(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch stock ticker and number of shares for the given user
    query = """
        SELECT stock_ticker, number_of_shares
        FROM Stocks;
    """
    cursor.execute(query, (user_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    # Fetch current prices and compute net values
    stock_values = {}
    for row in rows:
        ticker = row['stock_ticker']
        shares = row['Number_of_shares']
        try:
            stock = yf.Ticker(ticker)
            current_price = stock.info['regularMarketPrice']
            stock_values[ticker] = round(current_price * shares, 2)
        except Exception as e:
            stock_values[ticker] = f"Error fetching price: {str(e)}"

    return jsonify(stock_values)
    
@app.route("/user/total_value", methods=["GET"])
def get_total_value(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT total_value FROM User_portfolio WHERE user_ID = %s", (user_id,))
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result:
            return jsonify({"user_id": user_id, "total_value": float(result[0])})
        else:
            return jsonify({"error": "User not found"}), 404

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500

if __name__ == "__main__":
    app.run(debug=True)
