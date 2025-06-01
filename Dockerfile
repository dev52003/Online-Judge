# Dockerfile
FROM python:3.10

WORKDIR /app
COPY . /app

RUN apt-get update && apt-get install -y gcc

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=myproject.settings

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]