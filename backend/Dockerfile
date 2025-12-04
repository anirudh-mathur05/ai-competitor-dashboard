FROM python:3.10-slim

WORKDIR /app

# Install backend dependencies (root requirements.txt includes FastAPI, httpx, etc.)
COPY ../requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy backend code into the container
COPY . /app/backend

# Expose API port
EXPOSE 8000

# Start FastAPI app
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
