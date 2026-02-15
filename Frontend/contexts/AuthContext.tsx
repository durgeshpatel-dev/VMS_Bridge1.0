/**
 * Authentication Context for managing user state across the application
 */
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { apiClient, User } from '../services/api';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string, recaptchaToken: string) => Promise<User>;
  signup: (email: string, password: string, fullName: string, recaptchaToken: string) => Promise<User>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check if user is authenticated on mount
    const initAuth = async () => {
      const storedUser = apiClient.getStoredUser();
      
      if (storedUser && apiClient.isAuthenticated()) {
        try {
          // Verify token is still valid by fetching current user
          const currentUser = await apiClient.getCurrentUser();
          setUser(currentUser);
          localStorage.setItem('user', JSON.stringify(currentUser));
        } catch (error) {
          // Token invalid, clear everything
          console.error('Auth verification failed:', error);
          apiClient.clearTokens();
          setUser(null);
        }
      }
      
      setIsLoading(false);
    };

    initAuth();
  }, []);

  const login = async (email: string, password: string, recaptchaToken: string): Promise<User> => {
    setIsLoading(true);
    try {
      const response = await apiClient.login({ email, password, recaptcha_token: recaptchaToken });
      setUser(response.user);
      return response.user;
    } finally {
      setIsLoading(false);
    }
  };

  const signup = async (email: string, password: string, fullName: string, recaptchaToken: string): Promise<User> => {
    setIsLoading(true);
    try {
      const response = await apiClient.signup({
        email,
        password,
        full_name: fullName,
        recaptcha_token: recaptchaToken,
      });
      setUser(response.user);
      return response.user;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    setIsLoading(true);
    try {
      await apiClient.logout();
    } finally {
      setUser(null);
      setIsLoading(false);
    }
  };

  const refreshUser = async () => {
    if (!apiClient.isAuthenticated()) return;
    
    try {
      const currentUser = await apiClient.getCurrentUser();
      setUser(currentUser);
      localStorage.setItem('user', JSON.stringify(currentUser));
    } catch (error) {
      console.error('Failed to refresh user:', error);
      apiClient.clearTokens();
      setUser(null);
    }
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    signup,
    logout,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
