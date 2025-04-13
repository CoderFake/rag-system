import apiService from './api';
import { Settings } from '../types';

class SettingsService {
  async getSettings(): Promise<Settings> {
    // Corrected endpoint path
    const response = await apiService.get<Settings>('/admin/settings'); 
    return response.data;
  }

  // Update return type to include optional message
  async updateSettings(settings: Partial<Settings>): Promise<{ success: boolean; message?: string }> {
    // Corrected endpoint path and removed duplicate variable declaration
    const updateResponse = await apiService.put<{ success: boolean; message?: string }>('/admin/settings', settings); 
    return updateResponse.data;
  }

  getLanguage(): string {
    return localStorage.getItem('language') || import.meta.env.VITE_DEFAULT_LANGUAGE || 'vi';
  }

  setLanguage(language: string): void {
    localStorage.setItem('language', language);
  }

  getTheme(): string {
    return localStorage.getItem('theme') || 'light';
  }

  setTheme(theme: string): void {
    localStorage.setItem('theme', theme);
    document.documentElement.setAttribute('data-theme', theme);
  }
}

export const settingsService = new SettingsService();
export default settingsService;
