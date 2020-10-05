FROM python:alpine
LABEL maintainer="Ian Spence <ian@ecn.io>"

RUN pip3 install requests
ADD download.py /download.py

VOLUME /backup
WORKDIR /backup

ENV PFSENSE_HOST=''
ENV PFSENSE_USERNAME=''
ENV PFSENSE_PASSWORD=''
ENV PFSENSE_ALLOW_UNTRUSTED_CERTIFICATES=''
ENV PFSENSE_ENCRYPT_PASSWORD=''

ENTRYPOINT ["python3", "/download.py"]