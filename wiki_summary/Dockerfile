FROM python:3.10 as base
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app

FROM base as poetry
RUN pip install poetry==1.7.1
COPY poetry.lock pyproject.toml /app/
RUN poetry export -o requirements.txt

FROM base as build
COPY --from=poetry /app/requirements.txt /tmp/requirements.txt
COPY configs/index_enwiki.db configs/index_enwiki.db
RUN python -m venv .venv && \
    .venv/bin/pip install 'wheel==0.42.0' && \
    .venv/bin/pip install -r /tmp/requirements.txt && \
    .venv/bin/python -m spacy download en_core_web_md  install

FROM python:3.10-slim as runtime
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app
ENV PATH=/app/.venv/bin:$PATH
COPY --from=build /app/.venv /app/.venv
COPY commons /app/commons
COPY wiki_summary /app/wiki_summary
COPY summary_processor.py /app/main.py

ENTRYPOINT ["python", "main.py"]
