FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir Flask==3.0.0 python-json-logger==2.0.7

# Copy application code
COPY app.py /app/

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

# Run application
CMD ["python", "app.py"]
