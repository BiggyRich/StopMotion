import os
from PySide6.QtWidgets import QListWidget, QAbstractItemView, QListWidgetItem
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt, QSize
from PIL import Image

class ReorderableListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setIconSize(QSize(100, 100))
        self.setSpacing(5)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
            paths = []
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if os.path.isdir(path):
                    for f in sorted(os.listdir(path)):
                        if f.lower().endswith(('.png', '.jpg', '.jpeg')):
                            paths.append(os.path.join(path, f))
                elif path.lower().endswith(('.png', '.jpg', '.jpeg')):
                    paths.append(path)
            
            self.add_images(paths)
        else:
            super().dropEvent(event)

    def add_images(self, paths):
        for path in paths:
            item = QListWidgetItem(os.path.basename(path))
            item.setData(Qt.UserRole, path)
            
            # Generate thumbnail
            try:
                img = Image.open(path)
                img.thumbnail((100, 100))
                # Convert PIL image to QPixmap
                # This is a bit slow for many images, could be optimized later
                qimg_data = img.convert("RGBA").tobytes("raw", "RGBA")
                from PySide6.QtGui import QImage
                qimg = QImage(qimg_data, img.size[0], img.size[1], QImage.Format_RGBA8888)
                item.setIcon(QIcon(QPixmap.fromImage(qimg)))
            except Exception as e:
                print(f"Error loading {path}: {e}")
            
            self.addItem(item)
        
        # Signal that images were added (can be connected to resolution detection)
        self.parent().on_images_changed() if hasattr(self.parent(), 'on_images_changed') else None
