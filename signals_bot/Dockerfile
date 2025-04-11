# Use an official Python base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install system dependencies (including nano)
RUN apt-get update && apt-get install -y \
    build-essential \
    nano \
    && rm -rf /var/lib/apt/lists/*


RUN apt-get update && apt-get install -y gcc libpq-dev
RUN pip install --upgrade pip setuptools wheel


# Copy the requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["python", "main.py"]