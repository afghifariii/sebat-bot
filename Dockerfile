FROM python:3.7

RUN pip install python-telegram-bot
RUN pip install apscheduler

RUN mkdir /app
ADD sebatbot.py /app
WORKDIR /app

CMD python /app/sebatbot.py