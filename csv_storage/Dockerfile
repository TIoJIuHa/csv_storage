FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip3 install -r requirements.txt --no-cache-dir

RUN python3 create_database.py

CMD ["python3", "app.py"] 