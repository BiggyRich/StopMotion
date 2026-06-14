from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QFileDialog, QSpinBox, QComboBox, 
                             QLabel, QSplitter, QMessageBox, QStatusBar)
from PySide6.QtCore import Qt, QTimer
from ui.widgets import ReorderableListWidget
from core.ffmpeg_engine import FFmpegEngine
from PIL import Image

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("StopMotion Builder")
        self.resize(1000, 700)
        
        self.ffmpeg_engine = FFmpegEngine()
        self.ffmpeg_engine.finished.connect(self.on_generation_finished)
        self.ffmpeg_engine.log_message.connect(self.log_to_console)
        
        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Left side: List and controls
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        self.image_list = ReorderableListWidget(self)
        left_layout.addWidget(QLabel("Images (Drag and Drop to Reorder):"))
        left_layout.addWidget(self.image_list)
        
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Add Images/Folder")
        self.btn_clear = QPushButton("Clear List")
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_clear)
        left_layout.addLayout(btn_layout)
        
        # Right side: Preview and Settings
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Preview area
        self.preview_label = QLabel("Preview Area")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(400, 300)
        self.preview_label.setStyleSheet("border: 1px solid gray; background-color: black;")
        right_layout.addWidget(self.preview_label)
        
        # Settings
        settings_group = QWidget()
        settings_layout = QVBoxLayout(settings_group)
        
        # FPS
        fps_layout = QHBoxLayout()
        fps_layout.addWidget(QLabel("FPS:"))
        self.fps_spin = QSpinBox()
        self.fps_spin.setRange(1, 60)
        self.fps_spin.setValue(24)
        fps_layout.addWidget(self.fps_spin)
        settings_layout.addLayout(fps_layout)

        # Duration Estimate
        self.duration_label = QLabel("Estimated Duration: 0.0s")
        self.duration_label.setStyleSheet("color: #aaa; font-style: italic;")
        settings_layout.addWidget(self.duration_label)
        
        # Resolution
        res_layout = QHBoxLayout()
        res_layout.addWidget(QLabel("Resolution:"))
        self.res_combo = QComboBox()
        self.res_combo.addItems(["Source", "1920x1080 (1080p)", "1280x720 (720p)", "3840x2160 (4K)"])
        res_layout.addWidget(self.res_combo)
        settings_layout.addLayout(res_layout)

        # Log Console
        settings_layout.addWidget(QLabel("Process Log:"))
        from PySide6.QtWidgets import QTextEdit
        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setFixedHeight(150)
        self.log_console.setStyleSheet("background-color: #1e1e1e; color: #00ff00; font-family: monospace; font-size: 10px;")
        settings_layout.addWidget(self.log_console)

        # Diagnostic Button
        self.btn_diagnostic = QPushButton("Run Path Diagnostics")
        self.btn_diagnostic.clicked.connect(self.run_diagnostics)
        settings_layout.addWidget(self.btn_diagnostic)
        
        right_layout.addWidget(settings_group)
        
        # Generate Button
        self.btn_generate = QPushButton("Generate Video")
        self.btn_generate.setFixedHeight(50)
        self.btn_generate.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        right_layout.addWidget(self.btn_generate)
        
        # Add panels to main layout
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        main_layout.addWidget(splitter)
        
        # Status Bar
        self.setStatusBar(QStatusBar())
        
        # Connections
        self.btn_add.clicked.connect(self.on_add_clicked)
        self.btn_clear.clicked.connect(self.on_clear_clicked)
        self.btn_generate.clicked.connect(self.on_generate_clicked)
        self.fps_spin.valueChanged.connect(self.update_timer_interval)
        
        # Preview timer
        self.preview_timer = QTimer()
        self.preview_timer.timeout.connect(self.update_preview)
        self.current_preview_index = 0

    def run_diagnostics(self):
        import os, sys
        self.log_to_console("--- RUNNING DIAGNOSTICS ---")
        self.log_to_console(f"Executable: {sys.executable}")
        self.log_to_console(f"Frozen: {getattr(sys, 'frozen', False)}")
        self.log_to_console(f"Bundle DIR (MEIPASS): {getattr(sys, '_MEIPASS', 'N/A')}")
        self.log_to_console(f"Working DIR: {os.getcwd()}")
        self.log_to_console(f"FFmpeg Path: {self.ffmpeg_engine.ffmpeg_path}")
        
        if self.ffmpeg_engine.ffmpeg_path and os.path.exists(self.ffmpeg_engine.ffmpeg_path):
            self.log_to_console("FFmpeg exists.")
            self.log_to_console(f"FFmpeg permissions: {oct(os.stat(self.ffmpeg_engine.ffmpeg_path).st_mode)}")
            # Try to run version check
            try:
                import subprocess
                res = subprocess.run([self.ffmpeg_engine.ffmpeg_path, "-version"], capture_output=True, text=True)
                self.log_to_console(f"FFmpeg test run: {res.stdout.splitlines()[0]}")
            except Exception as e:
                self.log_to_console(f"FFmpeg test run failed: {str(e)}")
        else:
            self.log_to_console("ERROR: FFmpeg path does not exist or is invalid.")

    def on_add_clicked(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Images", "", "Images (*.png *.jpg *.jpeg)"
        )
        if files:
            self.image_list.add_images(files)

    def on_clear_clicked(self):
        self.image_list.clear()
        self.preview_label.clear()
        self.preview_label.setText("Preview Area")
        self.preview_timer.stop()
        self.log_console.clear()
        self.update_duration()

    def on_images_changed(self):
        self.detect_resolution()
        self.update_duration()
        if not self.preview_timer.isActive() and self.image_list.count() > 0:
            self.start_preview()

    def update_timer_interval(self):
        self.update_duration()
        if self.preview_timer.isActive():
            self.preview_timer.setInterval(1000 // self.fps_spin.value())

    def update_duration(self):
        count = self.image_list.count()
        fps = self.fps_spin.value()
        duration = count / fps if fps > 0 else 0
        self.duration_label.setText(f"Estimated Duration: {duration:.1f}s ({count} frames)")

    def on_generate_clicked(self):
        if self.image_list.count() == 0:
            QMessageBox.warning(self, "No Images", "Please add some images first.")
            return
        
        output_path, _ = QFileDialog.getSaveFileName(
            self, "Save Video", "output.mp4", "Video Files (*.mp4)"
        )
        if not output_path:
            return
        
        # Collect image paths
        image_paths = []
        for i in range(self.image_list.count()):
            image_paths.append(self.image_list.item(i).data(Qt.UserRole))
        
        self.log_console.clear()
        self.log_to_console(f"Starting generation for {len(image_paths)} images...")
        self.btn_generate.setEnabled(False)
        self.statusBar().showMessage("Generating video...")
        
        self.ffmpeg_engine.generate_video(
            image_paths, 
            output_path, 
            self.fps_spin.value(), 
            self.res_combo.currentText()
        )

    def on_generation_finished(self, success, message):
        self.btn_generate.setEnabled(True)
        self.statusBar().showMessage(message)
        self.log_to_console(f"FINISHED: {message}")
        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.critical(self, "Error", message)

    def log_to_console(self, message):
        self.log_console.append(message)
        print(message)

    def detect_resolution(self):
        if self.image_list.count() == 0:
            return
        
        first_path = self.image_list.item(0).data(Qt.UserRole)
        try:
            with Image.open(first_path) as img:
                w, h = img.size
            
            all_match = True
            for i in range(1, self.image_list.count()):
                path = self.image_list.item(i).data(Qt.UserRole)
                with Image.open(path) as img:
                    if img.size != (w, h):
                        all_match = False
                        break
            
            if all_match:
                res_str = f"{w}x{h} (Source)"
                # Remove existing source entries if any
                for i in range(self.res_combo.count()):
                    if "(Source)" in self.res_combo.itemText(i):
                        self.res_combo.removeItem(i)
                        break
                self.res_combo.insertItem(0, res_str)
                self.res_combo.setCurrentIndex(0)
        except Exception as e:
            print(f"Error detecting resolution: {e}")

    def start_preview(self):
        fps = self.fps_spin.value()
        self.preview_timer.start(1000 // fps)

    def update_preview(self):
        count = self.image_list.count()
        if count == 0:
            self.preview_timer.stop()
            return
        
        self.current_preview_index = (self.current_preview_index + 1) % count
        path = self.image_list.item(self.current_preview_index).data(Qt.UserRole)
        
        from PySide6.QtGui import QPixmap
        pixmap = QPixmap(path)
        scaled_pixmap = pixmap.scaled(self.preview_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.preview_label.setPixmap(scaled_pixmap)
