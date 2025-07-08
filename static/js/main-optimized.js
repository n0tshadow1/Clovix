class VideoDownloader {
    constructor() {
        this.currentDownloadId = null;
        this.progressInterval = null;
        this.selectedType = 'video'; // Default to video
        this.videoData = null;
        this.init();
    }

    init() {
        this.bindEvents();
        console.log('VideoDownloader initialized successfully');
    }

    bindEvents() {
        // URL form submissions
        document.querySelectorAll('.url-form').forEach(form => {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                const input = form.querySelector('.video-url');
                this.analyzeVideo(input.value.trim());
            });
        });

        // Format type selection
        document.addEventListener('click', (e) => {
            if (e.target.closest('.format-type-option')) {
                this.handleFormatTypeSelection(e.target.closest('.format-type-option'));
            }
        });

        // Quick download button
        document.getElementById('quick-download-btn')?.addEventListener('click', () => {
            this.quickDownload();
        });

        // Advanced options toggle
        document.getElementById('advanced-toggle')?.addEventListener('click', () => {
            this.toggleAdvancedOptions();
        });

        // Custom download button
        document.getElementById('custom-download-btn')?.addEventListener('click', () => {
            this.customDownload();
        });
    }

    showLoading(show = true) {
        document.getElementById('loading').style.display = show ? 'block' : 'none';
        document.querySelectorAll('.analyze-btn').forEach(btn => {
            btn.disabled = show;
        });
    }

    showError(message) {
        const errorDiv = document.getElementById('error-display');
        const errorMessage = document.getElementById('error-message');
        
        // Convert newlines to HTML breaks for proper formatting
        const formattedMessage = message.replace(/\n/g, '<br>');
        errorMessage.innerHTML = formattedMessage;
        
        errorDiv.style.display = 'block';
        this.hideVideoInfo();
    }

    hideError() {
        document.getElementById('error-display').style.display = 'none';
    }

    handleFormatTypeSelection(element) {
        // Remove active class from all options
        document.querySelectorAll('.format-type-option').forEach(opt => {
            opt.classList.remove('active');
        });
        
        // Add active class to selected option
        element.classList.add('active');
        
        // Update selected type
        this.selectedType = element.dataset.type;
        
        // Update advanced options if visible
        if (document.getElementById('advanced-options').style.display !== 'none') {
            this.populateAdvancedOptions();
        }
    }

    showVideoInfo(videoData) {
        this.videoData = videoData;
        
        // Hide other sections
        this.hideError();
        document.getElementById('loading').style.display = 'none';
        
        // Populate video information
        const thumbnail = document.getElementById('video-thumbnail');
        const title = document.getElementById('video-title');
        const uploader = document.getElementById('video-uploader');
        const duration = document.getElementById('video-duration');
        const views = document.getElementById('video-views');
        
        if (thumbnail && videoData.thumbnail) {
            thumbnail.src = videoData.thumbnail;
            thumbnail.alt = videoData.title || 'Video Thumbnail';
        }
        
        if (title) {
            title.textContent = videoData.title || 'Unknown Title';
            title.style.color = 'white';
        }
        
        if (uploader) {
            uploader.textContent = videoData.uploader || 'Unknown';
        }
        
        if (duration) {
            duration.textContent = videoData.duration || 'Unknown';
        }
        
        if (views && videoData.view_count) {
            views.textContent = this.formatNumber(videoData.view_count);
        }
        
        // Show video info section
        document.getElementById('video-info').style.display = 'block';
        console.log('Video info section should now be visible');
        
        // Populate advanced options
        this.populateAdvancedOptions();
    }

    hideVideoInfo() {
        document.getElementById('video-info').style.display = 'none';
        this.hideDownloadProgress();
    }

    populateAdvancedOptions() {
        if (!this.videoData || !this.videoData.formats) return;

        const qualitySelect = document.getElementById('quality-select');
        const formatSelect = document.getElementById('format-select');
        
        if (!qualitySelect || !formatSelect) return;

        // Clear existing options (keep first default option)
        qualitySelect.innerHTML = '<option value="">Best Available</option>';
        formatSelect.innerHTML = '<option value="">Auto</option>';

        if (this.selectedType === 'video') {
            // Populate video qualities
            const availableHeights = [...new Set(this.videoData.formats.map(f => f.height))].sort((a, b) => b - a);
            
            availableHeights.forEach(height => {
                const format = this.videoData.formats.find(f => f.height === height);
                if (format) {
                    let label;
                    if (height >= 2160) label = '4K (2160p)';
                    else if (height >= 1440) label = '2K (1440p)';
                    else if (height >= 1080) label = '1080p';
                    else if (height >= 720) label = '720p';
                    else if (height >= 480) label = '480p';
                    else if (height >= 360) label = '360p';
                    else if (height >= 240) label = '240p';
                    else label = '144p';
                    
                    const option = document.createElement('option');
                    option.value = format.format_id;
                    option.textContent = label;
                    qualitySelect.appendChild(option);
                }
            });

            // Populate video formats
            const availableExts = [...new Set(this.videoData.formats.map(f => f.ext))];
            availableExts.forEach(ext => {
                const option = document.createElement('option');
                option.value = ext;
                option.textContent = ext.toUpperCase();
                formatSelect.appendChild(option);
            });
        } else {
            // Audio qualities
            const audioQualities = [
                { value: 'bestaudio', label: 'Best Quality' },
                { value: 'bestaudio[abr<=320]', label: '320 kbps' },
                { value: 'bestaudio[abr<=192]', label: '192 kbps' },
                { value: 'bestaudio[abr<=128]', label: '128 kbps' }
            ];
            
            audioQualities.forEach(quality => {
                const option = document.createElement('option');
                option.value = quality.value;
                option.textContent = quality.label;
                qualitySelect.appendChild(option);
            });

            // Audio formats
            const audioFormats = ['mp3', 'm4a', 'ogg', 'wav'];
            audioFormats.forEach(format => {
                const option = document.createElement('option');
                option.value = format;
                option.textContent = format.toUpperCase();
                formatSelect.appendChild(option);
            });
        }
    }

    toggleAdvancedOptions() {
        const panel = document.getElementById('advanced-options');
        const isHidden = panel.style.display === 'none';
        
        panel.style.display = isHidden ? 'block' : 'none';
        
        if (isHidden) {
            this.populateAdvancedOptions();
        }
    }

    async quickDownload() {
        const activeForm = document.querySelector('.tab-pane.active .url-form');
        const url = activeForm.querySelector('.video-url').value.trim();

        if (!url) {
            this.showError('Please enter a video URL');
            return;
        }

        this.showDownloadProgress();

        try {
            const response = await fetch('/download_video', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    url: url,
                    format_id: null, // Best quality
                    audio_only: this.selectedType === 'audio',
                    file_format: null // Auto format
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to start download');
            }

            this.currentDownloadId = data.download_id;
            this.trackDownloadProgress();

        } catch (error) {
            this.showError(error.message);
            this.hideDownloadProgress();
        }
    }

    async customDownload() {
        const activeForm = document.querySelector('.tab-pane.active .url-form');
        const url = activeForm.querySelector('.video-url').value.trim();
        const qualitySelect = document.getElementById('quality-select');
        const formatSelect = document.getElementById('format-select');

        if (!url) {
            this.showError('Please enter a video URL');
            return;
        }

        this.showDownloadProgress();

        try {
            const response = await fetch('/download_video', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    url: url,
                    format_id: qualitySelect.value || null,
                    audio_only: this.selectedType === 'audio',
                    file_format: formatSelect.value || null
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to start download');
            }

            this.currentDownloadId = data.download_id;
            this.trackDownloadProgress();

        } catch (error) {
            this.showError(error.message);
            this.hideDownloadProgress();
        }
    }

    showDownloadProgress() {
        document.getElementById('download-progress').style.display = 'block';
        document.querySelector('.download-spinner').style.display = 'flex';
        document.getElementById('download-complete').style.display = 'none';
    }

    hideDownloadProgress() {
        document.getElementById('download-progress').style.display = 'none';
    }

    updateProgress(percent, status) {
        const progressBar = document.getElementById('progress-bar');
        const percentageElement = document.getElementById('progress-percentage');
        const statusElement = document.getElementById('download-status');
        
        progressBar.style.width = `${percent}%`;
        if (percentageElement) {
            percentageElement.textContent = `${Math.round(percent)}%`;
        }
        statusElement.textContent = status;

        if (percent >= 100) {
            const spinner = document.querySelector('.download-spinner');
            if (spinner) {
                spinner.style.display = 'none';
            }
        }
    }

    async analyzeVideo(url) {
        console.log('Analyzing video URL:', url);
        
        if (!url) {
            this.showError('Please enter a valid URL');
            return;
        }

        this.showLoading(true);
        this.hideVideoInfo();
        this.hideError();

        try {
            console.log('Sending request to /get_video_info');
            
            const response = await fetch('/get_video_info', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: url })
            });

            console.log('Response status:', response.status);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('Response error:', errorText);
                throw new Error(`Server error: ${response.status}`);
            }

            const data = await response.json();
            console.log('Video data received:', data);

            if (data.error) {
                throw new Error(data.error);
            }

            this.showVideoInfo(data);
        } catch (error) {
            console.error('Analysis error:', error);
            
            let errorMessage = error.message || 'Failed to analyze video. Please check the URL and try again.';
            
            if (errorMessage.includes('blocking automated requests') || 
                errorMessage.includes('Sign in to confirm') ||
                errorMessage.includes('bot')) {
                errorMessage = `YouTube Access Issue: ${errorMessage}\n\nThis happens on some cloud hosting platforms. You can try:\n• Using a different video URL\n• Waiting a few minutes and trying again\n• Using videos from other platforms (Instagram, Facebook, etc.)`;
            } else if (errorMessage.includes('Private video')) {
                errorMessage = 'This video is private and cannot be downloaded.';
            } else if (errorMessage.includes('Video unavailable')) {
                errorMessage = 'This video is not available. It may have been deleted or restricted in your region.';
            } else if (errorMessage.includes('Age-restricted')) {
                errorMessage = 'This video is age-restricted and cannot be accessed without authentication.';
            }
            
            this.showError(errorMessage);
        } finally {
            this.showLoading(false);
        }
    }

    trackDownloadProgress() {
        if (!this.currentDownloadId) return;

        let attempts = 0;
        const maxAttempts = 120; // 1 minute timeout

        this.progressInterval = setInterval(async () => {
            attempts++;
            
            if (attempts > maxAttempts) {
                console.log('Download timeout reached');
                clearInterval(this.progressInterval);
                this.showError('Download timeout. Please try again.');
                this.hideDownloadProgress();
                return;
            }

            try {
                const response = await fetch(`/download_progress/${this.currentDownloadId}`);
                const data = await response.json();

                console.log('Progress data received:', data);
                
                if (data.error) {
                    console.error('Download error:', data.error);
                    clearInterval(this.progressInterval);
                    this.showError(data.error);
                    this.hideDownloadProgress();
                    return;
                }
                
                if (data.progress !== undefined) {
                    this.updateProgress(data.progress, data.status || 'Downloading...');

                    if (data.progress >= 100 || data.status === 'finished') {
                        clearInterval(this.progressInterval);
                        this.showDownloadComplete();
                        setTimeout(() => {
                            this.triggerFileDownload();
                        }, 500);
                    }
                } else {
                    console.log('No progress data available yet');
                }
            } catch (error) {
                console.error('Progress tracking error:', error);
                clearInterval(this.progressInterval);
            }
        }, 500);
    }

    showDownloadComplete() {
        document.getElementById('download-complete').style.display = 'block';
        document.querySelector('.download-spinner').style.display = 'none';
    }

    triggerFileDownload() {
        if (this.currentDownloadId) {
            const downloadLink = document.getElementById('download-link');
            downloadLink.href = `/download_file/${this.currentDownloadId}`;
            downloadLink.click();
        }
    }

    formatDuration(seconds) {
        if (!seconds) return "0:00";
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = Math.floor(seconds % 60);
        
        if (hours > 0) {
            return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        } else {
            return `${minutes}:${secs.toString().padStart(2, '0')}`;
        }
    }

    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }

    formatFileSize(bytes) {
        if (!bytes) return 'Unknown';
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return (bytes / Math.pow(1024, i)).toFixed(1) + ' ' + sizes[i];
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    try {
        new VideoDownloader();
    } catch (error) {
        console.error('Error initializing VideoDownloader:', error);
    }
});

// Handle unhandled promise rejections
window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    event.preventDefault();
});