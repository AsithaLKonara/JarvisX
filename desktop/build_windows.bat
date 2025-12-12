@echo off
echo Building Windows executable...
pyinstaller --name=JarvisX-V2 ^
    --windowed ^
    --onefile ^
    --icon=resources/icons/app_icon.ico ^
    --add-data "resources;resources" ^
    src/main.py
echo Build complete!

