import yt_dlp
import asyncio
from typing import List, Dict, Any

# yt-dlp options to get info without downloading
YDL_OPTS = {
    'quiet': True,
    'no_warnings': True,
    'noplaylist': True,
    'extract_flat': True, # Faster for getting metadata
}

def format_selector(ctx):
    """
    Custom format selector for yt-dlp to get a wide range of formats.
    This function is not used directly in extract_info, but can be useful
    for more advanced filtering if needed. For now, we process all formats.
    """
    formats = ctx.get('formats')[::-1]
    # We will process all available formats and filter later
    return {'formats': formats}

async def get_video_info(url: str) -> Dict[str, Any]:
    """
    Asynchronously extracts video information using yt-dlp.
    Runs the synchronous yt-dlp call in a separate thread to avoid blocking the event loop.
    """
    loop = asyncio.get_running_loop()
    
    with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
        try:
            # Use run_in_executor to run the blocking I/O operation in a thread pool
            info_dict = await loop.run_in_executor(
                None, lambda: ydl.extract_info(url, download=False)
            )

            # In case of a single entry from a playlist/user page
            if 'entries' in info_dict:
                info_dict = info_dict['entries'][0]

            processed_formats = []
            
            # Find the best audio-only format for MP3 download
            audio_formats = [f for f in info_dict.get('formats', []) if f.get('vcodec') == 'none' and f.get('url')]
            best_audio = max(audio_formats, key=lambda f: f.get('abr', 0), default=None)
            
            if best_audio:
                processed_formats.append({
                    "label": f"🎧 MP3 ({best_audio.get('abr', 0)}k)",
                    "quality": f"{best_audio.get('abr', 0)} kbps",
                    "url": best_audio['url'],
                    "ext": "mp3",
                })
            
            # Process video formats
            for f in info_dict.get('formats', []):
                # Filter for formats with both video and audio, or video-only
                if f.get('url') and (f.get('vcodec') != 'none'):
                    # Create a user-friendly label
                    quality = f.get('height')
                    if quality:
                        label = f"🎬 MP4 ({quality}p)"
                        if f.get('acodec') == 'none':
                            label += " (No Audio)"

                        processed_formats.append({
                            "label": label,
                            "quality": f"{quality}p",
                            "url": f['url'],
                            "ext": "mp4",
                        })

            # Handle TikTok image posts (slideshows)
            if not processed_formats and info_dict.get('images'):
                 for i, img in enumerate(info_dict['images']):
                     processed_formats.append({
                        "label": f"🖼️ Image {i+1}",
                        "quality": f"{img.get('width')}x{img.get('height')}",
                        "url": img['url'],
                        "ext": "jpg",
                     })

            return {
                "title": info_dict.get('title'),
                "thumbnail": info_dict.get('thumbnail'),
                "duration": info_dict.get('duration_string', 'N/A'),
                "formats": processed_formats
            }
            
        except yt_dlp.utils.DownloadError as e:
            print(f"Error extracting video info: {e}")
            raise ValueError("Invalid TikTok URL or video is private/unavailable.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            raise RuntimeError("An internal error occurred.")