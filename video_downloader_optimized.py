import yt_dlp
import tempfile
import os
import logging
import time
import random
import gc
from contextlib import contextmanager

class VideoDownloader:
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        
    @contextmanager
    def memory_managed_extraction(self, ydl_opts):
        """Context manager for memory-efficient video extraction"""
        ydl = None
        try:
            ydl = yt_dlp.YoutubeDL(ydl_opts)
            yield ydl
        finally:
            if ydl:
                del ydl
            gc.collect()
        
    def get_video_info(self, url):
        """Extract video information with memory optimization and enhanced YouTube handling"""
        # Try different extraction strategies for YouTube URLs
        if 'youtube.com' in url or 'youtu.be' in url:
            return self._get_youtube_info_optimized(url)
        else:
            return self._get_video_info_standard(url)
    
    def _get_youtube_info_optimized(self, url):
        """Optimized YouTube extraction with multiple fallback strategies"""
        strategies = [
            # Strategy 1: Android TV (best for serverless environments)
            {
                'name': 'Android TV',
                'opts': {
                    'quiet': True,
                    'no_warnings': True,
                    'writethumbnail': False,
                    'writeinfojson': False,
                    'writesubtitles': False,
                    'writeautomaticsub': False,
                    'extract_flat': False,
                    'user_agent': 'com.google.android.youtube/17.36.4 (Linux; U; Android 12; TV) gzip',
                    'socket_timeout': 20,
                    'retries': 1,
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['android_tv'],
                            'skip': ['hls', 'dash'],
                            'player_skip': ['js', 'configs'],
                        }
                    }
                }
            },
            # Strategy 2: iOS Mobile
            {
                'name': 'iOS Mobile',
                'opts': {
                    'quiet': True,
                    'no_warnings': True,
                    'writethumbnail': False,
                    'writeinfojson': False,
                    'extract_flat': False,
                    'user_agent': 'com.google.ios.youtube/17.36.4 (iPhone14,2; U; CPU iOS 15_6 like Mac OS X)',
                    'socket_timeout': 15,
                    'retries': 1,
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['ios'],
                            'skip': ['hls'],
                        }
                    }
                }
            },
            # Strategy 3: Android Creator
            {
                'name': 'Android Creator',
                'opts': {
                    'quiet': True,
                    'no_warnings': True,
                    'writethumbnail': False,
                    'writeinfojson': False,
                    'extract_flat': False,
                    'user_agent': 'Mozilla/5.0 (Linux; Android 12; SM-G973F) AppleWebKit/537.36',
                    'socket_timeout': 15,
                    'retries': 1,
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['android_creator'],
                            'skip': ['hls', 'dash'],
                        }
                    }
                }
            },
            # Strategy 4: Minimal Web
            {
                'name': 'Minimal Web',
                'opts': {
                    'quiet': True,
                    'no_warnings': True,
                    'writethumbnail': False,
                    'writeinfojson': False,
                    'extract_flat': False,
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'socket_timeout': 10,
                    'retries': 1,
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['web'],
                            'skip': ['hls', 'dash'],
                            'player_skip': ['js', 'configs'],
                        }
                    }
                }
            }
        ]
        
        for i, strategy in enumerate(strategies):
            try:
                logging.info(f"Trying {strategy['name']} extraction strategy")
                
                with self.memory_managed_extraction(strategy['opts']) as ydl:
                    info = ydl.extract_info(url, download=False)
                    if info:
                        result = self._process_video_info(info)
                        logging.info(f"Successfully extracted using {strategy['name']}")
                        return result
                        
            except Exception as e:
                error_msg = str(e).lower()
                logging.warning(f"{strategy['name']} failed: {str(e)}")
                
                # Handle specific YouTube errors
                if "player response" in error_msg:
                    continue  # Try next strategy
                elif "private video" in error_msg:
                    return {'error': 'This video is private and cannot be downloaded.'}
                elif "video unavailable" in error_msg:
                    return {'error': 'This video is not available. It may have been deleted or restricted.'}
                elif "age-restricted" in error_msg or "age gate" in error_msg:
                    return {'error': 'This video is age-restricted and cannot be accessed.'}
                elif i == len(strategies) - 1:
                    # Last strategy failed
                    return {
                        'error': f'Unable to access video after trying all methods. This may be due to:\n• YouTube bot detection on serverless platforms\n• Regional restrictions\n• Video access limitations\n\nTry waiting a few minutes and using a different video URL.'
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
            }
            
            with self.memory_managed_extraction(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return self._process_video_info(info)
                
        except Exception as e:
            logging.error(f"Standard extraction failed: {str(e)}")
            return {'error': f'Could not extract video information: {str(e)}'}
    
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
            
            # Process formats with memory efficiency
            formats = info.get('formats', [])
            seen_qualities = set()
            
            for fmt in formats:
                if not fmt.get('height'):
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
                    'quality': quality_key
                }
                
                video_info['formats'].append(format_info)
            
            # Sort by quality and limit to top 10 to save memory
            video_info['formats'].sort(key=lambda x: x['height'], reverse=True)
            video_info['formats'] = video_info['formats'][:10]
            
            # Clean up the original info object
            del info
            gc.collect()
            
            return video_info
            
        except Exception as e:
            logging.error(f"Error processing video info: {str(e)}")
            return {'error': f'Error processing video information: {str(e)}'}
    
    def _format_duration(self, duration):
        """Format duration with memory efficiency"""
        if not duration:
            return "Unknown"
        
        try:
            hours = duration // 3600
            minutes = (duration % 3600) // 60
            seconds = duration % 60
            
            if hours > 0:
                return f"{hours}:{minutes:02d}:{seconds:02d}"
            else:
                return f"{minutes}:{seconds:02d}"
        except:
            return "Unknown"
    
    def download_video(self, url, format_id=None, audio_only=False, file_format=None, progress_hook=None):
        """Download video with memory optimization - simplified for serverless"""
        try:
            # Create memory-efficient temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                ydl_opts = {
                    'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                    'quiet': True,
                    'no_warnings': True,
                    'writethumbnail': False,
                    'writeinfojson': False,
                    'writesubtitles': False,
                    'writeautomaticsub': False,
                }
                
                # Add format selection
                if audio_only:
                    ydl_opts['format'] = 'bestaudio/best'
                    ydl_opts['postprocessors'] = [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': file_format or 'mp3',
                    }]
                else:
                    if format_id and format_id != 'best':
                        ydl_opts['format'] = format_id
                    else:
                        ydl_opts['format'] = 'best[height<=720]/best'  # Limit quality for memory
                
                # Add progress hook
                if progress_hook:
                    ydl_opts['progress_hooks'] = [progress_hook]
                
                with self.memory_managed_extraction(ydl_opts) as ydl:
                    ydl.download([url])
                
                # Find downloaded file
                files = os.listdir(temp_dir)
                if files:
                    file_path = os.path.join(temp_dir, files[0])
                    return {
                        'status': 'success',
                        'file_path': file_path,
                        'filename': files[0]
                    }
                else:
                    return {'error': 'No file was downloaded'}
                    
        except Exception as e:
            logging.error(f"Download error: {str(e)}")
            return {'error': f'Download failed: {str(e)}'}