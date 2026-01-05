import React from 'react';
import { UploadedScan } from '../types';

const recentUploads: UploadedScan[] = [
  { id: '1', filename: 'Scan_Production_Cluster_A.xml', team: 'SEC', size: '142 MB', date: 'Oct 24, 2023 10:42 AM', status: 'RUNNING' },
  { id: '2', filename: 'Q3_Audit_IT_Infra.xml', team: 'IT', size: '84 MB', date: 'Oct 23, 2023 04:15 PM', status: 'PROCESSED' },
  { id: '3', filename: 'Prod_Payment_Gateway_v2.xml', team: 'PROD', size: '210 MB', date: 'Oct 22, 2023 09:00 AM', status: 'PROCESSED' },
  { id: '4', filename: 'Legacy_Systems_Check.xml', team: 'IT', size: '5 MB', date: 'Oct 20, 2023 11:30 AM', status: 'FAILED' },
];

const ScanUpload: React.FC = () => {
  return (
    <div className="flex flex-col h-full overflow-hidden bg-background">
      <header className="sticky top-0 z-10 bg-background/95 backdrop-blur-sm border-b border-border px-6 py-5">
        <div className="flex flex-wrap items-center justify-between gap-4 max-w-[1400px] mx-auto w-full">
          <div className="flex flex-col gap-1">
            <h2 className="text-white text-3xl font-bold leading-tight tracking-tight">Scan Upload</h2>
            <div className="flex items-center gap-2 text-secondary text-sm">
              <span className="material-symbols-outlined text-sm">upload_file</span>
              <span>Import external vulnerability data</span>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button className="flex items-center justify-center gap-2 h-10 px-4 bg-[#283039] hover:bg-border text-white text-sm font-bold rounded-lg border border-border transition-colors">
              <span className="material-symbols-outlined text-[20px]">help</span>
              <span>Documentation</span>
            </button>
          </div>
        </div>
      </header>

      <div className="flex-1 px-6 py-8 pb-20 overflow-y-auto custom-scroll">
        <div className="flex flex-col gap-8 max-w-[1400px] mx-auto w-full">
          {/* Upload Area */}
          <div className="w-full">
            <label htmlFor="file-upload" className="group relative flex flex-col items-center justify-center w-full h-64 border-2 border-dashed border-border hover:border-primary/50 rounded-xl bg-surface/50 hover:bg-[#283039]/50 transition-all cursor-pointer">
              <div className="flex flex-col items-center justify-center pt-5 pb-6">
                <div className="p-4 rounded-full bg-[#283039] group-hover:bg-border mb-4 transition-colors">
                  <span className="material-symbols-outlined text-4xl text-primary">cloud_upload</span>
                </div>
                <p className="mb-2 text-lg text-white font-medium"><span className="font-bold">Click to upload</span> or drag and drop</p>
                <p className="text-sm text-secondary">Upload a Nessus XML file</p>
                <p className="mt-2 text-xs text-[#586474] font-mono">Max file size: 500MB</p>
              </div>
              <input id="file-upload" type="file" className="hidden" accept=".xml" />
            </label>
          </div>

          {/* Recent Uploads Table */}
          <div className="flex flex-col gap-4">
            <h3 className="text-white text-xl font-bold leading-tight">Recent Uploads</h3>
            <div className="overflow-hidden rounded-xl border border-border bg-surface">
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-[#283039] text-secondary text-xs font-semibold uppercase tracking-wider border-b border-border">
                      <th className="px-6 py-4">Filename</th>
                      <th className="px-6 py-4">Team</th>
                      <th className="px-6 py-4">Upload Date</th>
                      <th className="px-6 py-4">Status</th>
                      <th className="px-6 py-4 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {recentUploads.map((file) => (
                      <tr key={file.id} className="group hover:bg-[#283039]/50 transition-colors">
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-3">
                            <div className="p-2 rounded bg-[#283039] text-secondary">
                              <span className="material-symbols-outlined text-[20px]">description</span>
                            </div>
                            <div className="flex flex-col">
                              <span className="text-white font-medium text-sm">{file.filename}</span>
                              <span className="text-[#586474] text-xs">{file.size}</span>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border
                             ${file.team === 'SEC' ? 'bg-purple-500/10 text-purple-400 border-purple-500/20' : 
                               file.team === 'IT' ? 'bg-blue-500/10 text-blue-400 border-blue-500/20' : 
                               'bg-orange-500/10 text-orange-400 border-orange-500/20'
                             }`}>
                             {file.team}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-secondary text-sm font-mono">{file.date}</td>
                        <td className="px-6 py-4">
                          <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold border 
                             ${file.status === 'RUNNING' ? 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20' : 
                               file.status === 'PROCESSED' ? 'bg-green-500/10 text-green-400 border-green-500/20' : 
                               'bg-red-500/10 text-red-400 border-red-500/20'}`}>
                             {file.status === 'RUNNING' && (
                               <span className="relative flex h-2 w-2">
                                 <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                                 <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-500"></span>
                               </span>
                             )}
                             {file.status !== 'RUNNING' && <span className={`w-1.5 h-1.5 rounded-full ${file.status === 'PROCESSED' ? 'bg-green-500' : 'bg-red-500'}`}></span>}
                             {file.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-right">
                          <button className="text-secondary hover:text-white p-2 rounded hover:bg-border transition-colors">
                            <span className="material-symbols-outlined text-[20px]">
                              {file.status === 'RUNNING' ? 'cancel' : file.status === 'FAILED' ? 'refresh' : 'visibility'}
                            </span>
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
    </div>
  );
};

export default ScanUpload;