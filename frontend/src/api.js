/**
 * NexaDesk API Client
 * Handles all communication with the FastAPI backend.
 * Auto-attaches JWT token to every request.
 * Handles token expiry and error responses gracefully.
 */

const API_BASE = 'http://localhost:8000';

// ─────────────────────────────────────────
// Token Management
// ─────────────────────────────────────────
const Auth = {
  getToken: () => sessionStorage.getItem('nd_token'),
  setToken: (token) => sessionStorage.setItem('nd_token', token),
  removeToken: () => sessionStorage.removeItem('nd_token'),
  
  getUser: () => {
    const u = sessionStorage.getItem('nd_user');
    return u ? JSON.parse(u) : null;
  },
  setUser: (user) => sessionStorage.setItem('nd_user', JSON.stringify(user)),
  removeUser: () => sessionStorage.removeItem('nd_user'),

  isLoggedIn: () => !!sessionStorage.getItem('nd_token'),

  logout: () => {
    sessionStorage.removeItem('nd_token');
    sessionStorage.removeItem('nd_user');
  },
};

// ─────────────────────────────────────────
// Core Fetch Wrapper
// ─────────────────────────────────────────
async function apiFetch(path, options = {}) {
  const token = Auth.getToken();
  
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...options.headers,
  };

  try {
    const response = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers,
    });

    // Handle 401 (token expired)
    if (response.status === 401) {
      Auth.logout();
      showToast('Session expired. Please log in again.', 'error');
      return null;
    }

    const data = await response.json();

    if (!response.ok) {
      const msg = data.detail || `Error ${response.status}`;
      throw new Error(typeof msg === 'string' ? msg : JSON.stringify(msg));
    }

    return data;
  } catch (err) {
    if (err.message.includes('Failed to fetch') || err.message.includes('NetworkError')) {
      // Backend not running — use demo mode
      return null;
    }
    throw err;
  }
}

// ─────────────────────────────────────────
// API Methods
// ─────────────────────────────────────────
const API = {
  // Auth
  login: (email, password) =>
    apiFetch('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),

  register: (data) =>
    apiFetch('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Tickets
  submitTicket: (data) =>
    apiFetch('/tickets/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  listTickets: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return apiFetch(`/tickets/?${qs}`);
  },

  getTicket: (id) => apiFetch(`/tickets/${id}`),

  submitFeedback: (ticketId, rating, feedback) =>
    apiFetch(`/tickets/${ticketId}/feedback`, {
      method: 'POST',
      body: JSON.stringify({ rating, feedback }),
    }),

  // Analytics
  getDashboard: () => apiFetch('/analytics/dashboard'),
  getROI: () => apiFetch('/analytics/roi'),

  // Knowledge Base
  getKB: (search = '', category = '') => {
    const params = new URLSearchParams();
    if (search) params.set('search', search);
    if (category) params.set('category', category);
    return apiFetch(`/kb/?${params}`);
  },

  // Health
  health: () => apiFetch('/health'),
};

// Export
window.API = API;
window.Auth = Auth;
