# Use the base image as the starting point
FROM feed:latest

# Copy strategy-specific code and files
COPY . .

# Set environment variables or add any other strategy-specific configurations
ENV STRATEGY_NAME="Yahoo Finance Feed"
ENV HTTP_PORT="8001"
ENV WEBSOCKET_PORT="4001"

EXPOSE $HTTP_PORT
EXPOSE $WEBSOCKET_PORT

# Define the command to run when the container starts
CMD ["python", "run.py"]