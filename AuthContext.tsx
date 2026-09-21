import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import type { User, AuthState } from '@/types';
import { authApi, profileApi } from '@/lib/api';

interface AuthContextType extends AuthState {
  login: (email: string, password: string) => Promise<{ success: boolean; message?: string }>;
  signup: (email: string, password: string, name: string) => Promise<{ success: boolean; message?: string }>;
  logout: () => Promise<void>;
  setOnboarded: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({
    user: null,
    isAuthenticated: false,
    isLoading: true,
  });

  useEffect(() => {
    checkAuth();
  }, []);

  async function checkAuth() {
    try {
      const response = await authApi.getCurrentUser();
      if (response.success && response.data) {
        // User is authenticated, now check if they have a profile (completed onboarding)
        let isOnboarded = response.data.isOnboarded || false;
        
        try {
          // Check if profile exists in backend
          const profile = await profileApi.getProfile();
          if (profile && profile.skills && profile.skills.length > 0) {
            // User has a profile, they're onboarded
            isOnboarded = true;
          }
        } catch {
          // Profile not found = not onboarded yet
          isOnboarded = false;
        }
        
        const user = { ...response.data, isOnboarded };
        localStorage.setItem('user', JSON.stringify(user));
        
        setState({
          user,
          isAuthenticated: true,
          isLoading: false,
        });
      } else {
        setState({
          user: null,
          isAuthenticated: false,
          isLoading: false,
        });
      }
    } catch {
      setState({
        user: null,
        isAuthenticated: false,
        isLoading: false,
      });
    }
  }

  async function login(email: string, password: string) {
    try {
      const response = await authApi.login(email, password);
      if (response.success) {
        localStorage.setItem('auth_token', response.data.token);
        
        // Check if user has profile (completed onboarding before)
        let isOnboarded = false;
        try {
          const profile = await profileApi.getProfile();
          if (profile && profile.skills && profile.skills.length > 0) {
            isOnboarded = true;
          }
        } catch {
          // Profile not found = not onboarded
          isOnboarded = false;
        }
        
        const user = { ...response.data.user, isOnboarded };
        localStorage.setItem('user', JSON.stringify(user));
        
        setState({
          user,
          isAuthenticated: true,
          isLoading: false,
        });
        return { success: true };
      }
      return { success: false, message: response.message };
    } catch (error) {
      return { success: false, message: 'Login failed. Please try again.' };
    }
  }

  async function signup(email: string, password: string, name: string) {
    try {
      const response = await authApi.signup(email, password, name);
      if (response.success) {
        localStorage.setItem('auth_token', response.data.token);
        // New user, not onboarded yet
        const user = { ...response.data.user, isOnboarded: false };
        localStorage.setItem('user', JSON.stringify(user));
        setState({
          user,
          isAuthenticated: true,
          isLoading: false,
        });
        return { success: true };
      }
      return { success: false, message: response.message };
    } catch (error) {
      return { success: false, message: 'Signup failed. Please try again.' };
    }
  }

  async function logout() {
    await authApi.logout();
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
    localStorage.removeItem('profile');
    setState({
      user: null,
      isAuthenticated: false,
      isLoading: false,
    });
  }

  function setOnboarded() {
    if (state.user) {
      const updatedUser = { ...state.user, isOnboarded: true };
      localStorage.setItem('user', JSON.stringify(updatedUser));
      setState(prev => ({
        ...prev,
        user: updatedUser,
      }));
    }
  }

  return (
    <AuthContext.Provider value={{ ...state, login, signup, logout, setOnboarded }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
