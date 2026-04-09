# APEX Python Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy all Python files
COPY *.py ./
COPY api/*.py ./api/
COPY start_risk_api.py ./

# Copy requirements
COPY requirements.txt ./

# Install required packages
RUN pip install --no-cache-dir \
    websockets \
    web3 \
    python-dotenv \
    requests \
    openai \
    fastapi \
    uvicorn \
    aiohttp \
    azure-cosmos \
    pandas \
    numpy

# Expose ports for WebSocket server and Risk API
EXPOSE 8766 3002

# Default command: run WebSocket server
CMD ["python", "apex_ws.py"]
