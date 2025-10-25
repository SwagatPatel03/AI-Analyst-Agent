import type { AuthResponse, LoginCredentials, RegisterData, User } from '../types';
import api from './api';

export const authService = {
  // Register new user
  register: async (data: RegisterData): Promise<User> => {
    const response = await api.post<User>('/auth/register', data);
    return response.data;
  },

  // Login user
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/auth/login', credentials);
    // Store token in localStorage
    localStorage.setItem('access_token', response.data.access_token);
    return response.data;
  },

  // Logout user
  logout: () => {
    localStorage.removeItem('access_token');
  },

  // Get current user
  getCurrentUser: async (): Promise<User> => {
    const response = await api.get<User>('/auth/me');
    return response.data;
  },

  // Check if user is authenticated
  isAuthenticated: (): boolean => {
    return !!localStorage.getItem('access_token');
  },

  // Get token
  getToken: (): string | null => {
    return localStorage.getItem('access_token');
  },
};
