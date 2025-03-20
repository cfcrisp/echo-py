/**
 * Authentication utilities for Echo application
 */

/**
 * Sets up the Authorization header with JWT token for fetch requests
 * @param {Object} options - The fetch options object
 * @returns {Object} - Updated options with Authorization header
 */
function setupAuthHeader(options = {}) {
    const token = localStorage.getItem('access_token');
    if (!token) return options;
    options.headers = options.headers || {};
    options.headers['Authorization'] = `Bearer ${token}`;
    return options;
}

/**
 * Refreshes the access token using the refresh token
 * @returns {Promise} - Resolves with new tokens or rejects with error
 */
function refreshToken() {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) throw new Error('No refresh token available');

    return fetch('/auth/refresh', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken })
    })
    .then(response => response.json())
    .then(data => {
        if (data.access_token) {
            localStorage.setItem('access_token', data.access_token);
            return data;
        }
        throw new Error('Refresh failed');
    })
    .catch(error => {
        console.error('Token refresh error:', error);
        logout(); // Logout if refresh fails
        throw error;
    });
}

/**
 * Handles fetch with automatic token refresh on 401
 * @param {string} url - The endpoint URL
 * @param {Object} options - Fetch options
 * @returns {Promise} - Fetch response
 */
async function authFetch(url, options = {}) {
    options = setupAuthHeader(options);
    let response = await fetch(url, options);

    if (response.status === 401) {
        await refreshToken();
        options = setupAuthHeader(options); // Update with new token
        response = await fetch(url, options);
    }
    return response;
}

/**
 * Handles login form submission
 * @param {string} formId - The ID of the login form
 * @param {string} emailId - The ID of the email input field
 * @param {string} passwordId - The ID of the password input field
 */
function handleLogin(formId, emailId, passwordId) {
    const form = document.getElementById(formId);
    if (!form) {
        console.error('Form not found:', formId);
        return;
    }
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        const email = document.getElementById(emailId).value;
        const password = document.getElementById(passwordId).value;
        const emailDomain = email.split('@')[1];
        const submitBtn = form.querySelector('button[type="submit"]');
        
        submitBtn.disabled = true;
        submitBtn.textContent = 'Logging in...';

        try {
            const response = await fetch('/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password, domain: emailDomain })
            });
            const data = await response.json();

            if (data.error) throw new Error(data.error);

            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('refresh_token', data.refresh_token);
            localStorage.setItem('user', JSON.stringify(data.user));
            
            // Close the modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('login-modal'));
            modal.hide();
            
            window.location.href = '/auth/dashboard';
        } catch (error) {
            alert(error.message || 'Login failed');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Login';
        }
    });
}

/**
 * Handles tenant registration form submission
 * @param {string} formId - The ID of the registration form
 * @param {string} domainNameId - The ID of the domain name input field
 * @param {string} emailId - The ID of the email input field
 * @param {string} passwordId - The ID of the password input field
 */
function handleTenantRegistration(formId, domainNameId, emailId, passwordId) {
    const form = document.getElementById(formId);
    if (!form) {
        console.error('Form not found:', formId);
        return;
    }
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        const domain_name = document.getElementById(domainNameId).value;
        const email = document.getElementById(emailId).value;
        const password = document.getElementById(passwordId).value;
        const submitBtn = form.querySelector('button[type="submit"]');

        if (email.split('@')[1] !== domain_name) {
            alert('Email domain must match the organization domain');
            return;
        }

        submitBtn.disabled = true;
        submitBtn.textContent = 'Registering...';

        try {
            const response = await fetch('/auth/register-tenant', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ domain_name, email, password })
            });
            const data = await response.json();

            if (data.error) throw new Error(data.error);

            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('refresh_token', data.refresh_token);
            localStorage.setItem('user', JSON.stringify(data.user));
            localStorage.setItem('tenant', JSON.stringify(data.tenant));
            
            // Close the modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('register-modal'));
            modal.hide();
            
            window.location.href = '/auth/dashboard';
        } catch (error) {
            alert(error.message || 'Registration failed');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Register';
        }
    });
}

/**
 * Logs out the user and redirects to login page
 */
function logout() {
    localStorage.clear();
    window.location.href = '/';
}

// Expose functions for use in other scripts if needed
window.authUtils = { handleLogin, handleTenantRegistration, logout, authFetch };