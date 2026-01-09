"""Tests for scan parsers."""
import tempfile
from pathlib import Path

import pytest

from app.core.parsers import get_parser
from app.core.parsers.nessus import NessusParser


SAMPLE_NESSUS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<NessusClientData_v2>
  <Report name="Sample Scan">
    <ReportHost name="192.168.1.100">
      <HostProperties>
        <tag name="operating-system">Linux Kernel 5.4</tag>
        <tag name="host-fqdn">server1.example.com</tag>
      </HostProperties>
      <ReportItem port="443" svc_name="https" protocol="tcp" severity="3" pluginID="12345">
        <plugin_name>SSL Certificate Expiring Soon</plugin_name>
        <description>The SSL certificate on this server is expiring soon.</description>
        <solution>Renew the SSL certificate.</solution>
        <cve>CVE-2021-1234</cve>
        <cvss_base_score>7.5</cvss_base_score>
        <cvss_vector>CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N</cvss_vector>
      </ReportItem>
      <ReportItem port="22" svc_name="ssh" protocol="tcp" severity="2" pluginID="12346">
        <plugin_name>SSH Weak Ciphers Supported</plugin_name>
        <description>The SSH server supports weak encryption ciphers.</description>
        <solution>Disable weak ciphers in SSH configuration.</solution>
        <cvss_base_score>5.3</cvss_base_score>
      </ReportItem>
      <ReportItem port="0" protocol="tcp" severity="0" pluginID="10000">
        <plugin_name>Host Information</plugin_name>
        <description>General information about the host.</description>
      </ReportItem>
    </ReportHost>
    <ReportHost name="192.168.1.101">
      <HostProperties>
        <tag name="operating-system">Windows Server 2019</tag>
      </HostProperties>
      <ReportItem port="445" protocol="tcp" severity="4" pluginID="12347">
        <plugin_name>SMB Signing Not Required</plugin_name>
        <description>SMB signing is not enforced.</description>
        <solution>Enable SMB signing.</solution>
        <cve>CVE-2020-5678</cve>
        <cvss_base_score>9.8</cvss_base_score>
      </ReportItem>
    </ReportHost>
  </Report>
</NessusClientData_v2>
"""


class TestNessusParser:
    """Test cases for Nessus XML parser."""
    
    def test_parse_nessus_file(self):
        """Test parsing a Nessus XML file."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.nessus', delete=False) as f:
            f.write(SAMPLE_NESSUS_XML)
            temp_file = f.name
        
        try:
            parser = NessusParser()
            result = parser.parse(temp_file)
            
            # Check assets
            assert len(result.assets) == 2
            asset_identifiers = {a.asset_identifier for a in result.assets}
            assert '192.168.1.100' in asset_identifiers
            assert '192.168.1.101' in asset_identifiers
            
            # Check vulnerabilities (should skip severity 0)
            assert len(result.vulnerabilities) == 3
            
            # Check first vulnerability details
            vuln1 = next(v for v in result.vulnerabilities if v.plugin_id == '12345')
            assert vuln1.title == 'SSL Certificate Expiring Soon'
            assert vuln1.cve_id == 'CVE-2021-1234'
            assert vuln1.scanner_severity == 'high'
            assert vuln1.cvss_score == 7.5
            assert vuln1.port == 443
            assert vuln1.protocol == 'tcp'
            assert vuln1.asset_identifier == '192.168.1.100'
            
            # Check critical vulnerability
            vuln_critical = next(v for v in result.vulnerabilities if v.plugin_id == '12347')
            assert vuln_critical.scanner_severity == 'critical'
            assert vuln_critical.cvss_score == 9.8
            
            # Check metadata
            assert result.metadata['parser'] == 'nessus'
            assert result.metadata['total_vulnerabilities'] == 3
            assert result.metadata['total_assets'] == 2
            
        finally:
            Path(temp_file).unlink()
    
    def test_parse_invalid_xml(self):
        """Test parsing invalid XML raises error."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write("<invalid xml>>")
            temp_file = f.name
        
        try:
            parser = NessusParser()
            with pytest.raises(ValueError, match="Invalid XML format"):
                parser.parse(temp_file)
        finally:
            Path(temp_file).unlink()
    
    def test_parse_nonexistent_file(self):
        """Test parsing non-existent file raises error."""
        parser = NessusParser()
        with pytest.raises(FileNotFoundError):
            parser.parse('/nonexistent/file.nessus')
    
    def test_severity_normalization(self):
        """Test severity normalization."""
        assert NessusParser.normalize_severity('4') == 'critical'
        assert NessusParser.normalize_severity('3') == 'high'
        assert NessusParser.normalize_severity('2') == 'medium'
        assert NessusParser.normalize_severity('1') == 'low'
        assert NessusParser.normalize_severity('0') == 'info'
        assert NessusParser.normalize_severity('Critical') == 'critical'
        assert NessusParser.normalize_severity('HIGH') == 'high'
        assert NessusParser.normalize_severity('Medium') == 'medium'
        assert NessusParser.normalize_severity('LOW') == 'low'
        assert NessusParser.normalize_severity('Informational') == 'info'


class TestParserFactory:
    """Test cases for parser factory."""
    
    def test_get_nessus_parser(self):
        """Test getting Nessus parser by extension."""
        parser = get_parser('/path/to/scan.nessus')
        assert isinstance(parser, NessusParser)
        
        parser = get_parser('/path/to/scan.xml')
        assert isinstance(parser, NessusParser)
    
    def test_unsupported_format(self):
        """Test unsupported file format raises error."""
        with pytest.raises(ValueError, match="Unsupported file format"):
            get_parser('/path/to/scan.txt')
