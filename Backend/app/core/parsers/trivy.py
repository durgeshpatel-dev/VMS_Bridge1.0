"""Trivy JSON and SARIF parser for container, filesystem, and code vulnerability scanning."""
import json
from pathlib import Path
from typing import Any

from app.core.parsers.base import (
    ParsedAsset,
    ParsedVulnerability,
    ParseResult,
    ScanParser,
)


class TrivyParser(ScanParser):
    """Parser for Trivy JSON and SARIF reports (container, FS, and code scanning)."""

    def parse(self, file_path: str) -> ParseResult:
        """
        Parse Trivy report in JSON or SARIF format.

        Args:
            file_path: Path to the Trivy report file

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
        if file_path.lower().endswith('.sarif'):
            return self._parse_sarif(file_path)
        else:
            return self._parse_json(file_path)

    def _parse_json(self, file_path: str) -> ParseResult:
        """Parse Trivy JSON format."""
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

        # Handle array of scan results or single result
        if isinstance(data, list):
            results = data
        elif isinstance(data, dict) and 'Results' in data:
            results = data.get('Results', [])
        else:
            results = [data] if isinstance(data, dict) else []

        # Process each scan result
        for result in results:
            artifact_name = result.get('ArtifactName', 'unknown-artifact')
            artifact_type = result.get('Type', 'unknown')
            target = result.get('Target', '')

            # Determine asset type and identifier
            asset_identifier = target or artifact_name
            if not asset_identifier or asset_identifier == 'unknown-artifact':
                asset_identifier = f"{artifact_type}:{artifact_name}"

            # Create asset if not seen
            if asset_identifier not in seen_assets:
                asset_metadata = {
                    'artifactName': artifact_name,
                    'artifactType': artifact_type,
                    'target': target,
                }
                assets.append(ParsedAsset(
                    asset_identifier=asset_identifier,
                    asset_type=self._map_artifact_type(artifact_type),
                    metadata=asset_metadata
                ))
                seen_assets.add(asset_identifier)

            # Process vulnerabilities
            for vuln_data in result.get('Vulnerabilities', []):
                vuln = self._parse_vulnerability(vuln_data, asset_identifier, artifact_type)
                if vuln:
                    vulnerabilities.append(vuln)

        metadata = {
            'parser': 'trivy',
            'total_vulnerabilities': len(vulnerabilities),
            'total_assets': len(assets),
            'report_format': 'json',
        }

        return ParseResult(
            vulnerabilities=vulnerabilities,
            assets=assets,
            metadata=metadata
        )

    def _parse_sarif(self, file_path: str) -> ParseResult:
        """Parse Trivy SARIF format."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid SARIF JSON format: {e}")
        except Exception as e:
            raise ValueError(f"Error reading SARIF file: {e}")

        vulnerabilities = []
        assets = []
        seen_assets = set()

        # Extract runs from SARIF
        runs = data.get('runs', [])
        for run in runs:
            # Get artifact information
            artifacts = run.get('artifacts', [])
            artifact_map = {}
            for idx, artifact in enumerate(artifacts):
                artifact_map[idx] = artifact.get('uri', f'artifact-{idx}')

            # Process results
            for result in run.get('results', []):
                # Determine asset
                locations = result.get('locations', [])
                asset_identifier = 'unknown'
                artifact_type = 'code'

                if locations:
                    first_loc = locations[0]
                    artifact_ref = first_loc.get('artifactLocation', {})
                    asset_identifier = artifact_ref.get('uri', 'unknown')

                # Create asset if not seen
                if asset_identifier not in seen_assets:
                    assets.append(ParsedAsset(
                        asset_identifier=asset_identifier,
                        asset_type=artifact_type,
                        metadata={'format': 'sarif'}
                    ))
                    seen_assets.add(asset_identifier)

                # Parse vulnerability from SARIF result
                vuln = self._parse_sarif_result(result, asset_identifier)
                if vuln:
                    vulnerabilities.append(vuln)

        metadata = {
            'parser': 'trivy',
            'total_vulnerabilities': len(vulnerabilities),
            'total_assets': len(assets),
            'report_format': 'sarif',
        }

        return ParseResult(
            vulnerabilities=vulnerabilities,
            assets=assets,
            metadata=metadata
        )

    def _parse_vulnerability(
        self,
        vuln_data: dict[str, Any],
        asset_identifier: str,
        artifact_type: str
    ) -> ParsedVulnerability | None:
        """Parse a single Trivy vulnerability from JSON."""
        vuln_id = vuln_data.get('VulnerabilityID')
        title = vuln_data.get('Title') or vuln_id or 'Unknown Vulnerability'

        if not title:
            return None

        # Extract severity
        severity = vuln_data.get('Severity', 'medium')

        # Extract description
        description = vuln_data.get('Description')

        # Extract CVSS score
        cvss_score = None
        cvss_data = vuln_data.get('CVSS', {})
        if isinstance(cvss_data, dict):
            cvss_score = cvss_data.get('nvd', {}).get('V3Score') or cvss_data.get('ghsa', {}).get('V3Score')
        elif isinstance(cvss_data, (int, float)):
            cvss_score = float(cvss_data)

        # Extract package information
        pkg_name = vuln_data.get('PkgName', '')
        installed_version = vuln_data.get('InstalledVersion', '')
        fixed_version = vuln_data.get('FixedVersion', '')

        remediation = None
        if fixed_version:
            remediation = f"Update {pkg_name} to {fixed_version}"

        # Extract references
        references = vuln_data.get('References', [])
        cve_id = None
        if references:
            # Look for CVE in references
            import re
            for ref in references:
                if isinstance(ref, str) and 'CVE' in ref.upper():
                    # Extract just the CVE ID from full URL if needed
                    match = re.search(r'(CVE-\d+-\d+)', ref)
                    if match:
                        cve_id = match.group(1)
                        break
                    else:
                        cve_id = ref
                        break
        if not cve_id:
            cve_id = vuln_id

        return ParsedVulnerability(
            title=title,
            description=description,
            remediation=remediation,
            cve_id=cve_id,
            scanner_severity=self.normalize_severity(severity),
            cvss_score=cvss_score,
            asset_identifier=asset_identifier,
            asset_type=self._map_artifact_type(artifact_type),
            raw_data={
                'vulnerabilityID': vuln_id,
                'title': title,
                'severity': severity,
                'packageName': pkg_name,
                'installedVersion': installed_version,
                'fixedVersion': fixed_version,
            }
        )

    def _parse_sarif_result(
        self,
        result: dict[str, Any],
        asset_identifier: str
    ) -> ParsedVulnerability | None:
        """Parse a single result from SARIF format."""
        message = result.get('message', {})
        title = message.get('text', 'Unknown Vulnerability')

        if not title:
            return None

        # Extract severity from level
        level = result.get('level', 'warning')
        severity_map = {
            'error': 'critical',
            'warning': 'high',
            'note': 'medium',
            'none': 'info',
        }
        severity = severity_map.get(level, 'medium')

        # Extract properties
        properties = result.get('properties', {})
        description = properties.get('description')
        cve_id = properties.get('cve')
        cvss_score = properties.get('cvss_score')

        if isinstance(cvss_score, str):
            try:
                cvss_score = float(cvss_score)
            except (ValueError, TypeError):
                cvss_score = None

        return ParsedVulnerability(
            title=title,
            description=description,
            cve_id=cve_id,
            scanner_severity=self.normalize_severity(severity),
            cvss_score=cvss_score,
            asset_identifier=asset_identifier,
            asset_type='code',
            raw_data=properties
        )

    def _map_artifact_type(self, trivy_type: str) -> str:
        """Map Trivy artifact type to our asset types."""
        type_lower = str(trivy_type).lower()

        if 'image' in type_lower or 'container' in type_lower:
            return 'container'
        elif 'fs' in type_lower or 'filesystem' in type_lower or 'dir' in type_lower:
            return 'code'
        elif 'repo' in type_lower or 'git' in type_lower:
            return 'code'
        elif 'package' in type_lower or 'library' in type_lower:
            return 'dependency'
        else:
            return 'code'
