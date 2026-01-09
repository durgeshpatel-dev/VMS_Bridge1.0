"""Parser factory for different scan file formats."""
from pathlib import Path

from app.core.parsers.base import ScanParser
from app.core.parsers.nessus import NessusParser


def get_parser(file_path: str) -> ScanParser:
    """
    Get appropriate parser based on file extension.
    
    Args:
        file_path: Path to the scan file
        
    Returns:
        Parser instance for the file type
        
    Raises:
        ValueError: If file format is not supported
    """
    path = Path(file_path)
    extension = path.suffix.lower()
    
    parsers = {
        '.nessus': NessusParser,
        '.xml': NessusParser,  # Assume XML is Nessus for now
    }
    
    parser_class = parsers.get(extension)
    if not parser_class:
        raise ValueError(f"Unsupported file format: {extension}")
    
    return parser_class()
