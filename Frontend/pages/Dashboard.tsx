import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { apiClient, DashboardStats, Vulnerability, Scan } from '../services/api';
import { useToast } from '../contexts/ToastContext';
import { MetricsSkeleton, ListSkeleton, TableSkeleton } from '../components/SkeletonLoader';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentVulns, setRecentVulns] = useState<Vulnerability[]>([]);
  const [recentScans, setRecentScans] = useState<Scan[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  // Memoized data loading function to prevent unnecessary API calls
  const loadDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      
      // Fetch all data in parallel to minimize wait time
      const [statsData, vulnsResponse, scansResponse] = await Promise.all([
        apiClient.getDashboardStats(),
        apiClient.listVulnerabilities({ limit: 5, skip: 0 }),
        apiClient.listScans({ limit: 5, skip: 0 })
      ]);
      
      setStats(statsData);
      setRecentVulns(vulnsResponse.items);
      setRecentScans(scansResponse.items);
      setLastUpdate(new Date());
    } catch (error: any) {
      showToast(error.message || 'Failed to load dashboard data', 'error');
    } finally {
      setLoading(false);
    }
  }, []); // Empty dependency array - function never changes

  // Load data once on mount
  useEffect(() => {
    loadDashboardData();
  }, [loadDashboardData]);

  // Memoize time formatting to avoid recalculating on every render
  const formatTimeAgo = useMemo(() => (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min${diffMins > 1 ? 's' : ''} ago`;
    
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
  }, []);

  const getSeverityColor = useCallback((severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-500/10 text-red-500 border-red-500/20';
      case 'high': return 'bg-orange-500/10 text-orange-500 border-orange-500/20';
      case 'medium': return 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20';
      case 'low': return 'bg-blue-500/10 text-blue-500 border-blue-500/20';
      default: return 'bg-gray-500/10 text-gray-500 border-gray-500/20';
    }
  }, []);

  const getSeverityDot = useCallback((severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-500 animate-pulse';
      case 'high': return 'bg-orange-500';
      case 'medium': return 'bg-yellow-500';
      case 'low': return 'bg-blue-500';
      default: return 'bg-gray-500';
    }
  }, []);

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-background/95 backdrop-blur-sm border-b border-border px-6 py-5">
        <div className="flex flex-wrap items-center justify-between gap-4 max-w-[1600px] mx-auto w-full">
          <div className="flex flex-col gap-1">
            <h2 className="text-white text-3xl font-bold leading-tight tracking-tight">Security Overview</h2>
            <div className="flex items-center gap-2 text-secondary text-sm">
              <span className="material-symbols-outlined text-sm">calendar_today</span>
              <span>Last updated: {formatTimeAgo(lastUpdate.toISOString())}</span>
              <span className="mx-1">•</span>
              <span>Organization: Default</span>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button 
              onClick={loadDashboardData}
              disabled={loading}
              className="flex items-center justify-center gap-2 h-10 px-4 bg-surface hover:bg-border text-white text-sm font-bold rounded-lg border border-border transition-colors disabled:opacity-50"
            >
              <span className={`material-symbols-outlined text-[20px] ${loading ? 'animate-spin' : ''}`}>refresh</span>
              <span>Refresh</span>
            </button>
            <button 
              onClick={() => navigate('/scans')}
              className="flex items-center justify-center gap-2 h-10 px-4 bg-primary hover:bg-blue-600 text-white text-sm font-bold rounded-lg shadow-lg shadow-primary/20 transition-colors"
            >
              <span className="material-symbols-outlined text-[20px]">upload_file</span>
              <span>Upload Scan</span>
            </button>
          </div>
        </div>
      </header>

      {/* Content */}
      <div className="flex-1 overflow-y-auto px-6 py-6 pb-20 custom-scroll">
        <div className="flex flex-col gap-6 max-w-[1600px] mx-auto w-full">
          
          {/* Metrics */}
          {loading ? (
            <MetricsSkeleton />
          ) : stats && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Metric 1 - Total Assets */}
              <div className="flex flex-col gap-2 rounded-xl p-5 border border-border bg-surface shadow-sm">
                <div className="flex justify-between items-start">
                  <p className="text-secondary text-sm font-medium uppercase tracking-wider">Total Assets</p>
                  <span className="material-symbols-outlined text-secondary">dns</span>
                </div>
                <div className="flex items-end gap-3 mt-1">
                  <p className="text-white text-3xl font-bold leading-none">{stats.total_assets}</p>
                </div>
              </div>

              {/* Metric 2 - Critical Vulns */}
              <div className="flex flex-col gap-2 rounded-xl p-5 border border-red-900/30 bg-surface shadow-sm relative overflow-hidden">
                <div className="absolute right-0 top-0 p-2 opacity-5">
                  <span className="material-symbols-outlined text-9xl text-danger">warning</span>
                </div>
                <div className="flex justify-between items-start relative z-10">
                  <p className="text-secondary text-sm font-medium uppercase tracking-wider">Critical</p>
                  <span className="material-symbols-outlined text-danger">gpp_maybe</span>
                </div>
                <div className="flex items-end gap-3 mt-1 relative z-10">
                  <p className="text-white text-3xl font-bold leading-none">{stats.critical}</p>
                </div>
              </div>

              {/* Metric 3 - High Vulns */}
              <div className="flex flex-col gap-2 rounded-xl p-5 border border-orange-900/30 bg-surface shadow-sm">
                <div className="flex justify-between items-start">
                  <p className="text-secondary text-sm font-medium uppercase tracking-wider">High</p>
                  <span className="material-symbols-outlined text-orange-400">priority_high</span>
                </div>
                <div className="flex items-end gap-3 mt-1">
                  <p className="text-white text-3xl font-bold leading-none">{stats.high}</p>
                </div>
              </div>

              {/* Metric 4 - Medium Vulns */}
              <div className="flex flex-col gap-2 rounded-xl p-5 border border-yellow-900/30 bg-surface shadow-sm">
                <div className="flex justify-between items-start">
                  <p className="text-secondary text-sm font-medium uppercase tracking-wider">Medium</p>
                  <span className="material-symbols-outlined text-yellow-400">error</span>
                </div>
                <div className="flex items-end gap-3 mt-1">
                  <p className="text-white text-3xl font-bold leading-none">{stats.medium}</p>
                </div>
              </div>

              {/* Metric 5 - Total Vulnerabilities */}
              <div className="flex flex-col gap-2 rounded-xl p-5 border border-primary/30 bg-surface shadow-sm col-span-1 sm:col-span-2">
                <div className="flex justify-between items-start">
                  <p className="text-secondary text-sm font-medium uppercase tracking-wider">Total Open Vulnerabilities</p>
                  <span className="material-symbols-outlined text-primary">bug_report</span>
                </div>
                <div className="flex items-end gap-3 mt-1">
                  <p className="text-white text-3xl font-bold leading-none">{stats.total_vulnerabilities}</p>
                  <div className="flex items-center gap-4 text-xs text-secondary mb-1">
                    <span>Low: {stats.low}</span>
                    <span>Info: {stats.info}</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Chart & Activity Feed */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 flex flex-col rounded-xl border border-border bg-surface p-6 h-[400px]">
              <div className="flex justify-between items-start gap-4 mb-6">
                <div>
                  <h3 className="text-white text-lg font-bold">Vulnerability Trends</h3>
                  <p className="text-secondary text-sm mt-1">Coming Soon - ML-Powered Analytics</p>
                </div>
              </div>
              <div className="flex-1 flex items-center justify-center">
                <div className="text-center">
                  <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-purple-900/20 text-purple-400 border border-purple-800 mb-4">
                    <span className="material-symbols-outlined text-4xl">insights</span>
                  </div>
                  <h4 className="text-white text-lg font-semibold mb-2">AI-Powered Trend Analysis</h4>
                  <p className="text-secondary text-sm max-w-md">
                    Historical vulnerability trends, remediation patterns, and predictive insights will be available soon with our ML integration.
                  </p>
                </div>
              </div>
            </div>

            {/* Activity Feed - Recent Scans */}
            <div className="flex flex-col rounded-xl border border-border bg-surface overflow-hidden h-[400px] shadow-lg hover:shadow-xl transition-shadow duration-300">
              <div className="p-5 border-b border-border flex justify-between items-center bg-gradient-to-r from-surface to-[#283039]/30">
                <div className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-primary text-lg">scan</span>
                  <h3 className="text-white text-lg font-bold">Recent Scans</h3>
                  {!loading && recentScans.length > 0 && (
                    <span className="ml-1 px-2 py-0.5 rounded-full text-xs font-semibold bg-primary/20 text-primary border border-primary/30">
                      {recentScans.length}
                    </span>
                  )}
                </div>
                <button 
                  onClick={() => navigate('/scans')}
                  className="flex items-center gap-1 text-primary text-sm font-medium hover:text-blue-400 transition-colors group"
                >
                  <span>View All</span>
                  <span className="material-symbols-outlined text-sm group-hover:translate-x-0.5 transition-transform">arrow_forward</span>
                </button>
              </div>
              <div className="flex-1 overflow-y-auto" style={{ 
                scrollbarWidth: 'thin',
                scrollbarColor: '#1169d4 #1a1d23'
              }}>
                {loading ? (
                  <ListSkeleton items={5} />
                ) : recentScans.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-full text-secondary text-sm gap-3 p-6">
                    <div className="w-16 h-16 rounded-full bg-surface border border-border flex items-center justify-center">
                      <span className="material-symbols-outlined text-4xl opacity-50">cloud_off</span>
                    </div>
                    <div className="text-center">
                      <p className="font-medium text-white mb-1">No scans yet</p>
                      <p className="text-xs">Upload your first scan to get started</p>
                    </div>
                    <button
                      onClick={() => navigate('/scan-upload')}
                      className="mt-2 px-4 py-2 bg-primary hover:bg-blue-600 text-white text-sm font-medium rounded-lg transition-colors"
                    >
                      Upload Scan
                    </button>
                  </div>
                ) : (
                  <div className="divide-y divide-border/30">
                    {recentScans.map((scan, index) => (
                      <div 
                        key={scan.id}
                        onClick={() => navigate(`/vulnerabilities?scan_id=${scan.id}`)}
                        className="relative flex gap-4 p-4 hover:bg-gradient-to-r hover:from-[#283039]/30 hover:to-transparent transition-all duration-150 group cursor-pointer"
                        style={{ 
                          animation: `slideIn 0.3s ease-out ${index * 0.1}s backwards`
                        }}
                      >
                        {/* Left border accent on hover */}
                        <div className="absolute left-0 top-0 bottom-0 w-1 bg-primary scale-y-0 group-hover:scale-y-100 transition-transform duration-150 origin-top rounded-r"></div>
                        
                        {/* Status Icon */}
                        <div className="relative mt-1 flex-shrink-0">
                          <div className={`size-10 rounded-xl flex items-center justify-center border-2 transition-all duration-150 group-hover:scale-105 ${
                            scan.status === 'completed' 
                              ? 'bg-gradient-to-br from-green-500/20 to-green-600/10 text-green-400 border-green-500/40'
                              : scan.status === 'failed'
                              ? 'bg-gradient-to-br from-red-500/20 to-red-600/10 text-red-400 border-red-500/40'
                              : scan.status === 'running'
                              ? 'bg-gradient-to-br from-blue-500/20 to-blue-600/10 text-primary border-blue-500/40'
                              : 'bg-gradient-to-br from-yellow-500/20 to-yellow-600/10 text-yellow-400 border-yellow-500/40'
                          }`}>
                            <span className={`material-symbols-outlined text-lg ${
                              scan.status === 'running' ? 'animate-spin' : ''
                            }`}>
                              scan
                            </span>
                          </div>
                          {/* Pulse effect for running scans */}
                          {scan.status === 'running' && (
                            <div className="absolute inset-0 rounded-xl bg-blue-500/20 animate-ping"></div>
                          )}
                        </div>
                        
                        {/* Content */}
                        <div className="flex flex-col gap-1.5 flex-1 min-w-0">
                          <div className="flex items-start justify-between gap-2">
                            <p className="text-white text-sm font-semibold truncate group-hover:text-primary transition-colors">
                              {scan.filename}
                            </p>
                            <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-all duration-150">
                              <button 
                                onClick={(e) => {
                                  e.stopPropagation();
                                  navigate(`/reports?scanId=${scan.id}`);
                                }}
                                className="text-secondary hover:text-primary p-1 rounded hover:bg-border transition-colors"
                                title="View Report"
                              >
                                <span className="material-symbols-outlined text-sm">description</span>
                              </button>
                              <span className="material-symbols-outlined text-secondary text-sm group-hover:translate-x-0.5">
                                arrow_forward
                              </span>
                            </div>
                          </div>
                          
                          {/* Status Badge */}
                          <div className="flex items-center gap-2">
                            <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-medium capitalize ${
                              scan.status === 'completed'
                                ? 'bg-green-500/10 text-green-400 border border-green-500/30'
                                : scan.status === 'failed'
                                ? 'bg-red-500/10 text-red-400 border border-red-500/30'
                                : scan.status === 'running'
                                ? 'bg-blue-500/10 text-primary border border-blue-500/30'
                                : 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/30'
                            }`}>
                              <span className={`w-1 h-1 rounded-full ${
                                scan.status === 'completed' ? 'bg-green-400' :
                                scan.status === 'failed' ? 'bg-red-400' :
                                scan.status === 'running' ? 'bg-blue-400 animate-pulse' :
                                'bg-yellow-400'
                              }`}></span>
                              {scan.status.replace('_', ' ')}
                            </span>
                            
                            {/* File size */}
                            <span className="text-xs text-secondary/70 font-mono">
                              {scan.file_size_mb} MB
                            </span>
                          </div>
                          
                          {/* Timestamp */}
                          <div className="flex items-center gap-1.5 text-[#586474] text-[11px] font-mono">
                            <span className="material-symbols-outlined text-xs">schedule</span>
                            <span>{formatTimeAgo(scan.uploaded_at)}</span>
                          </div>
                          
                          {/* Progress bar for running scans */}
                          {scan.status === 'running' && scan.job?.progress !== undefined && (
                            <div className="mt-1 flex items-center gap-2">
                              <div className="flex-1 h-1 bg-[#283039] rounded-full overflow-hidden">
                                <div
                                  className="h-full bg-gradient-to-r from-primary to-blue-400 transition-all duration-300 rounded-full"
                                  style={{ width: `${scan.job.progress}%` }}
                                />
                              </div>
                              <span className="text-xs text-primary font-semibold tabular-nums">
                                {scan.job.progress}%
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              
              {/* Scroll indicator */}
              {!loading && recentScans.length > 3 && (
                <div className="absolute bottom-0 left-0 right-0 h-8 bg-gradient-to-t from-surface to-transparent pointer-events-none"></div>
              )}
            </div>
          </div>

          {/* Table */}
          <div className="flex flex-col gap-4">
             <h3 className="text-white text-2xl font-bold leading-tight">Latest Findings</h3>
             <div className="overflow-hidden rounded-xl border border-border bg-surface">
                <div className="overflow-x-auto">
                   <table className="w-full text-left border-collapse">
                      <thead>
                         <tr className="bg-[#283039] text-secondary text-xs font-semibold uppercase tracking-wider border-b border-border">
                            <th className="px-6 py-4">Severity</th>
                            <th className="px-6 py-4">Vulnerability Name</th>
                            <th className="px-6 py-4">Asset</th>
                            <th className="px-6 py-4">Discovery Time</th>
                            <th className="px-6 py-4">AI Score</th>
                         </tr>
                      </thead>
                      <tbody className="divide-y divide-border">
                         {loading ? (
                            <tr>
                               <td colSpan={5} className="p-0">
                                  <TableSkeleton rows={5} />
                               </td>
                            </tr>
                         ) : recentVulns.length === 0 ? (
                            <tr>
                               <td colSpan={5} className="px-6 py-12 text-center">
                                  <div className="flex flex-col items-center gap-2 text-secondary">
                                     <span className="material-symbols-outlined text-4xl opacity-50">security</span>
                                     <span>No vulnerabilities found - Great job!</span>
                                  </div>
                               </td>
                            </tr>
                         ) : (
                            recentVulns.map((vuln) => (
                               <tr 
                                  key={vuln.id} 
                                  onClick={() => navigate(`/reports?id=${vuln.id}`)}
                                  className="group hover:bg-[#283039]/50 transition-colors cursor-pointer"
                               >
                                  <td className="px-6 py-4 whitespace-nowrap">
                                     <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold border uppercase ${getSeverityColor(vuln.scanner_severity)}`}>
                                        <span className={`w-1.5 h-1.5 rounded-full ${getSeverityDot(vuln.scanner_severity)}`}></span>
                                        {vuln.scanner_severity}
                                     </span>
                                  </td>
                                  <td className="px-6 py-4">
                                     <div className="flex flex-col">
                                        <span className="text-white font-medium text-sm">{vuln.title}</span>
                                        {vuln.cve_id && (
                                           <span className="text-[#586474] text-xs font-mono">{vuln.cve_id}</span>
                                        )}
                                     </div>
                                  </td>
                                  <td className="px-6 py-4 text-secondary text-sm">
                                     {vuln.asset?.asset_identifier || 'Unknown'}
                                  </td>
                                  <td className="px-6 py-4 text-secondary text-sm">
                                     {formatTimeAgo(vuln.discovered_at)}
                                  </td>
                                  <td className="px-6 py-4">
                                     <div className="flex items-center gap-2">
                                        <div className="px-2.5 py-1 rounded-full text-xs font-medium bg-purple-900/20 text-purple-400 border border-purple-800">
                                           Coming Soon
                                        </div>
                                     </div>
                                  </td>
                               </tr>
                            ))
                         )}
                      </tbody>
                   </table>
                </div>
             </div>
          </div>

        </div>
      </div>
      
      {/* Custom styles for animations and scrollbar */}
      <style>{`
        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateX(-10px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }
        
        /* Custom scrollbar styles */
        *::-webkit-scrollbar {
          width: 6px;
          height: 6px;
        }
        
        *::-webkit-scrollbar-track {
          background: #1a1d23;
          border-radius: 3px;
        }
        
        *::-webkit-scrollbar-thumb {
          background: #1169d4;
          border-radius: 3px;
        }
        
        *::-webkit-scrollbar-thumb:hover {
          background: #0d5cb8;
        }
      `}</style>
    </div>
  );
};

export default Dashboard;