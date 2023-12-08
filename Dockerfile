FROM python:latest

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

RUN chmod +x /app/init.sh
RUN ls -la /app

CMD ["sh", "/app/init.sh"]
