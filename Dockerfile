FROM mcr.microsoft.com/playwright/python:jammy

RUN pip install --upgrade pip
RUN pip install playwright

WORKDIR /app

COPY lock.py /app/
COPY entrypoint.sh /app/

ENTRYPOINT ["/app/entrypoint.sh"]
