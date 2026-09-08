import React, { createContext, useContext, useState } from 'react';
import { User } from '../types';
import { api } from '../services/api';

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (username?: string, password?: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('nwis_token') || null);

  const [user, setUser] = useState<User | null>(() => {
    const savedUser = localStorage.getItem('nwis_user');
    const savedToken = localStorage.getItem('nwis_token');
    if (savedUser && savedToken) {
      try {
        return JSON.parse(savedUser);
      } catch (e) {
        localStorage.removeItem('nwis_user');
        localStorage.removeItem('nwis_token');
      }
    }
    return null;
  });

  const login = async (username = 'driller', password = 'password123') => {
    try {
      const data = await api.login(username, password);
      const authUser: User = {
        id: data.user_id,
        username: data.username,
        email: `${data.username}@oilindia.demo`,
        full_name: data.full_name,
        role: data.role
      };
      setUser(authUser);
      setToken(data.access_token);
      localStorage.setItem('nwis_user', JSON.stringify(authUser));
      localStorage.setItem('nwis_token', data.access_token);
    } catch (err) {
      console.error('Login failed:', err);
      throw err;
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('nwis_user');
    localStorage.removeItem('nwis_token');
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, isAuthenticated: !!(user && token) }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
};
