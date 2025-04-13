import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { CssBaseline, ThemeProvider, createTheme } from '@mui/material';
import { AuthProvider, LanguageProvider, ThemeProvider as CustomThemeProvider, useTheme } from './contexts';
import { Layout } from './components';
import {
  HomePage,
  LoginPage,
  RegisterPage,
  HistoryPage,
  DocumentsPage,
  SettingsPage,
} from './pages';
import './i18n';

const PrivateRoute = ({ children }: { children: React.ReactNode }) => {
  const isAuthenticated = localStorage.getItem('accessToken') !== null;
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
};

const AdminRoute = ({ children }: { children: React.ReactNode }) => {
  const isAuthenticated = localStorage.getItem('accessToken') !== null;
  const userStr = localStorage.getItem('user');
  const user = userStr ? JSON.parse(userStr) : null;
  const isAdmin = user?.role === 'admin';
  
  return isAuthenticated && isAdmin ? <>{children}</> : <Navigate to="/login" />;
};

const App: React.FC = () => {
  return (
    <Router>
      <AuthProvider>
        <LanguageProvider>
          <CustomThemeProvider>
            <ThemeConsumer />
          </CustomThemeProvider>
        </LanguageProvider>
      </AuthProvider>
    </Router>
  );
};

const ThemeConsumer: React.FC = () => {
  const { theme } = useTheme();
  
  return (
    <ThemeProvider theme={createTheme({
      palette: {
        mode: theme as 'light' | 'dark',
      },
    })}>
      <CssBaseline />
      <Layout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route 
            path="/history" 
            element={
              <PrivateRoute>
                <HistoryPage />
              </PrivateRoute>
            } 
          />
          <Route 
            path="/admin/documents" 
            element={
              <AdminRoute>
                <DocumentsPage />
              </AdminRoute>
            } 
          />
          <Route 
            path="/admin/settings" 
            element={
              <AdminRoute>
                <SettingsPage />
              </AdminRoute>
            } 
          />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </Layout>
    </ThemeProvider>
  );
};

export default App;
