FROM python:3.12-slim-bookworm

WORKDIR /app

# Install Tesseract OCR and Poppler using HTTPS
RUN sed -i 's|http://|https://|g' /etc/apt/sources.list.d/debian.sources \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
       tesseract-ocr \
       poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=300 --retries=10 -r requirements.txt

# Copy application
COPY app ./app

# Start API server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]