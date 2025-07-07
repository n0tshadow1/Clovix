import os
import logging
from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from video_downloader_optimized import VideoDownloader
import tempfile
import threading
import time

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Global dictionary to store download progress (memory optimized)
download_progress = {}

# Memory optimization: Clean up old download records
import gc
import atexit

def cleanup_memory():
    """Clean up memory and old download records"""
    global download_progress
    download_progress.clear()
    gc.collect()

# Register cleanup on app exit
atexit.register(cleanup_memory)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_video_info', methods=['POST'])
def get_video_info():
    try:
        if not request.json:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        url = request.json.get('url', '').strip() if request.json else ''
        if not url:
            return jsonify({'error': 'Please provide a valid URL'}), 400
        
        logging.info(f"Analyzing URL: {url}")
        
        # Memory optimization: Use context manager
        downloader = VideoDownloader()
        video_info = downloader.get_video_info(url)
        
        # Clean up after each request
        gc.collect()
        
        if 'error' in video_info:
            logging.error(f"Video info error: {video_info['error']}")
            return jsonify(video_info), 400
        
        logging.info(f"Video info retrieved successfully for: {video_info.get('title', 'Unknown')}")
        return jsonify(video_info)
    
    except Exception as e:
        logging.error(f"Error getting video info: {str(e)}", exc_info=True)
        return jsonify({'error': f'Failed to get video information: {str(e)}'}), 500

@app.route('/download_video', methods=['POST'])
def download_video():
    try:
        data = request.json
        url = data.get('url', '').strip()
        format_id = data.get('format_id')
        audio_only = data.get('audio_only', False)
        file_format = data.get('file_format', 'mp4')
        
        if not url:
            return jsonify({'error': 'Please provide a valid URL'}), 400
        
        downloader = VideoDownloader()
        
        # Generate unique download ID with timestamp
        download_id = str(int(time.time() * 1000))
        download_progress[download_id] = {
            'progress': 0, 
            'status': 'starting',
            'timestamp': time.time(),
            'active': True  # Mark as active to prevent cleanup
        }
        
        def progress_hook(d):
            # Always check if download_id exists before updating
            if download_id not in download_progress:
                return
                
            if d['status'] == 'downloading':
                try:
                    percent = d.get('_percent_str', '0%').replace('%', '')
                    if percent:
                        download_progress[download_id]['progress'] = float(percent)
                    download_progress[download_id]['status'] = 'downloading'
                except (ValueError, TypeError):
                    pass
            elif d['status'] == 'finished':
                download_progress[download_id]['progress'] = 90  # Still need conversion
                download_progress[download_id]['status'] = 'converting'
                download_progress[download_id]['filename'] = d['filename']
            elif d['status'] == 'error':
                download_progress[download_id]['status'] = 'error'
                download_progress[download_id]['error'] = d.get('error', 'Unknown error')
        
        # Start download in background thread
        def download_thread():
            try:
                # Ensure download_id exists at start
                if download_id not in download_progress:
                    download_progress[download_id] = {
                        'status': 'downloading',
                        'progress': 0,
                        'timestamp': time.time()
                    }
                
                result = downloader.download_video(url, format_id, audio_only, file_format, progress_hook)
                
                # Only update if download_id still exists
                if download_id in download_progress:
                    if 'error' in result:
                        download_progress[download_id]['status'] = 'error'
                        download_progress[download_id]['error'] = result['error']
                        download_progress[download_id]['active'] = False  # Mark for cleanup
                    else:
                        download_progress[download_id].update(result)
                        if 'file_path' in result:
                            download_progress[download_id]['status'] = 'finished'
                            download_progress[download_id]['progress'] = 100
                            download_progress[download_id]['filename'] = result['file_path']  # Use file_path as filename
                            download_progress[download_id]['active'] = False  # Mark for cleanup
                        elif 'filename' in result:
                            download_progress[download_id]['status'] = 'finished'
                            download_progress[download_id]['progress'] = 100
                            download_progress[download_id]['active'] = False  # Mark for cleanup
                
            except Exception as e:
                logging.error(f"Download thread error: {str(e)}")
                # Only update if download_id still exists
                if download_id in download_progress:
                    download_progress[download_id]['error'] = str(e)
                    download_progress[download_id]['status'] = 'error'
                    download_progress[download_id]['active'] = False  # Mark for cleanup
            finally:
                # Memory cleanup after download
                gc.collect()
        
        thread = threading.Thread(target=download_thread)
        thread.daemon = True
        thread.start()
        
        return jsonify({'download_id': download_id})
    
    except Exception as e:
        logging.error(f"Error starting download: {str(e)}")
        return jsonify({'error': f'Failed to start download: {str(e)}'}), 500

@app.route('/download_progress/<download_id>')
def get_download_progress(download_id):
    # Don't clean up during active downloads - only clean on startup or specific intervals
    # cleanup_old_downloads()
    
    progress = download_progress.get(download_id, {'error': 'Download not found'})
    return jsonify(progress)

def cleanup_old_downloads():
    """Remove only inactive downloads that are truly old"""
    current_time = time.time()
    to_remove = []
    
    for download_id, info in download_progress.items():
        # Only clean up inactive downloads
        if not info.get('active', False):
            # Remove completed downloads after 5 minutes
            if info.get('status') in ['finished', 'error'] and current_time - info.get('timestamp', 0) > 300:
                to_remove.append(download_id)
            # Remove any inactive download older than 10 minutes
            elif current_time - info.get('timestamp', 0) > 600:
                to_remove.append(download_id)
    
    for download_id in to_remove:
        download_progress.pop(download_id, None)
        logging.info(f"Cleaned up old download: {download_id}")
    
    if to_remove:
        gc.collect()

# Schedule cleanup every 10 minutes instead of every request
import threading
def periodic_cleanup():
    import time
    while True:
        time.sleep(600)  # 10 minutes
        cleanup_old_downloads()

# Start cleanup thread
cleanup_thread = threading.Thread(target=periodic_cleanup, daemon=True)
cleanup_thread.start()

@app.route('/download_file/<download_id>')
def download_file(download_id):
    try:
        progress = download_progress.get(download_id)
        if not progress or 'filename' not in progress:
            return jsonify({'error': 'File not ready or not found'}), 404
        
        filename = progress['filename']
        if not os.path.exists(filename):
            return jsonify({'error': 'File not found'}), 404
        
        # Ensure we're not downloading JSON files
        if filename.endswith('.json') or filename.endswith('.info') or filename.endswith('.description'):
            return jsonify({'error': 'Invalid file type - video file not found'}), 404
        
        # Get original filename for download
        original_name = os.path.basename(filename)
        
        return send_file(filename, as_attachment=True, download_name=original_name)
    
    except Exception as e:
        logging.error(f"Error downloading file: {str(e)}")
        return jsonify({'error': f'Failed to download file: {str(e)}'}), 500

# For Vercel deployment
app.wsgi_app = app.wsgi_app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
