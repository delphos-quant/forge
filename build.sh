#!/bin/bash

create_executable() {
  if ! [ -x "$(command -v pyinstaller)" ]; then
    echo 'Error: pyinstaller is not installed.' >&2
    echo 'Installing pyinstaller...'
    pip install pyinstaller
  fi

  echo 'Creating executable with PyInstaller...'
  pyinstaller --onefile --name=strategy-manager orchestrator/server.py

  if [ ! -f "./dist/strategy-manager" ]; then
    echo 'Error: Failed to create the executable.' >&2
    exit 1
  fi
}

package() {
  # Create the .sh launcher
  echo '#!/bin/sh' > dist/strategy-manager.sh
  echo './strategy-manager' >> dist/strategy-manager.sh
  echo './strategy-manager.specr' >> dist/strategy-manager.spec
  chmod +x dist/strategy-manager.sh

  # Create the tarball
  (
    tar -czvf dist/strategy-manager.tar.gz \
      --exclude='build' \
      --exclude='.git' \
      --exclude='.gitignore' \
      --exclude='.idea' \
      --exclude='*.spec' \
      --exclude='*.log' \
      --exclude='*.pyc' \
      --exclude='build.sh' \
      --exclude='build.bat' \
      --exclude='requirements.txt' \
      --exclude='strategy-manager.tar.gz' \
      --transform='s,^,strategy-manager/,' \
      *
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
