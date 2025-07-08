// YTdown Simple Video Downloader
class VideoDownloader {
    constructor() {
        this.currentDownloadId = null;
        this.progressInterval = null;
        this.selectedFormat = null;
        this.selectedQuality = null;
        this.selectedFileFormat = null;
        this.videoData = null;
        this.init();
    }

    init() {
        this.bindEvents();
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

        // Enhanced click handler for all selections
        document.addEventListener('click', (e) => {
            const target = e.target.closest('.simple-option, .quality-option, .file-format-option');
            
            if (!target) return;
            
            console.log('Click detected on:', target, 'Classes:', target.className);
            
            // Handle format selection (step 1)
            if (target.dataset.step === 'format') {
                this.handleSimpleSelection(target);
            }
            // Handle quality selection (step 2) - check if it's a quality option but not a file format
            else if (target.classList.contains('quality-option') && !target.classList.contains('file-format-option')) {
                console.log('Handling quality selection');
                this.handleQualitySelection(target);
            }
            // Handle file format selection (step 3)
            else if (target.classList.contains('file-format-option')) {
                console.log('Handling file format selection');
                this.handleQualitySelection(target);
            }
        });

        // Download button
        document.getElementById('download-btn').addEventListener('click', () => {
            this.startDownload();
        });
    }

