#FROM python:3.9-slim-buster
FROM python:3.11-bullseye
WORKDIR /app
COPY /app /app
RUN pip install -r requirements.txt
RUN pwd
CMD ["python", "trading_bot.py"]