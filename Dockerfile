FROM python:3.12-slim

# Install system dependencies (Chrome + chromedriver)
RUN apt-get update && apt-get install -y \
    build-essential \
    wget gnupg unzip curl \
    chromium chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Environment variables for Chrome
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_BIN=/usr/lib/chromium/chromedriver
ENV PATH="${PATH}:${CHROMEDRIVER_BIN}"

# Set working directory
WORKDIR /app

# Copy project files into the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Flask port
EXPOSE 5000

# Set Flask environment (optional if using .flaskenv)
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# Run the Flask app
CMD ["python", "-u", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
