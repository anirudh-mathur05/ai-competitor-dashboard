FROM python:3.10-slim

WORKDIR /app

# Install dependencies from root requirements.txt
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the backend folder into container
COPY backend /app/backend

# Expose API port
EXPOSE 8000

# Run FastAPI backend
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
