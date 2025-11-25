// API Base URL (with local override support)
let API_URL = localStorage.getItem('api_base_url') || 'http://localhost:8000';
// Also expose on window for any inline scripts
window.API_URL = API_URL;
// Allow overriding at runtime, persists to localStorage
window.setApiBase = function(url){
  if(!url) return;
  API_URL = url.replace(/\/$/,'');
  window.API_URL = API_URL;
  localStorage.setItem('api_base_url', API_URL);
};
// Try to resolve a working API base from common candidates
// We validate by checking an actual API route, not just '/'
window.resolveApiBase = async function(candidates){
  const fromLocation = (typeof location !== 'undefined' && location.protocol && location.hostname)
    ? `${location.protocol}//${location.hostname}:8000` : null;
  const defaults = [
    localStorage.getItem('api_base_url'),
    fromLocation,
    'http://127.0.0.1:8000',
    'http://localhost:8000'
  ];
  const list = (candidates && Array.isArray(candidates) ? candidates : defaults)
    .filter(Boolean)
    .map(u=>u.replace(/\/$/,''));
  for (const base of list){
    try {
      const res = await fetch(`${base}/api/most-active`, { method:'GET' });
      if (res.ok){
        API_URL = base;
        window.API_URL = API_URL;
        localStorage.setItem('api_base_url', API_URL);
        return API_URL;
      }
    } catch(e) { /* try next */ }
  }
  // Fallback to previous or default
  window.API_URL = API_URL;
  return API_URL;
};

// Authentication utilities
class Auth {
    static setToken(token) {
        localStorage.setItem('access_token', token);
    }

    static getToken() {
        return localStorage.getItem('access_token');
    }

    static removeToken() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
    }

    static setUser(user) {
        localStorage.setItem('user', JSON.stringify(user));
    }

    static getUser() {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    }

    static isAuthenticated() {
        return !!this.getToken();
    }

    static isAdmin() {
        const user = this.getUser();
        return user && user.role === 'admin';
    }

    static logout() {
        this.removeToken();
        window.location.href = 'index.html';
    }

    static async checkAuth() {
        if (!this.isAuthenticated()) {
            window.location.href = 'index.html';
            return false;
        }
        return true;
    }

    static getAuthHeader() {
        const token = this.getToken();
        return token ? { 'Authorization': `Bearer ${token}` } : {};
    }
}

// Login function (identifier can be email or username); adminMode selects admin endpoint
async function login(identifier, password, adminMode = false) {
    try {
        // Ensure API base is resolved
        try { if (typeof window.resolveApiBase === 'function') { await window.resolveApiBase(); } } catch(e) {}
        const baseFromLocation = (typeof location!=='undefined' && location.protocol && location.hostname) ? `${location.protocol}//${location.hostname}:8000` : null;
        const base = (baseFromLocation || (typeof window !== 'undefined' && window.API_URL) || localStorage.getItem('api_base_url') || API_URL);
        const form = new URLSearchParams();
        form.append('username', identifier);
        form.append('password', password);

        const url = `${base.replace(/\/$/,'')}${adminMode ? '/auth/login/admin' : '/auth/login'}`;
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: form
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || (adminMode ? 'Admin login failed' : 'Login failed'));
        }

        const data = await response.json();
        Auth.setToken(data.access_token);
        Auth.setUser(data.user);
        
        return { success: true, user: data.user };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// Register function
async function register(username, email, password, fullName = '') {
    try {
        try { if (typeof window.resolveApiBase === 'function') { await window.resolveApiBase(); } } catch(e) {}
        const baseFromLocation = (typeof location!=='undefined' && location.protocol && location.hostname) ? `${location.protocol}//${location.hostname}:8000` : null;
        const base = (baseFromLocation || (typeof window !== 'undefined' && window.API_URL) || localStorage.getItem('api_base_url') || API_URL);
        const response = await fetch(`${base.replace(/\/$/,'')}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username,
                email,
                password,
                full_name: fullName
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Registration failed');
        }

        const data = await response.json();
        Auth.setToken(data.access_token);
        Auth.setUser(data.user);
        
        return { success: true, user: data.user };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// Show error message
function showError(elementId, message) {
    const errorEl = document.getElementById(elementId);
    if (errorEl) {
        errorEl.textContent = message;
        errorEl.classList.remove('hidden');
        setTimeout(() => {
            errorEl.classList.add('hidden');
        }, 5000);
    }
}

// Show success message
function showSuccess(elementId, message) {
    const successEl = document.getElementById(elementId);
    if (successEl) {
        successEl.textContent = message;
        successEl.classList.remove('hidden');
        setTimeout(() => {
            successEl.classList.add('hidden');
        }, 3000);
    }
}
