from airflow import DAG
from airflow.decorators import task
from airflow.models import Variable
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook

from datetime import datetime
import requests


def get_snowflake_cursor():
    hook = SnowflakeHook(snowflake_conn_id='snowflake_conn')
    conn = hook.get_conn()
    return conn.cursor()


@task
def extract_stock_data(symbol):
    api_key = Variable.get("vantage_api_key")
    url = (
        f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY"
        f"&symbol={symbol}&apikey={api_key}"
    )
    response = requests.get(url)
    data = response.json()
    return data


@task
def transform_stock_data(data, symbol):
    results = []
    if "Time Series (Daily)" in data:
        # Get the latest date from the response
        latest_date = max(data["Time Series (Daily)"])
        values = data["Time Series (Daily)"][latest_date]
        results.append({
            "symbol": symbol,
            "date": latest_date,
            "open": float(values["1. open"]),
            "high": float(values["2. high"]),
            "low": float(values["3. low"]),
            "close": float(values["4. close"]),
            "volume": int(values["5. volume"])
        })
    return results


@task
def load_to_snowflake(records):
    db_name = "STOCK"
    schema_name = "RAW"
    table_name = "STOCK_PRICES"

    cur = get_snowflake_cursor()
    try:
        cur.execute("BEGIN;")
        cur.execute(f"DELETE FROM {db_name}.{schema_name}.{table_name};")  # <-- Full refresh step
        
        insert_sql = f"""
            INSERT INTO {db_name}.{schema_name}.{table_name} 
            (symbol, date, open, close, high, low, volume) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        for record in records:
            cur.execute(insert_sql, (
                record["symbol"], record["date"], record["open"],
                record["close"], record["high"], record["low"],
                record["volume"]
            ))
        cur.execute("COMMIT;")
        print(f"✅ Inserted {len(records)} records successfully!")
    except Exception as e:
        cur.execute("ROLLBACK;")
        print("❌ Transaction failed:", e)
        raise e
    finally:
        cur.close()



with DAG(
    dag_id="stock_price_pipeline",
    start_date=datetime(2024, 3, 1),
    schedule_interval="30 2 * * *",
    catchup=False,
    tags=["ETL", "stock", "snowflake"],
) as dag:

    symbol = "NFLX"
    
    raw_data = extract_stock_data(symbol)
    processed_data = transform_stock_data(raw_data, symbol)
    load_to_snowflake(processed_data)
