from fastapi import APIRouter, HTTPException, Response
import pandas as pd
from backend.langchain_app.core.utils.db_utils import get_connection_redshift
from backend.langchain_app.api.models import Feedback
import logging
import awswrangler.redshift as rs


logger = logging.getLogger(__name__)

router = APIRouter()


@router.get('/')
async def index():
    return {"status": 200}


@router.post('/save_feedback')
async def save_feedback(feedback: Feedback):
    try:
        if type(feedback.answer) == pd.DataFrame:
            feedback.answer = feedback.answer.head().to_string()
        feedback.answer = str(feedback.answer)[:200]
        feedback.question = str(feedback.question)[:200]
        df = pd.DataFrame(dict(feedback), index=[0])
        df['total_cost'] = df['total_cost'].round(6)
        conn = get_connection_redshift()
        rs.to_sql(df=df, table='apollo_feedback_logs', schema='ml_output', con=conn, mode="upsert", primary_keys=['user_id', 'timestamp', 'question'], lock=True)
        conn.close()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500)