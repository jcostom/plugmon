FROM python:slim

ARG BUILD_DATE
ARG VCS_REF

ENV TZ=America/New_York

LABEL org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.vcs-url="https://github.com/jcostom/plugmon.git" \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.schema-version="1.0.0"

RUN \
    pip install requests \
    && pip install pyvesync

RUN mkdir /app
COPY ./plugmon.py /app
COPY ./finduuid.py /app
RUN chmod 755 /app/plugmon.py
RUN chmod 755 /app/finduuid.py

ENTRYPOINT [ "python3", "-u", "/app/plugmon.py" ]