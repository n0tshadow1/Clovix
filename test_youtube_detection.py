#!/usr/bin/env python3
"""
Test script to verify YouTube bot detection improvements
This simulates the conditions that might occur on Vercel deployment
"""

import sys
import json
from video_downloader_vercel import VideoDownloader

def test_youtube_urls():
    """Test various YouTube URLs to check bot detection handling"""
    
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Popular video (should work)
        "https://www.youtube.com/watch?v=invalid_test",   # Invalid ID 
        "https://youtu.be/dQw4w9WgXcQ",                  # Short URL format
    ]
    
    downloader = VideoDownloader()
    
    print("Testing YouTube Bot Detection Improvements")
    print("=" * 50)
    
    for i, url in enumerate(test_urls, 1):
        print(f"\nTest {i}: {url}")
        print("-" * 30)
        
        try:
            result = downloader.get_video_info(url)
            
            if 'error' in result:
                print(f"❌ Error: {result['error']}")
            else:
                print(f"✅ Success: {result['title']}")
                print(f"   Duration: {result.get('duration', 0)} seconds")
                print(f"   Formats: {len(result.get('formats', []))} available")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    test_youtube_urls()