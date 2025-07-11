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
            // FORCE advanced options to be visible before quick download
            const advancedPanel = document.getElementById('advanced-options');
            if (advancedPanel && advancedPanel.style.display === 'none') {
                advancedPanel.style.display = 'block';
                this.populateAdvancedOptions();
            }
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

        // Clear existing options and add comprehensive options
        qualitySelect.innerHTML = '<option value="">Best Available</option>';
        formatSelect.innerHTML = '';

        // Use actual format IDs from video data - REAL QUALITY SELECTION
        const sortedFormats = this.videoData.formats.sort((a, b) => (b.height || 0) - (a.height || 0));
        
        sortedFormats.forEach(format => {
            const option = document.createElement('option');
            option.value = format.format_id;
            option.textContent = `${format.height}p`;
            qualitySelect.appendChild(option);
        });
        
        // Add fallback options only if no real formats
        if (sortedFormats.length === 0) {
            const fallbacks = [
                { value: 'best', text: 'Best Available' },
                { value: 'worst', text: 'Lowest Quality' }
            ];
            fallbacks.forEach(quality => {
                const option = document.createElement('option');
                option.value = quality.value;
                option.textContent = quality.text;
                qualitySelect.appendChild(option);
            });
        }

        if (this.selectedType === 'video') {
            // Add format conversion options for video
            const formats = [
                { value: 'mp4', text: 'MP4 (Default)' },
                { value: 'mkv', text: 'MKV (High Quality)' },
                { value: 'webm', text: 'WebM (Web Optimized)' },
                { value: 'avi', text: 'AVI (Compatible)' },
                { value: '3gp', text: '3GP (Mobile)' },
                { value: 'flv', text: 'FLV (Flash Video)' }
            ];
            
            formats.forEach(format => {
                const option = document.createElement('option');
                option.value = format.value;
                option.textContent = format.text;
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
            // FORCE populate advanced options first to get current selections
            this.populateAdvancedOptions();
            
            const qualitySelect = document.getElementById('quality-select');
            const formatSelect = document.getElementById('format-select');
            
            let formatId = 'best';
            let fileFormat = 'mp4';
            
            // FORCE populate dropdowns first, then use selected values
            this.populateAdvancedOptions();
            
            // Wait for population to complete, then get fresh values
            setTimeout(() => {
                const freshQualitySelect = document.getElementById('quality-select');
                const freshFormatSelect = document.getElementById('format-select');
                
                if (this.selectedType === 'audio') {
                    formatId = freshQualitySelect?.value || 'bestaudio';
                    fileFormat = freshFormatSelect?.value || 'mp3';
                } else {
                    // For video, ALWAYS use selected quality and format from dropdowns
                    formatId = freshQualitySelect?.value || 'best[height<=720]';
                    fileFormat = freshFormatSelect?.value || 'mp4';
                }
                
                // Continue with download using fresh values
                this.executeQuickDownload(formatId, fileFormat);
            }, 100);
            
            return; // Exit here, executeQuickDownload will handle the rest
        } catch (error) {
            this.showError(error.message);
            this.hideDownloadProgress();
        }
    }

    async executeQuickDownload(formatId, fileFormat) {
        const activeForm = document.querySelector('.tab-pane.active .url-form');
        const url = activeForm.querySelector('.video-url').value.trim();

        try {
            console.log('Quick download with:', {
                formatId,
                fileFormat,
                selectedType: this.selectedType
            });

            const response = await fetch('/download_video', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    url: url,
                    format_id: formatId,
                    audio_only: this.selectedType === 'audio',
                    file_format: fileFormat
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
            // Enhanced format selection for custom download
            let formatId = 'best';
            let fileFormat = 'mp4';
            
            if (this.selectedType === 'audio') {
                formatId = qualitySelect.value || 'bestaudio';
                fileFormat = formatSelect.value || 'mp3';
            } else {
                // For video, use selected quality or default to best
                formatId = qualitySelect.value || 'best[height<=1080]/best';
                fileFormat = formatSelect.value || 'mp4';
            }

            console.log('Custom download with:', {
                formatId,
                fileFormat,
                selectedType: this.selectedType,
                qualityValue: qualitySelect.value,
                formatValue: formatSelect.value
            });

            const response = await fetch('/download_video', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    url: url,
                    format_id: formatId,
                    audio_only: this.selectedType === 'audio',
                    file_format: fileFormat
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
        const progressDiv = document.getElementById('download-progress');
        const completeDiv = document.getElementById('download-complete');
        
        if (progressDiv) progressDiv.style.display = 'block';
        if (completeDiv) completeDiv.style.display = 'none';
        
        // Reset progress bar
        const progressBar = document.getElementById('progress-bar');
        const progressPercentage = document.getElementById('progress-percentage');
        if (progressBar) progressBar.style.width = '0%';
        if (progressPercentage) progressPercentage.textContent = '0%';
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

        // Progress complete - no spinner to hide
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
                this.showError('Download tracking failed. Please try again.');
                this.hideDownloadProgress();
            }
        }, 500);
    }

    showDownloadComplete() {
        const completeDiv = document.getElementById('download-complete');
        if (completeDiv) completeDiv.style.display = 'block';
        
        // Update status text
        const statusElement = document.getElementById('download-status');
        if (statusElement) statusElement.textContent = 'Download completed!';
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
    // Don't prevent default to avoid masking real errors
});