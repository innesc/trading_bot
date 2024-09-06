from 3.11-alpine
WORKDIR /app
COPY /app /app
RUN pip install -r requirements.txt
ENV 
CMD ['PYTHON','trade_bot.py']