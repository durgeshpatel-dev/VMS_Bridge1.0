import React from 'react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { Severity } from '../types';

const data = [
  { name: 'Week 1', new: 20, fixed: 15 },
  { name: 'Week 2', new: 35, fixed: 25 },
  { name: 'Week 3', new: 50, fixed: 30 },
  { name: 'Week 4', new: 45, fixed: 55 },
  { name: 'Week 5', new: 60, fixed: 70 },
  { name: 'Week 6', new: 30, fixed: 40 },
];

const Dashboard: React.FC = () => {
  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-background/95 backdrop-blur-sm border-b border-border px-6 py-5">
        <div className="flex flex-wrap items-center justify-between gap-4 max-w-[1600px] mx-auto w-full">
          <div className="flex flex-col gap-1">
            <h2 className="text-white text-3xl font-bold leading-tight tracking-tight">Security Overview</h2>
            <div className="flex items-center gap-2 text-secondary text-sm">
              <span className="material-symbols-outlined text-sm">calendar_today</span>
              <span>Last updated: Just now</span>
              <span className="mx-1">•</span>
              <span>Organization: Default</span>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button className="flex items-center justify-center gap-2 h-10 px-4 bg-surface hover:bg-border text-white text-sm font-bold rounded-lg border border-border transition-colors">
              <span className="material-symbols-outlined text-[20px]">ios_share</span>
              <span>Export Report</span>
            </button>
            <button className="flex items-center justify-center gap-2 h-10 px-4 bg-primary hover:bg-blue-600 text-white text-sm font-bold rounded-lg shadow-lg shadow-primary/20 transition-colors">
              <span className="material-symbols-outlined text-[20px]">play_arrow</span>
              <span>Run Scan</span>
            </button>
          </div>
        </div>
      </header>

      {/* Content */}
      <div className="flex-1 overflow-y-auto px-6 py-6 pb-20 custom-scroll">
        <div className="flex flex-col gap-6 max-w-[1600px] mx-auto w-full">
          
          {/* Metrics */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Metric 1 */}
            <div className="flex flex-col gap-2 rounded-xl p-5 border border-border bg-surface shadow-sm">
              <div className="flex justify-between items-start">
                <p className="text-secondary text-sm font-medium uppercase tracking-wider">Total Assets</p>
                <span className="material-symbols-outlined text-secondary">dns</span>
              </div>
              <div className="flex items-end gap-3 mt-1">
                <p className="text-white text-3xl font-bold leading-none">1,240</p>
                <div className="flex items-center text-success bg-success/10 px-1.5 py-0.5 rounded text-xs font-bold mb-1">
                  <span className="material-symbols-outlined text-xs mr-0.5">trending_up</span>
                  12%
                </div>
              </div>
            </div>

            {/* Metric 2 - Critical */}
            <div className="flex flex-col gap-2 rounded-xl p-5 border border-red-900/30 bg-surface shadow-sm relative overflow-hidden">
               <div className="absolute right-0 top-0 p-2 opacity-5">
                  <span className="material-symbols-outlined text-9xl text-danger">warning</span>
               </div>
              <div className="flex justify-between items-start relative z-10">
                <p className="text-secondary text-sm font-medium uppercase tracking-wider">Critical Vulns</p>
                <span className="material-symbols-outlined text-danger">gpp_maybe</span>
              </div>
              <div className="flex items-end gap-3 mt-1 relative z-10">
                <p className="text-white text-3xl font-bold leading-none">42</p>
                <div className="flex items-center text-red-400 bg-red-500/10 px-1.5 py-0.5 rounded text-xs font-bold mb-1">
                  <span className="material-symbols-outlined text-xs mr-0.5">trending_up</span>
                  5%
                </div>
              </div>
            </div>

            {/* Metric 3 */}
            <div className="flex flex-col gap-2 rounded-xl p-5 border border-border bg-surface shadow-sm">
              <div className="flex justify-between items-start">
                <p className="text-secondary text-sm font-medium uppercase tracking-wider">Jira Tickets</p>
                <span className="material-symbols-outlined text-secondary">confirmation_number</span>
              </div>
              <div className="flex items-end gap-3 mt-1">
                <p className="text-white text-3xl font-bold leading-none">18</p>
                <div className="flex items-center text-secondary bg-secondary/10 px-1.5 py-0.5 rounded text-xs font-bold mb-1">
                  <span>100% Synced</span>
                </div>
              </div>
            </div>

             {/* Metric 4 */}
             <div className="flex flex-col gap-2 rounded-xl p-5 border border-border bg-surface shadow-sm">
              <div className="flex justify-between items-start">
                <p className="text-secondary text-sm font-medium uppercase tracking-wider">ML Enrichments</p>
                <span className="material-symbols-outlined text-primary">auto_awesome</span>
              </div>
              <div className="flex items-end gap-3 mt-1">
                <p className="text-white text-3xl font-bold leading-none">350</p>
                <div className="flex items-center text-success bg-success/10 px-1.5 py-0.5 rounded text-xs font-bold mb-1">
                  <span className="material-symbols-outlined text-xs mr-0.5">trending_up</span>
                  8%
                </div>
              </div>
            </div>
          </div>

          {/* Chart & Activity Feed */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 flex flex-col rounded-xl border border-border bg-surface p-6 h-[400px]">
              <div className="flex justify-between items-start gap-4 mb-6">
                <div>
                  <h3 className="text-white text-lg font-bold">Vulnerability Trends</h3>
                  <p className="text-secondary text-sm mt-1">Discoveries vs Remediations</p>
                </div>
              </div>
              <div className="flex-1 w-full min-h-0">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                    <defs>
                      <linearGradient id="colorNew" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#1169d4" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#1169d4" stopOpacity={0} />
                      </linearGradient>
                      <linearGradient id="colorFixed" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#3b4654" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#3b4654" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <XAxis dataKey="name" stroke="#9da9b9" fontSize={12} tickLine={false} axisLine={false} />
                    <YAxis stroke="#9da9b9" fontSize={12} tickLine={false} axisLine={false} />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#1a1d23', borderColor: '#3b4654', borderRadius: '8px' }}
                      itemStyle={{ color: '#fff' }}
                    />
                    <Area type="monotone" dataKey="new" stroke="#1169d4" fillOpacity={1} fill="url(#colorNew)" strokeWidth={3} />
                    <Area type="monotone" dataKey="fixed" stroke="#586474" strokeDasharray="5 5" fillOpacity={1} fill="url(#colorFixed)" strokeWidth={2} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Activity Feed */}
            <div className="flex flex-col rounded-xl border border-border bg-surface overflow-hidden h-[400px]">
              <div className="p-5 border-b border-border flex justify-between items-center">
                <h3 className="text-white text-lg font-bold">Recent Activity</h3>
                <button className="text-primary text-sm font-medium hover:text-blue-400">View All</button>
              </div>
              <div className="flex flex-col overflow-y-auto">
                <div className="flex gap-4 p-4 border-b border-border/50 hover:bg-[#283039] transition-colors group cursor-default">
                   <div className="relative mt-1">
                      <div className="size-8 rounded-full bg-blue-500/20 flex items-center justify-center text-primary border border-blue-500/30">
                         <span className="material-symbols-outlined text-sm">confirmation_number</span>
                      </div>
                   </div>
                   <div className="flex flex-col gap-1">
                      <p className="text-white text-sm font-medium">Jira Ticket #402 Synced</p>
                      <p className="text-secondary text-xs">CVE-2023-4802 identified on Payment-Gateway</p>
                      <p className="text-[#586474] text-[10px] mt-1 font-mono">2 mins ago</p>
                   </div>
                </div>
                <div className="flex gap-4 p-4 border-b border-border/50 hover:bg-[#283039] transition-colors group cursor-default">
                   <div className="relative mt-1">
                      <div className="size-8 rounded-full bg-green-500/20 flex items-center justify-center text-green-500 border border-green-500/30">
                         <span className="material-symbols-outlined text-sm">check_circle</span>
                      </div>
                   </div>
                   <div className="flex flex-col gap-1">
                      <p className="text-white text-sm font-medium">Scan Completed</p>
                      <p className="text-secondary text-xs">Full scan on 'Production-East-1'</p>
                      <p className="text-[#586474] text-[10px] mt-1 font-mono">45 mins ago</p>
                   </div>
                </div>
                <div className="flex gap-4 p-4 border-b border-border/50 hover:bg-[#283039] transition-colors group cursor-default">
                   <div className="relative mt-1">
                      <div className="size-8 rounded-full bg-red-500/20 flex items-center justify-center text-danger border border-red-500/30">
                         <span className="material-symbols-outlined text-sm">notification_important</span>
                      </div>
                   </div>
                   <div className="flex flex-col gap-1">
                      <p className="text-white text-sm font-medium">Critical Vulnerability</p>
                      <p className="text-secondary text-xs">Log4j signature detected</p>
                      <p className="text-[#586474] text-[10px] mt-1 font-mono">2 hours ago</p>
                   </div>
                </div>
              </div>
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
                         {[
                            { severity: Severity.CRITICAL, name: 'SQL Injection', cve: 'CVE-2023-9021', asset: 'Payment-Gateway-01', time: '2 mins ago', score: 98 },
                            { severity: Severity.HIGH, name: 'Outdated Apache Version', cve: 'CVE-2021-41773', asset: 'Web-Server-04', time: '1 hr ago', score: 75 },
                            { severity: Severity.MEDIUM, name: 'Weak SSL Cipher', cve: 'SSL-003', asset: 'Load-Balancer-EXT', time: '3 hrs ago', score: 45 },
                            { severity: Severity.LOW, name: 'Info Exposure', cve: 'INFO-102', asset: 'Dev-Env-Container', time: '5 hrs ago', score: 20 },
                         ].map((row, i) => (
                            <tr key={i} className="group hover:bg-[#283039]/50 transition-colors">
                               <td className="px-6 py-4 whitespace-nowrap">
                                  <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold border 
                                     ${row.severity === Severity.CRITICAL ? 'bg-red-500/10 text-red-500 border-red-500/20' : 
                                       row.severity === Severity.HIGH ? 'bg-orange-500/10 text-orange-500 border-orange-500/20' :
                                       row.severity === Severity.MEDIUM ? 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20' :
                                       'bg-blue-500/10 text-blue-500 border-blue-500/20'}`}>
                                     <span className={`w-1.5 h-1.5 rounded-full ${row.severity === Severity.CRITICAL ? 'bg-red-500 animate-pulse' : 
                                        row.severity === Severity.HIGH ? 'bg-orange-500' :
                                        row.severity === Severity.MEDIUM ? 'bg-yellow-500' : 'bg-blue-500'}`}></span>
                                     {row.severity}
                                  </span>
                               </td>
                               <td className="px-6 py-4">
                                  <div className="flex flex-col">
                                     <span className="text-white font-medium text-sm">{row.name}</span>
                                     <span className="text-[#586474] text-xs font-mono">{row.cve}</span>
                                  </div>
                               </td>
                               <td className="px-6 py-4 text-secondary text-sm">{row.asset}</td>
                               <td className="px-6 py-4 text-secondary text-sm">{row.time}</td>
                               <td className="px-6 py-4">
                                  <div className="flex items-center gap-2">
                                     <div className="w-16 h-1.5 bg-[#3b4654] rounded-full overflow-hidden">
                                        <div className={`h-full w-[${row.score}%] ${
                                           row.score > 90 ? 'bg-primary' : row.score > 60 ? 'bg-orange-500' : 'bg-yellow-500'
                                        }`} style={{width: `${row.score}%`}}></div>
                                     </div>
                                     <span className={`text-xs font-bold ${
                                        row.score > 90 ? 'text-primary' : row.score > 60 ? 'text-orange-500' : 'text-yellow-500'
                                     }`}>{row.score}%</span>
                                  </div>
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

export default Dashboard;