import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

export const axiosInstance = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Request Interceptor: Attach JWT Bearer Token
axiosInstance.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('decisionos_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Handle 401 Unauthorized & Normalize Errors
axiosInstance.interceptors.response.use(
  (response) => {
    // Unwrap data envelope if standardized { data: ... } is returned
    if (response.data && typeof response.data === 'object' && 'data' in response.data) {
      return response.data.data;
    }
    return response.data;
  },
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Clear token and broadcast auth expiry
      localStorage.removeItem('decisionos_token');
      localStorage.removeItem('decisionos_user');
      if (window.location.pathname !== '/login' && window.location.pathname !== '/') {
        window.location.href = `/login?redirect=${encodeURIComponent(window.location.pathname)}`;
      }
    }
    
    // Extract formatted message
    const errorData = error.response?.data as any;
    const message = errorData?.detail || errorData?.message || error.message || 'An unexpected API error occurred';
    return Promise.reject(new Error(message));
  }
);

export default axiosInstance;
