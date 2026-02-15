import React from 'react';
import { useLocation, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

interface SidebarProps {
  onClose?: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ onClose }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const isActive = (path: string) => location.pathname === path;

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const navItems = [
    { name: 'Dashboard', icon: 'dashboard', path: '/' },
    // Assets removed as requested
    { name: 'Scans', icon: 'radar', path: '/scans' }, // Maps to Upload in this demo
    { name: 'Vulnerabilities', icon: 'bug_report', path: '/vulnerabilities' },
    { name: 'Reports', icon: 'description', path: '/reports' },
    { name: 'Settings', icon: 'settings', path: '/settings' },
    { name: 'Help', icon: 'support_agent', path: '/help' },
    user?.is_admin ? { name: 'Admin Panel', icon: 'shield_admin', path: '/admin' } : null,
  ].filter(Boolean) as any[];

  return (
    <div className="flex w-64 flex-col bg-[#111418] border-r border-border flex-shrink-0 z-20 h-full lg:h-screen">
      {/* Mobile close button */}
      <div className="lg:hidden flex justify-end p-4">
        <button
          onClick={onClose}
          className="p-2 rounded-lg hover:bg-border transition-colors"
        >
          <span className="material-symbols-outlined text-white">close</span>
        </button>
      </div>
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
          
          {/* User Info */}
          <div className="flex items-center gap-3 px-3 py-2">
            <div className="size-8 rounded-full bg-gradient-to-tr from-primary to-blue-400 flex items-center justify-center text-white text-sm font-bold">
              {user?.full_name?.charAt(0).toUpperCase() || 'U'}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-white text-sm font-medium truncate">{user?.full_name || 'User'}</p>
              <p className="text-secondary text-xs truncate">{user?.email || ''}</p>
            </div>
          </div>
          
          {/* Logout Button */}
          <button
            onClick={handleLogout}
            className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-red-500/10 text-red-400 hover:text-red-300 transition-colors group"
          >
            <span className="material-symbols-outlined text-[24px]">logout</span>
            <p className="text-sm font-medium leading-normal">Logout</p>
          </button>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
