"""Parser factory for different scan file formats."""
import json
from pathlib import Path

from app.core.parsers.base import ScanParser
from app.core.parsers.dependency_check import DependencyCheckParser
from app.core.parsers.nessus import NessusParser
from app.core.parsers.snyk import SnykParser
from app.core.parsers.trivy import TrivyParser


def _detect_json_parser(file_path: str) -> ScanParser:
    """
    Detect which parser to use for JSON files by inspecting content.
    
    Returns: SnykParser, TrivyParser, or DependencyCheckParser
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except Exception:
        # Default to Snyk if can't parse
        return SnykParser()
    
    # Check for Trivy markers
    if isinstance(data, dict) and 'Results' in data:
        return TrivyParser()
    if isinstance(data, list) and len(data) > 0:
        if 'ArtifactName' in data[0] or 'Vulnerabilities' in data[0]:
            return TrivyParser()
    
    # Check for Snyk markers
    if isinstance(data, dict) and 'vulnerabilities' in data:
        if 'projectName' in data or 'displayTargetFile' in data:
            return SnykParser()
    
    # Check for Dependency-Check markers
    if isinstance(data, dict) and 'dependencies' in data:
        return DependencyCheckParser()
    
    # Default to Snyk for generic JSON
    return SnykParser()


def _detect_xml_parser(file_path: str) -> ScanParser:
    """
    Detect which parser to use for XML files by inspecting content.
    
    Returns: DependencyCheckParser or NessusParser
    """
    try:
        with open(file_path, 'r') as f:
            content = f.read(500)  # Read first 500 chars
    except Exception:
        return NessusParser()
    
    content_lower = content.lower()
    
    # Check for Dependency-Check
    if 'dependency' in content_lower or 'dependencies' in content_lower:
        return DependencyCheckParser()
    
    # Default to Nessus
    return NessusParser()


def get_parser(file_path: str) -> ScanParser:
    """
    Get appropriate parser based on file extension and content detection.
    
    Supports:
    - .nessus files (Nessus)
    - .xml files (Dependency-Check or Nessus, auto-detected)
    - .json files (Snyk, Trivy, or Dependency-Check, auto-detected)
    - .sarif files (Trivy)
    
    Args:
        file_path: Path to the scan file
        
    Returns:
        Parser instance for the file type
        
    Raises:
        ValueError: If file format is not supported
    """
    path = Path(file_path)
    extension = path.suffix.lower()
    
    # Direct mappings
    if extension == '.nessus':
        return NessusParser()
    elif extension == '.sarif':
        return TrivyParser()
    
    # Content-based detection
    elif extension == '.json':
        return _detect_json_parser(file_path)
    elif extension == '.xml':
        return _detect_xml_parser(file_path)
    
    # Try to infer from filename
    elif 'trivy' in path.name.lower():
        return TrivyParser()
    elif 'snyk' in path.name.lower():
        return SnykParser()
    elif 'dependency' in path.name.lower() or 'owasp' in path.name.lower():
        return DependencyCheckParser()
    
    # Generic extensions
    elif extension in {'.csv', '.txt', '.json', '.xml'}:
        if extension == '.json':
            return _detect_json_parser(file_path)
        else:
            raise ValueError(f"Unsupported file format: {extension}")
    
    else:
        raise ValueError(
            f"Unsupported file format: {extension}. "
            f"Supported formats: .nessus, .xml, .json, .sarif"
        )
