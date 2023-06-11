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
    },
    "Recession Shifted": {
        "series_id": "RECPROUSM156N",
        "balance": "inverse",
        "format": "{:,.2f}",
        "label": "Recession Shifted"
    }
}

# Create Streamlit dashboard
st.title('U.S. Economic Indicators')

# Calculate the start and end dates for the trailing twelve months
start_date = st.date_input("Start Date", value=datetime.strptime('1980-01-01', '%Y-%m-%d'), min_value=datetime.strptime('1980-01-01', '%Y-%m-%d'), max_value=datetime.today())
end_date = st.date_input("End Date", value=datetime.today(), min_value=datetime.strptime('1980-01-01', '%Y-%m-%d'), max_value=datetime.today())

# Retrieve data from the FRED API for the trailing twelve months on a quarterly basis
data = {"Date": pd.date_range(start=datetime.strptime('1980-01-01', '%Y-%m-%d'), end=datetime.today(), freq='Q')}

for indicator_name, indicator_data in indicators.items():
    try:
        if indicator_name == 'Recession Shifted':
            series_data = fred.get_series(indicator_data["series_id"], start_date=datetime.strptime('1980-01-01', '%Y-%m-%d'), end_date=datetime.today())
            series_data = series_data.resample('Q').last().reindex(data['Date']).shift(-4)
            data[indicator_name] = series_data
        else:
            series_data = fred.get_series(indicator_data["series_id"], start_date=datetime.strptime('1980-01-01', '%Y-%m-%d'), end_date=datetime.today())
            series_data = series_data.resample('Q').last().reindex(data['Date'])
            data[indicator_name] = series_data
    except Exception as e:
        print(f"Error fetching data for {indicator_name}: {e}")

# Create Pandas DataFrame
df = pd.DataFrame(data)

st.subheader('Recession Correlations')
st.markdown('Correlations between 1 year shifted in to the past recession indicator and recession indicator since 1980.')
df_correl = df[[indicator_name for indicator_name in indicators]]
df_correl = df_correl.corr()
fig = px.imshow(df_correl[['Recession Shifted', 'Recession Prob']], text_auto=True, width=400, height=800)
st.plotly_chart(fig)

date_range = pd.date_range(start=start_date, end=end_date, freq='Q')
plot_df = df[df['Date'].isin(date_range)].copy(deep=True)

# Calculate year-over-year percentage change for each series
for indicator_name, indicator_data in indicators.items():
    plot_df[f"{indicator_name} YoY"] = df[indicator_name].pct_change(periods=4) * 100

# Calculate 1-year moving average for each series
for indicator_name, indicator_data in indicators.items():
    if 'Recession' in indicator_name:
        continue
    else:
        plot_df[f"{indicator_name} 3 Year MA"] = plot_df[indicator_name].rolling(window=12).mean()

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
    if 'Recession Shifted' in indicator_name:
        continue
    else:
        st.subheader(indicator_data["label"])
        base_num = indicator_data["format"].format(plot_df[indicator_name].iloc[-1])
        change_num = "{:.2f}%".format(plot_df[f"{indicator_name} YoY"].iloc[-1])
        st.metric(indicator_data["label"], base_num, change_num, delta_color=indicator_data['balance'], label_visibility='hidden')

        if 'Recession Prob' in indicator_name:
            display_line_chart(indicator_data["label"], plot_df, [indicator_name])
        else:
            display_line_chart(indicator_data["label"], plot_df, [indicator_name, f"{indicator_name} 3 Year MA"])

st.download_button(label='Download Data', data=df.to_csv(), file_name='data.csv')
