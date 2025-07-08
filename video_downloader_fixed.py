import yt_dlp
import tempfile
import os
import logging
import gc
import time
import random
import subprocess
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
        """Extract video information with ultimate YouTube authentication bypass"""
        if 'youtube.com' in url or 'youtu.be' in url:
            return self._get_youtube_info_ultimate(url)
        else:
            return self._get_video_info_standard(url)

    def _get_youtube_info_ultimate(self, url):
        """Ultimate YouTube extraction with authentication bypass strategies"""
        
        # Strategy 1: Use TV embedded client (works without auth)
        strategies = [
            {
                'name': 'TV Embedded Client',
                'opts': {
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': False,
                    'user_agent': 'Mozilla/5.0 (SMART-TV; Linux; Tizen 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['tv_embedded'],
                            'skip': ['dash', 'hls'],
                        }
                    },
                    'socket_timeout': 30,
                    'retries': 1,
                }
            },
            {
                'name': 'Android TV Client',
                'opts': {
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': False,
                    'user_agent': 'com.google.android.youtube.tv/1.0 (Linux; U; Android 9; SM-T500) gzip',
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['android_tv'],
                            'skip': ['dash', 'hls'],
                        }
                    },
                    'socket_timeout': 30,
                    'retries': 1,
                }
            },
            {
                'name': 'iOS Mobile Client',
                'opts': {
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': False,
                    'user_agent': 'com.google.ios.youtube/19.29.1 (iPhone16,2; U; CPU OS 17_5_1 like Mac OS X)',
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['ios'],
                            'skip': ['dash', 'hls'],
                        }
                    },
                    'socket_timeout': 30,
                    'retries': 1,
                }
            },
            {
                'name': 'Web Client with Embed',
                'opts': {
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': False,
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['web_embedded'],
                            'skip': ['dash', 'hls'],
                        }
                    },
                    'socket_timeout': 30,
                    'retries': 1,
                }
            }
        ]
        
        for i, strategy in enumerate(strategies):
            try:
                logging.info(f"Trying strategy {i+1}: {strategy['name']}")
                
                with self.memory_managed_extraction(strategy['opts']) as ydl:
                    info = ydl.extract_info(url, download=False)
                    
                    if info and 'title' in info:
                        # Process formats
                        formats = []
                        seen_qualities = set()
                        
                        if 'formats' in info and info['formats']:
                            for fmt in info['formats']:
                                if fmt.get('vcodec') != 'none' and fmt.get('height'):
                                    height = fmt.get('height', 0)
                                    quality = f"{height}p"
                                    
                                    if quality not in seen_qualities and height in [720, 480, 360]:
                                        formats.append({
                                            'format_id': fmt.get('format_id', f"best[height<={height}]"),
                                            'height': height,
                                            'width': fmt.get('width', height * 16 // 9),
                                            'ext': fmt.get('ext', 'mp4'),
                                            'quality': quality,
                                            'vcodec': fmt.get('vcodec', 'avc1'),
                                            'acodec': fmt.get('acodec', 'mp4a'),
                                            'filesize': fmt.get('filesize'),
                                        })
                                        seen_qualities.add(quality)
                        
                        # If no formats found, use defaults
                        if not formats:
                            formats = self._get_default_formats()
                        else:
                            # Sort by quality
                            formats.sort(key=lambda x: x['height'], reverse=True)
                        
                        return {
                            'title': info.get('title', 'Unknown Video'),
                            'duration': self._format_duration(info.get('duration', 0)),
                            'thumbnail': info.get('thumbnail', ''),
                            'uploader': info.get('uploader', 'Unknown'),
                            'view_count': info.get('view_count', 0),
                            'formats': formats[:3],  # Top 3 formats
                            'working_url': url
                        }
                        
            except Exception as e:
                error_msg = str(e).lower()
                logging.warning(f"Strategy {i+1} failed: {str(e)}")
                
                # Check for authentication errors
                if "sign in" in error_msg or "cookies" in error_msg:
                    continue  # Try next strategy
                elif "private" in error_msg:
                    return {'error': 'This video is private and cannot be downloaded.'}
                elif "unavailable" in error_msg:
                    return {'error': 'This video is not available.'}
                
                # Continue to next strategy
                continue
        
        # All strategies failed - try command line approach
        return self._try_cmdline_extraction(url)

    def _try_cmdline_extraction(self, url):
        """Try command line yt-dlp as final fallback"""
        try:
            # Use command line yt-dlp with specific options
            cmd = [
                'yt-dlp', '--no-warnings', '--quiet',
                '--print', '%(title)s|%(duration)s|%(uploader)s|%(view_count)s|%(thumbnail)s',
                '--extractor-args', 'youtube:player_client=tv_embedded',
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
            
            if result.returncode == 0 and result.stdout.strip():
                parts = result.stdout.strip().split('|')
                
                if len(parts) >= 5:
                    title = parts[0] if parts[0] != 'NA' else 'Unknown Video'
                    duration = int(parts[1]) if parts[1].isdigit() else 0
                    uploader = parts[2] if parts[2] != 'NA' else 'Unknown'
                    view_count = int(parts[3]) if parts[3].isdigit() else 0
                    thumbnail = parts[4] if parts[4] != 'NA' else ''
                    
                    return {
                        'title': title,
                        'duration': self._format_duration(duration),
                        'thumbnail': thumbnail,
                        'uploader': uploader,
                        'view_count': view_count,
                        'formats': self._get_default_formats(),
                        'working_url': url
                    }
                    
        except Exception as e:
            logging.error(f"Command line extraction failed: {str(e)}")
        
        # Final fallback with user-friendly error
        return {
            'error': '🔒 This YouTube video requires authentication.\n\n💡 Solutions:\n• Try a different YouTube video\n• Wait a few minutes and try again\n• Use videos from other platforms (Instagram, TikTok, Facebook)\n\nOther platforms work perfectly!'
        }

    def _get_default_formats(self):
        """Provide default working formats"""
        return [
            {
                'format_id': 'best[height<=720]',
                'height': 720,
                'width': 1280,
                'ext': 'mp4',
                'quality': '720p',
                'vcodec': 'avc1',
                'acodec': 'mp4a'
            },
            {
                'format_id': 'best[height<=480]',
                'height': 480,
                'width': 854,
                'ext': 'mp4',
                'quality': '480p',
                'vcodec': 'avc1',
                'acodec': 'mp4a'
            },
            {
                'format_id': 'best[height<=360]',
                'height': 360,
                'width': 640,
                'ext': 'mp4',
                'quality': '360p',
                'vcodec': 'avc1',
                'acodec': 'mp4a'
            }
        ]

    def _get_video_info_standard(self, url):
        """Standard extraction for non-YouTube platforms"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'socket_timeout': 30,
                'retries': 2,
            }
            
            with self.memory_managed_extraction(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    return {'error': 'Could not extract video information'}
                
                # Process formats
                formats = []
                seen_qualities = set()
                
                if 'formats' in info and info['formats']:
                    for fmt in info['formats']:
                        if fmt.get('vcodec') != 'none' and fmt.get('height'):
                            height = fmt.get('height', 0)
                            quality = f"{height}p"
                            
                            if quality not in seen_qualities and height >= 240:
                                formats.append({
                                    'format_id': fmt.get('format_id', ''),
                                    'height': height,
                                    'width': fmt.get('width', height * 16 // 9),
                                    'ext': fmt.get('ext', 'mp4'),
                                    'quality': quality,
                                    'vcodec': fmt.get('vcodec', 'unknown'),
                                    'acodec': fmt.get('acodec', 'unknown'),
                                    'filesize': fmt.get('filesize'),
                                })
                                seen_qualities.add(quality)
                
                # Sort formats by quality
                formats.sort(key=lambda x: x['height'], reverse=True)
                
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': self._format_duration(info.get('duration', 0)),
                    'thumbnail': info.get('thumbnail', ''),
                    'uploader': info.get('uploader', 'Unknown'),
                    'view_count': info.get('view_count', 0),
                    'formats': formats[:6],  # Top 6 formats
                    'working_url': url
                }
                
        except Exception as e:
            logging.error(f"Standard extraction failed: {str(e)}")
            return {'error': f'Could not extract video information: {str(e)}'}

    def _format_duration(self, duration):
        """Format duration"""
        if not duration or duration == 0:
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

    def download_video(self, url, format_id=None, audio_only=False, file_format=None, progress_hook=None):
        """Download video with authentication bypass for YouTube"""
        try:
            output_template = os.path.join(self.temp_dir, '%(title)s.%(ext)s')
            
            # Base options
            ydl_opts = {
                'outtmpl': output_template,
                'quiet': True,
                'no_warnings': True,
            }
            
            # Add progress hook if provided
            if progress_hook:
                ydl_opts['progress_hooks'] = [progress_hook]
            
            # YouTube-specific options with authentication bypass
            if 'youtube.com' in url or 'youtu.be' in url:
                ydl_opts.update({
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['tv_embedded', 'android_tv', 'ios'],
                            'skip': ['dash', 'hls'],
                        }
                    },
                    'user_agent': 'Mozilla/5.0 (SMART-TV; Linux; Tizen 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
                })
            
            # Format selection
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
                ydl_opts['format'] = 'best[height<=720]/best'
            
            # Download
            with self.memory_managed_extraction(ydl_opts) as ydl:
                ydl.download([url])
            
            # Find downloaded file
            for file in os.listdir(self.temp_dir):
                if file.endswith(('.mp4', '.mkv', '.webm', '.avi', '.mp3', '.m4a')):
                    file_path = os.path.join(self.temp_dir, file)
                    return {'file_path': file_path, 'filename': file}
            
            return {'error': 'Download completed but file not found'}
            
        except Exception as e:
            error_msg = str(e)
            
            # Handle authentication errors with user-friendly messages
            if "sign in" in error_msg.lower() or "cookies" in error_msg.lower():
                return {
                    'error': '🔒 This YouTube video requires authentication.\n\n💡 Try:\n• A different YouTube video\n• Videos from Instagram, TikTok, or Facebook\n• Wait a few minutes and try again'
                }
            else:
                logging.error(f"Download failed: {error_msg}")
                return {'error': f'Download failed: {error_msg}'}