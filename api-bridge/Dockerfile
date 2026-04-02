FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY zhipu_bridge.py .

EXPOSE 8080

CMD ["python", "zhipu_bridge.py"]
