FROM python:3.12.6

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /django_app
COPY . /django_app/

RUN pip install -r requirements.txt

#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

CMD ["sh", "-c", "python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]

EXPOSE 8000