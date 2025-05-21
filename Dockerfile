# Use a base image with Python and OpenJDK installed
FROM openjdk:17-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV JAVA_HOME /usr/local/openjdk-17
ENV PATH="$JAVA_HOME/bin:$PATH"

# Install Python, pip, and necessary dependencies
RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-venv git curl unzip && \
    pip3 install --upgrade pip

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Start FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
