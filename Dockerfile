FROM alpine:3.12

ARG BUILD_DATE
ARG VCS_REF

LABEL org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.vcs-url="https://github.com/jcostom/dnsomatic-update.git" \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.schema-version="1.0.0"

VOLUME "/config"

RUN \
    apk add --no-cache py3-requests py3-pip \
    && rm -rf /var/cache/apk/* \
    && pip install pyvesync

RUN mkdir /app
COPY ./plugmon.py /app
RUN chmod 755 /app/plugmon.py

ENTRYPOINT [ "python3", "-u", "/app/plugmon.py" ]