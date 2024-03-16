# Use the base image as the starting point
FROM strategy:latest

# Copy strategy-specific code and files
COPY . .

# Set environment variables or add any other strategy-specific configurations
ENV STRATEGY_NAME="RSI Strategy"
ENV HTTP_PORT=8002
ENV INTERFACE_PORT=4001

# Define the command to run when the container starts
CMD ["python", "run.py"]