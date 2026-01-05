// Add video form handler
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('addVideoForm');
    
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const url = document.getElementById('videoUrl').value;
            const videoType = document.getElementById('videoType').value;
            const viewsCount = parseInt(document.getElementById('viewsCount').value);
            
            // Validate YouTube URL
            if (!isYouTubeUrl(url)) {
                showToast('Please enter a valid YouTube URL', 'error');
                return;
            }
            
            // Disable submit button
            const submitBtn = form.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.textContent = 'Adding...';
            
            try {
                const response = await fetch('/api/videos', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        url: url,
                        video_type: videoType,
                        views_requested: viewsCount
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showToast(`Video added successfully! ${viewsCount} views will be processed.`, 'success');
                    form.reset();
                } else {
                    showToast(data.error || 'Failed to add video', 'error');
                }
            } catch (error) {
                showToast('Network error. Please try again.', 'error');
                console.error('Error:', error);
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Add Video';
            }
        });
    }
});

function isYouTubeUrl(url) {
    const patterns = [
        /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\//i,
        /youtube\.com\/watch\?v=/i,
        /youtube\.com\/shorts\//i,
        /youtu\.be\//i
    ];
    
    return patterns.some(pattern => pattern.test(url));
}


