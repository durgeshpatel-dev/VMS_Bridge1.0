import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Severity } from '../types';
import { VulnList } from '../data';

const Vulnerabilities: React.FC = () => {
  const navigate = useNavigate();
  const [selectedId, setSelectedId] = useState<string | null>('1');

  const selectedVuln = VulnList.find(v => v.id === selectedId);

  return (
    <div className="flex flex-col h-full overflow-hidden bg-background">
      {/* Header */}
      <div className="h-14 flex items-center justify-between px-6 border-b border-border bg-background shrink-0">
        <div className="flex items-center gap-2 text-sm">
          <span className="text-secondary">Scans</span>
          <span className="material-symbols-outlined text-secondary text-xs">chevron_right</span>
          <span className="font-semibold text-white">Production-Full-Scan-2023-10-27</span>
          <span className="ml-2 px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-900/30 text-emerald-400 border border-emerald-800">Completed</span>
        </div>
        <div className="flex items-center gap-3">
          <button className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-white bg-primary rounded hover:bg-blue-600 transition-colors shadow-sm">
            <span className="material-symbols-outlined text-sm">play_arrow</span>
            Re-scan
          </button>
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        {/* Main List */}
        <div className="flex-1 flex flex-col min-w-0 bg-background">
           <div className="p-4 flex items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <button className="px-3 py-1.5 text-xs font-medium rounded-full bg-surface text-secondary hover:text-white hover:bg-border transition-colors">All (420)</button>
              <button className="px-3 py-1.5 text-xs font-medium rounded-full bg-red-900/20 text-red-400 border border-transparent hover:border-red-800 transition-colors">Critical (12)</button>
              <button className="px-3 py-1.5 text-xs font-medium rounded-full bg-orange-900/20 text-orange-400 border border-transparent hover:border-orange-800 transition-colors">High (45)</button>
            </div>
            <div className="flex items-center gap-2 text-secondary">
               <span className="material-symbols-outlined p-1 hover:bg-surface rounded cursor-pointer">filter_list</span>
               <span className="material-symbols-outlined p-1 hover:bg-surface rounded cursor-pointer">sort</span>
            </div>
           </div>

           <div className="flex-1 overflow-auto px-4 pb-4 custom-scroll">
              <table className="w-full text-left border-collapse">
                 <thead className="bg-surface/50 sticky top-0 z-10 backdrop-blur-sm">
                    <tr>
                       <th className="py-3 px-4 text-xs font-semibold text-secondary uppercase tracking-wider rounded-tl-lg rounded-bl-lg">Severity</th>
                       <th className="py-3 px-4 text-xs font-semibold text-secondary uppercase tracking-wider">Vulnerability</th>
                       <th className="py-3 px-4 text-xs font-semibold text-secondary uppercase tracking-wider">Asset</th>
                       <th className="py-3 px-4 text-xs font-semibold text-secondary uppercase tracking-wider">Discovered</th>
                       <th className="py-3 px-4 text-xs font-semibold text-secondary uppercase tracking-wider rounded-tr-lg rounded-br-lg text-right">Action</th>
                    </tr>
                 </thead>
                 <tbody className="divide-y divide-border text-sm">
                    {VulnList.map(v => (
                      <tr 
                        key={v.id} 
                        onClick={() => setSelectedId(v.id)}
                        className={`group cursor-pointer transition-colors border-l-4 ${selectedId === v.id ? 'bg-blue-900/10 border-primary' : 'hover:bg-surface/50 border-transparent'}`}
                      >
                         <td className="py-4 px-4 whitespace-nowrap">
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded text-xs font-medium 
                               ${v.severity === Severity.CRITICAL ? 'bg-red-900/50 text-red-300' : 
                                 v.severity === Severity.HIGH ? 'bg-orange-900/50 text-orange-300' :
                                 v.severity === Severity.MEDIUM ? 'bg-yellow-900/50 text-yellow-300' :
                                 'bg-slate-700 text-slate-300'}`}>
                               {v.severity}
                            </span>
                         </td>
                         <td className="py-4 px-4">
                            <div className="font-medium text-white group-hover:text-primary transition-colors">{v.name}</div>
                            <div className="text-xs text-secondary mt-0.5">{v.cve}</div>
                         </td>
                         <td className="py-4 px-4 text-slate-300">{v.asset}</td>
                         <td className="py-4 px-4 text-secondary whitespace-nowrap">{v.discoveredAt}</td>
                         <td className="py-4 px-4 text-right">
                            <button className="text-xs font-medium text-primary hover:text-blue-400">View</button>
                         </td>
                      </tr>
                    ))}
                 </tbody>
              </table>
           </div>
        </div>

        {/* Detail Panel */}
        <aside className={`w-[450px] flex flex-col border-l border-border bg-surface shadow-xl z-10 transition-all duration-300 transform ${selectedId ? 'translate-x-0' : 'translate-x-full'}`}>
           {selectedId && selectedVuln && (
             <>
               <div className="h-14 flex items-center justify-between px-6 border-b border-border shrink-0">
                  <h3 className="font-semibold text-white flex items-center gap-2">
                     <span className="material-symbols-outlined text-primary text-lg">manage_search</span>
                     Finding Details
                  </h3>
                  <div className="flex items-center gap-2">
                     <button 
                        onClick={() => navigate(`/reports?id=${selectedId}`)}
                        className="p-1.5 text-secondary hover:text-white hover:bg-slate-700 rounded transition-colors"
                        title="Open Full Report"
                     >
                        <span className="material-symbols-outlined text-lg">open_in_full</span>
                     </button>
                     <button onClick={() => setSelectedId(null)} className="p-1.5 text-secondary hover:text-white hover:bg-slate-700 rounded transition-colors">
                        <span className="material-symbols-outlined text-lg">close</span>
                     </button>
                  </div>
               </div>
               
               <div className="flex-1 overflow-y-auto p-6 space-y-6 custom-scroll">
                  <div>
                     <div className="flex items-start justify-between">
                        <h2 className="text-xl font-bold text-white leading-snug">{selectedVuln.name}</h2>
                        <span className="material-symbols-outlined text-secondary text-sm cursor-pointer hover:text-primary">link</span>
                     </div>
                     <p className="text-xs font-mono text-secondary mt-1">{selectedVuln.cve} • Detected in <span className="text-primary cursor-pointer hover:underline">{selectedVuln.asset}</span></p>
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                     <div className="bg-red-900/10 border border-red-900/30 rounded p-3 flex flex-col items-start">
                        <span className="text-[10px] uppercase font-bold tracking-wider text-red-400/70 mb-1">Scanner Severity</span>
                        <div className="flex items-center gap-1.5">
                           <span className="w-2 h-2 rounded-full bg-red-500"></span>
                           <span className="font-bold text-red-400">{selectedVuln.severity}</span>
                        </div>
                     </div>
                     <div className="bg-purple-900/10 border border-purple-900/30 rounded p-3 flex flex-col items-start relative overflow-hidden">
                        <div className="absolute -right-2 -top-2 opacity-10">
                           <span className="material-symbols-outlined text-5xl text-purple-600">psychology</span>
                        </div>
                        <span className="text-[10px] uppercase font-bold tracking-wider text-purple-400/70 mb-1 flex items-center gap-1">
                           ML Predicted Risk
                           <span className="material-symbols-outlined text-[10px]">auto_awesome</span>
                        </span>
                        <div className="flex items-center gap-1.5">
                           <span className="w-2 h-2 rounded-full bg-purple-500 animate-pulse"></span>
                           <span className="font-bold text-purple-300">Extreme</span>
                        </div>
                     </div>
                  </div>

                  <div className="text-sm text-slate-300 leading-relaxed">
                     {selectedVuln.description}
                  </div>

                  {/* AI Remediation */}
                  <div className="rounded border border-indigo-900/40 bg-surface overflow-hidden">
                     <div className="px-4 py-2 border-b border-indigo-900/40 bg-surface flex items-center justify-between">
                        <span className="text-xs font-bold text-indigo-300 flex items-center gap-1.5">
                           <span className="material-symbols-outlined text-sm">smart_toy</span>
                           ML Remediation Hint
                        </span>
                        <span className="text-[10px] text-secondary">Confidence: 98%</span>
                     </div>
                     <div className="p-4">
                        <p className="text-xs text-secondary mb-3">Suggested Remediation:</p>
                        <div className="relative group">
                           <pre className="bg-background text-slate-300 text-xs p-3 rounded font-mono overflow-x-auto border border-border whitespace-pre-wrap">{selectedVuln.remediation}</pre>
                           <button className="absolute top-2 right-2 p-1 bg-slate-700 text-slate-300 rounded hover:bg-slate-600 opacity-0 group-hover:opacity-100 transition-opacity" title="Copy">
                              <span className="material-symbols-outlined text-xs">content_copy</span>
                           </button>
                        </div>
                        <div className="mt-3 flex items-start gap-2 text-[10px] text-secondary italic">
                           <span className="material-symbols-outlined text-xs text-yellow-500">lightbulb</span>
                           This suggestion is AI-generated based on the codebase context. Verify before applying.
                        </div>
                     </div>
                  </div>

                  {/* Jira Card */}
                  {selectedVuln.jiraKey && (
                     <div className="border border-border rounded bg-surface p-4">
                        <div className="flex items-center justify-between mb-3">
                           <div className="flex items-center gap-2">
                              <div className="w-5 h-5 bg-[#0052CC] rounded flex items-center justify-center text-xs font-bold text-white">J</div>
                              <span className="text-sm font-semibold text-slate-200">Jira Ticket</span>
                           </div>
                           <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-900/30 text-blue-300 uppercase">In Progress</span>
                        </div>
                        <div className="flex items-center justify-between">
                           <div className="flex flex-col">
                              <span className="text-xs text-secondary">Key</span>
                              <span className="text-sm font-mono text-slate-200">{selectedVuln.jiraKey}</span>
                           </div>
                           <button className="flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-slate-300 hover:text-primary bg-slate-700 hover:bg-slate-600 rounded transition-colors">
                              Open in Jira
                              <span className="material-symbols-outlined text-xs">open_in_new</span>
                           </button>
                        </div>
                     </div>
                  )}
               </div>
               <div className="p-4 border-t border-border bg-slate-900/50 flex gap-3">
                   <button className="flex-1 py-2 text-sm font-medium text-slate-200 bg-surface border border-border rounded shadow-sm hover:bg-slate-700 transition-colors">Ignore</button>
                   <button className="flex-1 py-2 text-sm font-medium text-white bg-primary rounded shadow-sm hover:bg-blue-600 transition-colors">Fix Now</button>
               </div>
             </>
           )}
        </aside>
      </div>
    </div>
  );
};

export default Vulnerabilities;