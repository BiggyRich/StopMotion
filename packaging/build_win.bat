@echo off
:: Build script for Windows
pip install -r requirements.txt
pyinstaller StopMotion.spec --clean
echo Build complete. Check the dist\ folder for StopMotionBuilder.exe
pause
