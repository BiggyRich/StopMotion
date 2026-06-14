# StopMotion Builder

StopMotion Builder is a simple, cross-platform desktop application designed to convert image sequences into high-quality videos using FFmpeg. It's perfect for creating stop-motion animations, timelapses, or slideshows with ease.

## ✨ Features

- **Drag-and-Drop Interface**: Easily add images or entire folders by dragging them into the app.
- **Manual Reordering**: Drag and drop items in the list to fine-tune your animation sequence.
- **Auto-Resolution Detection**: Automatically matches the output resolution to your images if they share the same dimensions.
- **Customizable FPS**: Set your frame rate (from 1 to 60 FPS) to control the speed of your animation.
- **Real-time Preview**: See your animation in action before you export.
- **Professional Export**: Uses FFmpeg with high-quality H.264 encoding and automatic letterboxing to fit target resolutions (1080p, 720p, 4K, or Source).

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+**
- **FFmpeg**: Ensure FFmpeg is installed and available in your system's PATH.
  - *macOS*: `brew install ffmpeg`
  - *Windows*: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH.

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd StopMotion
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/bin/activate  # macOS/Linux
   # OR
   venv\Scripts\activate         # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running in Development

To run the application locally:
```bash
python main.py
```

## 📦 Building Standalone Executables

The project includes pre-configured scripts for building standalone apps using PyInstaller.

### macOS
Run the build script:
```bash
./packaging/build_mac.sh
```
The result will be in `dist/StopMotionBuilder.app`.

### Windows
Run the build script:
```batch
packaging\build_win.bat
```
The result will be in `dist\StopMotionBuilder.exe`.

*Note: The build scripts are configured to bundle your system's FFmpeg binary for a truly standalone experience.*

## 🛠 Tech Stack

- **UI Framework**: PySide6 (Qt for Python)
- **Image Processing**: Pillow
- **Video Engine**: FFmpeg
- **Packaging**: PyInstaller

## ⚖️ License

[MIT License](LICENSE)
