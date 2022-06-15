FROM python:3.9-slim

RUN pip install pipenv

RUN mkdir /storage

WORKDIR /app

COPY Pipfile Pipfile.lock pytest.ini ./

RUN pipenv install --system --deploy --dev

COPY ./src ./

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
