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

# Define the indicators dictionary with series IDs, metric information, and labels
indicators = {
    "Real GDP": {
        "series_id": "GDPC1",
        "balance": "normal",
        "format": "{:,.2f}",
        "label": "Real GDP"
    },
    "Inflation": {
        "series_id": "MICH",
        "balance": "inverse",
        "format": "{:.2f}%",
        "label": "Inflation"
    },
    "Unemployment Rate": {
        "series_id": "UNRATE",
        "balance": "inverse",
        "format": "{:.2f}%",
        "label": "Unemployment Rate"
    },
    "Real Wages": {
        "series_id": "LES1252881600Q",
        "balance": "normal",
        "format": "{:,.2f}",
        "label": "Real Wages"
    },
    "Interest Rates": {
        "series_id": "FEDFUNDS",
        "balance": "off",
        "format": "{:.2f}%",
        "label": "Interest Rates"
    },
    "Productivity": {
        "series_id": "OPHNFB",
        "balance": "normal",
        "format": "{:,.2f}",
        "label": "Productivity"
    },
    "Consumer Confidence": {
        "series_id": "UMCSENT",
        "balance": "normal",
        "format": "{:,.2f}",
        "label": "Consumer Confidence"
    },
    "S&P 500": {
        "series_id": "SP500",
        "balance": "normal",
        "format": "{:,.2f}",
        "label": "S&P 500"
    },
    "Recession Prob": {
        "series_id": "RECPROUSM156N",
        "balance": "inverse",
        "format": "{:,.2f}",
        "label": "Recession Prob"
    }
}

# Create Streamlit dashboard
st.title('U.S. Economic Indicators')

# Calculate the start and end dates for the trailing twelve months
start_date = st.date_input("Start Date", value=datetime.strptime('1980-01-01', '%Y-%m-%d'), min_value=datetime.strptime('1980-01-01', '%Y-%m-%d'), max_value=datetime.today())
end_date = st.date_input("End Date", value=datetime.today(), min_value=datetime.strptime('1980-01-01', '%Y-%m-%d'), max_value=datetime.today())

# Retrieve data from the FRED API for the trailing twelve months on a quarterly basis
data = {"Date": pd.date_range(start=start_date, end=end_date, freq='Q')}

for indicator_name, indicator_data in indicators.items():
    try:
        series_data = fred.get_series(indicator_data["series_id"], start_date=start_date, end_date=end_date)
        series_data = series_data.resample('Q').last().reindex(data['Date'])
        data[indicator_name] = series_data
    except Exception as e:
        print(f"Error fetching data for {indicator_name}: {e}")

# Create Pandas DataFrame
df = pd.DataFrame(data)

# Calculate year-over-year percentage change for each series
for indicator_name, indicator_data in indicators.items():
    df[f"{indicator_name} YoY"] = df[indicator_name].pct_change(periods=4) * 100

# Calculate 1-year moving average for each series
for indicator_name, indicator_data in indicators.items():
    df[f"{indicator_name} 3 Year MA"] = df[indicator_name].rolling(window=12).mean()

for indicator_name, indicator_data in indicators.items():
    df[f"{indicator_name} 1 Year MA"] = df[indicator_name].rolling(window=4).mean()

# Retrieve data within the selected date range
date_range = pd.date_range(start=start_date, end=end_date, freq='Q')
df = df[df['Date'].isin(date_range)]

# Define function to display KPI indicator
def display_kpi(title, value, append):
    formatted_value = locale.format_string("%.2f", value, grouping=True)
    st.markdown(f"**{title}**: {formatted_value}{append}")

# Define function to display line chart
def display_line_chart(title, data, y_label):
    fig = px.line(data, x='Date', y=y_label, title='', template='plotly_white',
                  color_discrete_sequence=['#1f77b4', '#ff7f0e', '#2ca02c'],)
    fig.update_traces(mode='lines')
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor='lightgray')
    fig.update_layout(legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
    st.plotly_chart(fig)

# Display data for each indicator
for indicator_name, indicator_data in indicators.items():
    st.subheader(indicator_data["label"])
    base_num = indicator_data["format"].format(df[indicator_name].iloc[-1])
    change_num = "{:.2f}%".format(df[f"{indicator_name} YoY"].iloc[-1])
    st.metric(indicator_data["label"], base_num, change_num, delta_color=indicator_data['balance'], label_visibility='hidden')
    display_line_chart(indicator_data["label"], df, [indicator_name, f"{indicator_name} 3 Year MA", f"{indicator_name} 1 Year MA"])

df_correl = df[[indicator_name for indicator_name in indicators]]
df_correl = df_correl.corr()
fig = px.imshow(df_correl, text_auto=True, width=800, height=800)
st.plotly_chart(fig)
