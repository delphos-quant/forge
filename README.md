# dxlib Forge

The Forge suite is a API-based orchestration server that integrates with multiple managers. This allows users to manage different strategies, feeds and portfolios via a centralized instance.

## Getting Started (Using Precompiled Executables)

If you prefer not to go through the installation process or simply want to run the `strategy_manager` without having Python and the dependencies set up, you can use the precompiled executables. This is especially useful for deployment or sharing with users who might not be familiar with Python environments.

1. Navigate to the [Releases section](https://github.com/delphos-quant/strategy-manager/releases).
2. Download the appropriate file for your operating system:
    - `strategy_manager.sh` for Linux/macOS
    - `strategy_manager.exe` for Windows
3. After downloading, follow the instructions below.

### For Linux/macOS Users

1. First, you'll need to extract the compressed file. If you've downloaded the \`**strategy_manager_linux.tar.gz**\` from the releases, you can decompress it using the following command:

```bash
tar -xzvf strategy_manager_linux.tar.gz
```

This will extract the contents, including strategy_manager.sh (the shell script) and the actual compiled binary strategy_manager.

To run the strategy manager using the shell script:

2. Access the directory containing the sample strategy and feed managers

    ```bash
    cd strategy-manager
    ```

3. Run the script:

    ```bash
    ./dist/strategy-manager [config_file] [--host] [--port]
    # e.g. ./dist/strategy-manager config.yaml
    ```

Replace `[arguments]` with any command-line arguments you wish to pass to the strategy manager.

### For Windows Users

A standalone executable named `strategy-manager.exe` is available for Windows users.

To run the strategy manager using the executable:

1. Navigate to the directory containing the project files using the Command Prompt or PowerShell.
    ```powershell
   cd strategy-manager
   ```    

2. Run the executable:

    ```powershell
    .\dist\strategy-manager.exe [config_file] [--host] [--port]
    # e.g. .\dist\strategy-manager.exe config.yaml
    ```

Replace `[arguments]` with any command-line arguments you wish to pass to the strategy manager.

**Note**: The first time you run these executables, your operating system might prompt you to verify if you trust software from the publisher. Ensure you trust the source (in this case, the `strategy_manager` project) before proceeding.


## Getting Started (compiling from Source)

### Requirements

- Python 3.7+
- FastAPI
- httpx
- yaml
- uvicorn
- dxlib (Sample usage provided in `my_strategy.py`)

1. Clone the repository:
   ```bash
   git clone github.com/dxlib/strategy-manager
   ```

2. Navigate to the repository directory and create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - For Linux/macOS:
     ```bash
     source venv/bin/activate
     ```
   - For Windows:
     ```bash
     venv\Scripts\activate
     ```

4. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Server

To start the orchestration server:

```bash
python app.py config.yaml
```

Optional command-line arguments:
- `--host` to specify the host (default is `0.0.0.0`)
- `--port` to specify the port (default is `8000`)

## Functionalities

- **Listing Strategies**:  
   Visit `http://localhost:8000/strategy/` to get a list of all available strategies.

- **Refreshing Strategy Status**:  
   POST request to `http://localhost:8000/strategy/` to refresh the status of all strategies.

- **Proxy Get Routes for a Strategy**:  
   GET request to `http://localhost:8000/strategy/{strategy}/` to get routes available for a strategy.

- **Proxy Get and Post Methods for a Strategy Endpoint**:  
   - GET: `http://localhost:8000/strategy/{strategy}/{endpoint}`
   - POST: `http://localhost:8000/strategy/{strategy}/{endpoint}` with appropriate data payload.

## Sample strategy for testing

A sample strategy folder (`strategies/rsi-strategy`) is provided to demonstrate how to use the `dxlib` library. 
This script uses historical stock data for a set of tickers, runs a simple RSI strategy on the data, and calculates a list of signals.

To run the sample strategy manager instance:
```bash
python strategies/rsi-strategy/run.py
```

And in another terminal, run the strategy manager:
```bash
 python app.py config.yaml
# or
# ./dist/strategy_manager config.yaml
```

## Configuration

Managers can be added or removed by modifying the a _yaml_ file.

Example:
_**config.yaml**_
```yaml
{
  "feeds": "feeds/docker-compose.yaml",
  "strategies": "strategies/docker-compose.yaml",
  "port": "5000",
  "host": "0.0.0.0"
}
```

In this configuration, `strategies` has a list of docker compose services that serve on different ports. These available ports can be accessed at `http://localhost:5000`.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[Apache](https://www.apache.org/licenses/LICENSE-2.0)
