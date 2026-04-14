import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import wrds

# ------------------- Page Setup -------------------
st.set_page_config(page_title="Stock Financial Analysis Dashboard", layout="wide")

st.title("📊 Stock Financial Analysis Dashboard")
st.markdown("""
This interactive dashboard helps users review a company's historical financial performance,
key accounting ratios, and a simple forecast.

**Target users:** Beginner investors and accounting/finance students  
**Analytical focus:** Profitability, leverage, earnings, and trend analysis  
**Data source: WRDS Compustat (REAL data only)**
""")

# ------------------- Sidebar -------------------
st.sidebar.header("User Input Parameters")
ticker = st.sidebar.text_input("Stock Ticker", "AAPL").upper().strip()
start_year = st.sidebar.slider("Start Year", 2015, 2024, 2018)
n_years = st.sidebar.slider("Forecast Years", 1, 5, 3)
growth_rate = st.sidebar.slider("Annual Growth Rate (%)", 0.0, 20.0, 5.0)

st.sidebar.markdown("""
**Notes**
- This tool uses real WRDS Compustat data for educational purposes.
- Not intended for professional investment advice.
""")

# ------------------- REAL WRDS LOGIN -------------------
WRDS_USERNAME = "PUT_YOUR_WRDS_USERNAME_HERE"
WRDS_PASSWORD = "PUT_YOUR_WRDS_PASSWORD_HERE"

# ------------------- Connect to WRDS -------------------
def connect_wrds():
    try:
        db = wrds.Connection(wrds_username=WRDS_USERNAME, wrds_password=WRDS_PASSWORD)
        st.success("✅ Successfully connected to WRDS – using real financial data")
        return db
    except Exception as e:
        st.error(f"❌ WRDS connection failed: {str(e)}")
        st.stop()

# ------------------- Load REAL DATA from WRDS -------------------
def load_real_data(ticker, start_year):
    db = connect_wrds()
    clean_ticker = ticker.strip().upper()

    query = f"""
        SELECT fyear, revt, ni, roe, at, lt, prcc_f, csho
        FROM comp.funda
        WHERE tic = '{clean_ticker}'
          AND fyear >= {start_year}
          AND indfmt = 'INDL'
          AND datafmt = 'STD'
          AND popsrc = 'D'
          AND consol = 'C'
        ORDER BY fyear
    """

    df = db.raw_sql(query)
    db.close()

    if df.empty:
        st.error("No data found for this ticker and period.")
        st.stop()

    df.columns = [
        "Year", "Revenue", "Net_Income", "ROE",
        "Total_Assets", "Total_Liabilities",
        "Stock_Price", "Shares_Outstanding"
    ]
    return df.round(2)

# ------------------- Data Preparation -------------------
def prepare_data(df):
    df["Profit_Margin(%)"] = (df["Net_Income"] / df["Revenue"] * 100).round(2)
    df["Debt_Ratio(%)"] = (df["Total_Liabilities"] / df["Total_Assets"] * 100).round(2)
    df["EPS"] = (df["Net_Income"] / df["Shares_Outstanding"]).round(2)
    return df

# ------------------- Forecast -------------------
def create_forecast(df, n_years, growth_rate):
    last_year = int(df["Year"].max())
    last_rev = df["Revenue"].iloc[-1]
    last_prof = df["Net_Income"].iloc[-1]

    forecast = pd.DataFrame({
        "Year": [last_year + i for i in range(1, n_years + 1)],
        "Forecast_Revenue": [last_rev * (1 + growth_rate / 100) ** i for i in range(1, n_years + 1)],
        "Forecast_Net_Income": [last_prof * (1 + growth_rate / 100) ** i for i in range(1, n_years + 1)]
    }).round(2)
    return forecast

