#!/bin/bash
# Build script for macOS
pip install -r requirements.txt
pyinstaller StopMotion.spec --clean --noconfirm
echo "Build complete. Check the dist/ folder for StopMotionBuilder.app"
