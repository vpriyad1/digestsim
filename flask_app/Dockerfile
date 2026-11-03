# DigestSim - Flask + SQLite containerized app
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose port Flask runs on
EXPOSE 5000

# Start the app
CMD ["python", "app.py"]
