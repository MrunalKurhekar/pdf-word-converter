FROM python:3.11-slim

# Install LibreOffice
RUN apt-get update && apt-get install -y libreoffice && apt-get clean

# Set working directory
WORKDIR /app

# Copy files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Start server
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:10000"]