import pandas as pd
from pandasai import SmartDataframe
from backend.langchain_app.core.utils.db_utils import sql_to_df
import typer
from shared_libraries.utils import setup_logger  # Ensure this path is correct
import yaml
from yaml import Loader


# Set up the logger
logger = setup_logger(__name__)

app = typer.Typer()


@app.command()
def save_df_for_sdf(sql_path: str, output_path: str):
    logger.info(f"Loading data from SQL file: {sql_path}")
    df = sql_to_df(sql_path)
    selected_columns = [
        'contact_id', 'deal_id', 'lead_timestamp', 'region', 'channel', 'sub_channel',
        'trial_booked_date', 'self_booked', 'customer_date',
        'normalised_subject', 'trial_completed', 'is_new_lead']

    integer_columns = ['contact_id', 'deal_id', 'trial_completed', 'is_new_lead', 'self_booked']
    date_columns = ['lead_timestamp', 'customer_date', 'trial_booked_date']
    category_columns = ['region', 'channel', 'sub_channel', 'normalised_subject']

    df_pai = df[selected_columns]
    logger.info("Applying data types to selected columns")

    df_pai[integer_columns] = df_pai[integer_columns].astype('Int64')
    for date_column in date_columns:
        df_pai[date_column] = pd.to_datetime(df_pai[date_column])
    df_pai[category_columns] = df_pai[category_columns].astype('category')

    logger.info(f"Saving DataFrame to pickle: {output_path}")
    df_pai.to_pickle(output_path)

    return df_pai


def get_current_used_pickle():
    config = yaml.load(open('backend/langchain_app/core/agent/training/config.yml'), Loader=Loader)
    df = pd.read_pickle(config['pickle_path'])
    return df


@app.command()
def setup_smart_df_from_pickle(pickle_path: str, llm: str):
    logger.info(f"Loading DataFrame from pickle: {pickle_path}")
    df = pd.read_pickle(pickle_path)

    logger.info("Setting up SmartDataframe")
    sdf = SmartDataframe(df, config={
        "llm": llm,
        "enable_cache": False,
        "custom_whitelisted_dependencies": ["pandasai", "sqlalchemy", "psycopg2-binary"]
    })

    return sdf


if __name__ == "__main__":
    app()
