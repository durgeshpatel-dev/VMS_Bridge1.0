import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { apiClient, Vulnerability, VulnerabilityListResponse } from '../services/api';
import { useToast } from '../contexts/ToastContext';

const Vulnerabilities: React.FC = () => {
    
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { showToast } = useToast();
  const [vulnerabilities, setVulnerabilities] = useState<Vulnerability[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  
  // Filters
  const scanIdFromUrl = searchParams.get('scan_id');
  const [severityFilter, setSeverityFilter] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState('');
  const [page, setPage] = useState(0);
  const [limit] = useState(50);

  const selectedVuln = vulnerabilities.find(v => v.id === selectedId);

  const loadVulnerabilities = async () => {
    try {
      setLoading(true);
      const response: VulnerabilityListResponse = await apiClient.listVulnerabilities({
        severity: severityFilter || undefined,
        status: statusFilter || undefined,
        scan_id: scanIdFromUrl || undefined,
        search: searchTerm || undefined,
        skip: page * limit,
        limit,
      });
      
      setVulnerabilities(response.items);
      setTotal(response.total);
      
      // Auto-select first item if none selected
      if (response.items.length > 0 && !selectedId) {
        setSelectedId(response.items[0].id);
      }
    } catch (error: any) {
      showToast(error.message || 'Failed to load vulnerabilities', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadVulnerabilities();
  }, [severityFilter, statusFilter, searchTerm, page]);

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

  const severityCounts = {
    critical: vulnerabilities.filter(v => v.scanner_severity === 'critical').length,
    high: vulnerabilities.filter(v => v.scanner_severity === 'high').length,
    medium: vulnerabilities.filter(v => v.scanner_severity === 'medium').length,
    low: vulnerabilities.filter(v => v.scanner_severity === 'low').length,
    info: vulnerabilities.filter(v => v.scanner_severity === 'info').length,
  };

  return (
    <div className="flex flex-col h-full overflow-hidden bg-background">
      {/* Header */}
      <div className="h-14 flex items-center justify-between px-6 border-b border-border bg-background shrink-0">
        <div className="flex items-center gap-2 text-sm">
          <span className="font-semibold text-white">Vulnerabilities</span>
          <span className="ml-2 px-2 py-0.5 rounded-full text-xs font-medium bg-surface text-secondary">{total} total</span>
          {scanIdFromUrl && (
            <span className="ml-2 px-2 py-0.5 rounded-full text-xs font-medium bg-primary/20 text-primary border border-primary/50 flex items-center gap-1">
              Filtered by Scan
              <button 
                onClick={() => navigate('/vulnerabilities')}
                className="hover:text-white"
                title="Clear scan filter"
              >
                <span className="material-symbols-outlined text-sm">close</span>
              </button>
            </span>
          )}
        </div>
        <div className="flex items-center gap-3">
          <div className="relative">
            <input
              type="text"
              placeholder="Search vulnerabilities..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-64 px-3 py-1.5 pl-9 text-sm bg-surface border border-border rounded text-white placeholder-secondary focus:outline-none focus:border-primary"
            />
            <span className="material-symbols-outlined absolute left-2 top-1/2 -translate-y-1/2 text-secondary text-sm">search</span>
          </div>
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        {/* Main List */}
        <div className="flex-1 flex flex-col min-w-0 bg-background">
          <div className="p-4 flex items-center justify-between gap-4">
            <div className="flex items-center gap-2 flex-wrap">
              <button 
                onClick={() => setSeverityFilter('')}
                className={`px-3 py-1.5 text-xs font-medium rounded-full transition-colors ${
                  severityFilter === '' 
                    ? 'bg-primary text-white' 
                    : 'bg-surface text-secondary hover:text-white hover:bg-border'
                }`}
              >
                All ({total})
              </button>
              <button 
                onClick={() => setSeverityFilter('critical')}
                className={`px-3 py-1.5 text-xs font-medium rounded-full border transition-colors ${
                  severityFilter === 'critical' 
                    ? 'bg-red-900/30 text-red-400 border-red-800' 
                    : 'bg-red-900/20 text-red-400 border-transparent hover:border-red-800'
                }`}
              >
                Critical ({severityCounts.critical})
              </button>
              <button 
                onClick={() => setSeverityFilter('high')}
                className={`px-3 py-1.5 text-xs font-medium rounded-full border transition-colors ${
                  severityFilter === 'high' 
                    ? 'bg-orange-900/30 text-orange-400 border-orange-800' 
                    : 'bg-orange-900/20 text-orange-400 border-transparent hover:border-orange-800'
                }`}
              >
                High ({severityCounts.high})
              </button>
              <button 
                onClick={() => setSeverityFilter('medium')}
                className={`px-3 py-1.5 text-xs font-medium rounded-full border transition-colors ${
                  severityFilter === 'medium' 
                    ? 'bg-yellow-900/30 text-yellow-400 border-yellow-800' 
                    : 'bg-yellow-900/20 text-yellow-400 border-transparent hover:border-yellow-800'
                }`}
              >
                Medium ({severityCounts.medium})
              </button>
              <button 
                onClick={() => setSeverityFilter('low')}
                className={`px-3 py-1.5 text-xs font-medium rounded-full border transition-colors ${
                  severityFilter === 'low' 
                    ? 'bg-blue-900/30 text-blue-400 border-blue-800' 
                    : 'bg-blue-900/20 text-blue-400 border-transparent hover:border-blue-800'
                }`}
              >
                Low ({severityCounts.low})
              </button>
            </div>
            <div className="flex items-center gap-2">
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-3 py-1.5 text-xs bg-surface border border-border rounded text-white focus:outline-none focus:border-primary"
              >
                <option value="">All Status</option>
                <option value="open">Open</option>
                <option value="in_progress">In Progress</option>
                <option value="resolved">Resolved</option>
                <option value="false_positive">False Positive</option>
              </select>
            </div>
          </div>

          <div className="flex-1 overflow-auto px-4 pb-4 custom-scroll">
            {loading ? (
              <div className="flex items-center justify-center h-64">
                <div className="text-secondary">Loading vulnerabilities...</div>
              </div>
            ) : vulnerabilities.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-64 text-secondary">
                <span className="material-symbols-outlined text-4xl mb-2">search_off</span>
                <p>No vulnerabilities found</p>
              </div>
            ) : (
              <table className="w-full text-left border-collapse">
                <thead className="bg-surface/50 sticky top-0 z-10 backdrop-blur-sm">
                  <tr>
                    <th className="py-3 px-4 text-xs font-semibold text-secondary uppercase tracking-wider">Severity</th>
                    <th className="py-3 px-4 text-xs font-semibold text-secondary uppercase tracking-wider">Vulnerability</th>
                    <th className="py-3 px-4 text-xs font-semibold text-secondary uppercase tracking-wider">Asset</th>
                    <th className="py-3 px-4 text-xs font-semibold text-secondary uppercase tracking-wider">CVE</th>
                    <th className="py-3 px-4 text-xs font-semibold text-secondary uppercase tracking-wider">Port</th>
                    <th className="py-3 px-4 text-xs font-semibold text-secondary uppercase tracking-wider">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/50">
                  {vulnerabilities.map((vuln) => (
                    <tr 
                      key={vuln.id}
                      onClick={() => setSelectedId(vuln.id)}
                      className={`cursor-pointer transition-colors ${
                        selectedId === vuln.id 
                          ? 'bg-primary/10 border-l-2 border-l-primary' 
                          : 'hover:bg-surface/50'
                      }`}
                    >
                      <td className="py-3 px-4">
                        <span className={`px-2 py-1 rounded text-xs font-medium uppercase border ${getSeverityColor(vuln.scanner_severity)}`}>
                          {vuln.scanner_severity}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <div className="text-sm font-medium text-white">{vuln.title}</div>
                        {vuln.cvss_score && (
                          <div className="text-xs text-secondary mt-1">CVSS: {vuln.cvss_score.toFixed(1)}</div>
                        )}
                      </td>
                      <td className="py-3 px-4 text-sm text-secondary">
                        {vuln.asset?.asset_identifier || 'Unknown'}
                      </td>
                      <td className="py-3 px-4">
                        {vuln.cve_id ? (
                          <span className="text-sm font-mono text-blue-400">{vuln.cve_id}</span>
                        ) : (
                          <span className="text-xs text-secondary">N/A</span>
                        )}
                      </td>
                      <td className="py-3 px-4 text-sm text-secondary">
                        {vuln.port ? `${vuln.port}/${vuln.protocol || 'tcp'}` : 'N/A'}
                      </td>
                      <td className="py-3 px-4">
                        <span className={`px-2 py-1 rounded text-xs font-medium capitalize border ${getStatusColor(vuln.status)}`}>
                          {vuln.status.replace('_', ' ')}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>

        {/* Details Panel */}
        {selectedVuln && (
          <div className="w-[500px] border-l border-border bg-background overflow-auto custom-scroll shrink-0">
            <div className="p-6 space-y-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h2 className="text-lg font-semibold text-white mb-2">{selectedVuln.title}</h2>
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className={`px-2 py-1 rounded text-xs font-medium uppercase border ${getSeverityColor(selectedVuln.scanner_severity)}`}>
                      {selectedVuln.scanner_severity}
                    </span>
                    <span className={`px-2 py-1 rounded text-xs font-medium capitalize border ${getStatusColor(selectedVuln.status)}`}>
                      {selectedVuln.status.replace('_', ' ')}
                    </span>
                    {selectedVuln.cvss_score && (
                      <span className="px-2 py-1 rounded text-xs font-medium bg-surface text-white border border-border">
                        CVSS: {selectedVuln.cvss_score.toFixed(1)}
                      </span>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button 
                    onClick={() => navigate(`/reports?id=${selectedVuln.id}`)}
                    className="p-2 hover:bg-surface rounded transition-colors"
                    title="Open Full Report"
                  >
                    <span className="material-symbols-outlined text-secondary hover:text-primary">open_in_full</span>
                  </button>
                  <button 
                    onClick={() => setSelectedId(null)}
                    className="p-2 hover:bg-surface rounded transition-colors"
                  >
                    <span className="material-symbols-outlined text-secondary">close</span>
                  </button>
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <h3 className="text-sm font-semibold text-white mb-2">Asset Information</h3>
                  <div className="space-y-1 text-sm">
                    <div className="flex justify-between">
                      <span className="text-secondary">Identifier:</span>
                      <span className="text-white font-mono">{selectedVuln.asset?.asset_identifier || 'Unknown'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-secondary">Type:</span>
                      <span className="text-white capitalize">{selectedVuln.asset?.asset_type || 'Unknown'}</span>
                    </div>
                    {selectedVuln.port && (
                      <div className="flex justify-between">
                        <span className="text-secondary">Port/Protocol:</span>
                        <span className="text-white">{selectedVuln.port}/{selectedVuln.protocol || 'tcp'}</span>
                      </div>
                    )}
                  </div>
                </div>

                {selectedVuln.cve_id && (
                  <div>
                    <h3 className="text-sm font-semibold text-white mb-2">CVE Information</h3>
                    <div className="space-y-1 text-sm">
                      <div className="flex justify-between">
                        <span className="text-secondary">CVE ID:</span>
                        <a 
                          href={`https://nvd.nist.gov/vuln/detail/${selectedVuln.cve_id}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-400 hover:underline font-mono"
                        >
                          {selectedVuln.cve_id}
                        </a>
                      </div>
                      {selectedVuln.cvss_vector && (
                        <div className="flex justify-between">
                          <span className="text-secondary">CVSS Vector:</span>
                          <span className="text-white font-mono text-xs">{selectedVuln.cvss_vector}</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {selectedVuln.description && (
                  <div>
                    <h3 className="text-sm font-semibold text-white mb-2">Description</h3>
                    <p className="text-sm text-secondary leading-relaxed whitespace-pre-wrap">{selectedVuln.description.trim()}</p>
                  </div>
                )}

                {selectedVuln.remediation && (
                  <div>
                    <h3 className="text-sm font-semibold text-white mb-2">Remediation</h3>
                    <p className="text-sm text-secondary leading-relaxed whitespace-pre-wrap">{selectedVuln.remediation.trim()}</p>
                  </div>
                )}

                <div>
                  <h3 className="text-sm font-semibold text-white mb-2">Metadata</h3>
                  <div className="space-y-1 text-sm">
                    {selectedVuln.plugin_id && (
                      <div className="flex justify-between">
                        <span className="text-secondary">Plugin ID:</span>
                        <span className="text-white font-mono">{selectedVuln.plugin_id}</span>
                      </div>
                    )}
                    <div className="flex justify-between">
                      <span className="text-secondary">Discovered:</span>
                      <span className="text-white">{new Date(selectedVuln.discovered_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Vulnerabilities;
