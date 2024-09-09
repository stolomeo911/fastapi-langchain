FROM  --platform=linux/amd64 python:3.11-slim as build

# Set environment variables to ensure Python/Pip behavior is as expected
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    POETRY_VERSION=1.7.1 \
    POETRY_ROOT_FOLDER=../../ \
    FOLDER_ROOT=backend/pandasai_app \
    SHARED_LIBRARIES=shared_libraries

# Adjust the PATH to include Poetry and ensure global packages are on it
ENV PATH="$POETRY_HOME/bin:$PATH"


# Install Poetry
RUN pip install "poetry==$POETRY_VERSION"
COPY $FOLDER_ROOT/pyproject.toml $FOLDER_ROOT/poetry.lock ./

# Poetry Project initialization:
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root


COPY ./$FOLDER_ROOT/ opt/$FOLDER_ROOT/

COPY ./$SHARED_LIBRARIES/ opt/$SHARED_LIBRARIES/

WORKDIR opt/

CMD uvicorn backend.pandasai_app.main:app --port 9000