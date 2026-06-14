import os
import subprocess
import shutil
from PySide6.QtCore import QObject, Signal, QProcess

class FFmpegEngine(QObject):
    progress = Signal(int)
    finished = Signal(bool, str)
    log_message = Signal(str)

    def __init__(self):
        super().__init__()
        self.process = QProcess()
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.on_process_finished)
        self.ffmpeg_path = self.find_ffmpeg()

    def find_ffmpeg(self):
        # 1. Check if running in a PyInstaller bundle
        import sys
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            bundle_dir = sys._MEIPASS
            local_path = os.path.join(bundle_dir, "ffmpeg")
            if os.name == "nt":
                local_path += ".exe"
            if os.path.exists(local_path):
                return local_path

        # 2. Check PATH
        path = shutil.which("ffmpeg")
        if path:
            return path
        
        # 3. Check local folder

    def generate_video(self, image_paths, output_path, fps, resolution):
        if not self.ffmpeg_path:
            self.finished.emit(False, "FFmpeg not found. Please install FFmpeg or place it in the app folder.")
            return

        # Create a temporary file for the concat list
        import tempfile
        try:
            # Create temp file and close immediately to write with 'with open'
            tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', prefix='stopmotion_', delete=False)
            concat_path = tmp.name
            
            with tmp as f:
                for path in image_paths:
                    escaped_path = path.replace("'", "'\\''")
                    f.write(f"file '{escaped_path}'\n")
                    f.write(f"duration {1/fps}\n")
                if image_paths:
                    escaped_path = image_paths[-1].replace("'", "'\\''")
                    f.write(f"file '{escaped_path}'\n")
            
            self.current_concat_path = concat_path
        except Exception as e:
            self.finished.emit(False, f"Failed to create temporary instruction file: {str(e)}")
            return

        # Parse resolution
        res_parts = resolution.split(' ')[0].split('x')
        if len(res_parts) == 2:
            target_w, target_h = res_parts
        else:
            target_w, target_h = None, None

        # Build FFmpeg command
        args = [
            "-f", "concat",
            "-safe", "0",
            "-i", concat_path,  
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p"
        ]

        if target_w and target_h:
            filter_str = f"scale=w={target_w}:h={target_h}:force_original_aspect_ratio=decrease,pad={target_w}:{target_h}:(ow-iw)/2:(oh-ih)/2:black"
            args.extend(["-vf", filter_str])

        args.append("-y")  # Overwrite
        args.append(output_path)

        self.log_message.emit(f"Running command: {self.ffmpeg_path} {' '.join(args)}")
        self.process.start(self.ffmpeg_path, args)

    def handle_stderr(self):
        data = self.process.readAllStandardError().data().decode()
        for line in data.splitlines():
            if line.strip():
                self.log_message.emit(f"FFmpeg: {line.strip()}")

    def on_process_finished(self, exit_code, exit_status):
        self.log_message.emit(f"FFmpeg process finished with exit code {exit_code}, status {exit_status}")
        
        # Cleanup temp file
        if hasattr(self, 'current_concat_path') and os.path.exists(self.current_concat_path):
            try:
                os.remove(self.current_concat_path)
            except:
                pass

        if exit_code == 0:
            self.finished.emit(True, "Video generated successfully!")
        else:
            try:
                error_msg = self.process.readAllStandardError().data().decode()
            except:
                error_msg = "Unknown error"
            self.finished.emit(False, f"FFmpeg failed with exit code {exit_code}. {error_msg}")
