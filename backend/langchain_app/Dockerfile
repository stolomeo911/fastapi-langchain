FROM  --platform=linux/amd64 tiangolo/uvicorn-gunicorn-fastapi:python3.11-slim
ENV PYTHONUNBUFFERED=1
ENV PIP_DEFAULT_TIMEOUT=100
ENV SHARED_LIBRARIES=shared_libraries

WORKDIR /code
# Install Poetry
RUN apt clean && apt update && apt install curl -y
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

# Copy poetry.lock* in case it doesn't exist in the repo
COPY backend/langchain_app/app/pyproject.toml backend/langchain_app/app/poetry.lock /code/
COPY backend/langchain_app/app/ /code/app/

COPY ./shared_libraries/ /code/shared_libraries/

# Allow installing dev dependencies to run tests
ARG INSTALL_DEV=false
RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install --no-root ; else poetry install --no-root --only main ; fi"

ENV PYTHONPATH=/code
EXPOSE 8000
