#!/bin/bash

ENTRY="dxforge/main.py"
BUILD_DIR="build"
# requirements are in requirements.txt
create_executable() {
  if ! [ -x "$(command -v pyinstaller)" ]; then
    echo 'Error: pyinstaller is not installed.' >&2
    echo 'Installing pyinstaller...'
    pip install pyinstaller
  fi

  echo 'Building module with PyInstaller...'
  pyinstaller --noconfirm --name dxforge "$ENTRY"

  echo 'Cleaning up...'
  rm -rf "$BUILD_DIR"

  echo 'Executable created successfully!'
  echo 'Run it with ./dist/dxforge/dxforge'
}

package() {
  # Create the .sh launcher
  echo '#!/bin/sh' > dist/dxforge.sh
  echo './dxforge' >> dist/dxforge.sh
  echo './dxforge.specr' >> dist/dxforge.spec
  chmod +x dist/dxforge.sh

  # Create the tarball
  (
    tar -czvf dist/dxforge.tar.gz \
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
      --exclude='dxforge.tar.gz' \
      --transform='s,^,dxforge/,' \
      *
  )
}

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
  create_executable
  echo 'Build and packaging process completed! You can find the tarball in the dist directory.'
else
  echo "OS $OSTYPE not supported"
  exit 1
fi
