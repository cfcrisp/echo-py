/**
 * Dashboard utilities for Echo application
 */

/**
 * Initializes dashboard functionality
 */
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tabs
    const triggerTabList = document.querySelectorAll('#dashboardTabs button[data-bs-toggle="tab"]');
    triggerTabList.forEach(triggerEl => {
        const tabTrigger = new bootstrap.Tab(triggerEl);
        triggerEl.addEventListener('click', event => {
            event.preventDefault();
            tabTrigger.show();
        });
    });

    // Attach event listeners to action buttons
    attachActionEventListeners();
});


async function loadInitiatives() {
    const container = document.querySelector('.initiative-list');
    container.innerHTML = '<p>Loading...</p>';

    try {
        const response = await authFetch('/api/initiatives');
        const initiatives = await response.json();
        
        if (!Array.isArray(initiatives)) {
            container.innerHTML = '<p class="text-muted">No initiatives found</p>';
            return;
        }

        container.innerHTML = initiatives.map(initiative => `
            <div class="initiative-item d-flex justify-content-between align-items-start mb-3" data-id="${initiative.id}">
                <div>
                    <h5>${initiative.title}</h5>
                    <p class="text-muted">${initiative.description}</p>
                    <a href="#" class="card-link">${initiative.goal}</a> • ${initiative.ideas_count} ideas
                </div>
                <div class="initiative-actions">
                    <button class="btn-action btn-edit" data-record-id="${initiative.id}" data-record-type="initiative"><span class="icon">✏️</span></button>
                    <button class="btn-action btn-delete" data-record-id="${initiative.id}" data-record-type="initiative"><span class="icon">🗑️</span></button>
                </div>
            </div>
        `).join('');
        
        // Attach event listeners to the newly created buttons
        attachActionEventListeners();
    } catch (error) {
        container.innerHTML = '<p>Error loading initiatives</p>';
        console.error('Error:', error);
    }
}

/**
 * Attaches event listeners to action buttons for all dashboard sections
 */
function attachActionEventListeners() {
    // Edit buttons
    document.querySelectorAll('.btn-action.btn-edit').forEach(btn => {
        btn.addEventListener('click', function() {
            const id = this.dataset.recordId;
            const type = this.dataset.recordType;
            alert(`Edit ${type} ${id} - Implement modal here`);
            // TODO: Open edit modal and fetch record details
        });
    });

    // Delete buttons
    document.querySelectorAll('.btn-action.btn-delete').forEach(btn => {
        btn.addEventListener('click', async function() {
            const id = this.dataset.recordId;
            const type = this.dataset.recordType;
            if (confirm(`Are you sure you want to delete this ${type}?`)) {
                try {
                    await authFetch(`/api/${type}s/${id}`, { method: 'DELETE' });
                    // Refresh the page to show updated data
                    window.location.reload();
                } catch (error) {
                    alert(`Failed to delete ${type}`);
                }
            }
        });
    });
}

/**
 * Handles tab persistence
 */
function setupTabPersistence() {
    const tabs = document.querySelectorAll('#dashboardTabs .nav-link');
    const activeTab = localStorage.getItem('activeTab') || 'initiatives-tab';

    // Set initial active tab
    document.getElementById(activeTab)?.click();

    tabs.forEach(tab => {
        tab.addEventListener('shown.bs.tab', function() {
            localStorage.setItem('activeTab', this.id);
        });
    });
}

/**
 * Initialize additional functionality when needed
 */
function initializeAdditionalFeatures() {
    setupTabPersistence();
    if (document.querySelector('.initiative-list')) {
        loadInitiatives();
    }
}