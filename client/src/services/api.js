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

  getGroupDashboard: (groupId) =>
    api.get(`/api/savings-groups/${groupId}/dashboard`),
};

export const membersAPI = {
  getById: (memberId) =>
    api.get(`/api/members/${memberId}`),

  getDashboard: (memberId) =>
    api.get(`/api/members/${memberId}/dashboard`),
};

export const meetingsAPI = {
  // Get all meetings for a group
  getGroupMeetings: (groupId, params) =>
    api.get(`/api/groups/${groupId}/meetings`, { params }),

  // Get meeting detail
  getMeetingDetail: (meetingId) =>
    api.get(`/api/meetings/${meetingId}`),

  // Create new meeting
  createMeeting: (groupId, data) =>
    api.post(`/api/groups/${groupId}/meetings`, data),

  // Update meeting
  updateMeeting: (meetingId, data) =>
    api.put(`/api/meetings/${meetingId}`, data),

  // Delete meeting
  deleteMeeting: (meetingId) =>
    api.delete(`/api/meetings/${meetingId}`),

  // Start meeting
  startMeeting: (meetingId) =>
    api.post(`/api/meetings/${meetingId}/start`),

  // Complete meeting
  completeMeeting: (meetingId) =>
    api.post(`/api/meetings/${meetingId}/complete`),

  // Record attendance
  recordAttendance: (meetingId, data) =>
    api.post(`/api/meetings/${meetingId}/attendance`, data),

  // Transaction recording endpoints
  recordSavingsTransaction: (meetingId, data) =>
    api.post(`/api/meetings/${meetingId}/savings`, data),
  recordFine: (meetingId, data) =>
    api.post(`/api/meetings/${meetingId}/fines`, data),
  recordLoanRepayment: (meetingId, data) =>
    api.post(`/api/meetings/${meetingId}/loan-repayments`, data),

  // Training endpoints
  createTrainingSession: (meetingId, data) =>
    api.post(`/api/meetings/${meetingId}/trainings`, data),
  recordTrainingAttendance: (trainingId, data) =>
    api.post(`/api/trainings/${trainingId}/attendance`, data),

  // Voting endpoints
  createVotingSession: (meetingId, data) =>
    api.post(`/api/meetings/${meetingId}/votings`, data),
  recordVotes: (votingId, data) =>
    api.post(`/api/votings/${votingId}/votes`, data),

  // Get meeting by ID (alias for compatibility)
  getById: (meetingId) =>
    api.get(`/api/meetings/${meetingId}`),

  // Get saving types for a group
  getSavingTypes: (groupId) =>
    api.get(`/api/groups/${groupId}/saving-types`),

  // Aliases for transaction recording (for compatibility)
  recordSavings: (meetingId, data) =>
    api.post(`/api/meetings/${meetingId}/savings`, data),
  recordFines: (meetingId, data) =>
    api.post(`/api/meetings/${meetingId}/fines`, data),
  createTraining: (meetingId, data) =>
    api.post(`/api/meetings/${meetingId}/trainings`, data),
  createVoting: (meetingId, data) =>
    api.post(`/api/meetings/${meetingId}/votings`, data),
};

// Documents API
export const documentsAPI = {
  // Upload documents for an activity
  uploadActivityDocuments: (activityId, formData) =>
    api.post(`/api/activities/${activityId}/documents`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),

  // Get all documents for an activity
  getActivityDocuments: (activityId) =>
    api.get(`/api/activities/${activityId}/documents`),

  // Get document details
  getDocument: (documentId) =>
    api.get(`/api/documents/${documentId}`),

  // Download document
  downloadDocument: (documentId) =>
    api.get(`/api/documents/${documentId}/download`, { responseType: 'blob' }),

  // Get document preview/thumbnail
  getDocumentPreview: (documentId) =>
    api.get(`/api/documents/${documentId}/preview`, { responseType: 'blob' }),

  // Update document metadata
  updateDocument: (documentId, data) =>
    api.put(`/api/documents/${documentId}`, data),

  // Compress document manually
  compressDocument: (documentId) =>
    api.post(`/api/documents/${documentId}/compress`),

  // Soft delete document
  deleteDocument: (documentId) =>
    api.delete(`/api/documents/${documentId}`),

  // Permanent delete document
  permanentDeleteDocument: (documentId) =>
    api.delete(`/api/documents/${documentId}/permanent-delete`),

  // Get storage usage
  getActivityStorageUsage: (activityId) =>
    api.get(`/api/activities/${activityId}/storage-usage`),

  getGroupStorageUsage: (groupId) =>
    api.get(`/api/groups/${groupId}/storage-usage`),

  getOverallStorageUsage: () =>
    api.get(`/api/storage-usage`),

  // Cascade delete files
  cascadeDeleteMeetingFiles: (meetingId) =>
    api.delete(`/api/meetings/${meetingId}/cascade-delete-files`),

  cascadeDeleteGroupFiles: (groupId) =>
    api.delete(`/api/groups/${groupId}/cascade-delete-files`),

  cascadeDeleteMemberFiles: (memberId) =>
    api.delete(`/api/members/${memberId}/cascade-delete-files`),
};

// Transactions API - for editing transactions
export const transactionsAPI = {
  // Update savings transaction
  updateSavingsTransaction: (transactionId, data) =>
    api.put(`/api/savings-transactions/${transactionId}`, data),

  // Update fine
  updateFine: (fineId, data) =>
    api.put(`/api/fines/${fineId}`, data),

  // Update loan repayment
  updateLoanRepayment: (repaymentId, data) =>
    api.put(`/api/loan-repayments/${repaymentId}`, data),

  // Update training session
  updateTraining: (trainingId, data) =>
    api.put(`/api/trainings/${trainingId}`, data),

  // Update voting session
  updateVoting: (votingId, data) =>
    api.put(`/api/votings/${votingId}`, data),
};

export default api;

