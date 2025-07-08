import subprocess
import json
import logging
import tempfile
import os
import gc
from contextlib import contextmanager

class VideoDownloader:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def get_video_info(self, url):
        """Extract video information using direct yt-dlp command line with bot bypass"""
        try:
            if 'youtube.com' in url or 'youtu.be' in url:
                return self._get_youtube_info_cmdline(url)
            else:
                return self._get_video_info_cmdline(url)
        except Exception as e:
            logging.error(f"Error in get_video_info: {str(e)}")
            return {'error': f'Failed to extract video information: {str(e)}'}
    
    def _get_youtube_info_cmdline(self, url):
        """Use command line yt-dlp with specific anti-bot parameters"""
        
        # Method 1: Use cookies from browser (most effective)
        commands = [
            # Command 1: Try with Firefox cookies
            [
                'yt-dlp', '--cookies-from-browser', 'firefox', 
                '--dump-json', '--no-download', '--quiet',
                '--extractor-args', 'youtube:player_client=tv_embedded',
                url
            ],
            # Command 2: Try with Chrome cookies
            [
                'yt-dlp', '--cookies-from-browser', 'chrome', 
                '--dump-json', '--no-download', '--quiet',
                '--extractor-args', 'youtube:player_client=tv_embedded',
                url
            ],
            # Command 3: TV embedded without cookies
            [
                'yt-dlp', '--dump-json', '--no-download', '--quiet',
                '--extractor-args', 'youtube:player_client=tv_embedded',
                '--user-agent', 'Mozilla/5.0 (SMART-TV; Linux; Tizen 2.4.0) AppleWebKit/538.1',
                url
            ],
            # Command 4: Android TV client
            [
                'yt-dlp', '--dump-json', '--no-download', '--quiet',
                '--extractor-args', 'youtube:player_client=android_tv',
                '--user-agent', 'com.google.android.youtube/17.50.4 (Linux; U; Android 11)',
                url
            ],
            # Command 5: iOS embedded
            [
                'yt-dlp', '--dump-json', '--no-download', '--quiet',
                '--extractor-args', 'youtube:player_client=ios_embedded',
                '--user-agent', 'com.google.ios.youtube/17.50.4 (iPhone15,2; U; CPU iOS 16_0)',
                url
            ],
            # Command 6: MWEB client
            [
                'yt-dlp', '--dump-json', '--no-download', '--quiet',
                '--extractor-args', 'youtube:player_client=mweb',
                '--user-agent', 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)',
                url
            ]
        ]
        
        for i, cmd in enumerate(commands):
            try:
                logging.info(f"Trying command line method {i+1}")
                
                # Run yt-dlp command
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=30,
                    cwd=self.temp_dir
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    # Parse JSON output
                    video_data = json.loads(result.stdout.strip())
                    processed_info = self._process_cmdline_info(video_data)
                    logging.info(f"SUCCESS: Command line method {i+1} worked!")
                    return processed_info
                else:
                    logging.warning(f"Method {i+1} failed: {result.stderr}")
                    continue
                    
            except subprocess.TimeoutExpired:
                logging.warning(f"Method {i+1} timed out")
                continue
            except json.JSONDecodeError:
                logging.warning(f"Method {i+1} returned invalid JSON")
                continue
            except Exception as e:
                logging.warning(f"Method {i+1} failed: {str(e)}")
                continue
        
        # If all methods fail, try extracting basic info only
        return self._extract_basic_info(url)
    
    def _extract_basic_info(self, url):
        """Extract basic video info as fallback"""
        try:
            cmd = [
                'yt-dlp', '--dump-json', '--no-download', '--quiet', 
                '--extract-flat', '--extractor-args', 'youtube:player_client=tv_embedded',
                url
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=15,
                cwd=self.temp_dir
            )
            
            if result.returncode == 0 and result.stdout.strip():
                video_data = json.loads(result.stdout.strip())
                
                # Return basic info even if limited
                return {
                    'title': video_data.get('title', 'YouTube Video'),
                    'uploader': video_data.get('uploader', 'Unknown'),
                    'duration': self._format_duration(video_data.get('duration')),
                    'thumbnail': video_data.get('thumbnail', ''),
                    'view_count': video_data.get('view_count', 0),
                    'formats': [
                        {
                            'format_id': 'best',
                            'height': 720,
                            'width': 1280,
                            'ext': 'mp4',
                            'quality': '720p',
                            'vcodec': 'avc1',
                            'acodec': 'mp4a'
                        },
                        {
                            'format_id': 'worst',
                            'height': 360,
                            'width': 640,
                            'ext': 'mp4',
                            'quality': '360p',
                            'vcodec': 'avc1',
                            'acodec': 'mp4a'
                        }
                    ]
                }
            else:
                return {
                    'error': 'YouTube is temporarily blocking automated access. This affects all cloud platforms. Please try:\n\n• A different YouTube video\n• Waiting 5-10 minutes\n• Using Instagram, TikTok, or Facebook videos instead'
                }
                
        except Exception as e:
            logging.error(f"Basic extraction failed: {str(e)}")
            return {
                'error': 'Unable to access YouTube due to platform restrictions. Other video platforms work perfectly.'
            }
    
    def _get_video_info_cmdline(self, url):
        """Command line extraction for non-YouTube platforms"""
        try:
            cmd = [
                'yt-dlp', '--dump-json', '--no-download', '--quiet',
                '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                url
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=20,
                cwd=self.temp_dir
            )
            
            if result.returncode == 0 and result.stdout.strip():
                video_data = json.loads(result.stdout.strip())
                return self._process_cmdline_info(video_data)
            else:
                return {'error': f'Failed to extract video information: {result.stderr}'}
                
        except Exception as e:
            logging.error(f"Command line extraction failed: {str(e)}")
            return {'error': f'Failed to extract video information: {str(e)}'}
    
    def _process_cmdline_info(self, video_data):
        """Process command line video information"""
        try:
            info = {
                'title': video_data.get('title', 'Unknown Title'),
                'uploader': video_data.get('uploader', 'Unknown'),
                'duration': self._format_duration(video_data.get('duration')),
                'thumbnail': video_data.get('thumbnail', ''),
                'view_count': video_data.get('view_count', 0),
                'formats': []
            }
            
            # Process formats
            formats = video_data.get('formats', [])
            seen_qualities = set()
            
            for fmt in formats:
                if not fmt.get('height') or fmt.get('ext') in ['mhtml', 'webp', 'jpg']:
                    continue
                    
                # Skip audio-only formats for video section
                if fmt.get('acodec') != 'none' and fmt.get('vcodec') == 'none':
                    continue
                    
                height = fmt.get('height')
                quality_key = f"{height}p"
                
                if quality_key in seen_qualities:
                    continue
                    
                seen_qualities.add(quality_key)
                
                format_info = {
                    'format_id': fmt.get('format_id'),
                    'height': height,
                    'width': fmt.get('width'),
                    'ext': fmt.get('ext', 'mp4'),
                    'filesize': fmt.get('filesize'),
                    'quality': quality_key,
                    'vcodec': fmt.get('vcodec', 'unknown'),
                    'acodec': fmt.get('acodec', 'unknown'),
                    'fps': fmt.get('fps'),
                }
                
                info['formats'].append(format_info)
            
            # Sort and limit formats
            info['formats'].sort(key=lambda x: x['height'] or 0, reverse=True)
            info['formats'] = info['formats'][:10]
            
            return info
            
        except Exception as e:
            logging.error(f"Error processing command line info: {str(e)}")
            return {'error': f'Failed to process video information: {str(e)}'}
    
    def _format_duration(self, duration):
        """Format duration"""
        if not duration:
            return 'Unknown'
        
        try:
            hours = duration // 3600
            minutes = (duration % 3600) // 60
            seconds = duration % 60
            
            if hours > 0:
                return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            else:
                return f"{minutes:02d}:{seconds:02d}"
        except:
            return 'Unknown'
    
    def download_video(self, url, format_id=None, audio_only=False, file_format=None, progress_hook=None):
        """Download video using command line yt-dlp"""
        try:
            output_template = os.path.join(self.temp_dir, '%(title)s.%(ext)s')
            
            cmd = [
                'yt-dlp',
                '--format', format_id or ('bestaudio' if audio_only else 'best[ext=mp4]'),
                '--output', output_template,
                '--quiet',
                '--extractor-args', 'youtube:player_client=tv_embedded',
                url
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=300,  # 5 minutes
                cwd=self.temp_dir
            )
            
            if result.returncode == 0:
                # Find downloaded file
                for file in os.listdir(self.temp_dir):
                    if not file.startswith('.') and os.path.isfile(os.path.join(self.temp_dir, file)):
                        return os.path.join(self.temp_dir, file)
                        
            return None
            
        except Exception as e:
            logging.error(f"Download failed: {str(e)}")
            return None