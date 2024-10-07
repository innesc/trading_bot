#FROM python:3.9-slim-buster
#docker --debug build . -t v2_trade
FROM python:3.11-bullseye
WORKDIR /app
COPY /app /app
RUN pip install -r requirements.txt
# Check available python versions
#RUN ls /usr/bin/ | grep python
#ENV PATH="/home/app" # was source of bug
RUN pwd
CMD ["python", "trading_bot.py"]