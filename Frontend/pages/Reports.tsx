import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { apiClient, Vulnerability } from '../services/api';
import { useToast } from '../contexts/ToastContext';
import { DetailSkeleton } from '../components/SkeletonLoader';

interface ScanReport {
  scan: any;
  statistics: {
    total_vulnerabilities: number;
    total_assets: number;
    risk_score: number;
    severity_counts: { [key: string]: number };
    asset_type_breakdown: { [key: string]: number };
  };
  top_vulnerabilities: Array<{
    id: string;
    title: string;
    severity: string;
    cvss_score: number | null;
    cve_id: string | null;
    asset_identifier: string;
  }>;
  vulnerabilities: Array<{
    id: string;
    title: string;
    severity: string;
    cvss_score: number | null;
    cve_id: string | null;
    asset_identifier: string;
    asset_type: string;
    status: string;
    discovered_at: string;
  }>;
}

const Reports: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { showToast } = useToast();
  const id = searchParams.get('id');
  const scanId = searchParams.get('scanId');
  
  const [vulnerability, setVulnerability] = useState<Vulnerability | null>(null);
  const [scanReport, setScanReport] = useState<ScanReport | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (scanId) {
      loadScanReport();
    } else if (id) {
      loadVulnerability();
    }
  }, [id, scanId]);

  const loadVulnerability = async () => {
    if (!id) return;
    
    try {
      setLoading(true);
      const data = await apiClient.getVulnerability(id);
      setVulnerability(data);
    } catch (error: any) {
      showToast(error.message || 'Failed to load vulnerability', 'error');
      navigate('/vulnerabilities');
    } finally {
      setLoading(false);
    }
  };

  const loadScanReport = async () => {
    if (!scanId) return;
    
    try {
      setLoading(true);
      const data = await apiClient.getScanReport(scanId);
      setScanReport(data);
    } catch (error: any) {
      showToast(error.message || 'Failed to load scan report', 'error');
      navigate('/vulnerabilities');
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-900/30 text-red-400 border-red-800';
      case 'high': return 'bg-orange-900/30 text-orange-400 border-orange-800';
      case 'medium': return 'bg-yellow-900/30 text-yellow-400 border-yellow-800';
      case 'low': return 'bg-blue-900/30 text-blue-400 border-blue-800';
      case 'info': return 'bg-gray-700/30 text-gray-400 border-gray-600';
      default: return 'bg-surface text-secondary border-border';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'open': return 'bg-red-900/30 text-red-400 border-red-800';
      case 'in_progress': return 'bg-yellow-900/30 text-yellow-400 border-yellow-800';
      case 'resolved': return 'bg-emerald-900/30 text-emerald-400 border-emerald-800';
      case 'false_positive': return 'bg-gray-700/30 text-gray-400 border-gray-600';
      default: return 'bg-surface text-secondary border-border';
    }
  };

  // Display scan report if scanId is provided
  if (scanId && scanReport) {
    return (
      <div className="flex flex-col h-full overflow-hidden bg-background">
        {/* Header */}
        <header className="flex-shrink-0 px-8 py-4 border-b border-border bg-background/95 backdrop-blur-sm z-10 flex justify-between items-center">
          <div>
            <div className="flex items-center gap-2 text-sm text-secondary mb-1">
              <span className="cursor-pointer hover:text-white" onClick={() => navigate('/dashboard')}>Dashboard</span>
              <span className="material-symbols-outlined text-xs">chevron_right</span>
              <span>Scan Report</span>
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-3">
              <span className="material-symbols-outlined text-3xl text-primary">assessment</span>
              {scanReport.scan.filename}
            </h1>
          </div>
          <div className="flex gap-3">
            <button className="flex items-center gap-2 px-4 py-2 bg-surface border border-border rounded hover:bg-border transition-colors text-white text-sm font-medium">
              <span className="material-symbols-outlined text-[20px]">print</span>
              Print
            </button>
            <button className="flex items-center gap-2 px-4 py-2 bg-primary rounded hover:bg-blue-600 transition-colors text-white text-sm font-medium shadow-lg shadow-primary/20">
              <span className="material-symbols-outlined text-[20px]">download</span>
              Download PDF
            </button>
          </div>
        </header>

        {/* Content */}
        <div className="flex-1 overflow-y-auto px-8 py-6 custom-scroll">
          <div className="max-w-6xl mx-auto space-y-6">
            
            {/* Scan Summary */}
            <div className="bg-surface border border-border rounded-lg p-6">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <span className="material-symbols-outlined text-primary">info</span>
                Scan Summary
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-xs text-secondary uppercase tracking-wider mb-1">Total Vulnerabilities</p>
                  <p className="text-white font-bold text-xl">{scanReport.statistics.total_vulnerabilities}</p>
                </div>
                <div>
                  <p className="text-xs text-secondary uppercase tracking-wider mb-1">Affected Assets</p>
                  <p className="text-white font-bold text-xl">{scanReport.statistics.total_assets}</p>
                </div>
                <div>
                  <p className="text-xs text-secondary uppercase tracking-wider mb-1">Risk Score</p>
                  <p className="text-white font-bold text-xl">{scanReport.statistics.risk_score}%</p>
                </div>
                <div>
                  <p className="text-xs text-secondary uppercase tracking-wider mb-1">Status</p>
                  <span className={`px-3 py-1.5 rounded text-sm font-medium uppercase border ${
                    scanReport.scan.status === 'completed' ? 'bg-emerald-900/30 text-emerald-400 border-emerald-800' :
                    scanReport.scan.status === 'running' ? 'bg-yellow-900/30 text-yellow-400 border-yellow-800' :
                    'bg-gray-700/30 text-gray-400 border-gray-600'
                  }`}>
                    {scanReport.scan.status}
                  </span>
                </div>
              </div>
            </div>

            {/* Severity Distribution */}
            <div className="bg-surface border border-border rounded-lg p-6">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <span className="material-symbols-outlined text-primary">bar_chart</span>
                Severity Distribution
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                {Object.entries(scanReport.statistics.severity_counts).map(([severity, count]) => (
                  <div key={severity} className="bg-background rounded-lg p-4 border border-border">
                    <p className={`text-xs font-medium uppercase mb-2 ${
                      severity === 'critical' ? 'text-red-400' :
                      severity === 'high' ? 'text-orange-400' :
                      severity === 'medium' ? 'text-yellow-400' :
                      severity === 'low' ? 'text-blue-400' :
                      'text-gray-400'
                    }`}>
                      {severity}
                    </p>
                    <p className="text-white font-bold text-2xl">{count}</p>
                    <div className="mt-2 bg-border rounded-full h-2 overflow-hidden">
                      <div 
                        className={`h-full transition-all ${
                          severity === 'critical' ? 'bg-red-500' :
                          severity === 'high' ? 'bg-orange-500' :
                          severity === 'medium' ? 'bg-yellow-500' :
                          severity === 'low' ? 'bg-blue-500' :
                          'bg-gray-500'
                        }`}
                        style={{ width: `${(Number(count) / Number(scanReport.statistics.total_vulnerabilities)) * 100}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Asset Type Breakdown */}
            <div className="bg-surface border border-border rounded-lg p-6">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <span className="material-symbols-outlined text-primary">storage</span>
                Asset Type Breakdown
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {Object.entries(scanReport.statistics.asset_type_breakdown).map(([assetType, count]) => (
                  <div key={assetType} className="bg-background rounded-lg p-4 border border-border">
                    <p className="text-xs text-secondary uppercase tracking-wider mb-1">
                      {assetType.replace('_', ' ')}
                    </p>
                    <p className="text-white font-bold text-xl">{count}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Top Vulnerabilities */}
            <div className="bg-surface border border-border rounded-lg p-6">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <span className="material-symbols-outlined text-primary">warning</span>
                Top Vulnerabilities by Severity
              </h3>
              <div className="space-y-4">
                {scanReport.top_vulnerabilities.map((vuln, index) => (
                  <div key={vuln.id} className="bg-background rounded-lg p-4 border border-border hover:border-primary transition-colors">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="text-xs font-bold text-secondary">{index + 1}.</span>
                          <h4 className="text-white font-medium">{vuln.title}</h4>
                        </div>
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className={`px-2 py-1 rounded text-xs font-medium uppercase border ${
                            vuln.severity === 'critical' ? 'bg-red-900/30 text-red-400 border-red-800' :
                            vuln.severity === 'high' ? 'bg-orange-900/30 text-orange-400 border-orange-800' :
                            vuln.severity === 'medium' ? 'bg-yellow-900/30 text-yellow-400 border-yellow-800' :
                            vuln.severity === 'low' ? 'bg-blue-900/30 text-blue-400 border-blue-800' :
                            'bg-gray-700/30 text-gray-400 border-gray-600'
                          }`}>
                            {vuln.severity}
                          </span>
                          {vuln.cvss_score && (
                            <span className="px-2 py-1 rounded text-xs font-medium bg-background text-white border border-border">
                              CVSS: {vuln.cvss_score.toFixed(1)}
                            </span>
                          )}
                          {vuln.cve_id && (
                            <a 
                              href={`https://nvd.nist.gov/vuln/detail/${vuln.cve_id}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-blue-400 hover:underline text-xs font-mono"
                            >
                              {vuln.cve_id}
                            </a>
                          )}
                        </div>
                        <p className="text-secondary text-sm mt-2">
                          Affected Asset: {vuln.asset_identifier}
                        </p>
                      </div>
                      <button 
                        onClick={() => navigate(`/reports?id=${vuln.id}`)}
                        className="ml-4 px-3 py-1.5 bg-primary rounded hover:bg-blue-600 transition-colors text-white text-sm font-medium"
                      >
                        View Details
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* All Vulnerabilities */}
            <div className="bg-surface border border-border rounded-lg p-6">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <span className="material-symbols-outlined text-primary">list_alt</span>
                All Vulnerabilities ({scanReport.vulnerabilities.length})
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left">
                  <thead>
                    <tr className="border-b border-border">
                      <th className="py-3 px-4 text-xs font-medium text-secondary uppercase tracking-wider">Title</th>
                      <th className="py-3 px-4 text-xs font-medium text-secondary uppercase tracking-wider">Severity</th>
                      <th className="py-3 px-4 text-xs font-medium text-secondary uppercase tracking-wider">CVSS Score</th>
                      <th className="py-3 px-4 text-xs font-medium text-secondary uppercase tracking-wider">CVE ID</th>
                      <th className="py-3 px-4 text-xs font-medium text-secondary uppercase tracking-wider">Asset</th>
                      <th className="py-3 px-4 text-xs font-medium text-secondary uppercase tracking-wider">Status</th>
                      <th className="py-3 px-4 text-xs font-medium text-secondary uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {scanReport.vulnerabilities.map((vuln) => (
                      <tr key={vuln.id} className="hover:bg-background transition-colors">
                        <td className="py-3 px-4">
                          <p className="text-white text-sm font-medium">{vuln.title}</p>
                        </td>
                        <td className="py-3 px-4">
                          <span className={`px-2 py-1 rounded text-xs font-medium uppercase border ${
                            vuln.severity === 'critical' ? 'bg-red-900/30 text-red-400 border-red-800' :
                            vuln.severity === 'high' ? 'bg-orange-900/30 text-orange-400 border-orange-800' :
                            vuln.severity === 'medium' ? 'bg-yellow-900/30 text-yellow-400 border-yellow-800' :
                            vuln.severity === 'low' ? 'bg-blue-900/30 text-blue-400 border-blue-800' :
                            'bg-gray-700/30 text-gray-400 border-gray-600'
                          }`}>
                            {vuln.severity}
                          </span>
                        </td>
                        <td className="py-3 px-4">
                          <span className="text-white text-sm">{vuln.cvss_score?.toFixed(1) || '-'}</span>
                        </td>
                        <td className="py-3 px-4">
                          {vuln.cve_id ? (
                            <a 
                              href={`https://nvd.nist.gov/vuln/detail/${vuln.cve_id}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-blue-400 hover:underline text-sm font-mono"
                            >
                              {vuln.cve_id}
                            </a>
                          ) : (
                            '-'
                          )}
                        </td>
                        <td className="py-3 px-4">
                          <p className="text-white text-sm">{vuln.asset_identifier}</p>
                        </td>
                        <td className="py-3 px-4">
                          <span className={`px-2 py-1 rounded text-xs font-medium capitalize border ${
                            vuln.status === 'open' ? 'bg-red-900/30 text-red-400 border-red-800' :
                            vuln.status === 'in_progress' ? 'bg-yellow-900/30 text-yellow-400 border-yellow-800' :
                            vuln.status === 'resolved' ? 'bg-emerald-900/30 text-emerald-400 border-emerald-800' :
                            'bg-gray-700/30 text-gray-400 border-gray-600'
                          }`}>
                            {vuln.status.replace('_', ' ')}
                          </span>
                        </td>
                        <td className="py-3 px-4">
                          <button 
                            onClick={() => navigate(`/reports?id=${vuln.id}`)}
                            className="px-3 py-1.5 bg-primary rounded hover:bg-blue-600 transition-colors text-white text-xs font-medium"
                          >
                            View
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!id && !scanId) {
    return (
      <div className="flex flex-col h-full items-center justify-center text-secondary">
        <span className="material-symbols-outlined text-6xl mb-4 opacity-50">description</span>
        <h2 className="text-xl font-medium text-white">No Report Selected</h2>
        <p className="mt-2">Please select a vulnerability from the Vulnerabilities page to view its report.</p>
        <button 
          onClick={() => navigate('/vulnerabilities')}
          className="mt-6 px-4 py-2 bg-primary text-white rounded hover:bg-blue-600 transition-colors"
        >
          Go to Vulnerabilities
        </button>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex flex-col h-full overflow-hidden bg-background">
        <header className="flex-shrink-0 px-8 py-4 border-b border-border bg-background/95 backdrop-blur-sm z-10">
          <div className="h-8 bg-border rounded w-64 animate-pulse"></div>
        </header>
        <div className="flex-1 overflow-y-auto px-8 py-6 custom-scroll">
          <div className="max-w-5xl mx-auto">
            <DetailSkeleton />
          </div>
        </div>
      </div>
    );
  }

  if (!vulnerability) {
    return (
      <div className="flex flex-col h-full items-center justify-center text-secondary">
        <span className="material-symbols-outlined text-6xl mb-4 opacity-50">error</span>
        <h2 className="text-xl font-medium text-white">Vulnerability Not Found</h2>
        <button 
          onClick={() => navigate('/vulnerabilities')}
          className="mt-6 px-4 py-2 bg-primary text-white rounded hover:bg-blue-600 transition-colors"
        >
          Go to Vulnerabilities
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full overflow-hidden bg-background">
      {/* Header */}
      <header className="flex-shrink-0 px-8 py-4 border-b border-border bg-background/95 backdrop-blur-sm z-10 flex justify-between items-center">
        <div>
          <div className="flex items-center gap-2 text-sm text-secondary mb-1">
            <span className="cursor-pointer hover:text-white" onClick={() => navigate('/vulnerabilities')}>Vulnerabilities</span>
            <span className="material-symbols-outlined text-xs">chevron_right</span>
            <span>Report</span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-3">
            <span className="material-symbols-outlined text-3xl text-primary">summarize</span>
            Vulnerability Report
          </h1>
        </div>
        <div className="flex gap-3">
          <button className="flex items-center gap-2 px-4 py-2 bg-surface border border-border rounded hover:bg-border transition-colors text-white text-sm font-medium">
            <span className="material-symbols-outlined text-[20px]">print</span>
            Print
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-primary rounded hover:bg-blue-600 transition-colors text-white text-sm font-medium shadow-lg shadow-primary/20">
            <span className="material-symbols-outlined text-[20px]">download</span>
            Download PDF
          </button>
        </div>
      </header>

      {/* Content */}
      <div className="flex-1 overflow-y-auto px-8 py-6 custom-scroll">
        <div className="max-w-5xl mx-auto space-y-6">
          
          {/* Title & Overview */}
          <div className="bg-surface border border-border rounded-lg p-6">
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <h2 className="text-2xl font-bold text-white mb-3">{vulnerability.title}</h2>
                <div className="flex items-center gap-2 flex-wrap">
                  <span className={`px-3 py-1.5 rounded text-sm font-medium uppercase border ${getSeverityColor(vulnerability.scanner_severity)}`}>
                    {vulnerability.scanner_severity} Severity
                  </span>
                  <span className={`px-3 py-1.5 rounded text-sm font-medium capitalize border ${getStatusColor(vulnerability.status)}`}>
                    {vulnerability.status.replace('_', ' ')}
                  </span>
                  {vulnerability.cvss_score && (
                    <span className="px-3 py-1.5 rounded text-sm font-medium bg-background text-white border border-border">
                      CVSS Score: {vulnerability.cvss_score.toFixed(1)}
                    </span>
                  )}
                </div>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4 mt-6 pt-6 border-t border-border">
              <div>
                <p className="text-xs text-secondary uppercase tracking-wider mb-1">Discovered</p>
                <p className="text-white font-medium">{new Date(vulnerability.discovered_at).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}</p>
              </div>
              {vulnerability.plugin_id && (
                <div>
                  <p className="text-xs text-secondary uppercase tracking-wider mb-1">Plugin ID</p>
                  <p className="text-white font-mono">{vulnerability.plugin_id}</p>
                </div>
              )}
              {vulnerability.cve_id && (
                <div>
                  <p className="text-xs text-secondary uppercase tracking-wider mb-1">CVE ID</p>
                  <a 
                    href={`https://nvd.nist.gov/vuln/detail/${vulnerability.cve_id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-400 hover:underline font-mono"
                  >
                    {vulnerability.cve_id}
                  </a>
                </div>
              )}
            </div>
          </div>

          {/* Asset Information */}
          <div className="bg-surface border border-border rounded-lg p-6">
            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <span className="material-symbols-outlined text-primary">dns</span>
              Affected Asset
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-secondary uppercase tracking-wider mb-1">Asset Identifier</p>
                <p className="text-white font-mono text-lg">{vulnerability.asset?.asset_identifier || 'Unknown'}</p>
              </div>
              <div>
                <p className="text-xs text-secondary uppercase tracking-wider mb-1">Asset Type</p>
                <p className="text-white capitalize">{vulnerability.asset?.asset_type || 'Unknown'}</p>
              </div>
              {vulnerability.port && (
                <>
                  <div>
                    <p className="text-xs text-secondary uppercase tracking-wider mb-1">Port</p>
                    <p className="text-white font-mono">{vulnerability.port}</p>
                  </div>
                  <div>
                    <p className="text-xs text-secondary uppercase tracking-wider mb-1">Protocol</p>
                    <p className="text-white uppercase">{vulnerability.protocol || 'TCP'}</p>
                  </div>
                </>
              )}
              {vulnerability.asset?.first_seen && (
                <div>
                  <p className="text-xs text-secondary uppercase tracking-wider mb-1">First Seen</p>
                  <p className="text-white">{new Date(vulnerability.asset.first_seen).toLocaleDateString()}</p>
                </div>
              )}
              {vulnerability.asset?.last_seen && (
                <div>
                  <p className="text-xs text-secondary uppercase tracking-wider mb-1">Last Seen</p>
                  <p className="text-white">{new Date(vulnerability.asset.last_seen).toLocaleDateString()}</p>
                </div>
              )}
            </div>
          </div>

          {/* Technical Details */}
          {vulnerability.cvss_vector && (
            <div className="bg-surface border border-border rounded-lg p-6">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <span className="material-symbols-outlined text-primary">analytics</span>
                CVSS Details
              </h3>
              <div className="space-y-3">
                <div>
                  <p className="text-xs text-secondary uppercase tracking-wider mb-1">CVSS Vector</p>
                  <p className="text-white font-mono text-sm bg-background px-3 py-2 rounded border border-border">{vulnerability.cvss_vector}</p>
                </div>
                {vulnerability.cvss_score && (
                  <div>
                    <p className="text-xs text-secondary uppercase tracking-wider mb-1">Base Score</p>
                    <div className="flex items-center gap-3">
                      <div className="flex-1 bg-background rounded-full h-3 overflow-hidden border border-border">
                        <div 
                          className={`h-full transition-all ${
                            vulnerability.cvss_score >= 9.0 ? 'bg-red-500' :
                            vulnerability.cvss_score >= 7.0 ? 'bg-orange-500' :
                            vulnerability.cvss_score >= 4.0 ? 'bg-yellow-500' :
                            'bg-blue-500'
                          }`}
                          style={{ width: `${(vulnerability.cvss_score / 10) * 100}%` }}
                        />
                      </div>
                      <span className="text-white font-bold text-lg min-w-[3rem] text-right">{vulnerability.cvss_score.toFixed(1)}</span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Description */}
          {vulnerability.description && (
            <div className="bg-surface border border-border rounded-lg p-6">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <span className="material-symbols-outlined text-primary">description</span>
                Description
              </h3>
              <div className="text-secondary leading-relaxed whitespace-pre-wrap">{vulnerability.description.trim()}</div>
            </div>
          )}

          {/* Remediation */}
          {vulnerability.remediation && (
            <div className="bg-surface border border-emerald-900/30 rounded-lg p-6">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <span className="material-symbols-outlined text-emerald-400">build</span>
                Remediation Steps
              </h3>
              <div className="text-secondary leading-relaxed whitespace-pre-wrap">{vulnerability.remediation.trim()}</div>
            </div>
          )}

          {/* ML Analysis Placeholder */}
          <div className="bg-surface border border-purple-900/30 rounded-lg p-6">
            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <span className="material-symbols-outlined text-purple-400">psychology</span>
              ML Risk Analysis
              <span className="ml-2 px-2 py-0.5 rounded text-xs font-medium bg-purple-900/30 text-purple-400 border border-purple-800">
                Coming Soon
              </span>
            </h3>
            <div className="text-secondary text-sm">
              Machine learning-powered risk analysis and prioritization will be available soon. This will include:
              <ul className="list-disc list-inside mt-2 space-y-1 ml-2">
                <li>Automated risk scoring based on context and exploitability</li>
                <li>Attack surface analysis</li>
                <li>Remediation priority recommendations</li>
                <li>Similar vulnerability patterns across your infrastructure</li>
              </ul>
            </div>
          </div>

          {/* Jira Integration Placeholder */}
          <div className="bg-surface border border-blue-900/30 rounded-lg p-6">
            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <div className="w-6 h-6 bg-[#0052CC] rounded flex items-center justify-center text-xs font-bold text-white">J</div>
              Jira Ticket Integration
              <span className="ml-2 px-2 py-0.5 rounded text-xs font-medium bg-blue-900/30 text-blue-400 border border-blue-800">
                Coming Soon
              </span>
            </h3>
            <div className="text-secondary text-sm">
              Automatic Jira ticket creation for critical and high severity vulnerabilities will be available soon.
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};

export default Reports;
