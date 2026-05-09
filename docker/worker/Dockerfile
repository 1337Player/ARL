# syntax=docker/dockerfile:1
FROM python:3.11-slim-bookworm AS builder
ENV DEBIAN_FRONTEND noninteractive
WORKDIR /opt/
RUN set -x; \
    apt-get update \
    && apt-get install -y g++ make wget libssl-dev zlib1g-dev git \
    && git clone https://github.com/blechschmidt/massdns.git \
    && cd /opt/massdns \
    && make \
    && /opt/massdns/bin/massdns --version \
    && cd /opt/ \
    && wget https://nmap.org/ncrack/dist/ncrack-0.7.tar.gz --no-check-certificate \
    && tar -xzf ncrack-0.7.tar.gz \
    && cd ncrack-0.7 \
    && ./configure \
    && make \
    && /opt/ncrack-0.7/ncrack -V


FROM python:3.11-slim-bookworm
ENV DEBIAN_FRONTEND noninteractive
ENV LANG en_US.UTF-8

WORKDIR /code

RUN set -x; \
    apt-get update \
    && apt-get install -y --no-install-recommends \
        nginx nmap wget unzip \
        fonts-wqy-microhei \
        fontconfig \
        python3-dev gcc \
    && useradd -s /bin/false nginx \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY docker/ARL-NPoC/ /opt/ARL-NPoC/
WORKDIR /opt/ARL-NPoC/
RUN pip install --no-cache-dir -e . \
    && pip install --no-cache-dir -r requirements.txt

RUN apt-get purge -y python3-dev gcc && apt-get autoremove -y

WORKDIR /code
COPY app/ app/
COPY test/ test/
COPY --from=builder /opt/ncrack-0.7/ncrack /usr/local/bin/ncrack
COPY --from=builder /opt/ncrack-0.7/ncrack-services /usr/local/share/ncrack/ncrack-services
COPY --from=builder /opt/massdns/bin/massdns app/tools/massdns
COPY docker/frontend/ frontend/
COPY docker/nginx.conf  /etc/nginx/nginx.conf

COPY docker/worker/gen_crt.sh /usr/bin/gen_crt.sh
COPY docker/worker/wait-for-it.sh /usr/bin/wait-for-it.sh

COPY docker/GeoLite2/ /data/GeoLite2/

RUN curl https://ssl-config.mozilla.org/ffdhe2048.txt -o /etc/ssl/certs/dhparam.pem

ARG TARGETARCH
ARG NUCLEI_VERSION=3.2.4
RUN wget "https://github.com/projectdiscovery/nuclei/releases/download/v${NUCLEI_VERSION}/nuclei_${NUCLEI_VERSION}_linux_${TARGETARCH}.zip" \
    && unzip "nuclei_${NUCLEI_VERSION}_linux_${TARGETARCH}.zip" nuclei \
    && mv nuclei /usr/bin/ \
    && rm -f "nuclei_${NUCLEI_VERSION}_linux_${TARGETARCH}.zip"

RUN nuclei -ut

RUN wget https://github.com/1c3z/arl_files/raw/master/wih/wih_linux_${TARGETARCH} -O /usr/bin/wih \
    && chmod +x /usr/bin/wih

WORKDIR /code

RUN env FLASK_APP=app.main:arl_app python -m flask routes
RUN python -m app.celerytask
