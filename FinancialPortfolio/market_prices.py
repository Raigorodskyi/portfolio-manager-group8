# import yfinance as yf
#
# # List of top stock symbols (tickers)
# top_stocks = {
#     "Apple": "AAPL",
#     "Microsoft": "MSFT",
#     "Tesla": "TSLA",
#     "Amazon": "AMZN",
#     "Google": "GOOGL",
#     "Bitcoin": "BTC-USD",
#     "NIVIDIA Corporation": "NVDA",
# }
#
# # Fetch stock data
# def fetch_stock_prices(tickers):
#     prices = {}
#     for name, symbol in tickers.items():
#         stock = yf.Ticker(symbol)
#         data = stock.history(period="1d")
#         if not data.empty:
#             last_price = data['Close'].iloc[-1]
#             prices[name] = round(last_price, 2)
#         else:
#             prices[name] = "N/A"
#     return prices
#
# # Display the prices
# if __name__ == "__main__":
#     prices = fetch_stock_prices(top_stocks)
#     print("Top Stock Prices:")
#     for name, price in prices.items():
#         print(f"{name}: ${price}")


import pandas as pd
import yfinance as yf

def get_sp500_tickers_and_names():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    table = pd.read_html(url, header=0)[0]  # Get first table on the page
    symbols = table['Symbol']
    companies = table['Security']
    return list(zip(symbols, companies))  # List of (Symbol, Company Name)

# Fetch data
sp500 = get_sp500_tickers_and_names()

# Download prices using yfinance
tickers = [symbol for symbol, _ in sp500]
prices = yf.download(tickers, period="1d")['Close']

# Show paired output
print("Latest Closing Prices:")
for i, (symbol, name) in enumerate(sp500):
    try:
        price = prices[symbol].iloc[-1]
        print(f"{name} ({symbol}): ${price:.2f}")
    except:
        print(f"{name} ({symbol}): Price not available")
