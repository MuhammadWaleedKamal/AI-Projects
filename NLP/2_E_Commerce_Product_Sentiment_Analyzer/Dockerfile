# 1. Base Image
FROM python:3.10-slim

# 2. Working Directory
WORKDIR /app

ENV PYTHONUNBUFFERED=1

# 3. System Dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt-get/lists/*

# 4. Requirements Copy & Install
COPY requirements.txt .

# Install PyTorch CPU-only version first
RUN pip install --no-cache-dir torch --extra-index-url https://download.pytorch.org/whl/cpu

# Install remaining dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download SpaCy model
RUN python -m spacy download en_core_web_sm

# 5. Copy Application Code
COPY . .

# 6. Expose Port
EXPOSE 8000

# 7. Uvicorn Command
CMD ["uvicorn", "api.index:app", "--host", "0.0.0.0", "--port", "8000"]