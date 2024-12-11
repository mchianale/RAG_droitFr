FROM python:3.10.11-slim
WORKDIR /usr/src/app

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

CMD ["uvicorn", "app.main:app", "--workers"]
