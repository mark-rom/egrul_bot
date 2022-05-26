FROM apache/beam_python3.6_sdk

RUN mkdir -p /usr/src/bot/
WORKDIR /usr/src/bot/

COPY . /usr/src/bot/
RUN pip install -r requirements.txt

EXPOSE 8080

CMD ["python", "bot.py"]
