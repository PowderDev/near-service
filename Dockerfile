FROM python:3.12-alpine

RUN apk add --no-cache git cargo

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 4000

CMD ["python", "src/main.py"]