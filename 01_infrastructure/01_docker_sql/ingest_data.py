#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import argparse
import os
from sqlalchemy import create_engine
from time import time


def main(params):
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    dbname = params.dbname
    table_name = params.table_name
    url = params.url

    if url.endswith('.csv.gz'):
        csv_name = 'yellow_tripdata_2021-01.csv.gz'
    else:
        csv_name = 'yellow_tripdata_2021-01.csv'

    # Download dataset
    os.system(f"wget {url} -O {csv_name}")

    # Format URL: 'postgresql://[user]:[password]@[host]:[port]/[dbname]'
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{dbname}')

    # Membagi data dalam chunk
    df_iter = pd.read_csv(csv_name, iterator=True, chunksize=100000)

    # Mendapatkan chunk pertama dan menyimpannya ke dalam variabel df
    df = next(df_iter)

    # Mengubah kolom tpep_pickup_datetime dan tpep_dropoff_datetime
    # dari format string ke datetime menggunakan pandas.to_datetime
    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)


    df.head(n=0).to_sql(name=table_name, con=engine, if_exists='replace')


    df.to_sql(name=table_name, con=engine, if_exists='append')


    # Loop yang akan berjalan terus sampai terjadi exception (seperti StopIteration)
    while True:
        try:
            t_start = time()    # Menandai waktu mulai proses

            df = next(df_iter)  # Mengambil chunck berikutnya dari iterator df_iter

            # Mengubah kolom tpep_pickup_datetime dan tpep_dropoff_datetime
            # dari format string ke datetime menggunakan pandas.to_datetime
            df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
            df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

            # Menyimpan DataFrame ke dalam tabel SQL 'yellow_taxi_data'.
            # - 'con=engine' menggunakan engine SQLAlchemy yang telah dibuat sebelumnya untuk koneksi database.
            # - 'if_exists='append'' berarti bahwa data akan ditambahkan ke tabel jika tabel itu sudah ada.
            df.to_sql(name=table_name, con=engine, if_exists='append')

            t_end = time()  # Menandai waktu akhir proses

            # Mencetak waktu yang diperlukan untuk memproses dan memasukkan chunk data tersebut
            print('inserted another chunk, took %.3f second' % (t_end - t_start))
        except StopIteration:
            print("Finisihed ingesting data into postgres database")
            break


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Ingest CSV data to Postgres")

    parser.add_argument('--user', required=True, help='username for postgres')
    parser.add_argument('--password', required=True, help='password for postgres')
    parser.add_argument('--host', required=True, help='host for postgres')
    parser.add_argument('--port', required=True, help='port for postgres')
    parser.add_argument('--dbname', required=True, help='database name for postgres')
    parser.add_argument('--table_name', required=True, help='table name for postgres')
    parser.add_argument('--url', required=True, help='raw data url')

    args = parser.parse_args()

    main(args)