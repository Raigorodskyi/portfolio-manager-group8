import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State
import plotly.graph_objs as go
import yfinance as yf
import pandas as pd
import datetime
import mysql.connector
from decimal import Decimal

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

# Your portfolio holdings with quantities TODO Fetch this data from DB
owned_stocks = [
    {"ticker": "AAPL", "quantity": 5, "purchased_date": "2025-05-20", "purchased_cost": 400},
    {"ticker": "MSFT", "quantity": 5, "purchased_date": "2025-05-20", "purchased_cost": 120},
    {"ticker": "TSLA", "quantity": 5, "purchased_date": "2025-05-20", "purchased_cost": 100},
    {"ticker": "HST", "quantity": 5, "purchased_date": "2025-05-20", "purchased_cost": 100},
]

def fetch_value():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='n3u3da!',
        database='financial_portfolio'
    )
    cursor = connection.cursor(dictionary=True)

    query = "SELECT total_value FROM user_portfolio where User_id = 1"
    cursor.execute(query)
    result = cursor.fetchall()

    cursor.close()
    connection.close()
    # Convert Decimal to float
    value = float(result[0]['total_value'])

    return value

def fetch_portfolio_data(owned):
    tickers = [s["ticker"] for s in owned]
    data = yf.download(tickers, period="2d", progress=False)
    close = data["Close"]

    updated_owned = []
    gainers = []
    losers = []
    global_value = 0
    previous_global_value = 0

    for stock in owned:
        ticker = stock["ticker"]
        quantity = stock["quantity"]
        purchased_cost = stock["purchased_cost"]

        try:
            prev_price = close[ticker].iloc[-2]
            curr_price = close[ticker].iloc[-1]
            change_pct = ((curr_price - prev_price) / prev_price) * 100
            total_value = curr_price * quantity
            global_value += total_value
            previous_global_value += prev_price * quantity

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

    if global_value - previous_global_value >= 0:
        daily_profit = html.P("+${}".format(round(global_value - previous_global_value, 4)), className="text-success")
    else:
        daily_profit = html.P("-${}".format(round(global_value - previous_global_value, 4)), className="text-error")

    return updated_owned, gainers, losers, market_movers, global_value, daily_profit, previous_global_value

updated_owned, gainers, losers, market_movers, global_value, daily_profit, previous_global_value = fetch_portfolio_data(owned_stocks)
owned_df = pd.DataFrame(updated_owned)

def get_company_name(ticker):
    try:
        return yf.Ticker(ticker).info.get("shortName", ticker)
    except:
        return ticker

owned_df["Name"] = owned_df["ticker"].apply(get_company_name)
owned_df = owned_df[["trend", "Name", "ticker", "quantity", "purchased_date", "purchased_cost", "price", "value"]]
owned_df.columns = ["", "Long Name", "Short Name", "Shares Owned", "Date Purchased", "Purchase Cost", "Current Market Price", "Current Value"]

# Color-code values based on trend
trend_colors = []
for trend in owned_df[""]:
    if trend == "📈":
        trend_colors.append("green")
    elif trend == "📉":
        trend_colors.append("red")
    else:
        trend_colors.append("gray")

# Zebra striping
fill_colors = []
for i in range(len(owned_df)):
    row_color = "#f9f9f9" if i % 2 == 0 else "white"
    fill_colors.append([row_color] * len(owned_df.columns))

# Add custom styling to the table
owned_stocks_table = go.Figure(
    data=[
        go.Table(
            columnwidth=[35*3, 150*3, 80*3, 80*3, 120*3, 120*3, 150*3, 120*3],
            header=dict(
                values=[f"<b>{col}</b>" for col in owned_df.columns],
                fill_color='#1f2c56',
                font=dict(color='white', size=14),
                align='center',
                line_color='darkslategray'
            ),
            cells=dict(
                values=[owned_df[col].tolist() for col in owned_df.columns],
                fill_color=[["white" if i % 2 else "#f4f4f4"] * len(owned_df) for i in range(len(owned_df.columns))],
                align=['center'] + ['left'] * (len(owned_df.columns) - 1),
                font=dict(size=13),
                line_color='lightgrey',
                height=30,
            )
        )
    ]
)

owned_stocks_table.update_layout(
    margin=dict(l=0, r=0, t=20, b=20),
    autosize=True,
)

#Navbar
header = dbc.NavbarSimple(
            brand="My Financial Portfolio",
            color="dark",
            dark=True,
            children=[
                dbc.NavItem(dbc.NavLink("Overview", href="#")),
                dbc.NavItem(dbc.NavLink("Global Market", href="#")),
                dbc.NavItem(dbc.NavLink("My Profile", href="#")),
            ],
        )

