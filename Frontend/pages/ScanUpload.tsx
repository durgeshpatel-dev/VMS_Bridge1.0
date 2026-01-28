import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiClient, Scan } from '../services/api';
import { useToast } from '../contexts/ToastContext';
import { TableSkeleton } from '../components/SkeletonLoader';

const ALLOWED_EXTENSIONS = ['.json', '.xml', '.csv', '.txt', '.sarif', '.cyclonedx'];
const MAX_FILE_SIZE_MB = 100;

const ScanUpload: React.FC = () => {
  const navigate = useNavigate();
  const [scans, setScans] = useState<Scan[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [limit] = useState(10);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { success, error } = useToast();
  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    loadScans(true); // Initial load with loading spinner
    
    // Start polling for scan status updates every 2 seconds
    pollIntervalRef.current = setInterval(() => {
      loadScans(false); // Silent background refresh
    }, 2000);
    
    // Cleanup on unmount
    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, [page]);

  const loadScans = async (showLoading = true) => {
    try {
      if (showLoading) {
        setLoading(true);
      }
      const response = await apiClient.listScans({ skip: page * limit, limit });
      setScans(response.items);
      setTotal(response.total);
    } catch (error) {
      error('Failed to load scans');
      console.error('Error loading scans:', error);
    } finally {
      if (showLoading) {
        setLoading(false);
      }
    }
  };

  const validateFile = (file: File): string | null => {
    const fileExt = '.' + file.name.split('.').pop()?.toLowerCase();
    
    if (!ALLOWED_EXTENSIONS.includes(fileExt)) {
      return `Invalid file type. Allowed: ${ALLOWED_EXTENSIONS.join(', ')}`;
    }
    
    const fileSizeMB = file.size / (1024 * 1024);
    if (fileSizeMB > MAX_FILE_SIZE_MB) {
      return `File too large (${fileSizeMB.toFixed(1)}MB). Maximum: ${MAX_FILE_SIZE_MB}MB`;
    }
    
    return null;
  };

  const handleUpload = async (file: File) => {
    const validationError = validateFile(file);
    if (validationError) {
      error(validationError);
      return;
    }

    try {
      setUploading(true);
      setUploadProgress(0);

      const scan = await apiClient.uploadScan(file, (progress) => {
        setUploadProgress(Math.round(progress));
      });

      success(`File "${file.name}" uploaded successfully`);
      setUploadProgress(0);
      
      // Reload scans list immediately
      await loadScans(false);
    } catch (err: any) {
      error(err.message || 'Upload failed');
      console.error('Upload error:', err);
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleUpload(file);
    }
    // Reset input value to allow re-uploading the same file
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const file = e.dataTransfer.files?.[0];
    if (file) {
      handleUpload(file);
    }
  };

  const handleDelete = async (scanId: string, filename: string) => {
    if (!confirm(`Delete scan "${filename}"?`)) return;

    try {
      await apiClient.deleteScan(scanId);
      success('Scan deleted successfully');
      await loadScans(false);
    } catch (err: any) {
      error(err.message || 'Failed to delete scan');
      console.error('Delete error:', err);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'processed':
      case 'completed':
        return 'bg-green-500/10 text-green-400 border-green-500/20';
      case 'running':
      case 'pending':
        return 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20';
      case 'failed':
        return 'bg-red-500/10 text-red-400 border-red-500/20';
      case 'uploaded':
        return 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20';
      default:
        return 'bg-gray-500/10 text-gray-400 border-gray-500/20';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'processed':
      case 'completed':
        return 'check_circle';
      case 'running':
        return 'sync';
      case 'pending':
        return 'schedule';
      case 'failed':
        return 'error';
      case 'uploaded':
        return 'upload_file';
      default:
        return 'help';
    }
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    });
  };
  return (
    <div className="flex flex-col h-full overflow-hidden bg-background">
      <header className="sticky top-0 z-10 bg-background/95 backdrop-blur-sm border-b border-border px-6 py-5">
        <div className="flex flex-wrap items-center justify-between gap-4 max-w-[1400px] mx-auto w-full">
          <div className="flex flex-col gap-1">
            <h2 className="text-white text-3xl font-bold leading-tight tracking-tight">Scan Upload</h2>
            <div className="flex items-center gap-2 text-secondary text-sm">
              <span className="material-symbols-outlined text-sm">upload_file</span>
              <span>Import vulnerability scan files</span>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button 
              onClick={() => loadScans(true)}
              disabled={loading}
              className="flex items-center justify-center gap-2 h-10 px-4 bg-[#283039] hover:bg-border text-white text-sm font-bold rounded-lg border border-border transition-colors disabled:opacity-50"
            >
              <span className="material-symbols-outlined text-[20px]">refresh</span>
              <span>Refresh</span>
            </button>
          </div>
        </div>
      </header>

      <div className="flex-1 px-6 py-8 pb-20 overflow-y-auto custom-scroll">
        <div className="flex flex-col gap-8 max-w-[1400px] mx-auto w-full">
          {/* Upload Area */}
          <div className="w-full">
            <label
              htmlFor="file-upload"
              className={`group relative flex flex-col items-center justify-center w-full h-64 border-2 border-dashed rounded-xl transition-all cursor-pointer ${
                dragActive
                  ? 'border-primary bg-primary/10'
                  : 'border-border hover:border-primary/50 bg-surface/50 hover:bg-[#283039]/50'
              } ${uploading ? 'pointer-events-none opacity-50' : ''}`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <div className="flex flex-col items-center justify-center pt-5 pb-6">
                {uploading ? (
                  <>
                    <div className="p-4 rounded-full bg-[#283039] mb-4">
                      <span className="material-symbols-outlined text-4xl text-primary animate-pulse">upload</span>
                    </div>
                    <p className="mb-2 text-lg text-white font-medium">Uploading... {uploadProgress}%</p>
                    <div className="w-64 h-2 bg-[#283039] rounded-full overflow-hidden">
                      <div
                        className="h-full bg-primary transition-all duration-300"
                        style={{ width: `${uploadProgress}%` }}
                      />
                    </div>
                  </>
                ) : (
                  <>
                    <div className="p-4 rounded-full bg-[#283039] group-hover:bg-border mb-4 transition-colors">
                      <span className="material-symbols-outlined text-4xl text-primary">cloud_upload</span>
                    </div>
                    <p className="mb-2 text-lg text-white font-medium">
                      <span className="font-bold">Click to upload</span> or drag and drop
                    </p>
                    <p className="text-sm text-secondary">
                      Supported formats: {ALLOWED_EXTENSIONS.join(', ')}
                    </p>
                    <p className="mt-2 text-xs text-[#586474] font-mono">
                      Max file size: {MAX_FILE_SIZE_MB}MB
                    </p>
                  </>
                )}
              </div>
              <input
                ref={fileInputRef}
                id="file-upload"
                type="file"
                className="hidden"
                accept={ALLOWED_EXTENSIONS.join(',')}
                onChange={handleFileSelect}
                disabled={uploading}
              />
            </label>
          </div>

          {/* Recent Uploads Table */}
          <div className="flex flex-col gap-4">
            <div className="flex items-center justify-between">
              <h3 className="text-white text-xl font-bold">Recent Uploads</h3>
              <span className="text-secondary text-sm">{scans.length} scans</span>
            </div>

            {loading ? (
              <div className="overflow-hidden rounded-xl border border-border bg-surface">
                <TableSkeleton rows={10} />
              </div>
            ) : scans.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-64 text-secondary">
                <span className="material-symbols-outlined text-6xl mb-4">cloud_off</span>
                <p className="text-lg">No scans uploaded yet</p>
                <p className="text-sm">Upload your first scan file to get started</p>
              </div>
            ) : (
              <div className="overflow-hidden rounded-xl border border-border bg-surface">
                <div className="overflow-x-auto">
                  <table className="w-full text-left border-collapse">
                    <thead>
                      <tr className="bg-[#283039] text-secondary text-xs font-semibold uppercase tracking-wider border-b border-border">
                        <th className="px-6 py-4">Filename</th>
                        <th className="px-6 py-4">Size</th>
                        <th className="px-6 py-4">Upload Date</th>
                        <th className="px-6 py-4">Status</th>
                        <th className="px-6 py-4 text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border">
                      {scans.map((scan) => (
                        <tr 
                          key={scan.id} 
                          onClick={() => navigate(`/vulnerabilities?scan_id=${scan.id}`)}
                          className="group hover:bg-[#283039]/50 transition-colors cursor-pointer"
                        >
                          <td className="px-6 py-4">
                            <div className="flex items-center gap-3">
                              <div className="p-2 rounded bg-[#283039] text-secondary">
                                <span className="material-symbols-outlined text-[20px]">description</span>
                              </div>
                              <div className="flex flex-col">
                                <span className="text-white font-medium text-sm">{scan.filename}</span>
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4">
                            <span className="text-secondary text-sm">{scan.file_size_mb} MB</span>
                          </td>
                          <td className="px-6 py-4 text-secondary text-sm font-mono">{formatDate(scan.uploaded_at)}</td>
                          <td className="px-6 py-4">
                            {scan.job ? (
                              <div className="flex flex-col gap-1">
                                <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold border ${getStatusColor(scan.job.status)}`}>
                                  {scan.job.status === 'running' && (
                                    <span className="relative flex h-2 w-2">
                                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                                      <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-500"></span>
                                    </span>
                                  )}
                                  {scan.job.status !== 'running' && <span className="material-symbols-outlined text-sm">{getStatusIcon(scan.job.status)}</span>}
                                  {scan.job.status.toUpperCase()}
                                </span>
                                {scan.job.status === 'running' && scan.job.progress !== null && (
                                  <div className="flex items-center gap-2">
                                    <div className="flex-1 h-1.5 bg-[#283039] rounded-full overflow-hidden">
                                      <div
                                        className="h-full bg-cyan-500 transition-all duration-300"
                                        style={{ width: `${scan.job.progress}%` }}
                                      />
                                    </div>
                                    <span className="text-xs text-cyan-400 font-mono">{scan.job.progress}%</span>
                                  </div>
                                )}
                              </div>
                            ) : (
                              <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold border ${getStatusColor(scan.status)}`}>
                                <span className="material-symbols-outlined text-sm">{getStatusIcon(scan.status)}</span>
                                {scan.status.toUpperCase()}
                              </span>
                            )}
                          </td>
                          <td className="px-6 py-4 text-right">
                            <button 
                              onClick={(e) => {
                                e.stopPropagation();
                                handleDelete(scan.id, scan.filename);
                              }}
                              className="text-secondary hover:text-red-400 p-2 rounded hover:bg-border transition-colors"
                            >
                              <span className="material-symbols-outlined text-[20px]">delete</span>
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                
                {/* Pagination Controls */}
                {total > limit && (
                  <div className="px-6 py-4 border-t border-border flex items-center justify-between bg-[#283039]/30">
                    <div className="text-sm text-secondary">
                      Showing {page * limit + 1}-{Math.min((page + 1) * limit, total)} of {total} scans
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => setPage(Math.max(0, page - 1))}
                        disabled={page === 0}
                        className="px-3 py-1.5 text-sm bg-surface border border-border rounded text-white hover:bg-border transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        Previous
                      </button>
                      <span className="px-3 py-1.5 text-sm text-white">
                        Page {page + 1} of {Math.ceil(total / limit)}
                      </span>
                      <button
                        onClick={() => setPage(Math.min(Math.ceil(total / limit) - 1, page + 1))}
                        disabled={page >= Math.ceil(total / limit) - 1}
                        className="px-3 py-1.5 text-sm bg-surface border border-border rounded text-white hover:bg-border transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        Next
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ScanUpload;