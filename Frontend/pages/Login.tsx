import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Login: React.FC = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    localStorage.setItem('isAuthenticated', 'true');
    navigate('/');
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 sm:p-6 md:p-8 relative overflow-y-auto bg-background">
        {/* Background Animation */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
            <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary/20 rounded-full mix-blend-screen filter blur-[100px] animate-blob"></div>
            <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-blue-900/20 rounded-full mix-blend-screen filter blur-[100px] animate-blob animation-delay-2000"></div>
            <div className="absolute -bottom-32 left-1/3 w-96 h-96 bg-primary/10 rounded-full mix-blend-screen filter blur-[100px] animate-blob animation-delay-4000"></div>
            {/* Grid Pattern */}
            <div className="fixed inset-0 z-0 pointer-events-none opacity-20" style={{backgroundImage: "radial-gradient(#3b4654 1px, transparent 1px)", backgroundSize: "32px 32px"}}></div>
        </div>

        <div className="w-full max-w-md z-10 flex flex-col gap-4 sm:gap-5 md:gap-6 my-4 sm:my-8">
            <div className="text-center flex flex-col items-center gap-2 sm:gap-3 md:gap-4">
                <div className="size-10 sm:size-12 bg-primary/20 rounded-xl flex items-center justify-center text-primary mb-1 sm:mb-2">
                   <span className="material-symbols-outlined text-[28px] sm:text-[32px]">hub</span>
                </div>
                <div className="space-y-1">
                    <h1 className="text-white tracking-tight text-2xl sm:text-[28px] font-bold leading-tight">Welcome Back</h1>
                    <p className="text-secondary text-sm sm:text-base font-normal">VMS Bridge - Vulnerability Management System Bridge</p>
                </div>
            </div>

            <div className="bg-surface rounded-xl border border-border shadow-2xl p-5 sm:p-6 md:p-8 w-full backdrop-blur-sm">
                <form className="flex flex-col gap-4 sm:gap-5" onSubmit={handleLogin}>
                    <div className="flex flex-col gap-2">
                        <label className="text-white text-sm font-medium leading-normal">Email</label>
                        <div className="group flex w-full items-center rounded-xl border border-border bg-[#1c2127] focus-within:border-primary focus-within:ring-1 focus-within:ring-primary overflow-hidden transition-all">
                            <input 
                              className="flex-1 bg-transparent border-none text-white h-12 px-4 placeholder:text-secondary focus:ring-0 text-base" 
                              placeholder="name@company.com" 
                              type="email" 
                              value={email}
                              onChange={(e) => setEmail(e.target.value)}
                              required
                            />
                        </div>
                    </div>

                    <div className="flex flex-col gap-2">
                        <label className="text-white text-sm font-medium leading-normal">Password</label>
                        <div className="group flex w-full items-center rounded-xl border border-border bg-[#1c2127] focus-within:border-primary focus-within:ring-1 focus-within:ring-primary overflow-hidden transition-all">
                            <input 
                              className="flex-1 bg-transparent border-none text-white h-12 px-4 placeholder:text-secondary focus:ring-0 text-base" 
                              placeholder="••••••••" 
                              type="password"
                              defaultValue="password123"
                            />
                            <div className="pr-4 flex items-center justify-center text-secondary cursor-pointer hover:text-primary transition-colors">
                                <span className="material-symbols-outlined">visibility_off</span>
                            </div>
                        </div>
                        <div className="flex justify-end">
                            <a href="#" className="text-xs text-primary hover:text-blue-400 font-medium">Forgot password?</a>
                        </div>
                    </div>

                    <button className="mt-2 w-full flex items-center justify-center gap-2 rounded-xl bg-primary px-6 py-3.5 text-base font-bold text-white shadow-sm hover:bg-blue-600 transition-all active:scale-[0.98] group">
                        Sign In
                        <span className="material-symbols-outlined text-[20px] transition-transform group-hover:translate-x-1">arrow_forward</span>
                    </button>
                </form>

                <div className="mt-6 text-center">
                    <p className="text-sm text-secondary">
                        Don't have an account? 
                        <a className="font-semibold text-primary hover:text-blue-400 hover:underline ml-1" href="#">Sign up</a>
                    </p>
                </div>
            </div>
            
            <div className="text-center opacity-40 pb-2">
               <p className="text-xs text-secondary">© 2024 VMS Bridge Security Inc.</p>
            </div>
        </div>
    </div>
  );
};

export default Login;