home_layout = dbc.Container(
        fluid=True,
        style={"background": "linear-gradient(to bottom right, #3f0d99, #b702bf)", "minHeight": "100vh", "padding": "2rem"},
        children=[
           # header,
            # Overview Card - Full Width
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Portfolio Value", className="text-info"),
                            html.H2("${}".format(round(global_value, 4)), className="text-white"),
                            html.H3("${}".format(fetch_value()), className="text-white"),
                            # html.P("${}".format(round(global_value - previous_global_value, 4)), className="text-success"),
                            daily_profit,
                            html.P("+17.5% Total Return", className="text-primary"),
                            html.P("Active Positions: 5", className="text-warning"),
                        ])
                    ], style={"marginBottom": "1rem", "background": "#1a1a2e"}),
                ], width=12)
            ]),

            # Bottom Two Columns
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Top Performers", className="text-light"),
                            html.Ul([
                                html.Li("AAPL - $9,266 (+1.34%)"),
                                html.Li("GOOGL - $3,571.75 (-0.85%)"),
                                html.Li("MSFT - $28,383.75 (+1.52%)"),
                            ], className="text-white")
                        ])
                    ], style={"marginBottom": "1rem", "background": "#bebefc"}),
                ], md=6),

                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div([
                                html.H4("Your Stocks", className="text-white mb-3"),
                                dcc.Graph(figure=owned_stocks_table, style={'height': '100%', 'width': '100%'})
                            ], style={'width': '100%', 'padding': '10px', 'overflowX': 'auto'}),
                        ])
                    ], style={"marginBottom": "1rem", "background": "#3f0d99"}),
                ], md=6),
            ]),
        ]
    )

# Create table of tickers and prices
def global_market_table():
    global_stocks = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "BRK-B", "META", "TSLA", "LLY", "AVGO",
        "UNH", "JPM", "V", "WMT", "MA", "XOM", "JNJ", "PG", "HD", "MRK",
        "COST", "ABBV", "CVX", "PEP", "ADBE", "KO", "BAC", "CRM", "TMO", "ORCL",
        "ACN", "NFLX", "ABT", "MCD", "DHR", "NKE", "WFC", "INTC", "LIN", "AMD",
        "TXN", "AMGN", "DIS", "UPS", "QCOM", "MS", "LOW", "NEE", "PM", "SBUX",
        "BMY", "GS", "HON", "RTX", "ISRG", "INTU", "AMAT", "MDT", "IBM", "CAT",
        "UNP", "CVS", "BLK", "GE", "ELV", "NOW", "ADI", "MO", "TGT", "ZTS",
        "DE", "GILD", "CI", "SYK", "LRCX", "VRTX", "MDLZ", "REGN", "SPGI", "MMC",
        "CB", "ADP", "USB", "PLD", "FISV", "PNC", "MU", "C", "FI", "HCA",
        "LMT", "APD", "BDX", "SCHW", "TFC", "PGR", "NSC", "DUK", "SO", "ITW",
        "ICE", "SLB", "GM", "CL", "ETN", "SHW", "TRV", "AON", "FDX", "EOG",
        "EXC", "PSX", "EW", "PSA", "D", "EMR", "AIG", "TEL", "MCO", "ADSK",
        "CME", "ROST", "HPQ", "KHC", "WMB", "MTD", "AEP", "TT", "STZ", "KLAC",
        "DLR", "ROK", "ILMN", "CDNS", "HUM", "DXCM", "OTIS", "BKR", "IDXX", "MAR",
        "KMB", "CTAS", "PCAR", "ODFL", "AZO", "PPL", "TSCO", "KDP", "ES", "ALGN",
        "PEG", "FAST", "WEC", "PAYX", "PPG", "AVB", "AFL", "AMP", "RSG", "WELL",
        "VMC", "CHD", "FANG", "NTRS", "WST", "LUV", "ALL", "ED", "YUM", "DRI",
        "EQR", "VRSK", "MLM", "EFX", "HIG", "CNC", "MKC", "TYL", "ZBRA", "MAA",
        "KEYS", "SRE", "BLL", "CTSH", "NTAP", "CMS", "COR", "CNP", "ATO", "NRG",
        "HOLX", "TRMB", "STE", "BRO", "CEG", "FE", "HBAN", "NI", "BTC-USD"
    ]
    data = yf.download(global_stocks, period="2d", progress=False)
    close = data["Close"]
    print(close)

    for ticker in global_stocks:
        try:
            prev_price = close[ticker].iloc[-2]
            curr_price = close[ticker].iloc[-1]
            trend = "📈" if curr_price > prev_price else "📉"
            name = get_company_name(ticker)
            data.append((ticker, name, f"${curr_price:.2f}", trend))
        except:
            continue

    # Build Dash table layout
    rows = []
    for t, name, price, trend in data:
        rows.append(
            dbc.Row([
                dbc.Col(html.Div(t), width=2),
                dbc.Col(html.Div(name), width=5),
                dbc.Col(html.Div(price), width=3),
                dbc.Col(html.Div(trend), width=2),
            ], className="border-bottom border-secondary py-1")
        )

    return html.Div([
        html.H3("Top 200 Companies", className="text-light mb-4", style={"color":"white"}),
        dbc.Row([
            dbc.Col(html.Strong("Ticker"), width=2),
            dbc.Col(html.Strong("Company"), width=5),
            dbc.Col(html.Strong("Price"), width=3),
            dbc.Col(html.Strong("Trend"), width=2),
        ], className="border-bottom border-white pb-2"),
        # *rows
    ])

# App layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),

    # Navbar
    dbc.NavbarSimple(
        brand="Financial Dashboard",
        brand_href="/",
        color="primary",
        dark=True,
        children=[
            dbc.NavItem(dbc.NavLink("Overview", href="/")),
            dbc.NavItem(dbc.NavLink("Global Market", href="/global")),
        ]
    ),

    html.Div(id='page-content', className="p-4")
])

# Route content dynamically
@app.callback(Output('page-content', 'children'), Input('url', 'pathname'))
def display_page(pathname):
    if pathname == "/global":
        return dbc.Container(global_market_table(), fluid=True)
    else:
        return home_layout


if __name__ == "__main__":
    app.run(debug=True)


