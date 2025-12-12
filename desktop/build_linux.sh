#!/bin/bash
echo "Building Linux AppImage..."
pyinstaller --name=JarvisX-V2 \
    --windowed \
    --onefile \
    --icon=resources/icons/app_icon.png \
    --add-data "resources:resources" \
    src/main.py
echo "Build complete!"

