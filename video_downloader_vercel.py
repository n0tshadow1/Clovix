import yt_dlp
import tempfile
import os
import logging
import time
import random

class VideoDownloader:
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        
    def get_video_info(self, url):
        """Extract video information without downloading"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Add random delay to avoid bot detection
                if attempt > 0:
                    time.sleep(random.uniform(1, 3))
                    logging.info(f"Retry attempt {attempt + 1} for URL: {url}")
                
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': False,
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'extractor_args': {
                        'youtube': {
                            'skip': ['hls', 'dash'],
                            'player_skip': ['configs'],
                        }
                    },
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-us,en;q=0.5',
                        'Accept-Encoding': 'gzip,deflate',
                        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
                        'Connection': 'keep-alive',
                    },
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    
                    # Get available formats
                    formats = []
                    if info and 'formats' in info and info['formats']:
                        seen_qualities = set()
                        for fmt in info['formats']:
                            if fmt.get('height') and fmt.get('ext') in ['mp4', 'webm']:
                                quality = f"{fmt['height']}p"
                                if quality not in seen_qualities:
                                    formats.append({
                                        'quality': quality,
                                        'format_id': fmt['format_id'],
                                        'ext': fmt['ext'],
                                        'filesize': fmt.get('filesize'),
                                    })
                                    seen_qualities.add(quality)
                    
                    # Sort formats by quality
                    formats.sort(key=lambda x: int(x['quality'].replace('p', '')), reverse=True)
                    
                    return {
                        'title': info.get('title', 'Unknown') if info else 'Unknown',
                        'duration': info.get('duration', 0) if info else 0,
                        'thumbnail': info.get('thumbnail', '') if info else '',
                        'uploader': info.get('uploader', 'Unknown') if info else 'Unknown',
                        'view_count': info.get('view_count', 0) if info else 0,
                        'formats': formats[:6],  # Limit to top 6 formats
                    }
                    
            except Exception as e:
                error_msg = str(e)
                logging.error(f"Attempt {attempt + 1} failed: {error_msg}")
                
                # Check if it's a bot detection error
                if "Sign in to confirm" in error_msg or "bot" in error_msg.lower():
                    if attempt < max_retries - 1:
                        logging.info(f"Bot detection detected, retrying in {2 ** attempt} seconds...")
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    else:
                        return {'error': 'YouTube detected automated access. Please try again later or use a different video.'}
                else:
                    return {'error': f'Failed to get video information: {error_msg}'}
        
        return {'error': 'Failed to get video information after multiple attempts'}
    
    def download_video(self, url, format_id=None, audio_only=False):
        """Download video - simplified for serverless"""
        try:
            output_path = os.path.join(self.temp_dir, '%(title)s.%(ext)s')
            
            ydl_opts = {
                'outtmpl': output_path,
                'quiet': True,
                'no_warnings': True,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'extractor_args': {
                    'youtube': {
                        'skip': ['hls', 'dash'],
                        'player_skip': ['configs'],
                    }
                },
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-us,en;q=0.5',
                    'Accept-Encoding': 'gzip,deflate',
                    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
                    'Connection': 'keep-alive',
                },
            }
            
            if audio_only:
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            elif format_id:
                ydl_opts['format'] = format_id
            else:
                ydl_opts['format'] = 'best[height<=720]'
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                
                return {
                    'filepath': filename,
                    'title': info.get('title', 'Downloaded Video') if info else 'Downloaded Video',
                    'success': True
                }
                
        except Exception as e:
            logging.error(f"Error downloading video: {str(e)}")
            return {'error': f'Download failed: {str(e)}', 'success': False}