import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import { axiosInstance } from '../../shared/api/axiosClient';

export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  role?: string;
  organization_id?: string;
}

export interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(() => {
    try {
      return typeof window !== 'undefined' ? localStorage.getItem('decisionos_token') : null;
    } catch {
      return null;
    }
  });

  const [user, setUser] = useState<User | null>(() => {
    try {
      const saved = typeof window !== 'undefined' ? localStorage.getItem('decisionos_user') : null;
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });

  const [isLoading, setIsLoading] = useState<boolean>(false);

  const logout = useCallback(() => {
    setToken(null);
    setUser(null);
    try {
      localStorage.removeItem('decisionos_token');
      localStorage.removeItem('decisionos_user');
    } catch (e) {
      console.warn('Error clearing localStorage', e);
    }
  }, []);

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      // First try JSON login endpoint, fallback to OAuth2 password form
      let loginData: any;
      try {
        loginData = await axiosInstance.post('/auth/login', { email, password });
      } catch {
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);
        loginData = await axiosInstance.post('/auth/access-token', formData, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        });
      }

      const receivedToken = loginData.access_token || loginData.token;
      const userData: User = loginData.user || {
        id: 'usr_exec',
        email: email,
        full_name: email.split('@')[0],
        is_active: true,
        role: 'executive',
      };

      setToken(receivedToken);
      setUser(userData);
      localStorage.setItem('decisionos_token', receivedToken);
      localStorage.setItem('decisionos_user', JSON.stringify(userData));
    } catch (err: any) {
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token,
        isLoading,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
