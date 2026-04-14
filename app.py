import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

try:
    import wrds
except ImportError:
    wrds = None

# ------------------- Page Setup -------------------
st.set_page_config(page_title="Stock Financial Analysis Dashboard", layout="wide")

st.title("📊 Stock Financial Analysis Dashboard")
st.markdown("""
This interactive dashboard helps users review a company's historical financial performance,
key accounting ratios, and a simple forecast.

**Target users:** Beginner investors and accounting/finance students  
**Analytical focus:** Profitability, leverage, earnings, and trend analysis  
**Data source:** WRDS Compustat (sample fallback data is used if WRDS is unavailable)
""")

# ------------------- Sidebar -------------------
st.sidebar.header("User Input Parameters")
ticker = st.sidebar.text_input("Stock Ticker", "AAPL").upper().strip()
start_year = st.sidebar.slider("Start Year", 2015, 2024, 2018)
n_years = st.sidebar.slider("Forecast Years", 1, 5, 3)
growth_rate = st.sidebar.slider("Annual Growth Rate (%)", 0.0, 20.0, 5.0)

st.sidebar.markdown("""
**Notes**
- This tool is a simple MVP for educational use.
- If WRDS is unavailable, the app will use sample fallback data.
- This dashboard is not professional investment advice.
""")

# ------------------- WRDS Username -------------------
# Recommended: store your WRDS username in Streamlit secrets
# Example in .streamlit/secrets.toml:
# wrds_username = "your_wrds_username"

if "wrds_username" in st.secrets:
    username = st.secrets["wrds_username"]
else:
    username = "your_wrds_username"  # Replace locally if needed

# ------------------- Helper Functions -------------------
def generate_sample_data(start_year):
    np.random.seed(42)
    years = list(range(start_year, 2024))
    if len(years) == 0:
        years =   [2023]

    base_revenue = np.linspace(180, 380, len(years)) + np.random.uniform(-20, 20, len(years))
    base_income = base_revenue * np.random.uniform(0.12, 0.22, len(years))
    assets = np.linspace(350, 850, len(years)) + np.random.uniform(-40, 40, len(years))
    liabilities = assets * np.random.uniform(0.28, 0.48, len(years))
    stock_price = np.linspace(70, 220, len(years)) + np.random.uniform(-15, 15, len(years))
    shares = np.random.uniform(12, 20, len(years))
    roe = np.random.uniform(14, 28, len(years))

    data = {
        "Year": years,
        "Revenue": base_revenue,
        "Net_Income": base_income,
        "ROE": roe,
        "Total_Assets": assets,
        "Total_Liabilities": liabilities,
        "Stock_Price": stock_price,
        "Shares_Outstanding": shares
    }
    return pd.DataFrame(data).round(2)


def connect_wrds_school():
    if wrds is None:
        st.warning("The wrds package is not installed. Using sample fallback data.")
        return None

    if username == "your_wrds_username":
        st.info("No WRDS username was provided. Using sample fallback data.")
        return None

    try:
        db = wrds.Connection(wrds_username=username)
        return db
    except Exception as e:
        st.error(f"WRDS connection failed: {e}")
        return None


def load_data(ticker, start_year):
    db = connect_wrds_school()

    if db is None:
        st.warning("WRDS is unavailable. Using sample fallback data.")
        return generate_sample_data(start_year), "Sample fallback data"

    safe_ticker = "".join(ch for ch in ticker if ch.isalnum() or ch in [".", "-"])

    query = f"""
    SELECT fyear, revt, ni, roe, at, lt, prcc_f, csho
    FROM comp.funda
    WHERE tic = '{safe_ticker}'
      AND fyear >= {start_year}
      AND indfmt = 'INDL'
      AND datafmt = 'STD'
      AND popsrc = 'D'
      AND consol = 'C'
    ORDER BY fyear
    """

    try:
        df = db.raw_sql(query)

        if df.empty:
            st.warning("No WRDS data found for the selected ticker and start year. Using sample fallback data.")
            return generate_sample_data(start_year), "Sample fallback data"

        df.columns = [
            "Year",
            "Revenue",
            "Net_Income",
            "ROE",
            "Total_Assets",
            "Total_Liabilities",
            "Stock_Price",
            "Shares_Outstanding"
        ]

        return df.round(2), "WRDS Compustat"

    except Exception as e:
        st.error(f"WRDS query failed: {e}")
        st.warning("Using sample fallback data.")
        return generate_sample_data(start_year), "Sample fallback data"

    finally:
        try:
            db.close()
        except:
            pass


