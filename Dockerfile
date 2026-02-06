FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for static files and database
RUN mkdir -p static templates

# Set environment variables
ENV FLASK_APP=web_app.py
ENV FLASK_ENV=production

# Expose port
EXPOSE 8080

# Create a non-root user
RUN useradd -m -u 1000 flaskuser && chown -R flaskuser:flaskuser /app
USER flaskuser

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "web_app:app"]