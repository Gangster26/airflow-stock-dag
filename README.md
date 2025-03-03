# Stock Price Pipeline using Apache Airflow & Snowflake

## 🚀 Overview
This project implements a daily ETL pipeline using **Apache Airflow** to extract stock data from the **Alpha Vantage API** and load it into **Snowflake**.

## 🛠️ Technologies Used
- Apache Airflow
- Snowflake
- Python
- Alpha Vantage API

## ⚙️ Pipeline Workflow
1. **Extract**: Get the latest daily stock prices for a specific symbol.
2. **Transform**: Parse and prepare the latest day's stock data.
3. **Load**: Insert the daily stock data into a Snowflake table.

## 🏗️ DAG Info
- **DAG ID**: `stock_price_pipeline`
- **Schedule**: Daily at 2:30 AM UTC
- **Symbol**: Currently set to `"NFLX"`

## 📝 Snowflake
Ensure a connection named **`snowflake_conn`** is configured in Airflow with:
- Username
- Password
- Account
- Warehouse
- Database
- Schema

## 🔑 Variables
Create an Airflow Variable:
- Key: `vantage_api_key`
- Value: *Your Alpha Vantage API Key*


## ✅ How to Run
1. Deploy the DAG file into your Airflow DAGs folder.
2. Configure the required Airflow connection and variable.
3. Trigger the DAG from the Airflow UI or wait for the scheduled run.



## 🧑‍💻 Author
Arya Mehta
