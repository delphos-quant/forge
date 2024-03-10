# Use the base image as the starting point
FROM feed:latest

# Copy strategy-specific code and files
COPY . .

# Set environment variables or add any other strategy-specific configurations
ENV STRATEGY_NAME="Alpaca Markets Feed"
ENV WEBSOCKET_PORT="6001"

EXPOSE $HTTP_PORT
EXPOSE $WEBSOCKET_PORT

RUN pip install alpaca-py

# Define the command to run when the container starts
CMD ["python", "run.py"]