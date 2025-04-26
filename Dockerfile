FROM python:3.13-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app

COPY . .

USER appuser

ENV PATH="/home/appuser/.local/bin:$PATH"
EXPOSE 8080
CMD ["python", "main.py"]