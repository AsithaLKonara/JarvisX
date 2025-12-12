#!/bin/bash
echo "Building macOS .app bundle..."
pyinstaller --name=JarvisX-V2 \
    --windowed \
    --onefile \
    --icon=resources/icons/app_icon.icns \
    --add-data "resources:resources" \
    src/main.py
echo "Build complete!"

