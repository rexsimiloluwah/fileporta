from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QDialog
)
from PyQt6.QtCore import Qt

from utils.utils import load_stylesheet

STYLES = load_stylesheet("./styles/styles.qss")

class ConfirmationDialog(QDialog):
    def __init__(self, message: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Confirmation")
        self.setFixedSize(400, 150)
        self.setStyleSheet(STYLES)

        layout = QVBoxLayout()
        
        label = QLabel(message)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        button_layout = QHBoxLayout()
        
        yes_button = QPushButton("Yes")
        no_button = QPushButton("No")
        
        yes_button.clicked.connect(self.accept)
        no_button.clicked.connect(self.reject)
        
        button_layout.addWidget(yes_button)
        button_layout.addWidget(no_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)