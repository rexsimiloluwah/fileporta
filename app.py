import sys 
import logging

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QFrame
)
from PyQt6.QtGui import QFont

from ui.settings_page import SettingsPage
from ui.about_page import AboutPage
from ui.home_page import MainTransferPage
from utils.utils import load_stylesheet

STYLES = load_stylesheet("./styles/styles.qss")

class FileMoverApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FilePorta")
        self.setMinimumSize(900, 600)
        
        # Initialize logging
        logging.basicConfig(
            filename='file_mover.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        self.setup_ui()
        self.setStyleSheet(STYLES)
        
    def setup_ui(self):
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create sidebar
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(200)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)
        sidebar_layout.setSpacing(5)
        
        # App title in sidebar
        title_label = QLabel("FilePorta 📁")
        title_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #2c3e50;
            padding: 0 20px 20px 20px;
        """)
        sidebar_layout.addWidget(title_label)
        
        # Sidebar buttons
        self.transfer_btn = QPushButton("File Transfer")
        self.transfer_btn.setObjectName("sidebarButton")
        self.transfer_btn.setCheckable(True)
        self.transfer_btn.setChecked(True)
        self.transfer_btn.clicked.connect(lambda: self.show_page(0))
        
        self.settings_btn = QPushButton("Settings")
        self.settings_btn.setObjectName("sidebarButton")
        self.settings_btn.setCheckable(True)
        self.settings_btn.clicked.connect(lambda: self.show_page(1))
        
        self.about_btn = QPushButton("About")
        self.about_btn.setObjectName("sidebarButton")
        self.about_btn.setCheckable(True)
        self.about_btn.clicked.connect(lambda: self.show_page(2))
        
        sidebar_layout.addWidget(self.transfer_btn)
        sidebar_layout.addWidget(self.settings_btn)
        sidebar_layout.addWidget(self.about_btn)
        sidebar_layout.addStretch()
        
        # Create stacked widget for different pages
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(MainTransferPage())
        self.stacked_widget.addWidget(SettingsPage())
        self.stacked_widget.addWidget(AboutPage())
        
        # Add sidebar and stacked widget to main layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stacked_widget)
    
    def show_page(self, index: int):
        # Update button states
        for btn in [self.transfer_btn, self.settings_btn, self.about_btn]:
            btn.setChecked(False)
            
        # Check the appropriate button
        if index == 0:
            self.transfer_btn.setChecked(True)
        elif index == 1:
            self.settings_btn.setChecked(True)
        else:
            self.about_btn.setChecked(True)
        
        # Show the selected page
        self.stacked_widget.setCurrentIndex(index)

def main():
    app = QApplication(sys.argv)
    
    # Set application-wide font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = FileMoverApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()