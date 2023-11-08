FROM python:3

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app
COPY ./static /code/static
COPY ./templates /code/templates

CMD ["uvicorn", "wsgi:app", "--workers", "2", "--host", "0.0.0.0", "--port", "80"]
