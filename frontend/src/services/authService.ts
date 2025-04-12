import apiService from './api';
import { LoginCredentials, RegisterData, User } from '../types';

export interface LoginResponse {
  user: User;
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface RegisterResponse {
  message: string;
  user: User;
}

class AuthService {
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    const response = await apiService.post<LoginResponse>('/auth/login', credentials);
    return response.data;
  }

  async register(data: RegisterData): Promise<RegisterResponse> {
    const response = await apiService.post<RegisterResponse>('/auth/register', data);
    return response.data;
  }

  async refreshToken(refreshToken: string): Promise<{ access_token: string; token_type: string }> {
    const response = await apiService.post<{ access_token: string; token_type: string }>(
      '/auth/refresh',
      { refresh_token: refreshToken }
    );
    return response.data;
  }

  async getProfile(): Promise<User> {
    const response = await apiService.get<{ user: User }>('/auth/profile');
    return response.data.user;
  }

  async getUsers(): Promise<User[]> {
    const response = await apiService.get<{ users: User[] }>('/auth/users');
    return response.data.users;
  }

  saveUserToLocalStorage(user: User, accessToken: string, refreshToken: string): void {
    localStorage.setItem('user', JSON.stringify(user));
    localStorage.setItem('accessToken', accessToken);
    localStorage.setItem('refreshToken', refreshToken);
  }

  getUserFromLocalStorage(): User | null {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      return JSON.parse(userStr);
    }
    return null;
  }

  getAccessToken(): string | null {
    return localStorage.getItem('accessToken');
  }

  getRefreshToken(): string | null {
    return localStorage.getItem('refreshToken');
  }

  logout(): void {
    localStorage.removeItem('user');
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
  }

  isAuthenticated(): boolean {
    return !!this.getAccessToken();
  }

  isAdmin(): boolean {
    const user = this.getUserFromLocalStorage();
    return user?.role === 'admin';
  }
}

export const authService = new AuthService();
export default authService;
