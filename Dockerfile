FROM mcr.microsoft.com/playwright/python:jammy

RUN pip install --upgrade pip
RUN pip install playwright

COPY lock.py /app/
COPY entrypoint.sh /app/

ENTRYPOINT ["/app/entrypoint.sh"]
