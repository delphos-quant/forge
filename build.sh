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

package() {
  # Create the .sh launcher
  echo '#!/bin/sh' > dist/strategy_manager.sh
  echo './strategy_manager' >> dist/strategy_manager.sh
  echo './strategy_manage.specr' >> dist/strategy_manager.spec
  chmod +x dist/strategy_manager.sh

  # Create the tarball
  (
    cd dist || { echo "Failed to change to dist directory"; exit 1; }
    tar -czvf strategy_manager_linux.tar.gz strategy_manager strategy_manager.sh
  )
}

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
  create_executable
  package
  echo 'Build and packaging process completed! You can find the tarball in the dist directory.'
else
  echo "OS $OSTYPE not supported"
  exit 1
fi
