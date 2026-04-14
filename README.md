# Stock Financial Analysis Dashboard

## Project Overview
This project is an interactive Python data product built with Streamlit. It helps users review a company's historical financial performance, key accounting ratios, and a simple forecast in a clear and accessible dashboard.

The tool is designed as a small educational MVP rather than a professional investment platform. Its main purpose is to demonstrate how Python can be used to turn financial data into a practical, user-facing analytical product.

## Problem Statement
Beginner investors and accounting/finance students often find raw financial data difficult to interpret. Financial statements contain useful information, but the data is not always easy to compare across years or turn into simple insights.

This dashboard addresses that problem by transforming financial data into:
- trend charts,
- key ratio indicators,
- a simple forecast table,
- and short analytical summaries.

## Target Users
The main target users are:
- beginner investors,
- accounting students,
- finance students,
- and anyone who wants a simple first-pass review of a company's financial performance.

## Analytical Value
This tool helps users answer questions such as:
- Has the company's revenue generally grown over time?
- Is profitability relatively strong or weak?
- Is the company using a high level of leverage?
- What might future revenue and net income look like under a simple growth assumption?

The goal is not to give direct investment advice, but to support basic financial review and interpretation.

## Features
The dashboard includes:
- historical financial data table,
- stock price trend chart,
- revenue vs net income comparison chart,
- key financial metrics such as:
  - ROE,
  - profit margin,
  - debt ratio,
  - EPS,
- simple multi-year forecast based on a user-selected growth rate,
- downloadable CSV files for financial data and forecast output,
- dynamic summary text that interprets the results.

## Data Source
The intended data source is **WRDS Compustat**.

If WRDS access is unavailable, the app uses **sample fallback data** for demonstration purposes so that the dashboard remains functional.

### Main variables used
- Year
- Revenue
- Net Income
- ROE
- Total Assets
- Total Liabilities
- Stock Price
- Shares Outstanding

## Methods
This project uses Python for:
1. data access,
2. data cleaning,
3. variable transformation,
4. ratio calculation,
5. data visualisation,
6. and simple forecasting.

### Key analytical steps
- Load financial data from WRDS Compustat or sample fallback data
- Clean and convert variables into numeric format
- Remove unusable rows
- Calculate:
  - Profit Margin (%)
  - Debt Ratio (%)
  - EPS
- Visualise historical trends
- Generate a simple forecast using a user-defined annual growth rate
- Produce a short automated interpretation of the results

## Forecast Method
The forecast in this dashboard is intentionally simple. It applies a constant user-selected annual growth rate to the latest available revenue and net income figures.

This method is used for educational demonstration only. It is not a full valuation model and should not be treated as a reliable prediction of future company performance.

## App Link
**Live app:** [Insert your Streamlit app link here]

## Demo Video
**Demo video:** [Insert your 1–3 minute demo video link here]

## Repository Structure
A simple recommended structure is:

```text
README.md
app.py
notebook.ipynb
requirements.txt
figures/        # optional
data/           # optional, only for small non-sensitive files
.streamlit/     # optional, for secrets or config