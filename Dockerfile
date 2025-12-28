FROM python:3.9-slim

WORKDIR /app

# Install system dependencies for ReportLab (fonts, etc.) if needed
RUN apt-get update && apt-get install -y \
    libfreetype6-dev \
    libxft-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Environment variables
ENV FLASK_APP=wtf_app_simple.py
ENV PYTHONUNBUFFERED=1

# Expose internal port
EXPOSE 5000

# Entrypoint script to handle DB init
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
