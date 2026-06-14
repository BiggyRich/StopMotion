```markdown
# Stop-Motion Video Builder (FFmpeg Desktop App)

## 🎯 Goal

Build a simple desktop application that converts a folder of image frames into a video file using FFmpeg.

The images are typically named in a timestamp format such as:

```

20260613_185030.jpg
20260613_185031.jpg
20260613_185032.jpg

```

The app should:

- Load a folder of images
- Sort them in chronological order
- Convert them into a smooth video (stop-motion / timelapse style)
- Export an `.mp4` file using FFmpeg
- Provide a simple graphical interface for non-technical users

---

## 🧰 Tech Stack

### Core Language
- Python 3.11+

### GUI Framework
- PySide6 (Qt for Python)

### Video Encoding
- FFmpeg (external binary, bundled or user-installed)

### Packaging
- PyInstaller (for Windows/macOS executables)

### Optional Enhancements
- pathlib (file handling)
- shutil (file copying if needed)
- subprocess (FFmpeg execution)

---

## 🧱 Core Features (MVP)

### 1. Folder Input
- User selects a folder containing image frames
- Supported formats:
  - `.jpg`
  - `.png`

---

### 2. Sorting Logic
Images must be sorted by:

Default:
- Filename (lexicographic order)

Optional modes:
- Creation time
- Modification time

Important:
- Filenames like `YYYYMMDD_HHMMSS.jpg` should sort correctly lexicographically

---

### 3. Video Generation Pipeline

Two acceptable approaches:

#### Option A (Preferred): FFmpeg concat file
- Generate a text file:

```

file 'image1.jpg'
file 'image2.jpg'
file 'image3.jpg'

````

- Pass to FFmpeg:

```bash
ffmpeg -f concat -safe 0 -i images.txt -r 24 -c:v libx264 -pix_fmt yuv420p output.mp4
````

---

#### Option B: Numbered sequence (fallback)

* Copy or rename images to:

```
00001.jpg
00002.jpg
00003.jpg
```

* Run:

```bash
ffmpeg -framerate 24 -i %05d.jpg output.mp4
```

---

### 4. User Controls (GUI)

The application must include:

* Folder picker
* Output file picker
* FPS input (default: 24)
* Sort mode selector
* “Generate Video” button
* Progress/log output window

---

### 5. FFmpeg Integration

The app must:

* Call FFmpeg via `subprocess`
* Capture stdout/stderr for progress feedback
* Detect missing FFmpeg binary and show error message

---

## 🖥️ GUI Requirements

Minimum UI layout:

* Input folder selector
* Output file selector
* FPS field
* Sort dropdown:

  * Filename
  * Creation time
  * Modification time
* Start button
* Log / progress panel

Optional:

* Drag and drop folder support
* Preview first/last frame
* Estimated video duration

---

## 📦 Packaging Requirements

The final app must be distributable as:

### Windows

* `StopMotionBuilder.exe`
* Bundled `ffmpeg.exe`

### macOS

* `StopMotionBuilder.app`
* Bundled `ffmpeg`

Build tool:

* PyInstaller

Example command:

```bash
pyinstaller --onefile --windowed main.py
```

---

## ⚙️ Implementation Guidance

### 1. Keep architecture simple

Recommended structure:

```
app/
  main.py
  ui.py
  ffmpeg_runner.py
  file_sorter.py
  config.py
```

OR single-file MVP is acceptable first.

---

### 2. Sorting is critical

Correct ordering is essential for animation quality.

Ensure:

* Stable sorting
* Deterministic order
* No OS-dependent behavior

---

### 3. Avoid unnecessary file duplication

Preferred approach:

* Use FFmpeg concat file
* Do NOT rename/copy images unless necessary

This improves performance significantly for large image sets.

---

### 4. FFmpeg handling

The app should:

* First check if FFmpeg exists in PATH
* Then check local bundled binary
* Fail gracefully if not found

---

### 5. Progress reporting (optional but recommended)

FFmpeg output should be parsed to show:

* Frame processing status
* Time elapsed
* Completion percentage (approximate)

---

## 💡 Suggested Enhancements (Post-MVP)

### Features

* Drag-and-drop folder input
* Timeline preview (first/last frame preview)
* Export presets:

  * 24 fps (cinematic)
  * 30 fps (smooth)
  * 12 fps (stop-motion look)
* Resolution scaling (1080p / 4K)
* Reverse playback option
* Loop video option

---

### Advanced Features

* GPU encoding support (h264_nvenc / videotoolbox)
* Image stabilization (optional preprocessing)
* Audio track overlay
* Batch export multiple folders

---

## ⚠️ Known Constraints

* FFmpeg is required (bundled or installed)
* Cross-platform builds require separate binaries per OS
* Large image folders may require efficient memory handling
* GUI must remain responsive during encoding (use threading)

---

## 🚀 Definition of Done (MVP)

The project is complete when:

* User can select a folder of images
* App correctly sorts them
* FFmpeg successfully generates an MP4
* GUI remains responsive
* Output video plays in correct chronological order
* App runs as a standalone executable

```
