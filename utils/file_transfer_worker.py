import os 
import time 
import shutil 
import fnmatch
from tqdm import tqdm 
from queue import Queue
from typing import Set, List
from concurrent.futures import ThreadPoolExecutor

from PyQt6.QtCore import QThread, pyqtSignal

from constants.constants import BatchItem

class FileTransferWorker(QThread):
    """Worker thread to handle file transfers without blocking the UI"""
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(str)
    
    # Constants for batch processing
    BATCH_SIZE = 100  # Number of files per batch
    MAX_WORKERS = 4   # Number of transfer threads
    
    def __init__(self, source_dir: str, dest_dir: str, ignore_patterns: Set[str], operation: str = 'copy'):
        """
        Initialize the worker with batch processing capabilities.
        
        Args:
            source_dir (str): Source directory path
            dest_dir (str): Destination directory path
            ignore_patterns (Set[str]): Set of patterns to ignore
            operation (str): 'copy' or 'move'. Defaults to 'copy'
        """
        super().__init__()
        self.source_dir = source_dir
        self.dest_dir = dest_dir
        self.ignore_patterns = self._process_patterns(ignore_patterns)
        self.should_stop = False
        self.operation = operation.lower()
        self.transfer_queue = Queue()
        self.processed_count = 0
        self.total_items = 0
        
        if self.operation not in ['copy', 'move']:
            raise ValueError("Operation must be either 'copy' or 'move'")
    
    def _process_patterns(self, patterns: Set[str]) -> Set[str]:
        """Process the ignore patterns to handle different formats"""
        processed = set()
        for pattern in patterns:
            pattern = pattern.strip()
            if pattern and not pattern.startswith('#'):
                if pattern.endswith('/'):
                    pattern = pattern[:-1]
                if not pattern.endswith('/*'):
                    processed.add(pattern)
                    processed.add(f"{pattern}/*")
                else:
                    processed.add(pattern)
        
        return processed

    def should_ignore(self, path: str) -> bool:
        """Check if a path should be ignored based on ignore patterns."""
        rel_path = os.path.relpath(path, self.source_dir)
        rel_path = rel_path.replace(os.sep, '/')
        
        path_parts = rel_path.split('/')
        current_path = ""
        
        for part in path_parts:
            if current_path:
                current_path += '/'
            current_path += part
            
            for pattern in self.ignore_patterns:
                if fnmatch.fnmatch(part, pattern):
                    return True
                if fnmatch.fnmatch(current_path, pattern):
                    return True
                if fnmatch.fnmatch(current_path + '/*', pattern):
                    return True
                if os.path.isdir(os.path.join(self.source_dir, current_path)):
                    if fnmatch.fnmatch(current_path + '/', pattern):
                        return True
        
        return False

    def scan_directory(self, max_depth: int = 5) -> List[BatchItem]:
        """Scan directory and return list of items to transfer, with an optional depth limit"""
        items = []
        base_depth = self.source_dir.rstrip(os.path.sep).count(os.path.sep)

        for root, dirs, files in tqdm(os.walk(self.source_dir)):
            # Check if scanning should stop early
            if self.should_stop:
                return items

            # Calculate the current depth
            current_depth = root.count(os.path.sep) - base_depth

            # Stop traversing deeper if the current depth exceeds max_depth
            if max_depth is not None and current_depth >= max_depth:
                dirs[:] = []  # Clear dirs to prevent further traversal
                continue

            # Skip directories if the root should be ignored
            if self.should_ignore(root):
                dirs[:] = []  # Clear dirs to prevent descending into subdirectories
                continue

            # Filter subdirectories that should be ignored
            dirs[:] = [d for d in dirs if not self.should_ignore(os.path.join(root, d))]

            # print(root, self.should_ignore(root))

            # Calculate the relative path and destination root
            rel_path = os.path.relpath(root, self.source_dir)
            dest_root = os.path.join(self.dest_dir, rel_path)

            # Add directory creation task
            items.append(BatchItem(root, dest_root, True))

            # Add file transfer tasks
            for file in files:
                # Check if scanning should stop early
                if self.should_stop:
                    return items

                src_file = os.path.join(root, file)
                if not self.should_ignore(src_file):
                    dest_file = os.path.join(dest_root, file)
                    items.append(BatchItem(src_file, dest_file, False))

        return items

    def process_batch(self, batch: List[BatchItem]) -> None:
        """Process a batch of transfers"""
        with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
            futures = []
            
            for item in batch:
                if self.should_stop:
                    break
                
                if item.is_directory:
                    try:
                        os.makedirs(item.dst, exist_ok=True)
                    except Exception as e:
                        self.error.emit(f"Error creating directory {item.dst}: {str(e)}")
                        continue
                else:
                    futures.append(executor.submit(self.transfer_file, item.src, item.dst))
            
            # Wait for all transfers in this batch to complete
            for future in futures:
                try:
                    future.result()
                    self.processed_count += 1
                    progress = int((self.processed_count / self.total_items) * 100)
                    self.progress.emit(progress)
                except Exception as e:
                    self.error.emit(f"Error in batch transfer: {str(e)}")

    def transfer_file(self, src: str, dst: str):
        """Transfer a single file with retry logic"""
        max_retries = 3
        retry_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                if self.operation == 'copy':
                    shutil.copy2(src, dst)
                else:  # move
                    shutil.move(src, dst)
                return
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    raise e

    def run(self):
        try:
            # Scan directory and create work items
            self.status.emit("Scanning directory...")
            items = self.scan_directory()
            
            if not items:
                self.error.emit("No files to transfer after applying ignore patterns")
                return
            
            # Count only files (not directories) for progress tracking
            self.total_items = sum(1 for item in items if not item.is_directory)
            
            if self.total_items == 0:
                self.error.emit("No files to transfer after applying ignore patterns")
                return
            
            # Process items in batches
            current_batch = []
            for item in items:
                if self.should_stop:
                    return
                
                current_batch.append(item)
                
                if len(current_batch) >= self.BATCH_SIZE:
                    self.process_batch(current_batch)
                    current_batch = []
            
            # Process remaining items
            if current_batch:
                self.process_batch(current_batch)
            
            # Clean up empty directories if this was a move operation
            if self.operation == 'move':
                self.status.emit("Cleaning up empty directories...")
                self._cleanup_empty_directories(self.source_dir)
            
            self.finished.emit()
            
        except Exception as e:
            self.error.emit(str(e))
    
    def _cleanup_empty_directories(self, directory: str):
        """Remove empty directories after move operation"""
        for root, dirs, files in os.walk(directory, topdown=False):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    if not os.listdir(dir_path):
                        os.rmdir(dir_path)
                except OSError:
                    continue