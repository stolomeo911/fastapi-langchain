FROM  --platform=linux/amd64 python:3.10-slim
ENV PYTHONUNBUFFERED=1

# Install Poetry
RUN apt clean && apt update && apt install curl -y
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

# Copy poetry.lock* in case it doesn't exist in the repo
COPY app/pyproject.toml app/poetry.lock /code/
COPY app/ code/app/

WORKDIR /code

ENV PYTHONPATH=/code
#ENV URL='http://fastapi_server:8000'
ENV PERSIST_DIR='helpers/persist_directory'
EXPOSE 8501

ARG INSTALL_DEV=false
RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install --no-root ; else poetry install --no-root ; fi"


#ENTRYPOINT ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
