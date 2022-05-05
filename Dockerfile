FROM python:slim

ARG TZ=America/New_York

RUN \
    pip install requests \
    && pip install pyvesync \
    && pip install python-telegram-bot \
    && pip cache purge

RUN mkdir /app
COPY ./plugmon.py /app
COPY ./finduuid.py /app
RUN chmod 755 /app/plugmon.py
RUN chmod 755 /app/finduuid.py

ENTRYPOINT [ "python3", "-u", "/app/plugmon.py" ]