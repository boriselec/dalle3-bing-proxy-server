FROM python:3.11-slim-bullseye

RUN apt-get update && apt-get install -y --no-install-recommends \
chromium \
&& \
apt-get clean && \
rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir dalle3

COPY server.py /usr/local/bin

EXPOSE 8081

ENTRYPOINT [ "python3", "/usr/local/bin/server.py" ]
