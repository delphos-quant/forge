FROM strategy:latest
LABEL authors="rzimmerdev"

# Copy strategy-specific code and files
COPY . .

# Set environment variables or add any other strategy-specific configurations
ENV STRATEGY_NAME="Windsock Tendency Strategy"
ENV HTTP_PORT=4002
ENV WEBSOCKET_PORT=5002

EXPOSE $HTTP_PORT
EXPOSE $WEBSOCKET_PORT

# Define the command to run when the container starts
CMD ["python", "run.py"]