import uuid
import os

LANGCHAIN_URL = os.environ.get('URL', 'http://localhost:8000')

PANDASAI_URL = os.environ.get('PANDASAI_URL', 'http://localhost:9000')

PERSIST_DIR = os.environ.get('PERSIST_DIR', 'frontend/app/persist_directory/')

SESSION_ID = str(uuid.uuid4())
