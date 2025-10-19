import axios from 'axios';

const apiClient = axios.create({
  // Force same-origin to avoid mixed content across environments
  baseURL: typeof window !== 'undefined' ? window.location.origin : '/',
  timeout: 10000,
  maxRedirects: 0,
});

// Optional: Add interceptors for logging or error handling, but keep URL manipulation minimal.
apiClient.interceptors.request.use(
  (config) => {
    const isHttps = window.location.protocol === 'https:';
    if (!config.url) return config;

    // 如果是明確的 http:// 且頁面在 HTTPS，強制升級為 https://
    if (isHttps && config.url.startsWith('http://')) {
      config.url = config.url.replace(/^http:\/\//i, 'https://');
    }

    // Keep same-origin for relative URLs
    if (!config.url.startsWith('http')) {
      // Let axios prepend baseURL (same-origin)
      // Ensure baseURL is current origin
      config.baseURL = window.location.origin;
    }
    console.log('API Request:', config.method?.toUpperCase(), (config.baseURL || '') + (config.url || ''));
    return config;
  },
  (error) => Promise.reject(error)
);

apiClient.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.config.method?.toUpperCase(), response.config.url, response.status);
    return response;
  },
  (error) => {
    console.error('API Error:', error.config?.method?.toUpperCase(), error.config?.url, error.response?.status || error.message);
    return Promise.reject(error);
  }
);

export default apiClient;
