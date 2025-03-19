/**
 * Authentication utilities for Echo application
 */

/**
 * Sets up the Authorization header with JWT token for fetch requests
 * @param {Object} options - The fetch options object
 * @returns {Object} - The updated fetch options with Authorization header
 */
function setupAuthHeader(options = {}) {
    const token = localStorage.getItem('access_token');
    if (!token) return options;
    
    // Create headers object if it doesn't exist
    if (!options.headers) {
        options.headers = {};
    }
    
    // Add Authorization header with Bearer token
    options.headers['Authorization'] = `Bearer ${token}`;
    
    return options;
}

/**
 * Handles login form submission
 * @param {string} formId - The ID of the login form
 * @param {string} emailId - The ID of the email input field
 * @param {string} passwordId - The ID of the password input field
 */
function handleLogin(formId, emailId, passwordId) {
    document.getElementById(formId).addEventListener('submit', function(e) {
        e.preventDefault();
        const email = document.getElementById(emailId).value;
        const password = document.getElementById(passwordId).value;
        
        // Extract domain from email for tenant determination
        const emailDomain = email.split('@')[1];
        
        fetch('/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password, domain: emailDomain })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
            } else {
                // Store tokens in localStorage
                localStorage.setItem('access_token', data.access_token);
                localStorage.setItem('refresh_token', data.refresh_token);
                localStorage.setItem('user', JSON.stringify(data.user));
                
                // Redirect to dashboard
                window.location.href = '/auth/dashboard';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred during login');
        });
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
    document.getElementById(formId).addEventListener('submit', function(e) {
        e.preventDefault();
        const domain_name = document.getElementById(domainNameId).value;
        const email = document.getElementById(emailId).value;
        const password = document.getElementById(passwordId).value;
        
        // Validate that email domain matches tenant domain
        const emailDomain = email.split('@')[1];
        if (emailDomain !== domain_name) {
            alert('Email domain must match the organization domain');
            return;
        }
        
        fetch('/auth/register-tenant', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ domain_name, email, password })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
            } else {
                // Store tokens in localStorage
                localStorage.setItem('access_token', data.access_token);
                localStorage.setItem('refresh_token', data.refresh_token);
                localStorage.setItem('user', JSON.stringify(data.user));
                localStorage.setItem('tenant', JSON.stringify(data.tenant));
                
                // Redirect to dashboard
                window.location.href = '/auth/dashboard';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred during registration');
        });
    });
}

/**
 * Initializes modal functionality
 * @param {string} modalId - The ID of the modal element
 */
function initModal(modalId) {
    // Close modal when clicking on X
    const closeBtn = document.querySelector(`#${modalId} .close`);
    if (closeBtn) {
        closeBtn.addEventListener('click', function() {
            document.getElementById(modalId).style.display = 'none';
        });
    }
    
    // Close modal when clicking outside of it
    window.addEventListener('click', function(event) {
        if (event.target.id === modalId) {
            document.getElementById(modalId).style.display = 'none';
        }
    });
}
