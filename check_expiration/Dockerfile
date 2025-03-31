# Use a lightweight Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install system dependencies including nano
RUN apt-get update && apt-get install -y \
    build-essential \
    nano \
    && rm -rf /var/lib/apt/lists/*

# Install psycopg2 dependencies if using PostgreSQL
RUN apt-get update && apt-get install -y gcc libpq-dev

# Copy requirements first for layer caching
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY . .

# Set environment variables (optional)
ENV PYTHONUNBUFFERED=1

# Command to run the bot
CMD ["python", "check_expirations.py"]