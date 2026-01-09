"""Nessus XML scan file parser."""
import xml.etree.ElementTree as ET
from pathlib import Path

from app.core.parsers.base import (
    ParsedAsset,
    ParsedVulnerability,
    ParseResult,
    ScanParser,
)


class NessusParser(ScanParser):
    """Parser for Nessus .nessus XML files."""
    
    def parse(self, file_path: str) -> ParseResult:
        """
        Parse a Nessus XML file.
        
        Nessus format:
        <NessusClientData_v2>
          <Report>
            <ReportHost name="192.168.1.1">
              <ReportItem pluginID="123" severity="3">
                <plugin_name>Vulnerability Name</plugin_name>
                <description>...</description>
                <solution>...</solution>
                <cve>CVE-2021-1234</cve>
                <cvss_base_score>7.5</cvss_base_score>
                <port>443</port>
                <protocol>tcp</protocol>
              </ReportItem>
            </ReportHost>
          </Report>
        </NessusClientData_v2>
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML format: {e}")
        
        vulnerabilities = []
        assets = []
        seen_assets = set()
        
        # Find all reports
        for report in root.findall('.//Report'):
            # Process each host
            for report_host in report.findall('ReportHost'):
                host_name = report_host.get('name', 'unknown')
                
                # Extract host properties
                host_props = {}
                for tag in report_host.findall('HostProperties/tag'):
                    name = tag.get('name')
                    if name:
                        host_props[name] = tag.text
                
                # Determine asset type
                asset_type = self._determine_asset_type(host_props)
                
                # Create asset if not seen
                if host_name not in seen_assets:
                    assets.append(ParsedAsset(
                        asset_identifier=host_name,
                        asset_type=asset_type,
                        metadata=host_props
                    ))
                    seen_assets.add(host_name)
                
                # Process each vulnerability (ReportItem)
                for item in report_host.findall('ReportItem'):
                    vuln = self._parse_report_item(item, host_name, asset_type)
                    if vuln:
                        vulnerabilities.append(vuln)
        
        metadata = {
            'parser': 'nessus',
            'total_vulnerabilities': len(vulnerabilities),
            'total_assets': len(assets),
            'unique_assets': list(seen_assets)
        }
        
        return ParseResult(
            vulnerabilities=vulnerabilities,
            assets=assets,
            metadata=metadata
        )
    
    def _parse_report_item(
        self, 
        item: ET.Element, 
        asset_identifier: str,
        asset_type: str
    ) -> ParsedVulnerability | None:
        """Parse a single ReportItem into a vulnerability."""
        # Skip informational items with severity 0
        severity = item.get('severity', '0')
        if severity == '0':
            return None
        
        plugin_id = item.get('pluginID')
        # Try attribute first, then child element
        plugin_name = item.get('pluginName') or self._get_text(item, 'plugin_name')
        
        if not plugin_name:
            return None
        
        # Extract CVE (may have multiple)
        cve_elements = item.findall('cve')
        cve_id = cve_elements[0].text if cve_elements else None
        
        # Extract CVSS
        cvss_score_text = self._get_text(item, 'cvss_base_score')
        cvss_score = float(cvss_score_text) if cvss_score_text else None
        cvss_vector = self._get_text(item, 'cvss_vector')
        
        # Extract port and protocol
        port_text = item.get('port')
        port = int(port_text) if port_text and port_text.isdigit() else None
        protocol = item.get('protocol')
        
        return ParsedVulnerability(
            title=plugin_name,
            description=self._get_text(item, 'description'),
            remediation=self._get_text(item, 'solution'),
            plugin_id=plugin_id,
            cve_id=cve_id,
            scanner_severity=self.normalize_severity(severity),
            cvss_score=cvss_score,
            cvss_vector=cvss_vector,
            port=port,
            protocol=protocol,
            asset_identifier=asset_identifier,
            asset_type=asset_type,
            raw_data={
                'plugin_id': plugin_id,
                'severity': severity,
                'port': port,
                'protocol': protocol,
            }
        )
    
    def _get_text(self, element: ET.Element, tag: str) -> str | None:
        """Safely extract text from an XML element."""
        child = element.find(tag)
        return child.text if child is not None else None
    
    def _determine_asset_type(self, host_props: dict) -> str:
        """Determine asset type from host properties."""
        # Simple heuristics based on common properties
        os_info = host_props.get('operating-system', '').lower()
        
        if 'router' in os_info or 'switch' in os_info:
            return 'network_device'
        elif 'load' in os_info and 'balanc' in os_info:
            return 'load_balancer'
        elif 'api' in host_props.get('host-fqdn', '').lower():
            return 'api'
        
        return 'server'
