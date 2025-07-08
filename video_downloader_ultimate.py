import yt_dlp
import tempfile
import os
import logging
import gc
import time
import random
import requests
from contextlib import contextmanager

class VideoDownloader:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        self.session = requests.Session()
        
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
        """Extract video information with ultimate YouTube bot detection bypass"""
        try:
            if 'youtube.com' in url or 'youtu.be' in url:
                return self._get_youtube_info_ultimate(url)
            else:
                return self._get_video_info_standard(url)
        except Exception as e:
            logging.error(f"Error in get_video_info: {str(e)}")
            return {'error': f'Failed to extract video information: {str(e)}'}
    
    def _get_youtube_info_ultimate(self, url):
        """Ultimate YouTube extraction with the most effective bypass methods"""
        
        # Method 1: Try with bypassing age restriction and bot detection
        bypass_strategies = [
            # Strategy 1: TV client with embed bypass
            {
                'name': 'TV Embed Bypass',
                'opts': {
                    'quiet': True,
                    'no_warnings': True,
                    'writethumbnail': False,
                    'writeinfojson': False,
                    'extract_flat': False,
                    'user_agent': 'Mozilla/5.0 (SMART-TV; Linux; Tizen 2.4.0) AppleWebKit/538.1 (KHTML, like Gecko) SamsungBrowser/1.0 TV Safari/538.1',
                    'socket_timeout': 30,
                    'retries': 3,
                    'sleep_interval': 1,
                    'max_sleep_interval': 3,
                    'http_headers': {
                        'Accept': '*/*',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate',
                        'Connection': 'keep-alive',
                        'X-YouTube-Client-Name': '85',  # TV client
                        'X-YouTube-Client-Version': '1.0',
                        'Origin': 'https://www.youtube.com',
                        'Referer': 'https://www.youtube.com/',
                    },
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['tv_embedded'],
                            'skip': ['hls', 'dash'],
                            'player_skip': ['js', 'configs'],
                        }
                    }
                }
            },
            # Strategy 2: Android TV with MWEB fallback  
            {
                'name': 'Android TV MWEB',
                'opts': {
                    'quiet': True,
                    'no_warnings': True,
                    'writethumbnail': False,
                    'writeinfojson': False,
                    'extract_flat': False,
                    'user_agent': 'com.google.android.youtube/17.50.4 (Linux; U; Android 11; BRAVIA 4K VH21 Build/R151014.012) gzip',
                    'socket_timeout': 25,
                    'retries': 2,
                    'sleep_interval': 2,
                    'max_sleep_interval': 5,
                    'http_headers': {
                        'Accept': '*/*',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate',
                        'Connection': 'keep-alive',
                        'X-YouTube-Client-Name': '85',
                        'X-YouTube-Client-Version': '17.50.4',
                    },
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['mweb', 'android_tv'],
                            'skip': ['hls', 'dash'],
                            'include_hls_manifest': False,
                        }
                    }
                }
            },
            # Strategy 3: Web with embed parameters
            {
                'name': 'Web Embed',
                'opts': {
                    'quiet': True,
                    'no_warnings': True,
                    'writethumbnail': False,
                    'writeinfojson': False,
                    'extract_flat': False,
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'socket_timeout': 20,
                    'retries': 2,
                    'sleep_interval': 1,
                    'max_sleep_interval': 4,
                    'http_headers': {
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Connection': 'keep-alive',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'none',
                        'Origin': 'https://www.youtube.com',
                        'Referer': 'https://www.youtube.com/embed/',
                    },
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['web_embedded'],
                            'skip': ['hls', 'dash'],
                            'player_skip': ['js'],
                        }
                    }
                }
            },
            # Strategy 4: iOS without age restrictions
            {
                'name': 'iOS Unrestricted',
                'opts': {
                    'quiet': True,
                    'no_warnings': True,
                    'writethumbnail': False,
                    'writeinfojson': False,
                    'extract_flat': False,
                    'user_agent': 'com.google.ios.youtube/17.50.4 (iPhone15,2; U; CPU iOS 16_0 like Mac OS X)',
                    'socket_timeout': 20,
                    'retries': 2,
                    'sleep_interval': 1,
                    'max_sleep_interval': 3,
                    'http_headers': {
                        'Accept': '*/*',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate',
                        'Connection': 'keep-alive',
                        'X-YouTube-Client-Name': '5',
                        'X-YouTube-Client-Version': '17.50.4',
                    },
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['ios_embedded'],
                            'skip': ['hls'],
                        }
                    }
                }
            }
        ]
        
        for i, strategy in enumerate(bypass_strategies):
            try:
                logging.info(f"Trying {strategy['name']} bypass strategy")
                
                # Add random delay between attempts
                if i > 0:
                    time.sleep(random.uniform(0.5, 2))
                
                with self.memory_managed_extraction(strategy['opts']) as ydl:
                    info = ydl.extract_info(url, download=False)
                    if info and 'title' in info:
                        result = self._process_video_info(info)
                        logging.info(f"SUCCESS: {strategy['name']} bypass worked!")
                        return result
                        
            except Exception as e:
                error_msg = str(e).lower()
                logging.warning(f"{strategy['name']} failed: {str(e)}")
                
                # Skip to next strategy for common bot detection errors
                if any(phrase in error_msg for phrase in ['sign in to confirm', 'not a bot', 'player response']):
                    continue
                    
                # Handle specific errors
                elif "private video" in error_msg:
                    return {'error': 'This video is private and cannot be downloaded.'}
                elif "video unavailable" in error_msg:
                    return {'error': 'This video is not available. It may have been deleted or restricted.'}
                elif "age-restricted" in error_msg:
                    continue  # Try next strategy for age-restricted
                elif "copyright" in error_msg or "blocked" in error_msg:
                    return {'error': 'This video is blocked due to copyright restrictions.'}
        
        # If all bypass strategies fail, try a different approach with youtube-dl format
        logging.info("All bypass strategies failed, trying alternative extraction")
        try:
            return self._try_alternative_extraction(url)
        except:
            return {
                'error': 'Unable to access this YouTube video. YouTube is currently blocking automated access from cloud platforms. Try:\n\n• Using a different video URL\n• Waiting a few minutes and trying again\n• Using other platforms (Instagram, TikTok, Facebook work perfectly)'
            }
    
    def _try_alternative_extraction(self, url):
        """Alternative extraction method as last resort"""
        try:
            # Simplified extraction with minimal options
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,  # Only get basic info
                'user_agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
                'socket_timeout': 15,
                'retries': 1,
            }
            
            with self.memory_managed_extraction(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info:
                    # Return basic info if available
                    return {
                        'title': info.get('title', 'Video'),
                        'uploader': info.get('uploader', 'Unknown'),
                        'duration': 'Unknown',
                        'thumbnail': info.get('thumbnail', ''),
                        'view_count': 0,
                        'formats': [
                            {
                                'format_id': 'best',
                                'height': 720,
                                'width': 1280,
                                'ext': 'mp4',
                                'quality': '720p'
                            }
                        ]
                    }
                    
        except Exception as e:
            logging.error(f"Alternative extraction failed: {str(e)}")
            raise e
    
    def _get_video_info_standard(self, url):
        """Standard extraction for non-YouTube platforms"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'writethumbnail': False,
                'writeinfojson': False,
                'extract_flat': False,
                'socket_timeout': 20,
                'retries': 2,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            }
            
            with self.memory_managed_extraction(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return self._process_video_info(info)
                
        except Exception as e:
            logging.error(f"Standard extraction failed: {str(e)}")
            return {'error': f'Failed to extract video information: {str(e)}'}
    
    def _process_video_info(self, info):
        """Process and format video information with memory optimization"""
        try:
            video_info = {
                'title': info.get('title', 'Unknown Title'),
                'uploader': info.get('uploader', 'Unknown'),
                'duration': self._format_duration(info.get('duration')),
                'thumbnail': info.get('thumbnail', ''),
                'view_count': info.get('view_count', 0),
                'formats': []
            }
            
            # Process formats with memory efficiency
            formats = info.get('formats', [])
            seen_qualities = set()
            
            for fmt in formats:
                if not fmt.get('height') or fmt.get('ext') in ['mhtml', 'webp', 'jpg']:
                    continue
                    
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
                
                video_info['formats'].append(format_info)
            
            # Sort and limit formats
            video_info['formats'].sort(key=lambda x: x['height'] or 0, reverse=True)
            video_info['formats'] = video_info['formats'][:10]
            
            return video_info
            
        except Exception as e:
            logging.error(f"Error processing video info: {str(e)}")
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
        """Download video with optimized settings"""
        try:
            ydl_opts = {
                'format': format_id or ('bestaudio' if audio_only else 'best[ext=mp4]'),
                'outtmpl': os.path.join(self.temp_dir, '%(title)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'socket_timeout': 30,
                'retries': 2,
            }
            
            if progress_hook:
                ydl_opts['progress_hooks'] = [progress_hook]
            
            with self.memory_managed_extraction(ydl_opts) as ydl:
                ydl.download([url])
                
                for file in os.listdir(self.temp_dir):
                    if not file.startswith('.'):
                        return os.path.join(self.temp_dir, file)
                        
                return None
                
        except Exception as e:
            logging.error(f"Download failed: {str(e)}")
            return None