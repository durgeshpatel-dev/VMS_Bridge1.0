import React from 'react';

const Settings: React.FC = () => {
  return (
    <div className="flex flex-col h-full overflow-hidden relative">
      <header className="flex-shrink-0 px-8 py-6 border-b border-border bg-background/95 backdrop-blur-sm z-10">
        <h1 className="text-2xl font-bold tracking-tight text-white">Account Settings</h1>
        <p className="text-secondary text-sm mt-1">Manage your profile details, security preferences, and integrations.</p>
      </header>

      <div className="flex-1 overflow-y-auto p-8 custom-scroll">
        <div className="max-w-4xl mx-auto flex flex-col gap-8 pb-10">
          
          {/* Profile Section */}
          <section className="bg-surface rounded-xl border border-border shadow-sm overflow-hidden">
            <div className="p-6 border-b border-border flex justify-between items-center bg-[#1c2127]">
              <div>
                <h2 className="text-lg font-semibold text-white">Personal Information</h2>
                <p className="text-secondary text-sm">Update your public profile and contact details.</p>
              </div>
            </div>
            <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="col-span-1 md:col-span-2 flex items-center gap-4 mb-2">
                <div className="size-16 rounded-full bg-cover bg-center border-2 border-border shadow-md bg-gradient-to-tr from-primary to-blue-400"></div>
                <div>
                  <button className="px-4 py-2 bg-[#283039] border border-border rounded-lg text-sm font-medium text-white hover:bg-[#323b46] transition-colors">
                    Change Avatar
                  </button>
                </div>
              </div>
              
              <label className="flex flex-col gap-2">
                <span className="text-sm font-medium text-white">Full Name</span>
                <input className="w-full rounded-lg border-border bg-[#1c2127] text-white focus:border-primary focus:ring-primary h-11 px-4 text-sm" type="text" defaultValue="Admin User" />
              </label>
              
              <label className="flex flex-col gap-2">
                <span className="text-sm font-medium text-white">Job Title</span>
                <input className="w-full rounded-lg border-border bg-[#1c2127] text-white focus:border-primary focus:ring-primary h-11 px-4 text-sm" type="text" defaultValue="Senior Security Engineer" />
              </label>
              
              <label className="flex flex-col gap-2 col-span-1 md:col-span-2">
                <span className="text-sm font-medium text-white">Email Address</span>
                <div className="relative">
                  <input className="w-full rounded-lg border-border bg-[#1c2127] text-white focus:border-primary focus:ring-primary h-11 px-4 pr-10 text-sm" type="email" defaultValue="admin@vmsbridge.io" />
                  <span className="material-symbols-outlined absolute right-3 top-1/2 -translate-y-1/2 text-green-500 text-[20px]">check_circle</span>
                </div>
                <p className="text-xs text-secondary">Your email is verified.</p>
              </label>
              
              <div className="col-span-1 md:col-span-2 flex justify-end pt-2">
                <button className="px-5 py-2.5 bg-primary hover:bg-blue-600 text-white rounded-lg text-sm font-medium transition-colors shadow-lg shadow-blue-900/20">
                  Save Changes
                </button>
              </div>
            </div>
          </section>

          {/* Integrations */}
          <section className="bg-surface rounded-xl border border-border shadow-sm overflow-hidden">
            <div className="p-6 border-b border-border flex justify-between items-center bg-[#1c2127]">
              <div className="flex items-center gap-3">
                <div className="size-8 rounded bg-[#0052CC] flex items-center justify-center text-white font-bold text-xs">J</div>
                <div>
                  <h2 className="text-lg font-semibold text-white">Jira Integration</h2>
                  <p className="text-secondary text-sm">Connect your issue tracker for automated ticket creation.</p>
                </div>
              </div>
              <div className="flex items-center gap-2 px-2 py-1 bg-green-500/10 border border-green-500/20 rounded-md">
                <div className="size-2 rounded-full bg-green-500"></div>
                <span className="text-xs font-medium text-green-500">Connected</span>
              </div>
            </div>
            <div className="p-6 grid grid-cols-1 gap-6">
              <label className="flex flex-col gap-2">
                <span className="text-sm font-medium text-white">Jira URL</span>
                <input className="w-full rounded-lg border-border bg-[#1c2127] text-white focus:border-primary focus:ring-primary h-11 px-4 text-sm" type="url" defaultValue="https://vmsbridge.atlassian.net" />
              </label>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <label className="flex flex-col gap-2">
                  <span className="text-sm font-medium text-white">Username / Email</span>
                  <input className="w-full rounded-lg border-border bg-[#1c2127] text-white focus:border-primary focus:ring-primary h-11 px-4 text-sm" type="text" defaultValue="bot@vmsbridge.io" />
                </label>
                <label className="flex flex-col gap-2">
                  <span className="text-sm font-medium text-white">API Token</span>
                  <div className="relative group/input">
                    <input className="w-full rounded-lg border-border bg-[#1c2127] text-white focus:border-primary focus:ring-primary h-11 px-4 pr-10 text-sm" type="password" defaultValue="fake-token-value" />
                    <button className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white transition-colors">
                      <span className="material-symbols-outlined text-[20px]">visibility_off</span>
                    </button>
                  </div>
                </label>
              </div>
            </div>
          </section>

          {/* API Keys */}
          <section className="bg-surface rounded-xl border border-border shadow-sm overflow-hidden">
            <div className="p-6 border-b border-border flex justify-between items-center bg-[#1c2127]">
              <div>
                <h2 className="text-lg font-semibold text-white">API Keys</h2>
                <p className="text-secondary text-sm">Manage API access tokens for external scripts.</p>
              </div>
              <button className="px-3 py-2 bg-primary/10 hover:bg-primary/20 text-primary border border-primary/20 rounded-lg text-sm font-medium transition-colors flex items-center gap-2">
                <span className="material-symbols-outlined text-[18px]">add</span>
                Generate New Key
              </button>
            </div>
            <div className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="border-b border-border bg-[#1c2127]/50 text-xs uppercase text-secondary">
                      <th className="px-6 py-4 font-medium">Key Name</th>
                      <th className="px-6 py-4 font-medium">Token Hint</th>
                      <th className="px-6 py-4 font-medium">Created</th>
                      <th className="px-6 py-4 font-medium text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="text-sm">
                    <tr className="border-b border-border hover:bg-[#1c2127]/30 transition-colors group">
                      <td className="px-6 py-4 font-medium text-white">CI/CD Pipeline</td>
                      <td className="px-6 py-4 font-mono text-secondary">sk_live_...93kd</td>
                      <td className="px-6 py-4 text-secondary">Oct 24, 2023</td>
                      <td className="px-6 py-4 text-right">
                        <button className="text-slate-400 hover:text-danger transition-colors p-1 rounded-md hover:bg-red-500/10" title="Revoke Key">
                          <span className="material-symbols-outlined text-[20px]">delete</span>
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </section>

        </div>
      </div>
    </div>
  );
};

export default Settings;