def prepare_data(df):
    numeric_cols = [
        "Year", "Revenue", "Net_Income", "ROE",
        "Total_Assets", "Total_Liabilities",
        "Stock_Price", "Shares_Outstanding"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna().copy()
    df = df[(df["Revenue"] != 0) & (df["Total_Assets"] != 0) & (df["Shares_Outstanding"] != 0)]

    if df.empty:
        return df

    df["Profit_Margin(%)"] = (df["Net_Income"] / df["Revenue"] * 100).round(2)
    df["Debt_Ratio(%)"] = (df["Total_Liabilities"] / df["Total_Assets"] * 100).round(2)
    df["EPS"] = (df["Net_Income"] / df["Shares_Outstanding"]).round(2)

    return df


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


def generate_summary(df):
    rev_first = df["Revenue"].iloc  [0]
    rev_last = df["Revenue"].iloc[-1]
    roe_avg = df["ROE"].mean()
    margin_avg = df["Profit_Margin(%)"].mean()
    debt_avg = df["Debt_Ratio(%)"].mean()
    eps_avg = df["EPS"].mean()

    if rev_first != 0:
        rev_change_pct = ((rev_last - rev_first) / rev_first) * 100
    else:
        rev_change_pct = 0

    if rev_change_pct > 20:
        growth_text = "Revenue shows a strong upward trend over time."
    elif rev_change_pct > 5:
        growth_text = "Revenue shows moderate growth over time."
    elif rev_change_pct >= -5:
        growth_text = "Revenue appears relatively stable over time."
    else:
        growth_text = "Revenue shows a declining trend over time."

    if margin_avg >= 15:
        profit_text = "Profitability appears relatively strong."
    elif margin_avg >= 8:
        profit_text = "Profitability appears moderate."
    else:
        profit_text = "Profitability appears relatively weak."

    if debt_avg >= 60:
        debt_text = "Leverage is relatively high."
    elif debt_avg >= 35:
        debt_text = "Leverage is at a moderate level."
    else:
        debt_text = "Leverage is relatively low."

    if roe_avg >= 20 and margin_avg >= 15:
        overall_text = "Overall financial performance appears strong based on these simple indicators."
    elif roe_avg >= 10 and margin_avg >= 8:
        overall_text = "Overall financial performance appears mixed but acceptable."
    else:
        overall_text = "Overall financial performance appears weaker and may require more careful review."

    return growth_text, profit_text, debt_text, overall_text, roe_avg, margin_avg, debt_avg, eps_avg


# ------------------- Load and Prepare Data -------------------
raw_df, data_source = load_data(ticker, start_year)
df = prepare_data(raw_df)

if df.empty:
    st.warning("No usable data is available for the selected ticker and start year.")
    st.stop()

st.success(f"Dashboard loaded successfully. Current source: {data_source}")

# ------------------- Data Table -------------------
st.subheader("Financial Data Table")
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
growth_text, profit_text, debt_text, overall_text, roe_avg, margin_avg, debt_avg, eps_avg = generate_summary(df)

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Average ROE", f"{roe_avg:.2f}%")
kpi2.metric("Average Profit Margin", f"{margin_avg:.2f}%")
kpi3.metric("Average Debt Ratio", f"{debt_avg:.2f}%")
kpi4.metric("Average EPS", f"{eps_avg:.2f}")

# ------------------- Forecast -------------------
st.subheader("Financial Forecast")
forecast = create_forecast(df, n_years, growth_rate)
st.dataframe(forecast, use_container_width=True)

fig3, ax3 = plt.subplots()
ax3.plot(df["Year"], df["Revenue"], marker="o", label="Historical Revenue", color="#ff7f0e")
ax3.plot(forecast["Year"], forecast["Forecast_Revenue"], marker="o", linestyle="--", label="Forecast Revenue", color="#ffbb78")
ax3.plot(df["Year"], df["Net_Income"], marker="o", label="Historical Net Income", color="#2ca02c")
ax3.plot(forecast["Year"], forecast["Forecast_Net_Income"], marker="o", linestyle="--", label="Forecast Net Income", color="#98df8a")
ax3.set_title("Historical and Forecast Financial Trend")
ax3.set_xlabel("Year")
ax3.set_ylabel("Amount")
ax3.legend()
st.pyplot(fig3)
plt.close(fig3)

# ------------------- Downloads -------------------
st.subheader("Download Report")

csv_main = df.to_csv(index=False, encoding="utf-8-sig")
st.download_button(
    "Download Financial Data CSV",
    csv_main,
    file_name=f"{ticker}_financial_data.csv",
    mime="text/csv"
)

csv_forecast = forecast.to_csv(index=False, encoding="utf-8-sig")
st.download_button(
    "Download Forecast CSV",
    csv_forecast,
    file_name=f"{ticker}_forecast.csv",
    mime="text/csv"
)

# ------------------- Summary -------------------
st.subheader("Investment Summary")
st.write(f"""
1. **Growth:** {growth_text}  
2. **Profitability:** {profit_text} Average ROE is **{roe_avg:.1f}%**, and average profit margin is **{margin_avg:.1f}%**.  
3. **Leverage:** {debt_text} Average debt ratio is **{debt_avg:.1f}%**.  
4. **Earnings:** Average EPS is **{eps_avg:.2f}**.  
5. **Overall interpretation:** {overall_text}
""")

# ------------------- Limitation Note -------------------
st.info("""
This dashboard is a small educational MVP. It provides a simple first-pass financial review
and should not be treated as professional investment advice.
""")

st.caption(f"Source note: {data_source}. If WRDS access fails, the app uses sample fallback data for demonstration.")