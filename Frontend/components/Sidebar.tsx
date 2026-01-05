import React from 'react';
import { useLocation, Link } from 'react-router-dom';

const Sidebar: React.FC = () => {
  const location = useLocation();
  const isActive = (path: string) => location.pathname === path;

  const navItems = [
    { name: 'Dashboard', icon: 'dashboard', path: '/' },
    // Assets removed as requested
    { name: 'Scans', icon: 'radar', path: '/scans' }, // Maps to Upload in this demo
    { name: 'Vulnerabilities', icon: 'bug_report', path: '/vulnerabilities' },
    { name: 'Reports', icon: 'description', path: '/reports' },
    { name: 'Settings', icon: 'settings', path: '/settings' },
  ];

  return (
    <div className="flex w-64 flex-col bg-[#111418] border-r border-border flex-shrink-0 z-20 h-full">
      <div className="flex h-full flex-col justify-between p-4">
        <div className="flex flex-col gap-4">
          {/* Logo */}
          <div className="flex gap-3 items-center px-2 mb-2">
            <div className="bg-center bg-no-repeat aspect-square bg-cover rounded-full size-10 bg-primary/20 flex items-center justify-center text-primary">
              <span className="material-symbols-outlined text-2xl">shield_lock</span>
            </div>
            <div className="flex flex-col">
              <h1 className="text-white text-base font-bold leading-normal">VMS Bridge</h1>
              <p className="text-secondary text-xs font-normal leading-normal">Vulnerability Management Bridge</p>
            </div>
          </div>

          {/* Nav Items */}
          <div className="flex flex-col gap-2">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer transition-colors group ${
                  isActive(item.path)
                    ? 'bg-[#283039] text-white'
                    : 'hover:bg-[#283039] text-secondary hover:text-white'
                }`}
              >
                <span className={`material-symbols-outlined text-[24px] ${isActive(item.path) ? 'text-white' : 'text-secondary group-hover:text-white'}`}>
                  {item.icon}
                </span>
                <p className="text-sm font-medium leading-normal">{item.name}</p>
              </Link>
            ))}
          </div>
        </div>

        {/* User Profile */}
        <div className="flex flex-col gap-3">
          <div className="h-[1px] bg-border w-full"></div>
          <div className="flex items-center gap-3 px-3 py-2">
            <div className="size-8 rounded-full bg-gradient-to-tr from-primary to-blue-400"></div>
            <div>
              <p className="text-white text-sm font-medium">Admin User</p>
              <p className="text-secondary text-xs">admin@vmsbridge.io</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;