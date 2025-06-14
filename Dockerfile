# Start from an official Python base image
FROM python:3.11-slim

# Set working directory in the container
WORKDIR /app/src

# Install system dependencies (for pip and wheels)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Now copy the rest of your application code
COPY . .

# Expose port (optional, for local testing/documentation)
EXPOSE 9000

# Run the app (modify this line for your actual entrypoint)
CMD ["uvicorn", "app.src.main:app", "--host", "0.0.0.0", "--port", "9000"]
