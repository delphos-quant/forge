# Use the base image as the starting point
FROM feed:latest

# Copy strategy-specific code and files
COPY . .

# Set environment variables or add any other strategy-specific configurations
ENV STRATEGY_NAME="Alpaca Markets Feed"
ENV PORT="6001"
ENV HOST="rsi-strategy"
ENV APCA-API-KEY-ID="AKI9TMTIHHES0DAY75BF"
ENV APCA-API-SECRET-KEY="QJwgAMkWu36gdBU1yaubTSeRmNwNw5niHR61cBI7"

RUN pip install alpaca-py

# Define the command to run when the container starts
CMD ["python", "run.py"]