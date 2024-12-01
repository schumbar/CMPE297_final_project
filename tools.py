# ===============================
# File: tools.py
# ===============================
from langchain.tools import StructuredTool
from utils import get_youtube_transcription
import json
import yt_dlp
import whisper
import os

def audio_transcriber_tool(input_str: str) -> str:
    """
    Extracts audio and transcribes the audio from a YouTube video given its URL.
    If subtitles are available from YouTube, it fetches them; otherwise, it uses Whisper to transcribe the audio.

    Parameters:
    - input_str (str): A JSON string containing the URL of the YouTube video.

    Returns:
    str: The transcribed text from the YouTube audio or subtitles.
    """
    try:
        if input_str.strip().startswith('{'):
            inputs = json.loads(input_str)
            url = inputs.get('url') or inputs.get('input_str') or inputs.get('youtube_url')
            if url is None:
                raise ValueError("URL is required in the input JSON.")
        else:
            url = input_str.strip()
            if not url:
                raise ValueError("Input URL is empty.")

        # Try YouTube subtitles first
        youtube_transcription = get_youtube_transcription(url)
        if youtube_transcription:
            return youtube_transcription

        # If no subtitles, use Whisper
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

        os.remove(audio_file)
        return result["text"]
    except Exception as e:
        return f"Error processing audio: {e}"

# Create the tool instance
audio_transcriber = StructuredTool.from_function(
    func=audio_transcriber_tool,
    name="audio_transcriber",
    description="Transcribe audio from a YouTube video URL"
)