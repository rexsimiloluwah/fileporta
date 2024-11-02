from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame
)

from utils.utils import load_stylesheet

STYLES = load_stylesheet("./styles/styles.qss")

class AboutPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        
        title = QLabel("About FilePorta")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        card_layout.addWidget(title)
        
        description = QLabel(
            "FilePorta is a simple tool that helps you transport (move/copy) your files from one point to another efficiently."
            "With support for ignore patterns similar "
            "to .gitignore, it provides a powerful way to selectively move files while "
            "excluding unnecessary ones.\n\n"
            "Features:\n"
            "• Intuitive user interface\n"
            "• Pattern-based file/folder ignoring\n"
            "• Progress tracking\n"
            "• Cancelable operations\n"
            "• Detailed logging\n\n"
            "Version: 1.0.0\n"
            "© 2024 FilePorta. All rights reserved."
        )
        description.setWordWrap(True)
        description.setStyleSheet("line-height: 1.6;")
        card_layout.addWidget(description)
        
        layout.addWidget(card)
        layout.addStretch()
        self.setLayout(layout)