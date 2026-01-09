"""Base parser interface for vulnerability scan files."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class ParsedVulnerability:
    """Structured vulnerability data from scan."""
    title: str
    description: str | None = None
    remediation: str | None = None
    plugin_id: str | None = None
    cve_id: str | None = None
    scanner_severity: str | None = None
    cvss_score: float | None = None
    cvss_vector: str | None = None
    port: int | None = None
    protocol: str | None = None
    
    # Asset information
    asset_identifier: str | None = None  # hostname or IP
    asset_type: str = "server"
    
    # Raw data
    raw_data: dict[str, Any] | None = None


@dataclass
class ParsedAsset:
    """Structured asset data from scan."""
    asset_identifier: str
    asset_type: str = "server"
    metadata: dict[str, Any] | None = None


@dataclass
class ParseResult:
    """Complete parsing result."""
    vulnerabilities: list[ParsedVulnerability]
    assets: list[ParsedAsset]
    metadata: dict[str, Any]


class ScanParser(ABC):
    """Base class for scan file parsers."""
    
    @abstractmethod
    def parse(self, file_path: str) -> ParseResult:
        """
        Parse a scan file and extract vulnerabilities and assets.
        
        Args:
            file_path: Path to the scan file
            
        Returns:
            ParseResult containing vulnerabilities, assets, and metadata
            
        Raises:
            ValueError: If file format is invalid
            FileNotFoundError: If file doesn't exist
        """
        pass
    
    @staticmethod
    def normalize_severity(severity: str | None) -> str | None:
        """
        Normalize severity to standard values.
        
        Args:
            severity: Raw severity string from scanner
            
        Returns:
            Normalized severity: 'critical', 'high', 'medium', 'low', 'info'
        """
        if not severity:
            return None
        
        severity_lower = severity.lower().strip()
        
        # Map common variations
        severity_map = {
            'critical': 'critical',
            'high': 'high',
            'medium': 'medium',
            'med': 'medium',
            'moderate': 'medium',
            'low': 'low',
            'info': 'info',
            'informational': 'info',
            'information': 'info',
            'none': 'info',
        }
        
        # Try numeric mapping (Nessus uses 0-4)
        if severity_lower.isdigit():
            severity_num = int(severity_lower)
            if severity_num == 4:
                return 'critical'
            elif severity_num == 3:
                return 'high'
            elif severity_num == 2:
                return 'medium'
            elif severity_num == 1:
                return 'low'
            else:
                return 'info'
        
        return severity_map.get(severity_lower, 'info')
