# Use the base image as the starting point
FROM feed:latest

# Copy strategy-specific code and files
COPY . .

# Set environment variables or add any other strategy-specific configurations
ENV STRATEGY_NAME="Yahoo Finance Feed"
ENV WEBSOCKET_PORT="7002"

EXPOSE $WEBSOCKET_PORT

# Define the command to run when the container starts
CMD ["python", "run.py"]