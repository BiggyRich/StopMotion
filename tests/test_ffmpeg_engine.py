import pytest
import os
from core.ffmpeg_engine import FFmpegEngine

def test_find_ffmpeg():
    engine = FFmpegEngine()
    # On most dev machines, this should find something
    assert engine.ffmpeg_path is not None
    assert os.path.exists(engine.ffmpeg_path)

def test_resolution_parsing():
    # Test logic for extracting WxH from the combo box strings
    res_string = "1920x1080 (1080p)"
    parts = res_string.split(' ')[0].split('x')
    assert parts == ["1920", "1080"]
    
    # Check how the MainWindow formatted "Source" string is handled
    res_string = "640x360 (Source)"
    res_parts = res_string.split(' ')[0].split('x')
    assert res_parts == ["640", "360"]