    showLoading(show = true) {
        document.getElementById('loading').style.display = show ? 'block' : 'none';
        // Disable all analyze buttons
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

    handleSimpleSelection(element) {
        const step = element.dataset.step;
        const value = element.dataset.value;
        
        if (step === 'format') {
            // Clear previous format selections
            document.querySelectorAll('[data-step="format"]').forEach(opt => opt.classList.remove('selected'));
            element.classList.add('selected');
            
            this.selectedFormat = value;
            this.selectedQuality = null;
            this.selectedFileFormat = null;
            
            // Show quality section
            this.showQualityOptions();
            
            // Hide file format section
            document.getElementById('file-format-section').style.display = 'none';
        }
        
        this.updateDownloadButton();
        this.updateStatus();
    }
    
    handleQualitySelection(element) {
        const isFileFormat = element.classList.contains('file-format-option');
        
        if (isFileFormat) {
            // Handle file format selection
            document.querySelectorAll('.file-format-option').forEach(opt => opt.classList.remove('selected'));
            element.classList.add('selected');
            
            this.selectedFileFormat = element.dataset.format;
        } else {
            // Handle quality selection
            document.querySelectorAll('.quality-option:not(.file-format-option)').forEach(opt => opt.classList.remove('selected'));
            element.classList.add('selected');
            
            this.selectedQuality = element.dataset.quality;
            
            // Show file format section
            this.showFileFormatOptions();
        }
        
        this.updateDownloadButton();
        this.updateStatus();
    }
    
    updateDownloadButton() {
        const downloadBtn = document.getElementById('download-btn');
        const isComplete = this.selectedFormat && this.selectedQuality && this.selectedFileFormat;
        downloadBtn.disabled = !isComplete;
    }
    
    updateStatus() {
        const statusDiv = document.getElementById('selection-status');
        const steps = [];
        
        if (this.selectedFormat) steps.push('Format');
        if (this.selectedQuality) steps.push('Quality');
        if (this.selectedFileFormat) steps.push('File Format');
        
        if (steps.length === 3) {
            statusDiv.textContent = 'Ready to download!';
            statusDiv.style.color = 'rgba(0, 255, 0, 0.8)';
        } else {
            statusDiv.textContent = `Complete: ${steps.join(', ')} | Missing: ${3 - steps.length} step(s)`;
            statusDiv.style.color = 'rgba(255, 255, 255, 0.6)';
        }
    }

    showVideoInfo(videoData) {
        console.log('Showing video info:', videoData);
        this.hideError();
        this.videoData = videoData;
        
        // Update video information
        document.getElementById('video-title').textContent = videoData.title;
        document.getElementById('video-uploader').textContent = videoData.uploader || 'Unknown';
        document.getElementById('video-duration').textContent = this.formatDuration(videoData.duration);
        document.getElementById('video-views').textContent = this.formatNumber(videoData.view_count);
        
        // Update thumbnail
        const thumbnail = document.getElementById('video-thumbnail');
        if (videoData.thumbnail) {
            thumbnail.src = videoData.thumbnail;
            thumbnail.style.display = 'block';
        } else {
            thumbnail.style.display = 'none';
        }

        // Reset selections
        this.selectedFormat = null;
        this.selectedQuality = null;
        this.selectedFileFormat = null;
        
        // Reset format options visual state
        document.querySelectorAll('.format-option').forEach(opt => opt.classList.remove('selected'));
        document.querySelectorAll('.quality-option').forEach(opt => opt.classList.remove('selected'));
        
        // Hide quality and file format sections initially
        document.getElementById('quality-section').style.display = 'none';
        document.getElementById('file-format-section').style.display = 'none';
        document.getElementById('download-btn').disabled = true;

        // Show video info section
        document.getElementById('video-info').style.display = 'block';
        console.log('Video info section should now be visible');
    }
    
    showQualityOptions() {
        console.log('showQualityOptions called for format:', this.selectedFormat);
        const qualitySection = document.getElementById('quality-section');
        const qualityOptions = document.getElementById('quality-options');
        
        if (!qualitySection || !qualityOptions) {
            console.error('Quality section elements not found');
            return;
        }
        
        qualityOptions.innerHTML = '';
        
        if (this.selectedFormat === 'video') {
            // Use actual format data from the video
            const videoQualities = [];
            
            // Get available formats from video data
            if (this.videoData && this.videoData.formats) {
                // Create quality options based on available formats
                const availableHeights = [...new Set(this.videoData.formats.map(f => f.height))].sort((a, b) => b - a);
                
                availableHeights.forEach(height => {
                    const format = this.videoData.formats.find(f => f.height === height);
                    if (format) {
                        let label, desc;
                        if (height >= 2160) { label = '4K (2160p)'; desc = 'Ultra HD'; }
                        else if (height >= 1440) { label = '2K (1440p)'; desc = 'Quad HD'; }
                        else if (height >= 1080) { label = '1080p'; desc = 'Full HD'; }
                        else if (height >= 720) { label = '720p'; desc = 'HD Ready'; }
                        else if (height >= 480) { label = '480p'; desc = 'Standard'; }
                        else if (height >= 360) { label = '360p'; desc = 'Low'; }
                        else if (height >= 240) { label = '240p'; desc = 'Mobile'; }
                        else { label = '144p'; desc = 'Data Saver'; }
                        
                        videoQualities.push({
                            label: label,
                            formatId: format.format_id,
                            desc: desc,
                            height: height
                        });
                    }
                });
            }
            
            // Add comprehensive quality options from 4K to 144p
            if (videoQualities.length === 0) {
                videoQualities.push(
                    { label: '4K (2160p)', formatId: 'best[height<=2160]', desc: 'Ultra HD', height: 2160 },
                    { label: '2K (1440p)', formatId: 'best[height<=1440]', desc: 'Quad HD', height: 1440 },
                    { label: '1080p', formatId: 'best[height<=1080]', desc: 'Full HD', height: 1080 },
                    { label: '720p', formatId: 'best[height<=720]', desc: 'HD Ready', height: 720 },
                    { label: '480p', formatId: 'best[height<=480]', desc: 'Standard', height: 480 },
                    { label: '360p', formatId: 'best[height<=360]', desc: 'Low', height: 360 },
                    { label: '240p', formatId: 'best[height<=240]', desc: 'Mobile', height: 240 },
                    { label: '144p', formatId: 'best[height<=144]', desc: 'Data Saver', height: 144 }
                );
            }
            
            videoQualities.forEach(quality => {
                const option = document.createElement('div');
                option.className = 'quality-option simple-option';
                option.dataset.quality = quality.formatId;
                option.innerHTML = `
                    <div style="font-weight: 700; font-size: 1.1rem; margin-bottom: 0.25rem;">${quality.label}</div>
                    <div style="font-size: 0.8rem; opacity: 0.8; font-weight: 500;">${quality.desc}</div>
                `;
                console.log('Creating quality option:', quality.label, 'with classes:', option.className);
                qualityOptions.appendChild(option);
            });
        } else if (this.selectedFormat === 'audio') {
            const audioQualities = [
                { label: 'Best Quality', formatId: 'bestaudio', desc: 'Highest Available' },
                { label: '320 kbps', formatId: 'bestaudio[abr<=320]', desc: 'Premium' },
                { label: '192 kbps', formatId: 'bestaudio[abr<=192]', desc: 'High Quality' },
                { label: '128 kbps', formatId: 'bestaudio[abr<=128]', desc: 'Standard' }
            ];
            
            audioQualities.forEach(quality => {
                const option = document.createElement('div');
                option.className = 'quality-option simple-option';
                option.dataset.quality = quality.formatId;
                option.innerHTML = `
                    <div style="font-weight: 700; font-size: 1.1rem; margin-bottom: 0.25rem;">${quality.label}</div>
                    <div style="font-size: 0.8rem; opacity: 0.8; font-weight: 500;">${quality.desc}</div>
                `;
                qualityOptions.appendChild(option);
            });
        }
        
        qualitySection.style.display = 'block';
    }
    
    showFileFormatOptions() {
        const fileFormatSection = document.getElementById('file-format-section');
        const fileFormatOptions = document.getElementById('file-format-options');
        
        fileFormatOptions.innerHTML = '';
        
        if (this.selectedFormat === 'video') {
            // Get available formats from video data
            let videoFormats = [];
            if (this.videoData && this.videoData.formats && this.videoData.formats.length > 0) {
                const availableExts = [...new Set(this.videoData.formats.map(f => f.ext))];
                videoFormats = availableExts.map(ext => ({
                    format: ext,
                    label: ext.toUpperCase()
                }));
            }
            
            // Add comprehensive format conversion options
            if (videoFormats.length === 0) {
                videoFormats = [
                    { format: 'mp4', label: 'MP4', desc: 'Most Compatible' },
                    { format: 'mkv', label: 'MKV', desc: 'High Quality' },
                    { format: 'webm', label: 'WebM', desc: 'Web Optimized' },
                    { format: 'avi', label: 'AVI', desc: 'Classic Format' },
                    { format: '3gp', label: '3GP', desc: 'Mobile Device' },
                    { format: 'flv', label: 'FLV', desc: 'Flash Video' }
                ];
            }
            
            videoFormats.forEach(format => {
                const option = document.createElement('div');
                option.className = 'quality-option file-format-option simple-option';
                option.dataset.format = format.format;
                option.innerHTML = `
                    <div style="font-weight: 700; font-size: 1.1rem; margin-bottom: 0.25rem;">${format.label}</div>
                    ${format.desc ? `<div style="font-size: 0.8rem; opacity: 0.8; font-weight: 500;">${format.desc}</div>` : ''}
                `;
                fileFormatOptions.appendChild(option);
            });
        } else if (this.selectedFormat === 'audio') {
            const audioFormats = [
                { format: 'mp3', label: 'MP3' },
                { format: 'm4a', label: 'M4A' },
                { format: 'ogg', label: 'OGG' },
                { format: 'wav', label: 'WAV' }
            ];
            
            audioFormats.forEach(format => {
                const option = document.createElement('div');
                option.className = 'quality-option file-format-option simple-option';
                option.dataset.format = format.format;
                option.textContent = format.label;
                fileFormatOptions.appendChild(option);
            });
        }
        
        fileFormatSection.style.display = 'block';
    }

    hideVideoInfo() {
        document.getElementById('video-info').style.display = 'none';
        this.hideDownloadProgress();
    }

    populateFormats(formats) {
        const formatSelect = document.getElementById('format-select');
        formatSelect.innerHTML = '<option value="">Select format and quality...</option>';

        // Group formats by type
        const videoFormats = formats.filter(f => f.type === 'video');
        const audioFormats = formats.filter(f => f.type === 'audio');

        // Add video formats
        if (videoFormats.length > 0) {
            const videoGroup = document.createElement('optgroup');
            videoGroup.label = 'Video Formats';
            
            videoFormats.forEach(format => {
                const option = document.createElement('option');
                option.value = format.format_id;
                option.textContent = `${format.resolution} - ${format.ext.toUpperCase()}${format.filesize ? ` (${this.formatFileSize(format.filesize)})` : ''}`;
                videoGroup.appendChild(option);
            });
            
            formatSelect.appendChild(videoGroup);
        }

        // Add audio formats
        if (audioFormats.length > 0) {
            const audioGroup = document.createElement('optgroup');
            audioGroup.label = 'Audio Only';
            
            audioFormats.forEach(format => {
                const option = document.createElement('option');
                option.value = format.format_id;
                option.dataset.audioOnly = 'true';
                option.textContent = `${format.resolution} - ${format.ext.toUpperCase()}${format.filesize ? ` (${this.formatFileSize(format.filesize)})` : ''}`;
                audioGroup.appendChild(option);
            });
            
            formatSelect.appendChild(audioGroup);
        }

        // Reset download button
        document.getElementById('download-btn').disabled = true;
    }

    showDownloadProgress() {
        document.getElementById('download-progress').style.display = 'block';
        document.getElementById('download-complete').style.display = 'none';
        this.updateProgress(0, 'Preparing download...');
    }

    hideDownloadProgress() {
        document.getElementById('download-progress').style.display = 'none';
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
        }
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

        // Hide spinner when complete
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

            this.videoData = data; // Store video data for quality selection
            this.showVideoInfo(data);
        } catch (error) {
            console.error('Analysis error:', error);
            
            // Provide more helpful error messages for common issues
            let errorMessage = error.message || 'Failed to analyze video. Please check the URL and try again.';
            
            // Check for YouTube bot detection or common hosting platform issues
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

    async startDownload() {
        if (!this.selectedFormat || !this.selectedQuality || !this.selectedFileFormat) {
            this.showError('Please complete all 3 selection steps');
            return;
        }

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
                    format_id: this.selectedQuality,
                    audio_only: this.selectedFormat === 'audio',
                    file_format: this.selectedFileFormat
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

    trackDownloadProgress() {
        if (!this.currentDownloadId) return;

        this.progressInterval = setInterval(async () => {
            try {
                const response = await fetch(`/download_progress/${this.currentDownloadId}`);
                const data = await response.json();

                if (data.error) {
                    this.showError(data.error);
                    this.hideDownloadProgress();
                    return;
                }

                if (data.status === 'downloading') {
                    this.updateProgress(data.progress || 0, 'Downloading...');
                } else if (data.status === 'converting') {
                    this.updateProgress(data.progress || 90, 'Converting to selected format...');
                } else if (data.status === 'finished' || data.progress >= 100) {
                    this.updateProgress(100, 'Download completed!');
                    this.showDownloadComplete();
                    clearInterval(this.progressInterval);
                } else if (data.status === 'error') {
                    this.showError(data.error || 'Download failed');
                    this.hideDownloadProgress();
                    clearInterval(this.progressInterval);
                }

            } catch (error) {
                console.error('Error tracking progress:', error);
            }
        }, 1000);
    }

    showDownloadComplete() {
        const completeDiv = document.getElementById('download-complete');
        const downloadLink = document.getElementById('download-link');
        
        downloadLink.href = `/download_file/${this.currentDownloadId}`;
        completeDiv.style.display = 'block';
        
        // Automatically trigger the browser download
        this.triggerFileDownload();
    }
    
    triggerFileDownload() {
        // Create a temporary anchor element to trigger download
        const link = document.createElement('a');
        link.href = `/download_file/${this.currentDownloadId}`;
        link.download = ''; // This will use the filename from server
        link.style.display = 'none';
        
        // Add to DOM, click, and remove
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        console.log('Download triggered automatically');
    }

    // Utility functions
    formatDuration(seconds) {
        if (!seconds) return 'Unknown';
        
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;

        if (hours > 0) {
            return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        } else {
            return `${minutes}:${secs.toString().padStart(2, '0')}`;
        }
    }

    formatNumber(num) {
        if (!num) return '0';
        
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }

    formatFileSize(bytes) {
        if (!bytes) return '';
        
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    try {
        new VideoDownloader();
        console.log('VideoDownloader initialized successfully');
    } catch (error) {
        console.error('Error initializing VideoDownloader:', error);
    }
});

// Handle unhandled promise rejections
window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    event.preventDefault();
});

// Handle page navigation
window.addEventListener('beforeunload', (e) => {
    // Warn user if download is in progress
    const progressDiv = document.getElementById('download-progress');
    if (progressDiv && progressDiv.style.display !== 'none') {
        e.preventDefault();
        e.returnValue = 'Download in progress. Are you sure you want to leave?';
        return e.returnValue;
    }
});
