(function() {
    const searchInput = document.getElementById('userSearch');
    const searchResults = document.getElementById('searchResults');
    const documentId = window.COLLAB_CONFIG.documentId;
    let searchTimeout;
    
    // Get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');
    
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        const query = this.value.trim();
        
        if (query.length < 2) {
            searchResults.classList.remove('active');
            searchResults.innerHTML = '';
            return;
        }
        
        searchTimeout = setTimeout(() => {
            fetch(`/api/search-users/?q=${encodeURIComponent(query)}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('Search results:', data);
                    displaySearchResults(data.users);
                })
                .catch(error => {
                    console.error('Search error:', error);
                    searchResults.innerHTML = '<div style="padding: 12px; color: #f85149;">Error searching users</div>';
                    searchResults.classList.add('active');
                });
        }, 300);
    });
    
    function displaySearchResults(users) {
        if (users.length === 0) {
            searchResults.innerHTML = '<div style="padding: 12px; color: #8b8b8b;">No users found</div>';
            searchResults.classList.add('active');
            return;
        }
        
        searchResults.innerHTML = users.map(user => `
            <div class="search-result-item">
                <div class="user-info">
                    <div class="user-name">${escapeHtml(user.username)}</div>
                    <div class="user-email">${escapeHtml(user.email)}</div>
                </div>
                <div>
                    <select class="permission-select" id="permission-${user.id}" onclick="event.stopPropagation()">
                        <option value="view">View Only</option>
                        <option value="edit">Can Edit</option>
                    </select>
                    <button class="add-btn" onclick="event.stopPropagation(); addCollaborator(${user.id}, '${escapeHtml(user.username)}')">
                        Add
                    </button>
                </div>
            </div>
        `).join('');
        
        searchResults.classList.add('active');
    }
    
    function escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }
    
    function addCollaborator(userId, username) {
        const permissionSelect = document.getElementById(`permission-${userId}`);
        const permissionLevel = permissionSelect ? permissionSelect.value : 'view';
        
        fetch(`/api/add-collaborator/${documentId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({
                user_id: userId,
                permission_level: permissionLevel
            })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Failed to add collaborator');
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert(data.error || 'Failed to add collaborator');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert(error.message || 'Failed to add collaborator');
        });
    }
    
    // Handle permission changes
    document.querySelectorAll('.permission-change').forEach(select => {
        select.addEventListener('change', function() {
            const collaboratorId = this.dataset.collaboratorId;
            const newPermission = this.value;
            
            fetch(`/api/update-permission/${documentId}/${collaboratorId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({
                    permission_level: newPermission
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to update permission');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    // Show success message
                    const msg = document.createElement('div');
                    msg.style.cssText = 'position: fixed; top: 20px; right: 20px; background: #0e4429; color: #3fb950; padding: 12px 20px; border-radius: 6px; z-index: 10000;';
                    msg.textContent = data.message;
                    document.body.appendChild(msg);
                    setTimeout(() => msg.remove(), 3000);
                } else {
                    alert(data.error || 'Failed to update permission');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Failed to update permission');
            });
        });
    });
    
    // Close search results when clicking outside
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
            searchResults.classList.remove('active');
        }
    });
})();