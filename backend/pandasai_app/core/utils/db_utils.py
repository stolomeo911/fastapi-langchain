
import awswrangler.redshift as rs
import awswrangler.s3 as s3
import boto3
import pandas as pd
import warnings


def get_connection_redshift():
    REDSHIFT_CONNECTION = "redshift-master"
    conn_str = REDSHIFT_CONNECTION
    conn = rs.connect(conn_str)
    return conn


def sql_to_df(sql_file):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fd = open(sql_file, "r")
        sql_file = fd.read()
        fd.close()
        conn_database = get_connection_redshift()
        df = pd.read_sql(sql_file, conn_database)
    return df