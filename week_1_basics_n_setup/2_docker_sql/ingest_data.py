#!/usr/bin/env python
# coding: utf-8

import os
import pandas as pd
import argparse
from sqlalchemy import create_engine
from time import time

def main(params):
    user        = params.user
    password    = params.password
    port        = params.port
    host        = params.host
    db          = params.db
    table_name  = params.table_name
    url         = params.url
    csv_name    = 'output.csv'


    #Download the csv
    # the backup files are gzipped, and it's important to keep the correct extension
    # for pandas to be able to open the file
    if url.endswith('.csv.gz'):
        csv_name = 'output.csv.gz'
    else:
        csv_name = 'output.csv'
        
    print(f'URL:{url}')
    os.system(f"wget {url} -O {csv_name}")

    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')

    #This is to upload data by chunks 
    df_iter = pd.read_csv(csv_name, iterator=True, chunksize=100000) 

    df = next(df_iter)


    df.tpep_pickup_datetime  =  pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

    #Create the table
    df.head(n=0).to_sql(name=table_name, con=engine, if_exists='replace')

    #insert records into database
    df.to_sql(name=table_name, con=engine, if_exists='append')

    while True:
        t_start = time()
        
        #upload next 100000 records
        df = next(df_iter)
        
        #Converting fields to datetime type.
        df.tpep_pickup_datetime  =  pd.to_datetime(df.tpep_pickup_datetime)
        df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
        
        #insert records into database
        df.to_sql(name=table_name, con=engine, if_exists='append')
        
        t_end = time()
        
        print('inserted another chunk..., took % 3f second' % (t_end - t_start))



if __name__ == '__main__':
    # Execute when the module is not initialized from an import statement.

    parser = argparse.ArgumentParser(description='Ingest CSV data to Postgres')

    parser.add_argument('--user', required=True, help='user name for postgres')
    parser.add_argument('--password', required=True, help='password for postgres')
    parser.add_argument('--host', required=True, help='host for postgres')
    parser.add_argument('--port', required=True, help='port for postgres')
    parser.add_argument('--db', required=True, help='database name for postgres')
    parser.add_argument('--table_name', required=True, help='name of the table where we will write the results to')
    parser.add_argument('--url', required=True, help='url of the csv file')

    #args = parser.parse_args()
    args, unknown = parser.parse_known_args()

    main(args)

