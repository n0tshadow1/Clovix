import yt_dlp
import tempfile
import os
import logging
import gc
import time
import random
import subprocess
import json
from contextlib import contextmanager

class VideoDownloader:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        logging.info("VideoDownloader initialized successfully")

    @contextmanager
    def memory_managed_extraction(self, ydl_opts):
        """Context manager for memory-efficient video extraction"""
        ydl = None
        try:
            ydl = yt_dlp.YoutubeDL(ydl_opts)
            yield ydl
        finally:
            if ydl:
                try:
                    ydl.close()
                except:
                    pass
            gc.collect()

    def get_video_info(self, url):
        """Extract video information with platform-specific handling"""
        if 'youtube.com' in url or 'youtu.be' in url:
            return self._handle_youtube_blocked(url)
        else:
            return self._get_video_info_other_platforms(url)

    def _handle_youtube_blocked(self, url):
        """Handle YouTube with server blocking - provide notification"""
        video_id = self._extract_video_id(url)
        
        # Return a working response for UI but notify about blocking
        return {
            'title': f'YouTube Video {video_id[:8]} (Server IP Blocked)',
            'duration': '0:00',
            'thumbnail': f'https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg',
            'uploader': 'YouTube',
            'view_count': 0,
            'formats': [
                {
                    'format_id': '18',
                    'ext': 'mp4',
                    'height': 360,
                    'width': 640,
                    'acodec': 'mp4a',
                    'vcodec': 'avc1',
                    'quality': '360p'
                },
                {
                    'format_id': '22', 
                    'ext': 'mp4',
                    'height': 720,
                    'width': 1280,
                    'acodec': 'mp4a',
                    'vcodec': 'avc1',
                    'quality': '720p'
                }
            ],
            'working_url': url,
            'server_notice': 'This server IP is currently blocked by YouTube. Downloads work perfectly for Instagram, TikTok, Facebook and other platforms. Try a different platform or contact admin for YouTube access.'
        }

    def _get_video_info_other_platforms(self, url):
        """Enhanced extraction for non-YouTube platforms with quality support"""
        
        # Enhanced extraction strategies for different platforms
        extraction_strategies = [
            {
                'name': 'Enhanced Standard Extraction',
                'opts': {
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': False,
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'socket_timeout': 20,
                    'retries': 2,
                    'format_sort': ['height:720', 'height:1080', 'height:480', 'height:360'],
                }
            },
            {
                'name': 'Mobile Client Extraction', 
                'opts': {
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': False,
                    'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
                    'socket_timeout': 15,
                    'retries': 1,
                }
            },
            {
                'name': 'Basic Fallback',
                'opts': {
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': False,
                    'socket_timeout': 10,
                    'retries': 1,
                }
            }
        ]

        for strategy in extraction_strategies:
            try:
                logging.info(f"Trying {strategy['name']} for platform extraction")
                
                with self.memory_managed_extraction(strategy['opts']) as ydl:
                    info = ydl.extract_info(url, download=False)
                    
                    if info:
                        logging.info(f"Successfully extracted info with {strategy['name']}")
                        return self._process_platform_info(info, url)
                        
            except Exception as e:
                error_msg = str(e)
                logging.warning(f"{strategy['name']} failed: {error_msg}")
                continue
        
        # Fallback response if all strategies fail
        return {'error': 'Could not extract video information. Please check the URL and try again.'}

    def _process_platform_info(self, info, url):
        """Process video info with enhanced format support"""
        try:
            # Extract basic info
            title = info.get('title', 'Unknown Video')
            duration = self._format_duration(info.get('duration', 0))
            thumbnail = info.get('thumbnail', '')
            uploader = info.get('uploader', info.get('channel', 'Unknown'))
            view_count = info.get('view_count', 0)
            
            # Enhanced format processing
            formats = []
            if 'formats' in info and info['formats']:
                # Sort formats by quality (height) descending
                sorted_formats = sorted(
                    [f for f in info['formats'] if f.get('height') and f.get('ext')],
                    key=lambda x: x.get('height', 0),
                    reverse=True
                )
                
                # Include top quality formats
                seen_heights = set()
                for fmt in sorted_formats:
                    height = fmt.get('height')
                    if height and height not in seen_heights and len(formats) < 8:
                        formats.append({
                            'format_id': fmt.get('format_id', ''),
                            'ext': fmt.get('ext', 'mp4'),
                            'height': height,
                            'width': fmt.get('width', 0),
                            'acodec': fmt.get('acodec', 'unknown'),
                            'vcodec': fmt.get('vcodec', 'unknown'),
                            'quality': f"{height}p",
                            'filesize': fmt.get('filesize'),
                        })
                        seen_heights.add(height)
            
            # Ensure we have at least some formats
            if not formats:
                formats = [
                    {
                        'format_id': 'best',
                        'ext': 'mp4',
                        'height': 720,
                        'width': 1280,
                        'acodec': 'mp4a',
                        'vcodec': 'avc1',
                        'quality': '720p'
                    },
                    {
                        'format_id': 'worst',
                        'ext': 'mp4', 
                        'height': 360,
                        'width': 640,
                        'acodec': 'mp4a',
                        'vcodec': 'avc1',
                        'quality': '360p'
                    }
                ]
            
            logging.info(f"Video info processed: {title}, {len(formats)} formats available")
            
            return {
                'title': title,
                'duration': duration,
                'thumbnail': thumbnail,
                'uploader': uploader,
                'view_count': view_count,
                'formats': formats,
                'working_url': url
            }
            
        except Exception as e:
            logging.error(f"Error processing video info: {str(e)}")
            return {'error': f'Error processing video information: {str(e)}'}

    def download_video(self, url, format_id=None, audio_only=False, file_format=None, progress_hook=None):
        """Enhanced download with proper format selection for all platforms"""
        
        if 'youtube.com' in url or 'youtu.be' in url:
            return {'error': 'YouTube downloads are currently blocked on this server IP. Please try Instagram, TikTok, Facebook or other platforms.'}
        
        try:
            # Enhanced download options
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'outtmpl': os.path.join(self.temp_dir, '%(title)s.%(ext)s'),
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'socket_timeout': 30,
                'retries': 3,
            }
            
            if progress_hook:
                ydl_opts['progress_hooks'] = [progress_hook]
            
            # FIXED: Proper format selection using actual format IDs
            if audio_only:
                ydl_opts['format'] = 'bestaudio/best'
                if file_format in ['mp3', 'm4a', 'wav', 'flac']:
                    ydl_opts['postprocessors'] = [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': file_format,
                        'preferredquality': '192',
                    }]
            else:
                # FIXED: Use exact format ID from video analysis
                if format_id and format_id not in ['best', 'worst', 'server_blocked']:
                    # Use the actual format ID from the video info
                    ydl_opts['format'] = format_id
                    logging.info(f"Using specific format ID: {format_id}")
                elif format_id == 'worst':
                    ydl_opts['format'] = 'worst[height<=480]/worst'
                else:
                    ydl_opts['format'] = 'best[height<=1080]/best'
                
                # Skip format conversion - download MP4 directly
                # Format conversion disabled due to FFmpeg encoder issues
                logging.info(f"Requested format: {file_format}, downloading as MP4")
            
            # Simplified format selection - no complex fallbacks
            logging.info(f"Final download format: {ydl_opts['format']}")
            
            logging.info(f"Starting download with format: {ydl_opts['format']}")
            
            with self.memory_managed_extraction(ydl_opts) as ydl:
                ydl.download([url])
            
            # Find the downloaded file
            for filename in os.listdir(self.temp_dir):
                if os.path.isfile(os.path.join(self.temp_dir, filename)):
                    file_path = os.path.join(self.temp_dir, filename)
                    logging.info(f"Download completed successfully: {filename}")
                    return {'file_path': file_path, 'filename': filename}
            
            return {'error': 'Download completed but file not found'}
            
        except Exception as e:
            error_msg = str(e)
            logging.error(f"Download failed: {error_msg}")
            return {'error': f'Download failed: {error_msg}'}

    def _extract_video_id(self, url):
        """Extract video ID from YouTube URL"""
        import re
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'(?:v\/)([0-9A-Za-z_-]{11})',
            r'youtu\.be\/([0-9A-Za-z_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def _format_duration(self, duration):
        """Format duration from seconds to MM:SS or HH:MM:SS"""
        if not duration:
            return "0:00"
        
        try:
            duration = int(duration)
            hours = duration // 3600
            minutes = (duration % 3600) // 60
            seconds = duration % 60
            
            if hours > 0:
                return f"{hours}:{minutes:02d}:{seconds:02d}"
            else:
                return f"{minutes}:{seconds:02d}"
        except:
            return "0:00"