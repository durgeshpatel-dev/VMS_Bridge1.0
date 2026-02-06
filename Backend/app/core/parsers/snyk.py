"""Snyk JSON report parser for code and dependency vulnerability scanning."""
import json
from pathlib import Path
from typing import Any

from app.core.parsers.base import (
    ParsedAsset,
    ParsedVulnerability,
    ParseResult,
    ScanParser,
)


class SnykParser(ScanParser):
    """Parser for Snyk JSON reports (code, dependency, container scanning)."""

    def parse(self, file_path: str) -> ParseResult:
        """
        Parse Snyk JSON report.

        Snyk format includes vulnerability issues with package/code references.
        Typically one JSON file per scan.

        Args:
            file_path: Path to the Snyk JSON report

        Returns:
            ParseResult containing vulnerabilities, assets, and metadata

        Raises:
            ValueError: If file format is invalid
            FileNotFoundError: If file doesn't exist
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

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

        # Check if this is a Snyk report (has 'vulnerabilities' key)
        if not isinstance(data, dict):
            raise ValueError("Invalid Snyk JSON: expected object at root level")

        # Get project metadata
        project_name = data.get('projectName', 'unknown-project')
        target = data.get('displayTargetFile', '')

        # Process vulnerabilities
        snyk_vulns = data.get('vulnerabilities', [])
        if not isinstance(snyk_vulns, list):
            snyk_vulns = []

        for vuln_data in snyk_vulns:
            # Extract package information from 'from' array
            from_list = vuln_data.get('from', [])
            # Get the actual package (not the project), which is the first element if length > 1
            if len(from_list) > 1:
                package_name = from_list[1]  # e.g., 'lodash@4.17.15'
            else:
                package_name = from_list[0] if from_list else 'unknown'

            # Create asset if not seen
            if package_name not in seen_assets:
                asset_metadata = {
                    'projectName': project_name,
                    'displayTargetFile': target,
                    'introducedBy': from_list,
                }
                asset_type = self._determine_asset_type(vuln_data, package_name)
                assets.append(ParsedAsset(
                    asset_identifier=package_name,
                    asset_type=asset_type,
                    metadata=asset_metadata
                ))
                seen_assets.add(package_name)

            # Parse vulnerability
            vuln = self._parse_vulnerability(vuln_data, package_name)
            if vuln:
                vulnerabilities.append(vuln)

        metadata = {
            'parser': 'snyk',
            'total_vulnerabilities': len(vulnerabilities),
            'total_assets': len(assets),
            'project_name': project_name,
            'target': target,
        }

        return ParseResult(
            vulnerabilities=vulnerabilities,
            assets=assets,
            metadata=metadata
        )

    def _parse_vulnerability(
        self,
        vuln_data: dict[str, Any],
        asset_identifier: str
    ) -> ParsedVulnerability | None:
        """Parse a single Snyk vulnerability."""
        title = vuln_data.get('title')
        if not title:
            return None

        # Extract issue type
        issue_type = vuln_data.get('type', 'vulnerability')

        # Skip license issues (only process vulnerabilities)
        if issue_type == 'license':
            return None

        # Extract CVE
        cve_list = vuln_data.get('cves', [])
        cve_id = None
        if cve_list and isinstance(cve_list, list) and len(cve_list) > 0:
            cve_id = cve_list[0].get('id') if isinstance(cve_list[0], dict) else cve_list[0]

        # Extract severity
        severity = vuln_data.get('severity', 'medium')

        # Extract description
        description = vuln_data.get('description')
        # If no description, use remediation info
        if not description:
            remediation = vuln_data.get('remediation')
            if remediation:
                description = f"Remediation: {remediation}"

        # Extract CVSS score if available
        cvss_score = None
        cvss_data = vuln_data.get('cvssScore')
        if cvss_data:
            try:
                cvss_score = float(cvss_data)
            except (ValueError, TypeError):
                cvss_score = None

        # Extract package version and upgrade info
        package_version = vuln_data.get('packageVersion', '')
        upgrade_path = vuln_data.get('upgradePath', [])
        upgrade_version = upgrade_path[1] if len(upgrade_path) > 1 else None

        remediation_text = vuln_data.get('remediation')
        if upgrade_version and not remediation_text:
            remediation_text = f"Upgrade to {upgrade_version}"

        return ParsedVulnerability(
            title=title,
            description=description,
            remediation=remediation_text,
            cve_id=cve_id,
            scanner_severity=self.normalize_severity(severity),
            cvss_score=cvss_score,
            asset_identifier=asset_identifier,
            asset_type=self._determine_asset_type(vuln_data, asset_identifier),
            raw_data={
                'title': title,
                'issueType': issue_type,
                'severity': severity,
                'cves': cve_id,
                'packageVersion': package_version,
                'identifiers': vuln_data.get('identifiers', {}),
            }
        )

    def _determine_asset_type(self, vuln_data: dict[str, Any], package_name: str) -> str:
        """
        Determine asset type based on vulnerability data.

        Returns: 'dependency', 'code', 'container', or 'code'
        """
        issue_type = vuln_data.get('type', 'vulnerability')
        from_list = vuln_data.get('from', [])

        # Check issue type
        if 'container' in str(issue_type).lower():
            return 'container'

        # Check package name patterns
        if '@' in package_name or '/' in package_name:
            return 'dependency'

        # Default to code
        return 'code'
