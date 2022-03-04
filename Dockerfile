FROM python:slim

ENV TZ=America/New_York

RUN apt update && apt -yq install curl

RUN \
    pip install requests \
    && pip install pyvesync \
    && pip cache purge

RUN mkdir /app
COPY ./plugmon.py /app
COPY ./finduuid.py /app
RUN chmod 755 /app/plugmon.py
RUN chmod 755 /app/finduuid.py

HEALTHCHECK --interval=5m --timeout=10s --retries=3 \
    CMD /bin/curl -f https://smartapi.vesync.com/cloud/v1 || exit 1

ENTRYPOINT [ "python3", "-u", "/app/plugmon.py" ]