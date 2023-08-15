# Strategy Manager

Strategy Manager is a FastAPI-based orchestration server that integrates with multiple managers. This allows users to manage different strategies via a centralized API.

## Getting Started (Using Precompiled Executables)


If you prefer not to go through the installation process or simply want to run the `strategy_manager` without having Python and the dependencies set up, you can use the precompiled executables. This is especially useful for deployment or sharing with users who might not be familiar with Python environments.

1. Navigate to the [Releases section](https://github.com/delphos-quant/strategy-manager/releases).
2. Download the appropriate file for your operating system:
    - `strategy_manager.sh` for Linux/macOS
    - `strategy_manager.exe` for Windows
3. After downloading, follow the instructions below.

### For Linux/macOS Users

A shell script named `strategy_manager.sh` is provided. This script encapsulates the actual compiled binary for ease of use.

To run the strategy manager using the shell script:

1. Ensure the script has execute permissions:

    ```bash
    chmod +x strategy_manager.sh
    ```

2. Run the script:

    ```bash
    ./strategy_manager.sh [arguments]
    ```

Replace `[arguments]` with any command-line arguments you wish to pass to the strategy manager.

### For Windows Users

A standalone executable named `strategy_manager.exe` is available for Windows users.

To run the strategy manager using the executable:

1. Navigate to the directory containing `strategy_manager.exe` using the Command Prompt or PowerShell.

2. Run the executable:

    ```powershell
    .\strategy_manager.exe [arguments]
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
python server.py my_managers.yaml
```

Optional command-line arguments:
- `--host` to specify the host (default is `0.0.0.0`)
- `--port` to specify the port (default is `8000`)

## Functionalities

- **Listing Managers**:  
   Visit `http://localhost:8000/managers/` to get a list of all available managers.

- **Refreshing Manager Status**:  
   POST request to `http://localhost:8000/managers/` to refresh the status of all managers.

- **Proxy Get Routes for a Manager**:  
   GET request to `http://localhost:8000/managers/{manager_name}/` to get routes available for a manager.

- **Proxy Get and Post Methods for a Manager Endpoint**:  
   - GET: `http://localhost:8000/managers/{manager_name}/{endpoint}`
   - POST: `http://localhost:8000/managers/{manager_name}/{endpoint}` with appropriate data payload.

## Sample strategy for testing

A sample strategy script (`my_strategy.py`) is provided to demonstrate how to use the `dxlib` library. This script fetches historical stock data for a set of tickers, runs a simple RSI strategy on the data, and calculates returns.

To run the sample strategy manager instance:
```bash
python managers_example/my_strategy.py
```

And in another terminal, run the strategy manager:
```bash
./strategy_manager.sh managers_example/my_managers.yaml
# or
# python server.py my_managers.yaml
```

## Configuration

Managers can be added or removed by modifying the a _yaml_ file.

Example:
_**my_managers.yaml**_
```yaml
simulation_manager_1:
  route: "http://localhost:5000"
execution_manager2:
  route: "http://localhost:6002"
  disabled: true
```

In this configuration, `simulation_manager_1` is enabled and available at `http://localhost:5000`, while `execution_manager2` is disabled.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[Apache](https://www.apache.org/licenses/LICENSE-2.0)
