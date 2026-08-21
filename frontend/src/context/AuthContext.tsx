import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (token: string, user: User) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(() => {
    try {
      return typeof window !== 'undefined' && window.localStorage ? window.localStorage.getItem('decisionos_token') : null;
    } catch {
      return null;
    }
  });

  const [user, setUser] = useState<User | null>(() => {
    try {
      const saved = typeof window !== 'undefined' && window.localStorage ? window.localStorage.getItem('decisionos_user') : null;
      return saved ? JSON.parse(saved) : { id: 'exec-1', email: 'executive@decisionos.ai', full_name: 'Executive User', is_active: true };
    } catch {
      return { id: 'exec-1', email: 'executive@decisionos.ai', full_name: 'Executive User', is_active: true };
    }
  });

  const login = (newToken: string, newUser: User) => {
    setToken(newToken);
    setUser(newUser);
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        window.localStorage.setItem('decisionos_token', newToken);
        window.localStorage.setItem('decisionos_user', JSON.stringify(newUser));
      }
    } catch (e) {
      console.warn('Could not write to localStorage', e);
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        window.localStorage.removeItem('decisionos_token');
        window.localStorage.removeItem('decisionos_user');
      }
    } catch (e) {
      console.warn('Could not remove from localStorage', e);
    }
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

const defaultAuthContext: AuthContextType = {
  user: null,
  token: null,
  login: () => {},
  logout: () => {},
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  return context || defaultAuthContext;
};
