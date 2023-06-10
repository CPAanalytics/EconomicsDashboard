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
gdp_series_id = "GDP"
inflation_series_id = "MICH"
unemployment_series_id = "UNRATE"
wage_growth_series_id = "LES1252881600Q"
interest_rates_series_id = "FEDFUNDS"
productivity_series_id = "OPHNFB"
consumer_confidence_series_id = "UMCSENT"
sp500_series_id = "SP500"

# Calculate the start and end dates for the trailing twelve months
end_date = datetime.today().strftime('%Y-%m-%d')
start_date = (datetime.today() - timedelta(days=365*10)).strftime('%Y-%m-%d')

# Retrieve data from the FRED API for the trailing twelve months on a quarterly basis
data = {}
data['Date'] = pd.date_range(start=start_date, end=end_date, freq='Q')
series_ids = [
    gdp_series_id,
    inflation_series_id,
    unemployment_series_id,
    wage_growth_series_id,
    interest_rates_series_id,
    productivity_series_id,
    consumer_confidence_series_id,
    sp500_series_id
]

for series_id in series_ids:
    try:
        series_data = fred.get_series(series_id, start_date=start_date, end_date=end_date)
        series_data = series_data.resample('Q').last().reindex(data['Date'])
        data[series_id] = series_data
    except Exception as e:
        print(f"Error fetching data for {series_id}: {e}")

# Create Pandas DataFrame
df = pd.DataFrame(data)

# Calculate year-over-year percentage change for each series
df['GDP YoY'] = df['GDP'].pct_change(periods=4) * 100
df['Inflation YoY'] = df['MICH'].pct_change(periods=4) * 100
df['Unemployment Rate YoY'] = df['UNRATE'].pct_change(periods=4) * 100
df['Real Wages YoY'] = df['LES1252881600Q'].pct_change(periods=4) * 100
df['Interest Rates YoY'] = df['FEDFUNDS'].pct_change(periods=4) * 100
df['Productivity YoY'] = df['OPHNFB'].pct_change(periods=4) * 100
df['Consumer Confidence YoY'] = df['UMCSENT'].pct_change(periods=4) * 100
df['S&P 500 YoY'] = df['SP500'].pct_change(periods=4) * 100

# Calculate 1-year moving average for each series
df['GDP MA'] = df['GDP'].rolling(window=4).mean()
df['Inflation MA'] = df['MICH'].rolling(window=4).mean()
df['Unemployment Rate MA'] = df['UNRATE'].rolling(window=4).mean()
df['Real Wages MA'] = df['LES1252881600Q'].rolling(window=4).mean()
df['Interest Rates MA'] = df['FEDFUNDS'].rolling(window=4).mean()
df['Productivity MA'] = df['OPHNFB'].rolling(window=4).mean()
df['Consumer Confidence MA'] = df['UMCSENT'].rolling(window=4).mean()
df['S&P 500 MA'] = df['SP500'].rolling(window=4).mean()

# Create Streamlit dashboard
st.title('U.S. Economic Indicators')

# Define function to display KPI indicator
def display_kpi(title, value, append):
    formatted_value = locale.format_string("%.2f", value, grouping=True)
    st.markdown(f"**{title}**: {formatted_value}{append}")

# Define function to display line chart
def display_line_chart(title, data, y_label):
    fig = px.line(data, x='Date', y=y_label, title=title, template='plotly_white',
                  color_discrete_sequence=['#1f77b4', '#ff7f0e'])
    fig.update_traces(mode='lines+markers')
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor='lightgray')
    fig.update_layout(legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
    st.plotly_chart(fig)

# Display line chart for GDP
st.subheader('GDP')
display_kpi("GDP", df['GDP'].iloc[-1], '')
display_kpi("GDP YoY", df['GDP YoY'].iloc[-1], '%')
display_line_chart("GDP", df, ['GDP', 'GDP MA'])

# Display line chart for Inflation
st.subheader('Inflation')
display_kpi("Inflation", df['MICH'].iloc[-1], '%')
display_kpi("Inflation YoY", df['Inflation YoY'].iloc[-1], '%')
display_line_chart("Inflation", df, ['MICH', 'Inflation MA'])

# Display line chart for Unemployment Rate
st.subheader('Unemployment Rate')
display_kpi("Unemployment Rate", df['UNRATE'].iloc[-1], '%')
display_kpi("Unemployment Rate YoY", df['Unemployment Rate YoY'].iloc[-1], '%')
display_line_chart("Unemployment Rate", df, ['UNRATE', 'Unemployment Rate MA'])

# Display line chart for Real Wages
st.subheader('Real Wages')
display_kpi("Real Wages", df['LES1252881600Q'].iloc[-1], '')
display_kpi("Real Wages YoY", df['Real Wages YoY'].iloc[-1], '%')
display_line_chart("Real Wages", df, ['LES1252881600Q', 'Real Wages MA'])

# Display line chart for Interest Rates
st.subheader('Interest Rates')
display_kpi("Interest Rates", df['FEDFUNDS'].iloc[-1], '%')
display_kpi("Interest Rates YoY", df['Interest Rates YoY'].iloc[-1], '%')
display_line_chart("Interest Rates", df, ['FEDFUNDS', 'Interest Rates MA'])

# Display line chart for Productivity
st.subheader('Productivity')
display_kpi("Productivity", df['OPHNFB'].iloc[-1], '')
display_kpi("Productivity YoY", df['Productivity YoY'].iloc[-1], '%')
display_line_chart("Productivity", df, ['OPHNFB', 'Productivity MA'])

# Display line chart for Consumer Confidence
st.subheader('Consumer Confidence')
display_kpi("Consumer Confidence", df['UMCSENT'].iloc[-1], '')
display_kpi("Consumer Confidence YoY", df['Consumer Confidence YoY'].iloc[-1], '%')
display_line_chart("Consumer Confidence", df, ['UMCSENT', 'Consumer Confidence MA'])

# Display line chart for S&P 500
st.subheader('S&P 500')
display_kpi("S&P 500", df['SP500'].iloc[-1], '')
display_kpi("S&P 500 YoY", df['S&P 500 YoY'].iloc[-1], '%')
display_line_chart("S&P 500", df, ['SP500', 'S&P 500 MA'])



