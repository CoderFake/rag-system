import apiService from './api';
import { Settings } from '../types';

class SettingsService {
  async getSettings(): Promise<Settings> {
    const response = await apiService.get<Settings>('/settings');
    return response.data;
  }

  async updateSettings(settings: Partial<Settings>): Promise<{ success: boolean }> {
    const response = await apiService.post<{ success: boolean }>('/settings', settings);
    return response.data;
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
