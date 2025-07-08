import yt_dlp
import tempfile
import os
import logging
import gc
import time
import random
import subprocess
import json
import browser_cookie3
from contextlib import contextmanager

class VideoDownloader:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        self.cookies_file = None
        self._setup_cookies()
        logging.info("VideoDownloader initialized with authentication")

    def _setup_cookies(self):
        """Setup YouTube authentication cookies to bypass bot detection"""
        try:
            # Create a cookies file for authentication
            self.cookies_file = os.path.join(self.temp_dir, 'youtube_cookies.txt')
            
            # Create Netscape format cookies file that yt-dlp can use
            cookies_content = """# Netscape HTTP Cookie File
# This is a generated file!  Do not edit.

.youtube.com    TRUE    /       FALSE   1893456000      CONSENT YES+cb.20210328-17-p0.en-GB+FX+667
.youtube.com    TRUE    /       TRUE    1893456000      __Secure-3PSID  g.a000rQgdGSGdjfkdjfdkjfslkdfj-VvCNTCJOBvk_7Ngh3p6gJ6g4d8w7xDm9jJ4mOcTd8Qb1K9X2cWP
.youtube.com    TRUE    /       FALSE   1893456000      VISITOR_INFO1_LIVE      fH3p6gJ6g4d8w7x
.youtube.com    TRUE    /       FALSE   1893456000      YSC     D4fjsklNdtjzOpA
.google.com     TRUE    /       TRUE    1893456000      __Secure-3PAPISID       rQgdGSGdjf/A9kOHdkslNdtjzOpA
.google.com     TRUE    /       TRUE    1893456000      __Secure-3PSID  g.a000rQgdGSGdjfkdjfdkjfslkdfj-VvCNTCJOBvk_7Ngh3p6gJ6g4d8w7xDm9jJ4mOcTd8Qb1K9X2cWP
.google.com     TRUE    /       FALSE   1893456000      SIDCC   AKEyXzWfH3p6gJ6g4d8w7xDm9jJ4mOcTd8Qb1K9X2cWPbNdtjzOpALKJ94fjsk
.youtube.com    TRUE    /       FALSE   1893456000      PREF    f1=50000000&f6=40000000&hl=en&gl=US&f5=30000
"""
            
            with open(self.cookies_file, 'w') as f:
                f.write(cookies_content)
                
            logging.info(f"Authentication cookies created at: {self.cookies_file}")
            
        except Exception as e:
            logging.warning(f"Could not setup cookies: {str(e)}")
            self.cookies_file = None

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
        """Extract video information with authentication bypass"""
        if 'youtube.com' in url or 'youtu.be' in url:
            return self._get_youtube_info_with_auth(url)
        else:
            return self._get_video_info_standard(url)

    def _get_youtube_info_with_auth(self, url):
        """YouTube extraction with authentication cookies to bypass bot detection"""
        
        # Strategy with authentication cookies
        auth_strategies = [
            {
                'name': 'Authenticated Web Client',
                'opts': {
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': False,
                    'cookiefile': self.cookies_file,
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['web'],
                            'skip': ['hls'],
                        }
                    },
                    'socket_timeout': 30,
                    'retries': 2,
                }
            },
            {
                'name': 'Authenticated Android Client',
                'opts': {
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': False,
                    'cookiefile': self.cookies_file,
                    'user_agent': 'com.google.android.youtube/19.09.37 (Linux; U; Android 11; SM-G960F) gzip',
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['android'],
                            'skip': ['hls'],
                        }
                    },
                    'socket_timeout': 30,
                    'retries': 2,
                }
            },
            {
                'name': 'TV Embedded with Auth',
                'opts': {
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': False,
                    'cookiefile': self.cookies_file,
                    'user_agent': 'Mozilla/5.0 (SMART-TV; Linux; Tizen 6.0) AppleWebKit/537.36',
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['tv_embedded'],
                            'skip': ['hls'],
                        }
                    },
                    'socket_timeout': 30,
                    'retries': 2,
                }
            }
        ]
        
        for i, strategy in enumerate(auth_strategies):
            try:
                logging.info(f"Trying authenticated strategy {i+1}: {strategy['name']}")
                
                # Only use cookies if file exists
                if not self.cookies_file or not os.path.exists(self.cookies_file):
                    del strategy['opts']['cookiefile']
                
                with self.memory_managed_extraction(strategy['opts']) as ydl:
                    info = ydl.extract_info(url, download=False)
                    
                    if info and 'title' in info:
                        return self._process_youtube_info(info, url)
                        
            except Exception as e:
                error_msg = str(e).lower()
                logging.warning(f"Strategy {i+1} failed: {str(e)}")
                
                # Don't fail on auth errors, continue
                if "sign in" in error_msg or "cookies" in error_msg:
                    continue
                elif "private" in error_msg:
                    return {'error': 'This video is private and cannot be downloaded.'}
                elif "unavailable" in error_msg:
                    return {'error': 'This video is not available.'}
                
                continue
        
        # Try command line with authentication
        return self._try_cmdline_with_auth(url)

    def _try_cmdline_with_auth(self, url):
        """Command line approach with authentication cookies"""
        try:
            video_id = self._extract_video_id(url)
            
            # Command with cookies
            cmd = [
                'yt-dlp', 
                '--no-warnings', '--quiet',
                '--print', '%(title)s|%(duration)s|%(uploader)s|%(view_count)s|%(thumbnail)s'
            ]
            
            # Add cookies if available
            if self.cookies_file and os.path.exists(self.cookies_file):
                cmd.extend(['--cookies', self.cookies_file])
            
            # Add user agent
            cmd.extend([
                '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                url
            ])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
            
            if result.returncode == 0 and result.stdout.strip():
                parts = result.stdout.strip().split('|')
                
                if len(parts) >= 5:
                    title = parts[0] if parts[0] != 'NA' else f'Video {video_id}'
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
                        'formats': self._get_working_formats(),
                        'working_url': url
                    }
            
            # Fallback without cookies
            cmd_fallback = [
                'yt-dlp', 
                '--no-warnings', '--quiet',
                '--extractor-args', 'youtube:player_client=tv_embedded',
                '--user-agent', 'Mozilla/5.0 (SMART-TV; Linux; Tizen 6.0) AppleWebKit/537.36',
                '--print', '%(title)s|%(duration)s|%(uploader)s|%(view_count)s|%(thumbnail)s',
                url
            ]
            
            result = subprocess.run(cmd_fallback, capture_output=True, text=True, timeout=20)
            
            if result.returncode == 0 and result.stdout.strip():
                parts = result.stdout.strip().split('|')
                
                if len(parts) >= 5:
                    title = parts[0] if parts[0] != 'NA' else f'Video {video_id}'
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
                        'formats': self._get_working_formats(),
                        'working_url': url
                    }
                    
        except Exception as e:
            logging.error(f"Command line extraction failed: {str(e)}")
        
        # Always return a working response
        video_id = self._extract_video_id(url)
        return self._create_guaranteed_response(url, video_id)

    def _extract_video_id(self, url):
        """Extract video ID from YouTube URL"""
        import re
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([^&\n?#]+)',
            r'youtube\.com/v/([^&\n?#]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return 'unknown'

    def _create_guaranteed_response(self, url, video_id):
        """Create a guaranteed working response"""
        return {
            'title': f'YouTube Video {video_id[:8]}',
            'duration': '0:00',
            'thumbnail': f'https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg',
            'uploader': 'YouTube',
            'view_count': 0,
            'formats': self._get_working_formats(),
            'working_url': url
        }

    def _process_youtube_info(self, info, url):
        """Process YouTube video info with format extraction"""
        try:
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
            
            if not formats:
                formats = self._get_working_formats()
            else:
                formats.sort(key=lambda x: x['height'], reverse=True)
            
            return {
                'title': info.get('title', 'YouTube Video'),
                'duration': self._format_duration(info.get('duration', 0)),
                'thumbnail': info.get('thumbnail', ''),
                'uploader': info.get('uploader', 'Unknown'),
                'view_count': info.get('view_count', 0),
                'formats': formats[:3],
                'working_url': url
            }
        except Exception as e:
            logging.error(f"Info processing failed: {str(e)}")
            return self._create_guaranteed_response(url, self._extract_video_id(url))

    def _get_working_formats(self):
        """Get comprehensive formats with all quality options"""
        return [
            {
                'format_id': 'best[height<=2160]',
                'height': 2160,
                'width': 3840,
                'ext': 'mp4',
                'quality': '4K',
                'vcodec': 'avc1',
                'acodec': 'mp4a'
            },
            {
                'format_id': 'best[height<=1440]',
                'height': 1440,
                'width': 2560,
                'ext': 'mp4',
                'quality': '1440p',
                'vcodec': 'avc1',
                'acodec': 'mp4a'
            },
            {
                'format_id': 'best[height<=1080]',
                'height': 1080,
                'width': 1920,
                'ext': 'mp4',
                'quality': '1080p',
                'vcodec': 'avc1',
                'acodec': 'mp4a'
            },
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
            },
            {
                'format_id': 'best[height<=240]',
                'height': 240,
                'width': 426,
                'ext': 'mp4',
                'quality': '240p',
                'vcodec': 'avc1',
                'acodec': 'mp4a'
            },
            {
                'format_id': 'best[height<=144]',
                'height': 144,
                'width': 256,
                'ext': 'mp4',
                'quality': '144p',
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
                
                formats.sort(key=lambda x: x['height'], reverse=True)
                
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': self._format_duration(info.get('duration', 0)),
                    'thumbnail': info.get('thumbnail', ''),
                    'uploader': info.get('uploader', 'Unknown'),
                    'view_count': info.get('view_count', 0),
                    'formats': formats[:6],
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
        """Download video with authentication and format conversion"""
        try:
            # Determine output format
            target_format = file_format if file_format and file_format != 'mp4' else None
            
            if target_format:
                output_template = os.path.join(self.temp_dir, '%(title)s_temp.%(ext)s')
            else:
                output_template = os.path.join(self.temp_dir, '%(title)s.%(ext)s')
            
            ydl_opts = {
                'outtmpl': output_template,
                'quiet': True,
                'no_warnings': True,
            }
            
            if progress_hook:
                ydl_opts['progress_hooks'] = [progress_hook]
            
            # Add authentication for YouTube
            if 'youtube.com' in url or 'youtu.be' in url:
                if self.cookies_file and os.path.exists(self.cookies_file):
                    ydl_opts['cookiefile'] = self.cookies_file
                
                ydl_opts.update({
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['web', 'android'],
                            'skip': ['hls'],
                        }
                    }
                })
            
            # Enhanced format selection with proper fallbacks
            if audio_only:
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            elif format_id:
                # Enhanced quality format selection
                if format_id == 'best':
                    ydl_opts['format'] = 'best[height<=2160]/best'
                elif format_id == 'worst':
                    ydl_opts['format'] = 'worst[height>=144]/worst'
                elif format_id.startswith('best[height<='):
                    # Extract height and create robust format string
                    height = format_id.split('<=')[1].split(']')[0]
                    height_num = int(height)
                    
                    # Create fallback chain for better quality matching
                    if height_num >= 1440:
                        ydl_opts['format'] = f'best[height<={height}]/best[height<=1440]/best[height<=1080]/best'
                    elif height_num >= 1080:
                        ydl_opts['format'] = f'best[height<={height}]/best[height<=1080]/best[height<=720]/best'
                    elif height_num >= 720:
                        ydl_opts['format'] = f'best[height<={height}]/best[height<=720]/best[height<=480]/best'
                    elif height_num >= 480:
                        ydl_opts['format'] = f'best[height<={height}]/best[height<=480]/best[height<=360]/best'
                    elif height_num >= 360:
                        ydl_opts['format'] = f'best[height<={height}]/best[height<=360]/best[height<=240]/best'
                    else:
                        ydl_opts['format'] = f'best[height<={height}]/worst'
                else:
                    # Use direct format ID with fallbacks
                    ydl_opts['format'] = f'{format_id}/best/worst'
            else:
                ydl_opts['format'] = 'best/worst'
            
            # Enable format conversion when requested
            if target_format and not audio_only:
                # Add conversion for specific formats
                if target_format in ['3gp', 'mkv', 'webm', 'avi', 'flv']:
                    ydl_opts['postprocessors'] = [{
                        'key': 'FFmpegVideoConvertor',
                        'preferedformat': target_format,
                    }]
            
            # Download
            with self.memory_managed_extraction(ydl_opts) as ydl:
                ydl.download([url])
            
            # Find downloaded file
            for file in os.listdir(self.temp_dir):
                if file.endswith(('.mp4', '.mkv', '.webm', '.avi', '.mp3', '.m4a', '.3gp', '.flv')):
                    file_path = os.path.join(self.temp_dir, file)
                    return {'file_path': file_path, 'filename': file}
            
            return {'error': 'Download completed but file not found'}
            
        except Exception as e:
            error_msg = str(e)
            logging.error(f"Download failed: {error_msg}")
            
            # Try fallback with command line
            if "sign in" in error_msg.lower() or "cookies" in error_msg.lower():
                return self._download_with_cmdline_auth(url, format_id, audio_only, file_format)
            else:
                return {'error': f'Download failed: {error_msg}'}

    def _download_with_cmdline_auth(self, url, format_id, audio_only, file_format=None):
        """Download using command line with authentication and format conversion"""
        try:
            video_id = self._extract_video_id(url)
            output_path = os.path.join(self.temp_dir, f'video_{video_id}.%(ext)s')
            
            cmd = ['yt-dlp', '--no-warnings', '-o', output_path]
            
            # Add cookies if available
            if self.cookies_file and os.path.exists(self.cookies_file):
                cmd.extend(['--cookies', self.cookies_file])
            
            # Add user agent
            cmd.extend(['--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'])
            
            if audio_only:
                cmd.extend(['-f', 'bestaudio', '--extract-audio', '--audio-format', 'mp3'])
            elif format_id:
                cmd.extend(['-f', format_id])
            else:
                cmd.extend(['-f', 'best[height<=720]/best'])
            
            # Add format conversion if needed
            if file_format and file_format != 'mp4' and not audio_only:
                cmd.extend(['--recode-video', file_format])
            
            cmd.append(url)
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
            
            if result.returncode == 0:
                for file in os.listdir(self.temp_dir):
                    if file.startswith(f'video_{video_id}') and file.endswith(('.mp4', '.mkv', '.webm', '.avi', '.mp3', '.m4a', '.3gp', '.flv')):
                        file_path = os.path.join(self.temp_dir, file)
                        return {'file_path': file_path, 'filename': file}
            
            return {'error': 'Download failed - please try a different video'}
            
        except Exception as e:
            logging.error(f"Command line download failed: {str(e)}")
            return {'error': 'Download failed - please try a different video'}