# Vulnerability Scanner Parsers

This directory contains parsers for multiple vulnerability scanning tools. Each parser converts tool-specific report formats into a normalized `ParsedVulnerability` schema for consistent processing.

## Supported Scanners

### 1. **Nessus** (.nessus, .xml)
- **Purpose:** Network and host vulnerability scanning
- **Format:** Nessus XML (`NessusClientData_v2`)
- **Key Fields:**
  - Report hosts and IPs
  - Plugin vulnerabilities with CVE/CVSS data
  - Port and protocol information
- **File Examples:** `*.nessus`, Nessus XML exports
- **Parser:** `NessusParser` in `nessus.py`

### 2. **OWASP Dependency-Check** (.xml, .json)
- **Purpose:** Dependency and library vulnerability scanning
- **Formats:** 
  - XML (default Dependency-Check format)
  - JSON (alternative export format)
- **Key Fields:**
  - Package/dependency names and versions
  - CVE and severity data
  - Remediation/upgrade paths
- **File Examples:** `sample_dependency_check.xml`
- **Parser:** `DependencyCheckParser` in `dependency_check.py`

### 3. **Snyk** (.json)
- **Purpose:** Code, dependency, and container scanning
- **Format:** Snyk JSON report
- **Key Fields:**
  - Vulnerabilities with issue type (vulnerability/license)
  - Package dependencies and upgrade paths
  - CVSS scores and CVE references
  - Project metadata
- **File Examples:** `sample_snyk_report.json`
- **Parser:** `SnykParser` in `snyk.py`

### 4. **Trivy** (.json, .sarif)
- **Purpose:** Lightweight container, filesystem, and code scanning
- **Formats:**
  - JSON (primary format)
  - SARIF (standardized format)
- **Key Fields:**
  - Multiple artifact types (images, filesystems, repositories)
  - Language-specific packages and OS packages
  - Severity and CVSS data
- **File Examples:** `sample_trivy_report.json`
- **Parser:** `TrivyParser` in `trivy.py`

## Parser Usage

### Automatic Detection

The `get_parser()` factory function automatically selects the correct parser:

```python
from app.core.parsers import get_parser

# Auto-detects based on file extension and content
parser = get_parser("scan_report.json")
result = parser.parse("scan_report.json")
```

### File Type Detection

| Extension | Detection Method | Possible Parsers |
|-----------|-----------------|------------------|
| `.nessus` | Extension-based | NessusParser |
| `.sarif` | Extension-based | TrivyParser |
| `.xml` | Content inspection | DependencyCheckParser, NessusParser |
| `.json` | Content inspection | SnykParser, TrivyParser, DependencyCheckParser |
| `.csv` | Not supported | — |

### Content-Based Detection for JSON

JSON files are inspected for markers to identify the scanner:

- **Trivy:** Contains `Results` key with array of scan results
- **Snyk:** Contains `vulnerabilities` key with `projectName` or `displayTargetFile`
- **Dependency-Check:** Contains `dependencies` key with package data
- **Default:** Falls back to SnykParser if markers unclear

### Content-Based Detection for XML

XML files are inspected for root element and content:

- **Dependency-Check:** Contains `dependency` or `dependencies` elements
- **Nessus:** Default fallback for unknown XML formats

## Data Normalization

All parsers normalize data into the `ParsedVulnerability` schema:

```python
@dataclass
class ParsedVulnerability:
    title: str                          # Vulnerability name
    description: str | None             # Detailed findings
    remediation: str | None             # Fix/patch guidance
    plugin_id: str | None               # Tool-specific ID
    cve_id: str | None                  # CVE identifier
    scanner_severity: str | None        # critical/high/medium/low/info
    cvss_score: float | None            # 0.0-10.0
    cvss_vector: str | None             # CVSS vector string
    port: int | None                    # Affected port (Nessus)
    protocol: str | None                # tcp/udp (Nessus)
    asset_identifier: str | None        # Host/package/container name
    asset_type: str = "server"          # server/dependency/container/code
    raw_data: dict[str, Any] | None     # Original tool fields
```

## Severity Normalization

All severities are normalized to a standard set:
- `critical`
- `high`
- `medium`
- `low`
- `info`

Tool-specific values are automatically mapped:
- Nessus: 0-4 numeric values
- Snyk: critical/high/medium/low
- Trivy: CRITICAL/HIGH/MEDIUM/LOW
- Dependency-Check: critical/high/medium/low

## Asset Types

Normalized asset types:
- `server` - Network host/server (Nessus)
- `dependency` - Package/library (Dependency-Check, Snyk, Trivy)
- `container` - Container image (Trivy)
- `code` - Source code files (Snyk, Trivy)

## Testing

Each parser includes comprehensive unit tests:

```bash
pytest tests/test_dependency_check_parser.py
pytest tests/test_snyk_parser.py
pytest tests/test_trivy_parser.py
pytest tests/test_nessus_parser.py  # existing
```

### Sample Reports

Sample reports are included in `Backend/upload/`:
- `sample_dependency_check.xml` - OWASP Dependency-Check XML
- `sample_snyk_report.json` - Snyk JSON report
- `sample_trivy_report.json` - Trivy JSON report

## Adding New Parsers

To add support for a new scanning tool:

1. **Create a parser class** inheriting from `ScanParser`:
   ```python
   class MyToolParser(ScanParser):
       def parse(self, file_path: str) -> ParseResult:
           # Implementation
           pass
   ```

2. **Update the factory** in `__init__.py`:
   - Add import
   - Add detection logic in `_detect_json_parser()` or `_detect_xml_parser()`
   - Add file extension mapping if applicable

3. **Add tests** in `tests/test_mytool_parser.py`

4. **Include sample report** in `Backend/upload/`

## Integration with VMS Bridge

- **Upload endpoint** accepts all supported formats
- **Worker process** automatically selects parser based on file type
- **Database** stores normalized vulnerability data (no schema changes)
- **API** provides unified vulnerability view regardless of source scanner

## References

- [Nessus Documentation](https://docs.tenable.com/nessus/Content/GettingStarted.htm)
- [OWASP Dependency-Check](https://jeremylong.github.io/DependencyCheck/)
- [Snyk API Documentation](https://snyk.io/docs/)
- [Trivy Documentation](https://aquasecurity.github.io/trivy/)
