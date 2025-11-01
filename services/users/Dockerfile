FROM python:3.11-slim

# Set working directory
WORKDIR /usr/src/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    poppler-utils \
    ffmpeg \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY services/users/requirements.txt /usr/src/app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY services/users/ /usr/src/app/

# Make startup script executable
RUN chmod +x /usr/src/app/startup.sh

# Expose port
EXPOSE 5001

# Run startup script
CMD ["/usr/src/app/startup.sh"]

