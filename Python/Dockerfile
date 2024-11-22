FROM python:3.8-slim

WORKDIR /app

# Copy requirements file into container
COPY requirements.txt .

# Install dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Download and install DragonflyDB
RUN apt-get update && \
    apt-get install -y curl && \
    curl -L https://github.com/dragonflydb/dragonfly/releases/latest/download/dragonfly-x86_64.tar.gz | tar xz && \
    mv dragonfly-x86_64 /usr/local/bin/dragonfly

# Copy the rest of app code to container
COPY . .

# Expose ports
EXPOSE 8080 6379 6380 6381

# Start 3 nodes
CMD ["sh", "-c", \
    "dragonfly --port 6379 & " \
    "dragonfly --port 6380 & " \
    "dragonfly --port 6381 & " \
    "sleep 5 && " \
    "python3 main.py"]