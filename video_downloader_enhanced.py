import yt_dlp
import tempfile
import os
import logging
import gc
import time
import random
from contextlib import contextmanager

class VideoDownloader:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        
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
            # Force garbage collection
            gc.collect()
    
    def get_video_info(self, url):
        """Extract video information with enhanced YouTube bot detection bypass"""
        try:
            # Try different extraction strategies for YouTube URLs
            if 'youtube.com' in url or 'youtu.be' in url:
                return self._get_youtube_info_enhanced(url)
            else:
                return self._get_video_info_standard(url)
        except Exception as e:
            logging.error(f"Error in get_video_info: {str(e)}")
            return {'error': f'Failed to extract video information: {str(e)}'}
    
    def _get_youtube_info_enhanced(self, url):
        """Enhanced YouTube extraction with advanced bot detection bypass"""
        
        # Anti-bot detection strategies with randomization
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
        ]
        
        strategies = [
            # Strategy 1: iOS with realistic behavior simulation
            {
                'name': 'iOS Mobile Enhanced',
                'opts': {
                    'quiet': True,
                    'no_warnings': True,
                    'writethumbnail': False,
                    'writeinfojson': False,
                    'extract_flat': False,
                    'user_agent': random.choice(user_agents),
                    'socket_timeout': 30,
                    'retries': 3,
                    'sleep_interval': random.uniform(2, 4),
                    'max_sleep_interval': 8,
                    'http_headers': {
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'DNT': '1',
                        'Connection': 'keep-alive',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'none',
                        'Sec-Fetch-User': '?1',
                        'Cache-Control': 'no-cache',
                        'Pragma': 'no-cache',
                    },
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['ios'],
                            'skip': ['hls', 'dash'],
                            'player_skip': ['configs'],
                            'innertube_host': 'youtubei.googleapis.com',
                            'innertube_key': 'AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8',
                        }
                    }
                }
            },
            # Strategy 2: Android TV with anti-detection headers
            {
                'name': 'Android TV Anti-Bot',
                'opts': {
                    'quiet': True,
                    'no_warnings': True,
                    'writethumbnail': False,
                    'writeinfojson': False,
                    'extract_flat': False,
                    'user_agent': 'com.google.android.youtube/17.49.4 (Linux; U; Android 11; SM-T870 Build/RP1A.200720.012) gzip',
                    'socket_timeout': 30,
                    'retries': 3,
                    'sleep_interval': random.uniform(3, 5),
                    'max_sleep_interval': 10,
                    'http_headers': {
                        'Accept': '*/*',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate',
                        'Connection': 'keep-alive',
                        'X-YouTube-Client-Name': '3',
                        'X-YouTube-Client-Version': '17.49.4',
                    },
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['android_tv'],
                            'skip': ['hls', 'dash'],
                            'player_skip': ['js'],
                            'include_hls_manifest': False,
                            'include_dash_manifest': False,
                        }
                    }
                }
            },
            # Strategy 3: Web with residential-like fingerprint
            {
                'name': 'Web Residential',
                'opts': {
                    'quiet': True,
                    'no_warnings': True,
                    'writethumbnail': False,
                    'writeinfojson': False,
                    'extract_flat': False,
                    'user_agent': random.choice(user_agents),
                    'socket_timeout': 35,
                    'retries': 2,
                    'sleep_interval': random.uniform(4, 6),
                    'max_sleep_interval': 12,
                    'http_headers': {
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'none',
                        'Sec-Fetch-User': '?1',
                        'Cache-Control': 'max-age=0',
                    },
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['web'],
                            'skip': ['hls', 'dash'],
                            'player_skip': ['js', 'configs'],
                        }
                    }
                }
            },
            # Strategy 4: Android mobile with realistic timing
            {
                'name': 'Android Mobile Realistic',
                'opts': {
                    'quiet': True,
                    'no_warnings': True,
                    'writethumbnail': False,
                    'writeinfojson': False,
                    'extract_flat': False,
                    'user_agent': 'com.google.android.youtube/17.49.4 (Linux; U; Android 12; SM-G973F Build/SP1A.210812.016) gzip',
                    'socket_timeout': 25,
                    'retries': 2,
                    'sleep_interval': random.uniform(2, 4),
                    'max_sleep_interval': 8,
                    'http_headers': {
                        'Accept': '*/*',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate',
                        'Connection': 'keep-alive',
                        'X-YouTube-Client-Name': '3',
                        'X-YouTube-Client-Version': '17.49.4',
                    },
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['android'],
                            'skip': ['hls', 'dash'],
                        }
                    }
                }
            }
        ]
        
        for i, strategy in enumerate(strategies):
            try:
                logging.info(f"Trying {strategy['name']} extraction strategy")
                
                # Add random delay to simulate human behavior
                if i > 0:  # No delay for first attempt
                    time.sleep(random.uniform(1, 3))
                
                with self.memory_managed_extraction(strategy['opts']) as ydl:
                    info = ydl.extract_info(url, download=False)
                    if info and 'title' in info:
                        result = self._process_video_info(info)
                        logging.info(f"Successfully extracted using {strategy['name']}")
                        return result
                        
            except Exception as e:
                error_msg = str(e).lower()
                logging.warning(f"{strategy['name']} failed: {str(e)}")
                
                # Handle specific YouTube errors with better messages
                if "sign in to confirm" in error_msg or "not a bot" in error_msg:
                    if i == len(strategies) - 1:  # Last strategy
                        return {
                            'error': 'YouTube requires verification for this video. The platform is detecting automated requests. This is a temporary issue that affects cloud hosting platforms.'
                        }
                    continue
                elif "private video" in error_msg:
                    return {'error': 'This video is private and cannot be downloaded.'}
                elif "video unavailable" in error_msg:
                    return {'error': 'This video is not available. It may have been deleted or restricted.'}
                elif "age-restricted" in error_msg or "age gate" in error_msg:
                    return {'error': 'This video is age-restricted and cannot be accessed.'}
                elif "copyright" in error_msg or "blocked" in error_msg:
                    return {'error': 'This video is blocked due to copyright restrictions.'}
                
                # If not the last strategy, continue to next one
                if i < len(strategies) - 1:
                    continue
                else:
                    return {
                        'error': 'Unable to access this YouTube video after trying multiple methods. This may be due to regional restrictions or platform limitations.'
                    }
        
        return {'error': 'Failed to extract video information after all attempts'}
    
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
            # Extract essential information only to save memory
            video_info = {
                'title': info.get('title', 'Unknown Title'),
                'uploader': info.get('uploader', 'Unknown'),
                'duration': self._format_duration(info.get('duration')),
                'thumbnail': info.get('thumbnail', ''),
                'view_count': info.get('view_count', 0),
                'formats': []
            }
            
            # Process formats with memory efficiency - filter out non-video formats
            formats = info.get('formats', [])
            seen_qualities = set()
            
            for fmt in formats:
                # Skip non-video formats (like storyboard/mhtml)
                if not fmt.get('height') or fmt.get('ext') in ['mhtml', 'webp', 'jpg']:
                    continue
                    
                # Skip audio-only formats when processing video formats
                if fmt.get('acodec') != 'none' and fmt.get('vcodec') == 'none':
                    continue
                    
                height = fmt.get('height')
                quality_key = f"{height}p"
                
                # Avoid duplicate qualities to save memory
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
            
            # Sort formats by quality (highest first) and limit to top 10
            video_info['formats'].sort(key=lambda x: x['height'] or 0, reverse=True)
            video_info['formats'] = video_info['formats'][:10]
            
            return video_info
            
        except Exception as e:
            logging.error(f"Error processing video info: {str(e)}")
            return {'error': f'Failed to process video information: {str(e)}'}
    
    def _format_duration(self, duration):
        """Format duration with memory efficiency"""
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
        """Download video with memory optimization - simplified for serverless"""
        try:
            # Basic download configuration optimized for memory
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
                
                # Find the downloaded file
                for file in os.listdir(self.temp_dir):
                    if not file.startswith('.'):
                        return os.path.join(self.temp_dir, file)
                        
                return None
                
        except Exception as e:
            logging.error(f"Download failed: {str(e)}")
            return None