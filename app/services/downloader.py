import yt_dlp
import os
from app.core.config import settings

# In-memory progress store: {video_id: {status: str, progress: int}}
progress_data = {}

class YouTubeService:
    def __init__(self):
        self.ydl_opts = {
            'outtmpl': os.path.join(settings.DOWNLOAD_DIR, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
        }

    def get_progress(self, video_id: str):
        return progress_data.get(video_id, {"status": "idle", "progress": 0})

    def get_video_info(self, url: str):
        """
        Fetch video metadata including formats and subtitles.
        """
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Extract relevant data
                formats = []
                for f in info.get('formats', []):
                    if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                         # simple filter for video+audio files to keep it simple for now
                         # typically webm/mp4 are best
                        formats.append({
                            'format_id': f['format_id'],
                            'ext': f['ext'],
                            'resolution': f.get('resolution', 'unknown'),
                            'filesize': f.get('filesize', 0),
                            'note': f.get('format_note', '')
                        })
                
                # Filter out video-only or audio-only logic if needed more strictly
                # For now let's just return what we have

                return {
                    'id': info.get('id'),
                    'title': info.get('title'),
                    'thumbnail': info.get('thumbnail'),
                    'duration': info.get('duration'),
                    'formats': formats,
                    'subtitles': list(info.get('subtitles', {}).keys()) if info.get('subtitles') else [],
                    'auto_subtitles': list(info.get('automatic_captions', {}).keys()) if info.get('automatic_captions') else []
                }
        except Exception as e:
            print(f"Error fetching info: {e}")
            return None

    def download_video(self, url: str, format_id: str, video_id: str):
        """
        Download video with specific format and track progress.
        """
        def progress_hook(d):
            if d['status'] == 'downloading':
                try:
                    total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                    downloaded = d.get('downloaded_bytes', 0)
                    if total > 0:
                        percent = (downloaded / total) * 100
                        progress_data[video_id] = {
                            "status": "downloading", 
                            "progress": int(percent),
                            "speed": d.get('speed', 0),
                            "eta": d.get('eta', 0)
                        }
                except Exception:
                    pass
            elif d['status'] == 'finished':
                progress_data[video_id] = {"status": "completed", "progress": 100}

        opts = self.ydl_opts.copy()
        opts['format'] = format_id
        opts['progress_hooks'] = [progress_hook]
        
        # Initialize
        progress_data[video_id] = {"status": "starting", "progress": 0}
        
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
            return True
        except Exception as e:
            print(f"Error downloading: {e}")
            progress_data[video_id] = {"status": "error", "error": str(e)}
            return False

    def download_subtitles(self, url: str, lang: str = 'en'):
        """
        Download subtitles for RAG processing.
        Returns the path to the subtitle file and the video title.
        """
        opts = {
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': [lang],
            'outtmpl': os.path.join(settings.DOWNLOAD_DIR, '%(id)s'),
            'quiet': True
        }
        
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_id = info['id']
                # Check for the file. yt-dlp appends .lang.vtt
                expected_path = os.path.join(settings.DOWNLOAD_DIR, f"{video_id}.{lang}.vtt")
                if os.path.exists(expected_path):
                    return expected_path
                return None
        except Exception as e:
            print(f"Error downloading subtitles: {e}")
            return None
