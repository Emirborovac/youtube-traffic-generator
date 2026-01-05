// Management tab handler
let currentVideos = [];
let currentFilter = '';
let currentSearch = '';
let currentPage = 0;
let pageSize = 25;
let isLoading = false;

document.addEventListener('DOMContentLoaded', () => {
    const statusFilter = document.getElementById('statusFilter');
    const searchInput = document.getElementById('searchInput');
    
    if (statusFilter) {
        statusFilter.addEventListener('change', () => {
            currentFilter = statusFilter.value;
            loadVideos(true);
        });
    }
    
    if (searchInput) {
        searchInput.addEventListener('input', debounce(() => {
            currentSearch = searchInput.value;
            loadVideos(true);
        }, 500));
    }
});

async function loadVideos(reset = true) {
    const tbody = document.getElementById('videosTableBody');
    
    if (!tbody) return;
    
    if (reset) {
        currentPage = 0;
        currentVideos = [];
    }
    
    if (isLoading) return;
    isLoading = true;
    
    try {
        let url = '/api/videos';
        const params = new URLSearchParams();
        
        if (currentFilter) params.append('status', currentFilter);
        if (currentSearch) params.append('search', currentSearch);
        
        if (params.toString()) {
            url += '?' + params.toString();
        }
        
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.success) {
            currentVideos = data.videos;
            renderVideos(reset);
        } else {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center">Error loading videos</td></tr>';
        }
    } catch (error) {
        console.error('Error loading videos:', error);
        tbody.innerHTML = '<tr><td colspan="6" class="text-center">Network error</td></tr>';
    } finally {
        isLoading = false;
    }
}

function renderVideos(reset = true) {
    const tbody = document.getElementById('videosTableBody');
    
    if (currentVideos.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center">No videos found</td></tr>';
        return;
    }
    
    // Calculate page videos
    const startIdx = currentPage * pageSize;
    const endIdx = startIdx + pageSize;
    const pageVideos = currentVideos.slice(startIdx, endIdx);
    
    if (reset) {
        tbody.innerHTML = '';
    }
    
    const newRows = pageVideos.map(video => `
        <tr>
            <td>
                <a href="${video.url}" target="_blank" class="video-url" title="${video.url}">
                    ${video.url}
                </a>
            </td>
            <td>
                <span class="badge badge-${video.video_type}">${video.video_type}</span>
            </td>
            <td>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${video.progress_percentage}%"></div>
                </div>
                <div class="progress-text">${video.views_completed} / ${video.views_requested}</div>
            </td>
            <td>
                <span class="badge badge-${video.status}">${video.status}</span>
            </td>
            <td>${formatDate(video.created_at)}</td>
            <td>
                <div class="action-buttons">
                    ${renderActionButtons(video)}
                </div>
            </td>
        </tr>
    `).join('');
    
    tbody.insertAdjacentHTML('beforeend', newRows);
    
    // Add event listeners to buttons
    attachActionListeners();
    
    currentPage++;
}

// Infinite scroll for table
document.addEventListener('DOMContentLoaded', () => {
    const tableContainer = document.querySelector('.table-container');
    
    if (tableContainer) {
        tableContainer.addEventListener('scroll', () => {
            const scrollTop = tableContainer.scrollTop;
            const scrollHeight = tableContainer.scrollHeight;
            const clientHeight = tableContainer.clientHeight;
            
            // Load more when near bottom (100px threshold)
            if (scrollTop + clientHeight >= scrollHeight - 100) {
                const startIdx = currentPage * pageSize;
                if (startIdx < currentVideos.length && !isLoading) {
                    renderVideos(false);
                }
            }
        });
    }
});

function renderActionButtons(video) {
    const buttons = [];
    
    if (video.status === 'pending' || video.status === 'paused') {
        buttons.push(`
            <button class="btn btn-success" onclick="updateVideoStatus(${video.id}, 'active')">
                Activate
            </button>
        `);
    }
    
    if (video.status === 'active') {
        buttons.push(`
            <button class="btn btn-warning" onclick="updateVideoStatus(${video.id}, 'paused')">
                Pause
            </button>
        `);
    }
    
    if (video.status !== 'stopped' && video.status !== 'completed') {
        buttons.push(`
            <button class="btn btn-danger" onclick="updateVideoStatus(${video.id}, 'stopped')">
                Stop
            </button>
        `);
    }
    
    buttons.push(`
        <button class="btn btn-danger" onclick="deleteVideo(${video.id})">
            Delete
        </button>
    `);
    
    return buttons.join('');
}

function attachActionListeners() {
    // Listeners are attached via onclick in the HTML for simplicity
}

async function updateVideoStatus(videoId, status) {
    try {
        const response = await fetch(`/api/videos/${videoId}/status`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ status: status })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast(`Video ${status} successfully`, 'success');
            loadVideos();
        } else {
            showToast(data.error || 'Failed to update status', 'error');
        }
    } catch (error) {
        showToast('Network error', 'error');
        console.error('Error:', error);
    }
}

async function deleteVideo(videoId) {
    if (!confirm('Are you sure you want to delete this video and all its sessions?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/videos/${videoId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Video deleted successfully', 'success');
            loadVideos();
        } else {
            showToast(data.error || 'Failed to delete video', 'error');
        }
    } catch (error) {
        showToast('Network error', 'error');
        console.error('Error:', error);
    }
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);
    
    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    
    return date.toLocaleDateString();
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Auto-refresh every 10 seconds when on management tab
setInterval(() => {
    const managementTab = document.getElementById('managementTab');
    if (managementTab && managementTab.classList.contains('active')) {
        loadVideos();
    }
}, 10000);

