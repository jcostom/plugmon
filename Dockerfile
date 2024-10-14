FROM python:3.13.0-slim-bookworm AS builder

ARG TZ=America/New_York

RUN apt update && apt -yq install gcc make
RUN \
    pip install requests \
    && pip install pyvesync \
    && pip install python-telegram-bot \
    && pip cache purge

FROM python:3.13.0-slim-bookworm

ARG TZ=America/New_York
ARG PYVER=3.12

COPY --from=builder /usr/local/lib/python$PYVER/site-packages/ /usr/local/lib/python$PYVER/site-packages/

RUN mkdir /app
COPY ./plugmon.py /app
COPY ./finduuid.py /app
RUN chmod 755 /app/plugmon.py
RUN chmod 755 /app/finduuid.py

ENTRYPOINT [ "python3", "-u", "/app/plugmon.py" ]