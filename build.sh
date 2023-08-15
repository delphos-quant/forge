#!/bin/bash

create_executable() {
  if ! [ -x "$(command -v pyinstaller)" ]; then
    echo 'Error: pyinstaller is not installed.' >&2
    echo 'Installing pyinstaller...'
    pip install pyinstaller
  fi

  echo 'Creating executable with PyInstaller...'
  pyinstaller --onefile --name=strategy_manager orchestrator/server.py

  if [ ! -f "./dist/strategy_manager" ]; then
    echo 'Error: Failed to create the executable.' >&2
    exit 1
  fi
}

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
  create_executable
  echo '#!/bin/sh' > strategy_manager.sh
  echo './dist/strategy_manager' >> strategy_manager.sh
  chmod +x strategy_manager.sh
  echo 'Build process completed! You can run the application using strategy_manager.sh.'
else
  echo "OS $OSTYPE not supported"
  exit 1
fi
