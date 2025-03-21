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
    
    // Add Goal button functionality
    const addGoalBtn = document.querySelector('button.btn-primary');
    if (addGoalBtn && addGoalBtn.textContent.includes('Add Goal')) {
        addGoalBtn.addEventListener('click', openAddGoalModal);
    }
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
 * Opens the Add Goal modal
 */
function openAddGoalModal() {
    // Check if modal already exists
    let modal = document.getElementById('addGoalModal');
    
    // If modal doesn't exist, create it
    if (!modal) {
        const modalHTML = `
        <div class="modal fade" id="addGoalModal" tabindex="-1" aria-labelledby="addGoalModalLabel" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="addGoalModalLabel">Add New Goal</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <form id="addGoalForm">
                            <div class="mb-3">
                                <label for="goalTitle" class="form-label">Title</label>
                                <input type="text" class="form-control" id="goalTitle" required>
                            </div>
                            <div class="mb-3">
                                <label for="goalDescription" class="form-label">Description</label>
                                <textarea class="form-control" id="goalDescription" rows="3"></textarea>
                            </div>
                            <div class="mb-3">
                                <label for="goalTargetDate" class="form-label">Target Date</label>
                                <input type="date" class="form-control" id="goalTargetDate">
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" id="saveGoalBtn">Save Goal</button>
                    </div>
                </div>
            </div>
        </div>
        `;
        
        // Append modal to body
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        modal = document.getElementById('addGoalModal');
        
        // Add event listener to save button
        document.getElementById('saveGoalBtn').addEventListener('click', saveGoal);
    }
    
    // Show the modal
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
}

/**
 * Saves a new goal
 */
async function saveGoal() {
    const titleInput = document.getElementById('goalTitle');
    const descriptionInput = document.getElementById('goalDescription');
    const targetDateInput = document.getElementById('goalTargetDate');
    
    // Validate form
    if (!titleInput.value.trim()) {
        alert('Title is required');
        return;
    }
    
    // Prepare data
    const goalData = {
        title: titleInput.value.trim(),
        description: descriptionInput.value.trim(),
        target_date: targetDateInput.value || null
    };
    
    try {
        // Send request to create goal
        const response = await authFetch('/api/goals', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(goalData)
        });
        
        if (response.ok) {
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('addGoalModal'));
            modal.hide();
            
            // Refresh page to show new goal
            window.location.reload();
        } else {
            const errorData = await response.json();
            alert(`Failed to create goal: ${errorData.error || 'Unknown error'}`);
        }
    } catch (error) {
        console.error('Error creating goal:', error);
        alert('Failed to create goal. Please try again.');
    }
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