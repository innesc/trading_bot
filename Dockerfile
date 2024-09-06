FROM 3.11-alpine
WORKDIR /app
COPY /app /app
RUN pip install -r /app/requirements.txt
ENV PATH='/home/app'
CMD ['PYTHON','trade_bot.py']