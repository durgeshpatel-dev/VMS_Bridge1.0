"""OWASP Dependency-Check XML/JSON parser for dependency vulnerability scanning."""
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from app.core.parsers.base import (
    ParsedAsset,
    ParsedVulnerability,
    ParseResult,
    ScanParser,
)


class DependencyCheckParser(ScanParser):
    """Parser for OWASP Dependency-Check XML and JSON reports."""

    def parse(self, file_path: str) -> ParseResult:
        """
        Parse OWASP Dependency-Check report (XML or JSON format).

        Args:
            file_path: Path to the Dependency-Check report file

        Returns:
            ParseResult containing vulnerabilities, assets, and metadata

        Raises:
            ValueError: If file format is invalid
            FileNotFoundError: If file doesn't exist
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Detect format
        if file_path.lower().endswith('.json'):
            return self._parse_json(file_path)
        else:
            return self._parse_xml(file_path)

    def _parse_xml(self, file_path: str) -> ParseResult:
        """Parse Dependency-Check XML format."""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML format: {e}")

        vulnerabilities = []
        assets = []
        seen_assets = set()

        # Find all dependencies
        for dependency in root.findall('.//dependency'):
            # Extract package information
            file_name = self._get_text(dependency, 'fileName')
            package_name = self._get_text(dependency, 'packageName')
            package_version = self._get_text(dependency, 'packageVersion')

            # Use package name as asset identifier
            asset_identifier = package_name or file_name or 'unknown'

            # Create asset if not seen
            if asset_identifier not in seen_assets:
                asset_metadata = {
                    'fileName': file_name,
                    'packageName': package_name,
                    'packageVersion': package_version,
                }
                assets.append(ParsedAsset(
                    asset_identifier=asset_identifier,
                    asset_type='dependency',
                    metadata=asset_metadata
                ))
                seen_assets.add(asset_identifier)

            # Process vulnerabilities for this dependency
            for vuln_elem in dependency.findall('vulnerabilities/vulnerability'):
                vuln = self._parse_vulnerability(vuln_elem, asset_identifier)
                if vuln:
                    vulnerabilities.append(vuln)

        metadata = {
            'parser': 'dependency_check',
            'total_vulnerabilities': len(vulnerabilities),
            'total_assets': len(assets),
            'report_schema': 'xml'
        }

        return ParseResult(
            vulnerabilities=vulnerabilities,
            assets=assets,
            metadata=metadata
        )

    def _parse_json(self, file_path: str) -> ParseResult:
        """Parse Dependency-Check JSON format."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")
        except Exception as e:
            raise ValueError(f"Error reading JSON file: {e}")

        vulnerabilities = []
        assets = []
        seen_assets = set()

        # Process dependencies
        dependencies = data.get('dependencies', [])
        for dependency in dependencies:
            file_name = dependency.get('fileName', '')
            package_name = dependency.get('packageName', '')
            package_version = dependency.get('packageVersion', '')

            asset_identifier = package_name or file_name or 'unknown'

            # Create asset if not seen
            if asset_identifier not in seen_assets:
                asset_metadata = {
                    'fileName': file_name,
                    'packageName': package_name,
                    'packageVersion': package_version,
                }
                assets.append(ParsedAsset(
                    asset_identifier=asset_identifier,
                    asset_type='dependency',
                    metadata=asset_metadata
                ))
                seen_assets.add(asset_identifier)

            # Process vulnerabilities
            for vuln_data in dependency.get('vulnerabilities', []):
                vuln = self._parse_vulnerability_json(vuln_data, asset_identifier)
                if vuln:
                    vulnerabilities.append(vuln)

        metadata = {
            'parser': 'dependency_check',
            'total_vulnerabilities': len(vulnerabilities),
            'total_assets': len(assets),
            'report_schema': 'json'
        }

        return ParseResult(
            vulnerabilities=vulnerabilities,
            assets=assets,
            metadata=metadata
        )

    def _parse_vulnerability(
        self,
        vuln_elem: ET.Element,
        asset_identifier: str
    ) -> ParsedVulnerability | None:
        """Parse a single vulnerability from XML element."""
        name = self._get_text(vuln_elem, 'name')
        if not name:
            return None

        # Extract CVE
        cve_list = vuln_elem.findall('cve')
        cve_id = cve_list[0].text if cve_list else None

        # Extract CVSS score and vector
        cvss_score_text = self._get_text(vuln_elem, 'cvssScore')
        cvss_score = float(cvss_score_text) if cvss_score_text else None
        cvss_vector = self._get_text(vuln_elem, 'cvssVector')

        # Extract severity
        severity = self._get_text(vuln_elem, 'severity')

        # Extract description and notes
        description = self._get_text(vuln_elem, 'description')
        notes = self._get_text(vuln_elem, 'notes')
        if notes and not description:
            description = notes

        return ParsedVulnerability(
            title=name,
            description=description,
            remediation=self._get_text(vuln_elem, 'solution'),
            cve_id=cve_id,
            scanner_severity=self.normalize_severity(severity),
            cvss_score=cvss_score,
            cvss_vector=cvss_vector,
            asset_identifier=asset_identifier,
            asset_type='dependency',
            raw_data={
                'name': name,
                'cve': cve_id,
                'severity': severity,
                'cvss_score': cvss_score_text,
            }
        )

    def _parse_vulnerability_json(
        self,
        vuln_data: dict[str, Any],
        asset_identifier: str
    ) -> ParsedVulnerability | None:
        """Parse a single vulnerability from JSON object."""
        name = vuln_data.get('name')
        if not name:
            return None

        # Extract CVE
        cve_id = vuln_data.get('cve')

        # Extract CVSS
        cvss_score = vuln_data.get('cvssScore')
        if isinstance(cvss_score, str):
            try:
                cvss_score = float(cvss_score)
            except ValueError:
                cvss_score = None

        cvss_vector = vuln_data.get('cvssVector')

        # Extract severity
        severity = vuln_data.get('severity')

        # Extract description
        description = vuln_data.get('description')

        return ParsedVulnerability(
            title=name,
            description=description,
            remediation=vuln_data.get('solution'),
            cve_id=cve_id,
            scanner_severity=self.normalize_severity(severity),
            cvss_score=cvss_score,
            cvss_vector=cvss_vector,
            asset_identifier=asset_identifier,
            asset_type='dependency',
            raw_data=vuln_data
        )

    def _get_text(self, element: ET.Element, tag: str) -> str | None:
        """Safely extract text from an XML element."""
        child = element.find(tag)
        return child.text if child is not None else None
