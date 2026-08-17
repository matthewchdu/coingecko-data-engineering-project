import os
import io
import json
import logging
from datetime import datetime, timezone
import requests
import pandas as pd
import pyarrow
from google.cloud import storage

url = "https://api.coingecko.com/api/v3/coins/markets"
bucket_name = "coingecko-505717-crypto-bucket"
project_id = "coingecko-505717"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
key_path = os.path.join(SCRIPT_DIR, "..", "terraform", "USER_KEY.json")

def get_data():
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 100,
        "page": 1,
        "sparkline": False
    }
    response = requests.get(url,params = params)
    response.raise_for_status()

    # gets data from response and turns it into json
    data = response.json()
    return data

def parse_data(data):

    #turns the raw data into a pandas table
    df = pd.DataFrame(data)

    #keeps the important columns
    kept_columns = [
        "id","symbol","name","current_price","market_cap","total_volume","last_updated"
    ]
    df = df[kept_columns]

    df["extracted_at"] = datetime.now(timezone.utc)
    df["snapshot_date"] = datetime.now(timezone.utc).date()

    return df

def pq_converter(df):
    buffer = io.BytesIO()

    df.to_parquet(
        buffer, 
        index=False, 
        engine="pyarrow", 
        compression="snappy"
    )
    buffer.seek(0)
    return buffer

def upload_to_bucket(buffer,bucket_name,gcs_path):
    client = storage.Client.from_service_account_json(key_path)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(gcs_path)

    blob.upload_from_file(buffer, content_type="application/octet-stream")

def main():
    logging.basicConfig(
        level=logging.INFO, 
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logging.info("Starting crypto data ingestion pipeline...")

    logging.info("Fetching data from CoinGecko API...")
    raw_data = get_data()

    logging.info("Transforming raw data into Pandas DataFrame...")
    df = parse_data(raw_data)

    logging.info("Converting DataFrame to Parquet format in memory...")
    parquet_buffer = pq_converter(df)

    now = datetime.now(timezone.utc)
    year = now.strftime("%Y")
    month = now.strftime("%m")
    day = now.strftime("%d")
    timestamp = now.strftime("%H%M%S")

    gcs_path = f"raw/crypto_markets/year={year}/month={month}/day={day}/snapshot_{timestamp}.parquet"

    logging.info(f"Uploading file to gs://{bucket_name}/{gcs_path}")
    upload_to_bucket(parquet_buffer, bucket_name, gcs_path)

    logging.info("Pipeline completed successfully!")

main()