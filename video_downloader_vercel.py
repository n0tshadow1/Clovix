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
        # Try different extraction strategies for YouTube URLs
        if 'youtube.com' in url or 'youtu.be' in url:
            # First try the enhanced method
            result = self._get_youtube_info_enhanced(url)
            if result and 'error' not in result:
                return result
            
            # If that fails, try the basic method
            logging.info("Enhanced method failed, trying basic extraction...")
            return self._get_youtube_info_basic(url)
        else:
            # For non-YouTube URLs, use standard method
            return self._get_video_info_standard(url)
    
    def _get_youtube_info_enhanced(self, url):
        """Enhanced YouTube extraction with bot detection handling"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Add random delay to avoid bot detection
                if attempt > 0:
                    time.sleep(random.uniform(1, 3))
                    logging.info(f"Retry attempt {attempt + 1} for URL: {url}")
                
                # Rotate user agents to avoid detection
                user_agents = [
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/120.0',
                ]
                selected_ua = user_agents[attempt % len(user_agents)]
                
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': False,
                    'user_agent': selected_ua,
                    'socket_timeout': 60,
                    'retries': 3,
                    'fragment_retries': 3,
                    'extractor_args': {
                        'youtube': {
                            'skip': ['hls', 'dash'],
                            'player_skip': ['configs'],
                            'innertube_host': 'www.youtube.com',
                            'innertube_key': None,
                            'player_client': ['android', 'web'],
                        }
                    },
                    'http_headers': {
                        'User-Agent': selected_ua,
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'DNT': '1',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'none',
                        'Cache-Control': 'max-age=0',
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
                
                # Check for different types of YouTube errors and handle accordingly
                if "Sign in to confirm" in error_msg or "bot" in error_msg.lower():
                    if attempt < max_retries - 1:
                        delay = (2 ** attempt) + random.uniform(0.5, 2)
                        logging.info(f"Bot detection detected, retrying in {delay:.1f} seconds...")
                        time.sleep(delay)  # Exponential backoff with jitter
                        continue
                    else:
                        return {
                            'error': 'YouTube is blocking automated requests from this server. This is common on cloud platforms like Vercel. Try:\n• Using the video URL in a different downloader\n• Waiting a few minutes and trying again\n• Using a shorter or different YouTube URL'
                        }
                elif "Private video" in error_msg:
                    return {'error': 'This video is private and cannot be downloaded.'}
                elif "Video unavailable" in error_msg:
                    return {'error': 'This video is not available. It may have been deleted or restricted in your region.'}
                elif "Age-restricted" in error_msg or "age gate" in error_msg.lower():
                    return {'error': 'This video is age-restricted and cannot be accessed without authentication.'}
                elif "Premieres in" in error_msg:
                    return {'error': 'This video is a premiere that has not started yet.'}
                elif attempt == max_retries - 1:
                    # Last attempt failed, provide helpful error message
                    return {
                        'error': f'Could not access video after {max_retries} attempts. This may be due to:\n• Network restrictions on the hosting platform\n• YouTube\'s bot detection\n• Video access limitations\n\nOriginal error: {error_msg}'
                    }
                else:
                    # Continue retrying for other errors
                    delay = random.uniform(1, 3)
                    logging.info(f"Error on attempt {attempt + 1}, retrying in {delay:.1f} seconds...")
                    time.sleep(delay)
                    continue
        
        return {'error': 'Failed to get video information after multiple attempts'}
    
    def _get_youtube_info_basic(self, url):
        """Basic YouTube extraction with minimal options"""
        try:
            # Very basic extraction with mobile user agent
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'user_agent': 'com.google.android.youtube/17.36.4 (Linux; U; Android 12; GB) gzip',
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android'],
                        'skip': ['dash'],
                    }
                },
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    return {'error': 'Could not extract video information'}
                
                # Simplified format extraction
                formats = []
                if info.get('formats'):
                    for fmt in info['formats']:
                        if fmt.get('height') and fmt.get('ext') in ['mp4', 'webm']:
                            quality = f"{fmt['height']}p"
                            formats.append({
                                'quality': quality,
                                'format_id': fmt['format_id'],
                                'ext': fmt['ext'],
                                'filesize': fmt.get('filesize'),
                            })
                
                # Remove duplicates and sort
                seen = set()
                unique_formats = []
                for fmt in formats:
                    if fmt['quality'] not in seen:
                        unique_formats.append(fmt)
                        seen.add(fmt['quality'])
                
                unique_formats.sort(key=lambda x: int(x['quality'].replace('p', '')), reverse=True)
                
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'uploader': info.get('uploader', 'Unknown'),
                    'view_count': info.get('view_count', 0),
                    'formats': unique_formats[:6],
                }
                
        except Exception as e:
            logging.error(f"Basic extraction failed: {str(e)}")
            return {'error': f'Basic extraction failed: {str(e)}'}
    
    def _get_video_info_standard(self, url):
        """Standard extraction for non-YouTube platforms"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'socket_timeout': 30,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    return {'error': 'Could not extract video information'}
                
                # Process formats
                formats = []
                if info.get('formats'):
                    seen_qualities = set()
                    for fmt in info['formats']:
                        if fmt.get('height') and fmt.get('ext'):
                            quality = f"{fmt['height']}p"
                            if quality not in seen_qualities:
                                formats.append({
                                    'quality': quality,
                                    'format_id': fmt['format_id'],
                                    'ext': fmt['ext'],
                                    'filesize': fmt.get('filesize'),
                                })
                                seen_qualities.add(quality)
                
                formats.sort(key=lambda x: int(x['quality'].replace('p', '')), reverse=True)
                
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'uploader': info.get('uploader', 'Unknown'),
                    'view_count': info.get('view_count', 0),
                    'formats': formats[:6],
                }
                
        except Exception as e:
            logging.error(f"Standard extraction failed: {str(e)}")
            return {'error': f'Standard extraction failed: {str(e)}'}
    
    def download_video(self, url, format_id=None, audio_only=False):
        """Download video - simplified for serverless"""
        try:
            output_path = os.path.join(self.temp_dir, '%(title)s.%(ext)s')
            
            # Use the same enhanced headers for downloads
            user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            
            ydl_opts = {
                'outtmpl': output_path,
                'quiet': True,
                'no_warnings': True,
                'user_agent': user_agent,
                'socket_timeout': 60,
                'retries': 3,
                'fragment_retries': 3,
                'extractor_args': {
                    'youtube': {
                        'skip': ['hls', 'dash'],
                        'player_skip': ['configs'],
                        'innertube_host': 'www.youtube.com',
                        'innertube_key': None,
                        'player_client': ['android', 'web'],
                    }
                },
                'http_headers': {
                    'User-Agent': user_agent,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Cache-Control': 'max-age=0',
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