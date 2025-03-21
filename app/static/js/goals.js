/**
 * Goals-specific functionality for Echo application
 */

/**
 * Helper function to add ordinal suffix to a day
 */
function addOrdinalSuffix(day) {
    if (day >= 11 && day <= 13) {
        return day + 'th';
    }
    switch (day % 10) {
        case 1: return day + 'st';
        case 2: return day + 'nd';
        case 3: return day + 'rd';
        default: return day + 'th';
    }
}

/**
 * Helper function to format date as "April 15, 2025"
 */
function formatDateWithOrdinal(dateStr) {
    if (!dateStr) return 'N/A';
    const date = new Date(dateStr);
    const month = date.toLocaleString('default', { month: 'long' });
    const day = date.getDate();
    const year = date.getFullYear();
    return `${month} ${day}, ${year}`;
}

/**
 * Format all target dates on the page
 */
document.addEventListener('DOMContentLoaded', function() {
    // Format target dates on page load
    document.querySelectorAll('.goal-target-date .target-date').forEach(element => {
        // We don't need to modify this as the date is already formatted in the template
        // using strftime('%B %d, %Y')
    });

    // Handle Add Goal Form Submission
    const addGoalForm = document.getElementById('addGoalForm');
    if (addGoalForm) {
        addGoalForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = {
                title: document.getElementById('goalTitle').value,
                description: document.getElementById('goalDescription').value,
                target_date: document.getElementById('goalTargetDate').value,
                status: document.getElementById('goalStatus').value
            };

            try {
                const response = await authFetch('/api/goals', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });

                if (response.ok) {
                    const modal = bootstrap.Modal.getInstance(document.getElementById('addGoalModal'));
                    modal.hide();
                    addGoalForm.reset();
                    window.location.reload();
                } else {
                    const errorData = await response.json();
                    alert(`Failed to create goal: ${errorData.message || 'Unknown error'}`);
                }
            } catch (error) {
                console.error('Error creating goal:', error);
                alert('An error occurred while creating the goal');
            }
        });
    }

    // Handle Edit Goal Form Submission
    const editGoalForm = document.getElementById('editGoalForm');
    if (editGoalForm) {
        editGoalForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            const formData = {
                id: document.getElementById('editGoalId').value,
                title: document.getElementById('editGoalTitle').value,
                description: document.getElementById('editGoalDescription').value,
                target_date: document.getElementById('editGoalTargetDate').value,
                status: document.getElementById('editGoalStatus').value
            };

            try {
                const response = await authFetch(`/api/goals/${formData.id}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });

                if (response.ok) {
                    const modal = bootstrap.Modal.getInstance(document.getElementById('editGoalModal'));
                    modal.hide();
                    window.location.reload();
                } else {
                    const errorData = await response.json();
                    alert(`Failed to update goal: ${errorData.message || 'Unknown error'}`);
                }
            } catch (error) {
                console.error('Error updating goal:', error);
                alert('An error occurred while updating the goal');
            }
        });
    }
});

/**
 * Function to populate the edit modal with goal data
 */
function populateEditModal(id, title, description, target_date, status) {
    document.getElementById('editGoalId').value = id;
    document.getElementById('editGoalTitle').value = title;
    document.getElementById('editGoalDescription').value = description || '';
    
    // Format target_date for the date input (YYYY-MM-DD)
    if (target_date) {
        try {
            // Log the target_date for debugging
            console.log('Target date received:', target_date);
            
            // Parse the date - handle both ISO format and formatted strings
            let date;
            if (target_date.includes('-')) {
                // Already in ISO format or similar
                date = new Date(target_date);
            } else {
                // Try to parse formatted date like "April 15, 2023"
                const parts = target_date.split(' ');
                if (parts.length === 3) {
                    const month = parts[0];
                    const day = parseInt(parts[1].replace(',', ''));
                    const year = parseInt(parts[2]);
                    date = new Date(`${month} ${day}, ${year}`);
                } else {
                    date = new Date(target_date);
                }
            }
            
            // Check if date is valid
            if (!isNaN(date.getTime())) {
                const formattedDate = date.toISOString().split('T')[0]; // Convert to YYYY-MM-DD
                document.getElementById('editGoalTargetDate').value = formattedDate;
                console.log('Formatted date for input:', formattedDate);
            } else {
                console.error('Invalid date:', target_date);
                document.getElementById('editGoalTargetDate').value = '';
            }
        } catch (error) {
            console.error('Error parsing date:', error);
            document.getElementById('editGoalTargetDate').value = '';
        }
    } else {
        document.getElementById('editGoalTargetDate').value = '';
    }
    
    document.getElementById('editGoalStatus').value = status;
}

/**
 * Function to delete a goal
 */
async function deleteGoal() {
    const id = document.getElementById('editGoalId').value;
    if (confirm('Are you sure you want to delete this goal?')) {
        try {
            const response = await authFetch(`/api/goals/${id}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                const modal = bootstrap.Modal.getInstance(document.getElementById('editGoalModal'));
                modal.hide();
                window.location.reload();
            } else {
                const errorData = await response.json();
                alert(`Failed to delete goal: ${errorData.message || 'Unknown error'}`);
            }
        } catch (error) {
            console.error('Error deleting goal:', error);
            alert('An error occurred while deleting the goal');
        }
    }
}