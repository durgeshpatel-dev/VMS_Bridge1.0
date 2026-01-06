import React, { createContext, useContext, useState, ReactNode } from 'react';
import { v4 as uuidv4 } from 'uuid';

export type ToastType = 'success' | 'error' | 'info';

export interface Toast {
  id: string;
  message: string;
  type: ToastType;
  duration?: number;
}

interface ToastContextType {
  showToast: (message: string, type?: ToastType, duration?: number) => void;
  success: (message: string, duration?: number) => void;
  error: (message: string, duration?: number) => void;
  info: (message: string, duration?: number) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export const ToastProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const removeToast = (id: string) => {
    setToasts((t) => t.filter((x) => x.id !== id));
  };

  const showToast = (message: string, type: ToastType = 'info', duration = 4000) => {
    const id = uuidv4();
    const toast: Toast = { id, message, type, duration };
    setToasts((t) => [toast, ...t]);

    if (duration > 0) {
      setTimeout(() => removeToast(id), duration);
    }
  };

  const success = (message: string, duration?: number) => showToast(message, 'success', duration);
  const error = (message: string, duration?: number) => showToast(message, 'error', duration);
  const info = (message: string, duration?: number) => showToast(message, 'info', duration);

  return (
    <ToastContext.Provider value={{ showToast, success, error, info }}>
      {children}

      {/* Toast container */}
      <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 pointer-events-none">
        {toasts.map((t) => (
          <div
            key={t.id}
            className={`pointer-events-auto w-80 max-w-sm rounded-lg shadow-lg overflow-hidden border border-border flex items-start gap-3 p-3 animate-slide-in transition-all
              ${t.type === 'success' ? 'bg-green-600 text-white' : ''}
              ${t.type === 'error' ? 'bg-red-600 text-white' : ''}
              ${t.type === 'info' ? 'bg-surface text-white' : ''}`}
          >
            <div className="flex-1 text-sm leading-tight">{t.message}</div>
            <div className="ml-2 flex items-start">
              <button
                onClick={() => removeToast(t.id)}
                className="text-white/80 hover:text-white"
                aria-label="Dismiss"
              >
                <span className="material-symbols-outlined text-[18px]">close</span>
              </button>
            </div>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
};

export const useToast = (): ToastContextType => {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be used within a ToastProvider');
  return ctx;
};