# ------------------- Summary Text -------------------
def generate_summary(df):
    rev_first = df["Revenue"].iloc[0]
    rev_last = df["Revenue"].iloc[-1]
    rev_change_pct = ((rev_last - rev_first) / rev_first) * 100 if rev_first != 0 else 0

    roe_avg = df["ROE"].mean()
    margin_avg = df["Profit_Margin(%)"].mean()
    debt_avg = df["Debt_Ratio(%)"].mean()
    eps_avg = df["EPS"].mean()

    if rev_change_pct > 20:
        growth = "Strong revenue growth"
    elif rev_change_pct > 5:
        growth = "Moderate revenue growth"
    elif rev_change_pct >= -5:
        growth = "Relatively stable revenue"
    else:
        growth = "Declining revenue"

    profitability = "Strong" if margin_avg >= 15 else "Moderate" if margin_avg >= 8 else "Weak"
    leverage = "High" if debt_avg >= 60 else "Moderate" if debt_avg >= 35 else "Low"

    if roe_avg >= 20 and margin_avg >= 15:
        overall = "Strong overall financial performance"
    elif roe_avg >= 10 and margin_avg >= 8:
        overall = "Moderate but acceptable performance"
    else:
        overall = "Weaker performance that requires further review"

    return growth, profitability, leverage, overall, roe_avg, margin_avg, debt_avg, eps_avg

# ------------------- Run -------------------
df = load_real_data(ticker, start_year)
df = prepare_data(df)

st.subheader("Financial Data Table (Real WRDS Data)")
st.dataframe(df, use_container_width=True)

# ------------------- Charts -------------------
st.subheader("Trend Analysis")
col1, col2 = st.columns(2)

with col1:
    fig1, ax1 = plt.subplots()
    ax1.plot(df["Year"], df["Stock_Price"], marker="o", color="#1f77b4")
    ax1.set_title("Stock Price Trend")
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Stock Price")
    st.pyplot(fig1)
    plt.close(fig1)

with col2:
    fig2, ax2 = plt.subplots()
    ax2.bar(df["Year"] - 0.2, df["Revenue"], width=0.4, label="Revenue", color="#ff7f0e", alpha=0.8)
    ax2.bar(df["Year"] + 0.2, df["Net_Income"], width=0.4, label="Net Income", color="#2ca02c", alpha=0.8)
    ax2.legend()
    ax2.set_title("Revenue vs Net Income")
    ax2.set_xlabel("Year")
    ax2.set_ylabel("Amount")
    st.pyplot(fig2)
    plt.close(fig2)

# ------------------- KPIs -------------------
st.subheader("Key Financial Metrics")
growth_txt, profit_txt, leverage_txt, overall_txt, roe_avg, margin_avg, debt_avg, eps_avg = generate_summary(df)

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Average ROE", f"{roe_avg:.2f}%")
kpi2.metric("Avg Profit Margin", f"{margin_avg:.2f}%")
kpi3.metric("Avg Debt Ratio", f"{debt_avg:.2f}%")
kpi4.metric("Avg EPS", f"{eps_avg:.2f}")

# ------------------- Forecast -------------------
st.subheader("Financial Forecast")
forecast = create_forecast(df, n_years, growth_rate)
st.dataframe(forecast, use_container_width=True)

fig3, ax3 = plt.subplots()
ax3.plot(df["Year"], df["Revenue"], marker="o", label="Historical Revenue")
ax3.plot(forecast["Year"], forecast["Forecast_Revenue"], marker="o", linestyle="--", label="Forecast Revenue")
ax3.plot(df["Year"], df["Net_Income"], marker="o", label="Historical Net Income")
ax3.plot(forecast["Year"], forecast["Forecast_Net_Income"], marker="o", linestyle="--", label="Forecast Net Income")
ax3.set_title("Historical and Forecast Trend")
ax3.set_xlabel("Year")
ax3.set_ylabel("Amount")
ax3.legend()
st.pyplot(fig3)
plt.close(fig3)

# ------------------- Download -------------------
st.subheader("Download Data")
st.download_button("Download Financial Data", df.to_csv(index=False), f"{ticker}_financials.csv")
st.download_button("Download Forecast", forecast.to_csv(index=False), f"{ticker}_forecast.csv")

# ------------------- Summary -------------------
st.subheader("Summary")
st.write(f"""
1. **Growth**: {growth_txt}
2. **Profitability**: {profit_txt}
3. **Leverage**: {leverage_txt}
4. **Overall**: {overall_txt}
""")

st.caption("✅ All data from WRDS Compustat (real data only — no sample data)")
