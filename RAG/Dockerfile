# Use Python 3.12.3 slim base image
FROM python:3.12.3-slim

# Set working directory in the container
WORKDIR /app

# Copy all necessary files into the container
COPY . /app

# Copy Google credentials file into the container (assuming it's now in the credentials folder in your project)
COPY ./credentials/iprc-456620-6454ff816526.json /app/credentials/iprc-456620-6454ff816526.json

# Set the GOOGLE_APPLICATION_CREDENTIALS environment variable
ENV GOOGLE_APPLICATION_CREDENTIALS="/app/credentials/iprc-456620-6454ff816526.json"

# Install dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt || true

# Expose the port your server runs on
EXPOSE 5000

# Run the Python server
CMD ["python", "server.py"]
