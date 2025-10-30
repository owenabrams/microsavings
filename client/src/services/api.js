import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  login: (email, password) =>
    api.post('/api/auth/login', { email, password }),
  
  register: (username, email, password) =>
    api.post('/api/auth/register', { username, email, password }),
  
  getStatus: () =>
    api.get('/api/auth/status'),
};

export const groupsAPI = {
  getAll: (params) =>
    api.get('/api/savings-groups', { params }),

  getById: (id) =>
    api.get(`/api/savings-groups/${id}`),

  create: (data) =>
    api.post('/api/savings-groups', data),

  getMembers: (groupId) =>
    api.get(`/api/savings-groups/${groupId}/members`),

  addMember: (groupId, data) =>
    api.post(`/api/savings-groups/${groupId}/members`, data),

  getSettings: (groupId) =>
    api.get(`/api/groups/${groupId}/settings`),

  updateSettings: (groupId, data) =>
    api.put(`/api/groups/${groupId}/settings`, data),
};

export const membersAPI = {
  getById: (memberId) =>
    api.get(`/api/members/${memberId}`),

  getDashboard: (memberId) =>
    api.get(`/api/members/${memberId}/dashboard`),
};

export default api;

