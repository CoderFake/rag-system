import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authService, apiService } from '../services';
import { AuthState, LoginCredentials, RegisterData } from '../types';

interface AuthContextType extends AuthState {
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  clearError: () => void;
  refreshAuth: () => Promise<boolean>;
}

const initialState: AuthState = {
  user: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,
  accessToken: null,
  refreshToken: null,
};

const AuthContext = createContext<AuthContextType>({
  ...initialState,
  login: async () => {},
  register: async () => {},
  logout: () => {},
  clearError: () => {},
  refreshAuth: async () => false,
});

export const useAuth = () => useContext(AuthContext);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [state, setState] = useState<AuthState>(initialState);

  const refreshAuth = async (): Promise<boolean> => {
    try {
      const refreshToken = authService.getRefreshToken();
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }
      
      const response = await authService.refreshToken(refreshToken);
      const accessToken = response.access_token;
      
      const user = authService.getUserFromLocalStorage();
      
      if (user && accessToken) {
        authService.saveUserToLocalStorage(user, accessToken, refreshToken);
        
        setState({
          user,
          isAuthenticated: true,
          isLoading: false,
          error: null,
          accessToken,
          refreshToken,
        });
        
        return true;
      }
      return false;
    } catch (error) {
      console.error('Failed to refresh authentication:', error);
      logout();
      return false;
    }
  };

  useEffect(() => {
    const initAuth = async () => {
      try {
        const user = authService.getUserFromLocalStorage();
        const accessToken = authService.getAccessToken();
        const refreshToken = authService.getRefreshToken();

        if (user && accessToken && refreshToken) {
          try {
            await authService.getProfile();
            setState({
              user,
              isAuthenticated: true,
              isLoading: false,
              error: null,
              accessToken,
              refreshToken,
            });
          } catch (error) {
            const refreshed = await refreshAuth();
            if (!refreshed) {
              setState({
                ...initialState,
                isLoading: false,
              });
            }
          }
        } else {
          setState({
            ...initialState,
            isLoading: false,
          });
        }
      } catch (error) {
        setState({
          ...initialState,
          isLoading: false,
          error: 'Failed to initialize authentication',
        });
      }
    };

    initAuth();
  }, []);

  const login = async (credentials: LoginCredentials) => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));
    try {
      const { user, access_token, refresh_token } = await authService.login(credentials);
      authService.saveUserToLocalStorage(user, access_token, refresh_token);
      setState({
        user,
        isAuthenticated: true,
        isLoading: false,
        error: null,
        accessToken: access_token,
        refreshToken: refresh_token,
      });
    } catch (error) {
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Login failed',
      }));
      throw error;
    }
  };

  const register = async (data: RegisterData) => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));
    try {
      await authService.register(data);
      setState((prev) => ({ ...prev, isLoading: false }));
    } catch (error) {
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Registration failed',
      }));
      throw error;
    }
  };

  const logout = () => {
    authService.logout();
    setState({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      accessToken: null,
      refreshToken: null,
    });
  };

  const clearError = () => {
    setState((prev) => ({ ...prev, error: null }));
  };

  return (
    <AuthContext.Provider
      value={{
        ...state,
        login,
        register,
        logout,
        clearError,
        refreshAuth,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;