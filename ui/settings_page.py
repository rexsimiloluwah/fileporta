import json 

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout,
    QPushButton, QLabel, QTextEdit,
    QMessageBox, QFrame
)

from utils.utils import load_stylesheet

STYLES = load_stylesheet("./styles/styles.qss")

class SettingsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Create a card-like container
        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        
        title = QLabel("Ignore Patterns Settings")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        card_layout.addWidget(title)
        
        description = QLabel(
            "Enter patterns to ignore, one per line. Supports wildcards (*). "
            "Common patterns are pre-filled below."
        )
        description.setWordWrap(True)
        card_layout.addWidget(description)
        
        self.patterns_edit = QTextEdit()
        self.patterns_edit.setPlaceholderText(
            "Example patterns:\n"
            "node_modules\n"
            "env/\n"
            "*.pyc\n"
            "__pycache__\n"
            ".git/\n"
            "*.tmp"
        )
        card_layout.addWidget(self.patterns_edit)
        
        save_button = QPushButton("Save Patterns")
        save_button.clicked.connect(self.save_settings)
        card_layout.addWidget(save_button)
        
        layout.addWidget(card)
        layout.addStretch()
        self.setLayout(layout)
    
    def load_settings(self):
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
                self.patterns_edit.setPlainText(settings.get('ignore_patterns', ''))
        except FileNotFoundError:
            pass
    
    def save_settings(self):
        settings = {
            'ignore_patterns': self.patterns_edit.toPlainText()
        }
        with open('settings.json', 'w') as f:
            json.dump(settings, f)
        QMessageBox.information(self, "Success", "Settings saved successfully!")