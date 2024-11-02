import os 
import json 
import logging 
from typing import Set

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QFileDialog,
    QMessageBox, QProgressBar, QFrame, QDialog
)

from utils.file_transfer_worker import FileTransferWorker
from components.confirmation_dialog import ConfirmationDialog

class MainTransferPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Create a card-like container
        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        
        # Title
        title = QLabel("Transfer your Files")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 20px;")
        card_layout.addWidget(title)
        
        # Source directory selection
        source_layout = QHBoxLayout()
        self.source_input = QLineEdit()
        source_layout.addWidget(QLabel("Source:"))
        source_layout.addWidget(self.source_input)
        source_button = QPushButton("Browse")
        source_button.clicked.connect(lambda: self.browse_directory(self.source_input))
        source_layout.addWidget(source_button)
        card_layout.addLayout(source_layout)
        
        # Add some spacing
        card_layout.addSpacing(10)
        
        # Destination directory selection
        dest_layout = QHBoxLayout()
        self.dest_input = QLineEdit()
        dest_layout.addWidget(QLabel("Destination:"))
        dest_layout.addWidget(self.dest_input)
        dest_button = QPushButton("Browse")
        dest_button.clicked.connect(lambda: self.browse_directory(self.dest_input))
        dest_layout.addWidget(dest_button)
        card_layout.addLayout(dest_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        card_layout.addWidget(self.progress_bar)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Transfer")
        self.start_button.setStyleSheet("""
            QPushButton {
                margin-top: 20px;
            }
            QPushButton:hover {
                background-color: orange;
            }
        """)

        self.start_button.clicked.connect(self.start_transfer)
        button_layout.addWidget(self.start_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.cancel_button.clicked.connect(self.confirm_cancel)
        self.cancel_button.setVisible(False)
        button_layout.addWidget(self.cancel_button)
        
        card_layout.addLayout(button_layout)
        
        # Add the card to the main layout
        layout.addWidget(card)
        layout.addStretch()
        self.setLayout(layout)
    
    def browse_directory(self, line_edit: QLineEdit):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            line_edit.setText(directory)
    
    def get_ignore_patterns(self) -> Set[str]:
        """Load ignore patterns from settings"""
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
                patterns = settings.get('ignore_patterns', '').strip().split('\n')
                return {pattern.strip() for pattern in patterns if pattern.strip()}
        except FileNotFoundError:
            return set()
    
    def confirm_cancel(self):
        dialog = ConfirmationDialog(
            "Are you sure you want to cancel the file transfer?",
            self
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.cancel_transfer()
    
    def cancel_transfer(self):
        if self.worker and self.worker.isRunning():
            self.worker.should_stop = True
            self.worker.wait()
            self.transfer_finished(cancelled=True)
            logging.info("File transfer cancelled by user")
            QMessageBox.information(self, "Cancelled", "File transfer has been cancelled.")
    
    def start_transfer(self):
        source_dir = self.source_input.text()
        dest_dir = self.dest_input.text()
        
        if not source_dir or not dest_dir:
            QMessageBox.warning(self, "Error", "Please select both source and destination directories.")
            return
        
        if not os.path.exists(source_dir):
            QMessageBox.warning(self, "Error", "Source directory does not exist.")
            return
            
        if source_dir == dest_dir:
            QMessageBox.warning(self, "Error", "Source and destination directories cannot be the same.")
            return
        
        logging.info(f"Starting file transfer from {source_dir} to {dest_dir}")
        
        self.worker = FileTransferWorker(
            source_dir,
            dest_dir,
            self.get_ignore_patterns()
        )
        
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(lambda: self.transfer_finished(False))
        self.worker.error.connect(self.handle_error)
        
        self.worker.start()
        
        self.progress_bar.setVisible(True)
        self.start_button.setEnabled(False)
        self.cancel_button.setVisible(True)
    
    def update_progress(self, value: int):
        self.progress_bar.setValue(value)
    
    def transfer_finished(self, cancelled: bool = False):
        self.progress_bar.setVisible(False)
        self.start_button.setEnabled(True)
        self.cancel_button.setVisible(False)
        self.progress_bar.setValue(0)
        
        if not cancelled:
            logging.info("File transfer completed successfully")
            QMessageBox.information(self, "Complete", "File transfer has been completed successfully!")
    
    def handle_error(self, error_msg: str):
        logging.error(f"Error during file transfer: {error_msg}")
        QMessageBox.critical(self, "Error", f"An error occurred during transfer:\n{error_msg}")
        self.transfer_finished()