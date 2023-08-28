FROM python:3.8-slim

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app
RUN pip3 install -r /app/requirements.txt --no-cache-dir

COPY ./ /app

RUN ["mkdir", "logs"]

CMD ["python", "bot.py"]
