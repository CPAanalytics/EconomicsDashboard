from fredapi import Fred
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
import plotly.express as px
import locale

# Set the locale for formatting numbers
locale.setlocale(locale.LC_ALL, "")

# API key for the St. Louis FRED API (replace with your own API key)
api_key = "dde5ad634e39b6e288c9a2ebec181e58"

# Create a Fred object with your API key
fred = Fred(api_key=api_key)

# Define the series IDs for each data
series_ids = {
    "GDP": "GDP",
    "Inflation": "MICH",
    "Unemployment Rate": "UNRATE",
    "Real Wages": "LES1252881600Q",
    "Interest Rates": "FEDFUNDS",
    "Productivity": "OPHNFB",
    "Consumer Confidence": "UMCSENT",
    "S&P 500": "SP500"
}

metric = {
    "GDP": {"balance": "normal", "format": "{:,.2f}"},
    "Inflation": {"balance": "inverse", "format": "{:.2f}%"},
    "Unemployment Rate": {"balance": "inverse", "format": "{:.2f}%"},
    "Real Wages": {"balance": "normal", "format": "{:,.2f}"},
    "Interest Rates": {"balance": "off", "format": "{:.2f}%"},
    "Productivity": {"balance": "normal", "format": "{:,.2f}"},
    "Consumer Confidence": {"balance": "normal", "format": "{:,.2f}"},
    "S&P 500": {"balance": "normal", "format": "{:,.2f}"},
}


# Calculate the start and end dates for the trailing twelve months
end_date = datetime.today().strftime('%Y-%m-%d')
start_date = (datetime.today() - timedelta(days=365 * 10)).strftime('%Y-%m-%d')

# Retrieve data from the FRED API for the trailing twelve months on a quarterly basis
data = {"Date": pd.date_range(start=start_date, end=end_date, freq='Q')}

for series_name, series_id in series_ids.items():
    try:
        series_data = fred.get_series(series_id, start_date=start_date, end_date=end_date)
        series_data = series_data.resample('Q').last().reindex(data['Date'])
        data[series_name] = series_data
    except Exception as e:
        print(f"Error fetching data for {series_name}: {e}")

# Create Pandas DataFrame
df = pd.DataFrame(data)

# Calculate year-over-year percentage change for each series
for series_name in series_ids:
    df[f"{series_name} YoY"] = df[series_name].pct_change(periods=4) * 100

# Calculate 1-year moving average for each series
for series_name in series_ids:
    df[f"{series_name} MA"] = df[series_name].rolling(window=4).mean()

# Create Streamlit dashboard
st.title('U.S. Economic Indicators')

# Define function to display KPI indicator
def display_kpi(title, value, append):
    formatted_value = locale.format_string("%.2f", value, grouping=True)
    st.markdown(f"**{title}**: {formatted_value}{append}")



# Define function to display line chart
def display_line_chart(title, data, y_label):
    fig = px.line(data, x='Date', y=y_label, title='', template='plotly_white',
                  color_discrete_sequence=['#1f77b4', '#ff7f0e'],)
    fig.update_traces(mode='lines+markers')
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor='lightgray')
    fig.update_layout(legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
    st.plotly_chart(fig)

# Display data for each series
for series_name in series_ids:
    st.subheader(series_name)
    base_num =metric[series_name]["format"].format(df[series_name].iloc[-1])
    change_num = "{:.2f}%".format( df[f"{series_name} YoY"].iloc[-1])
    st.metric(series_name, base_num, change_num, delta_color=metric[series_name]['balance'], label_visibility='hidden' )
    display_line_chart(series_name, df, [series_name, f"{series_name} MA"])



