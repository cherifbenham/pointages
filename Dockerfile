FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the agent webapp code

# Copy the agent webapp code
COPY agent ./agent

# Copy .env file for environment variables
COPY .env .env

# Expose Streamlit default port
EXPOSE 8501

# Run the Streamlit app
CMD ["streamlit", "run", "agent/agent.py", "--server.port=8501", "--server.address=0.0.0.0"]
