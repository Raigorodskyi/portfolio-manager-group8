import dash
from dash import html, dcc, Input, Output, State
import plotly.graph_objs as go
import yfinance as yf
import pandas as pd
import datetime

app = dash.Dash(__name__)

# Your portfolio holdings with quantities TODO Fetch this data from DB
owned_stocks = [
    {"ticker": "AAPL", "quantity": 10, "purchased_date": "2025-05-20", "purchased_cost": 400},
    {"ticker": "MSFT", "quantity": 5, "purchased_date": "2025-05-20", "purchased_cost": 120},
    {"ticker": "TSLA", "quantity": 5, "purchased_date": "2025-05-20", "purchased_cost": 100},
    {"ticker": "HST", "quantity": 5, "purchased_date": "2025-05-20", "purchased_cost": 100},
    {"ticker": "BTC-USD", "quantity": 5, "purchased_date": "2025-05-20", "purchased_cost": 8000}
]

def fetch_portfolio_data(owned):
    tickers = [s["ticker"] for s in owned]
    data = yf.download(tickers, period="2d", progress=False)
    close = data["Close"]

    updated_owned = []
    gainers = []
    losers = []

    for stock in owned:
        ticker = stock["ticker"]
        quantity = stock["quantity"]
        purchased_cost = stock["purchased_cost"]

        try:
            prev_price = close[ticker].iloc[-2]
            curr_price = close[ticker].iloc[-1]
            change_pct = ((curr_price - prev_price) / prev_price) * 100
            total_value = curr_price * quantity

            if total_value - purchased_cost > 0:
                trend ="▲"
            elif total_value - purchased_cost == 0:
                trend = "➖"
            else:
                trend = "🔻"

            updated_owned.append({
                "ticker": ticker,
                "quantity": quantity,
                "price": round(curr_price, 4),
                "value": round(total_value, 4),
                "change": round(change_pct, 4),
                "purchased_date": datetime.date(2025, 5, 25),
                "purchased_cost": purchased_cost,
                "trend": trend
            })

            record = {"ticker": ticker, "change": round(change_pct, 2)}
            if change_pct > 0:
                gainers.append(record)
            elif change_pct < 0:
                losers.append(record)
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")

    gainers.sort(key=lambda x: x["change"], reverse=True)
    losers.sort(key=lambda x: x["change"])
    market_movers = gainers + losers
    market_movers.sort(key=lambda x: abs(x["change"]), reverse=True)

    return updated_owned, gainers, losers, market_movers

updated_owned, gainers, losers, market_movers = fetch_portfolio_data(owned_stocks)
owned_df = pd.DataFrame(updated_owned)

def get_company_name(ticker):
    try:
        return yf.Ticker(ticker).info.get("shortName", ticker)
    except:
        return ticker

owned_df["Name"] = owned_df["ticker"].apply(get_company_name)
owned_df = owned_df[["trend", "Name", "ticker", "quantity", "purchased_date", "purchased_cost", "price", "value"]]
owned_df.columns = ["", "Long Name", "Short Name", "Shares Owned", "Date Purchased", "Purchase Cost", "Current Market Price", "Current Value"]

owned_stocks_table = go.Figure(
    data=[
        go.Table(
            columnwidth=[35, 150, 80, 80, 120, 120, 150, 120, 80],
            header=dict(
                values=[f"<b>{col}</b>" for col in owned_df.columns],
                fill_color='lightgrey',
                align='left',
                font=dict(size=14)
            ),
            cells=dict(
                values=[owned_df[col].tolist() for col in owned_df.columns],
                align='left'
            )
        )
    ]
)

owned_stocks_table.update_layout(
    margin=dict(l=0, r=0, t=20, b=20),
    autosize=True,
)

# Net worth data (placeholder, you can enhance by summing owned stock values over time)
dates = pd.date_range(end=datetime.datetime.today(), periods=30)
net_worth_data = pd.DataFrame({
    "Date": dates,
    "Net Worth": (10000 + (pd.Series(range(30)) * 100) + (pd.Series(range(30)).apply(lambda x: 100 * (x % 5))) * 3)
})

