import sys
import pytest
from PySide6.QtCore import Qt
from ui.main_window import MainWindow

@pytest.fixture
def app(qtbot):
    test_app = MainWindow()
    qtbot.addWidget(test_app)
    return test_app

def test_initial_state(app):
    assert app.windowTitle() == "StopMotion Builder"
    assert app.image_list.count() == 0
    assert app.btn_generate.isEnabled()
    assert app.fps_spin.value() == 24

def test_clear_list(app):
    # Mock adding an item
    from PySide6.QtWidgets import QListWidgetItem
    item = QListWidgetItem("test.jpg")
    item.setData(Qt.UserRole, "/path/to/test.jpg")
    app.image_list.addItem(item)
    
    assert app.image_list.count() == 1
    app.on_clear_clicked()
    assert app.image_list.count() == 0
    assert app.preview_label.text() == "Preview Area"
