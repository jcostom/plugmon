FROM python:slim

ENV TZ=America/New_York

RUN apt update && apt -yq install netcat

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

HEALTHCHECK --interval=1m --timeout=10s --retries=3 \
    CMD [ "/bin/nc", "-z", "smartapi.vesync.com", "443" ] || exit 1

ENTRYPOINT [ "python3", "-u", "/app/plugmon.py" ]