net_worth_chart = go.Figure(
    data=[go.Scatter(x=net_worth_data['Date'], y=net_worth_data['Net Worth'], fill='tozeroy')],
    layout=go.Layout(title='', margin=dict(l=0, r=0, t=10, b=40))
)

income_pie = go.Figure(
    data=[go.Pie(labels=['Stocks', 'Crypto', 'Cash'], values=[60, 25, 15])],
    layout=go.Layout(title='Asset Distribution')
)

spending_pie = go.Figure(
    data=[go.Pie(labels=['Gains', 'Losses'], values=[len(gainers), len(losers)])],
    layout=go.Layout(title='24h Performance')
)

# Format data with arrows
def format_mover(mover):
    change = mover["change"]
    if change > 0:
        return f"🟢 {change:.4f}% ⬆️"
    elif change < 0:
        return f"🔴 {change:.4f}% ⬇️"
    else:
        return f"⚪ {change:.4f}% ➖"

names = [get_company_name(m["ticker"]) for m in market_movers]
tickers = [m["ticker"] for m in market_movers]
changes = [format_mover(m) for m in market_movers]

market_movers_table = go.Figure(
    data=[
        go.Table(
            header=dict(
                values=["<b>Long Name</b>", "<b>Short Name</b>", "<b>Change (24h)</b>"],
                fill_color="lightgrey",
                align="left"
            ),
            cells=dict(
                values=[names, tickers, changes],
                align="left"
            )
        )
    ]
)

market_movers_table.update_layout(
    margin=dict(l=0, r=0, t=20, b=20),
    autosize=True,
)

app.layout = html.Div(style={'display': 'flex', 'fontFamily': 'Arial, sans-serif'}, children=[

    # Left Column - Owned Stocks
    html.Div([
        html.H4("Your Stocks"),
        dcc.Graph(figure=owned_stocks_table, style={'height': '100%', 'width': '100%'})
    ], style={'width': '35%', 'padding': '10px', 'borderRight': '1px solid #ccc', 'display': 'flex',
              'flexDirection': 'column'}),

    # Center Column - Portfolio Performance
    html.Div([
        html.H4("Portfolio Performance"),
        dcc.Graph(figure=net_worth_chart, style={'height': '300px'}),
        html.Div([
            dcc.Graph(figure=income_pie, style={'width': '50%'}),
            dcc.Graph(figure=spending_pie, style={'width': '50%'}),
        ], style={'display': 'flex'}),
        html.Div([
            html.Div([
                html.H5("Top Gainers (24h)"),
                html.Ul([html.Li(f"{g['ticker']} +{g['change']}%") for g in gainers])
            ], style={'width': '50%'}),
            html.Div([
                html.H5("Top Losers (24h)"),
                html.Ul([html.Li(f"{l['ticker']} {l['change']}%") for l in losers])
            ], style={'width': '50%'}),
        ], style={'display': 'flex', 'marginTop': '20px'})
    ], style={'width': '35%', 'padding': '10px'}),

    # Right Column - Market Movers & Search
    html.Div([
        html.H4("Market Movers"),
        dcc.Graph(figure=market_movers_table, style={'height': '100%', 'width': '100%'}),
        html.Br(), html.Br(),
        dcc.Input(id='search-input', type='text', placeholder='Enter stock or crypto'),
        html.Div(id='search-results'),
        html.Br(),
        html.Button("Search to Buy", id="search-button")
    ], style={'width': '30%', 'padding': '10px', 'borderRight': '1px solid #ccc', 'display': 'flex',
              'flexDirection': 'column'})
])

@app.callback(
    Output('search-results', 'children'),
    Input('search-button', 'n_clicks'),
    State('search-input', 'value')
)
def search_stock(n_clicks, query):
    if n_clicks and query:
        try:
            ticker = yf.Ticker(query.upper())
            info = ticker.info
            return html.Div([
                html.P(f"{info.get('shortName', query.upper())} ({query.upper()})"),
                html.P(f"Current Price: ${info.get('currentPrice', 'N/A')}")
            ])
        except Exception as e:
            return html.P(f"Error fetching data for {query.upper()}: {str(e)}")
    return ""

if __name__ == '__main__':
    app.run(debug=True)
