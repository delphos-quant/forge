# Use the base image as the starting point
FROM strategy:latest

# Copy strategy-specific code and files
COPY . .

# Set environment variables or add any other strategy-specific configurations
ENV STRATEGY_NAME="RSI Strategy"
ENV HTTP_PORT=5001
ENV WEBSOCKET_PORT=6001

EXPOSE $HTTP_PORT
EXPOSE $WEBSOCKET_PORT

# Define the command to run when the container starts
CMD ["python", "run.py"]