import logging
import sys
import awswrangler.redshift as rs
import boto3
from retrying import retry
import pandas as pd


def setup_logger(name) -> logging.Logger:
    # Create a logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        # Create a stream handler that will write to stdout
        handler = logging.StreamHandler(sys.stdout)

        # Create a formatter and set it for the handler
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)

        # Add the handler to the logger
        logger.addHandler(handler)
    logger.propagate = False

    return logger


def get_connection_redshift():
    REDSHIFT_CONNECTION = "redshift-master"
    conn_str = REDSHIFT_CONNECTION
    conn = rs.connect(conn_str)
    return conn


@retry
async def save_feedback(feedback_dict):
    if type(feedback_dict['answer']) == pd.DataFrame:
        feedback_dict['answer'] = feedback_dict['answer'].head().to_string()
    feedback_dict['answer'] = str(feedback_dict['answer'])[:200]
    df = pd.DataFrame(feedback_dict, index=[0])
    df['total_cost'] = df['total_cost'].round(6)
    df = df.drop(columns=['context_session_feedback'])
    conn = get_connection_redshift()
    rs.to_sql(df=df, table='apollo_feedback_logs',
              schema='ml_output',
              con=conn,
              mode="upsert",
              primary_keys=['user_id', 'timestamp', 'question'],
              lock=True)
    conn.close()
