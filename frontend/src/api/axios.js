import axios from 'axios';

const apiClient = axios.create({
  // The base URL for all requests. No trailing slash.
  // It will use the environment variable on Cloudflare, or localhost for development.
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000',
  headers: {
    'Content-Type': 'application/json',
  }
});

export default apiClient;