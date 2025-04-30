ARG PYTHON=python:3.11
FROM ${PYTHON}

WORKDIR /manowhisper

COPY . .

RUN pip install --upgrade pip \
    && pip install -e .

ENTRYPOINT ["manowhisper"]
