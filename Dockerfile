FROM mcr.microsoft.com/playwright/python:jammy

RUN pip install --upgrade pip
RUN pip install playwright

WORKDIR /app

COPY lock.py ./
COPY entrypoint.sh ./

ENTRYPOINT ["./entrypoint.sh"]
