from dataclasses import dataclass

@dataclass
class BatchItem:
    src: str
    dst: str
    is_directory: bool