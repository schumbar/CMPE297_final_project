import os
import json
import urllib.parse
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled, VideoUnavailable
import yt_dlp
import whisper

def extract_video_id(url):
    """Extract YouTube video ID from URL"""
    parsed_url = urllib.parse.urlparse(url)
    hostname = parsed_url.hostname.lower() if parsed_url.hostname else ''
    if 'youtu.be' in hostname:
        return parsed_url.path[1:]
    elif 'youtube.com' in hostname:
        if parsed_url.path == '/watch':
            query = urllib.parse.parse_qs(parsed_url.query)
            return query.get('v', [None])[0]
        elif parsed_url.path.startswith(('/embed/', '/v/')):
            return parsed_url.path.split('/')[2]
    return None

def get_youtube_transcription(url: str) -> str:
    """Get transcription from YouTube video"""
    video_id = extract_video_id(url)
    if not video_id:
        return None

    try:
        # Try YouTube subtitles first
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Try manual transcripts first
        for transcript in transcript_list:
            if not transcript.is_generated:
                try:
                    transcript_data = transcript.fetch()
                    return ' '.join([t['text'] for t in transcript_data])
                except Exception:
                    continue

        # Fall back to auto-generated transcripts
        for transcript in transcript_list:
            if transcript.is_generated:
                try:
                    transcript_data = transcript.fetch()
                    return ' '.join([t['text'] for t in transcript_data])
                except Exception:
                    continue

        # If no transcripts available, use Whisper
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': 'audio_file.%(ext)s',
            'quiet': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        audio_file = "audio_file.mp3"
        whisper_model = whisper.load_model("small")
        result = whisper_model.transcribe(audio_file)

        # Clean up
        if os.path.exists(audio_file):
            os.remove(audio_file)
            
        return result["text"]
        
    except (NoTranscriptFound, TranscriptsDisabled, VideoUnavailable) as e:
        return f"Error: {str(e)}"