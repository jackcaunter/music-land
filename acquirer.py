import os
import sys
import tempfile
from pathlib import Path

from config_loader import CONFIG

import yt_dlp



# -----------------------------------------------------------------------------
# Config variables
# -----------------------------------------------------------------------------
AUDIO_FORMAT_PREFERRED = CONFIG['AUDIO_FORMAT']
BITRATE_PREFERRED = CONFIG['BITRATE']

def song_to_url(artist, title):
    # Create search queries using the separate artist and title
    query = f"{artist} {title}"
    search_queries = [
        f"ytsearch5:{query}",
        f"ytsearch5:{query} audio",
        f"ytsearch5:{query} topic",
    ]

    ydl_opts = {"quiet": True, "skip_download": True, "extract_flat": True}

    candidates = []

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for sq in search_queries:
            results = ydl.extract_info(sq, download=False)
            if "entries" in results:
                for entry in results["entries"]:
                    video_title = entry.get("title", "").lower()
                    channel = entry.get("channel", "").lower()
                    url = entry["url"]

                    # Convert inputs to lowercase for comparison
                    artist_lower = artist.lower()
                    title_lower = title.lower()
                    query_lower = f"{artist_lower} - {title_lower}"

                    # Classify candidate
                    if "edit" in video_title and "edit" not in title_lower:
                        rank = 9999
                    elif "remix" in video_title and "remix" not in title_lower:
                        rank = 9999
                    elif "slowed" in video_title and "slowed" not in title_lower:
                        rank = 99999
                    elif "sped up" in video_title and "sped up" not in title_lower:
                        rank = 99999
                    elif "nightcore" in video_title and "nightcore" not in title_lower:
                        rank = 99999
                    elif "version" in video_title and "version" not in title_lower:
                        rank = 3000
                    elif "remake" in video_title and "remake" not in title_lower:
                        rank = 99999
                    elif "fl studio" in video_title and "fl studio" not in title_lower:
                        rank = 99999
                    elif "reverb" in video_title and "reverb" not in title_lower:
                        rank = 99999
                    elif "reverbed" in video_title and "reverbed" not in title_lower:
                        rank = 99999
                    elif title_lower in video_title and "audio" in video_title:
                        rank = 1
                    elif (
                        video_title == query_lower
                    ):  # video title is exactly "Artist - Title"
                        rank = 2
                    elif (
                        video_title == title_lower and channel == artist_lower
                    ):  # video title is exactly "Title" and channel is "Artist"
                        rank = 3
                    elif (
                        artist_lower in channel and title_lower in video_title
                    ):  # "Artist" in channel and "Title" in video title
                        rank = 4
                    elif (
                        artist_lower in video_title
                        and title_lower in video_title
                        and "topic" in channel
                    ):  # contains both artist and title, with topic channel
                        rank = 5
                    elif "audio" in video_title:
                        rank = 6
                    elif (
                        artist_lower in video_title and title_lower in video_title
                    ):  # contains both artist and title
                        # Calculate leftover characters after removing all occurrences of artist and title
                        temp_title = video_title
                        temp_title = temp_title.replace(artist_lower, "")
                        temp_title = temp_title.replace(title_lower, "")
                        leftover_chars = len(temp_title)
                        rank = 7 + leftover_chars
                    elif title_lower in video_title:  # contains only the title
                        # Calculate leftover characters after removing all occurrences of title
                        temp_title = video_title.replace(title_lower, "")
                        leftover_chars = len(temp_title)
                        rank = 1000 + leftover_chars
                    elif "topic" in channel:
                        rank = 1500
                    else:
                        rank = 2000  # all else is ranked 2000

                    candidates.append(
                        (rank, url, entry.get("title", ""), entry.get("channel", ""))
                    )

                    # only need first set of results
                    break

    # sort by rank
    candidates.sort(key=lambda x: x[0])
    # throw away everything except the top ranked url
    rank, url, result_title, channel = candidates[0]
    print(f"Got url: {url}")
    return url


class SilentLogger:
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        pass


def download_url(
    artist, title, url, output_dir: Path, filename: str
):

    ydl_opts = {
        "format": "bestaudio/best",
        # filename without extension
        "outtmpl": str(output_dir / filename),
        "quiet": True,
        "no_warnings": True,
        "logger": SilentLogger(),
        "progress_hooks": [],
        "writesubtitles": False,
        "writeautomaticsub": False,
        "nopart": True,
        # convert to ext
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": AUDIO_FORMAT_PREFERRED,
                "preferredquality": BITRATE_PREFERRED,
            }
        ],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        # print(f"download failed for {title} by {artist}: {e}", file=sys.stderr)
        # print("download FAILED")
        return False

    return True


def acquire(
    artist: str, title: str, output_path: Path, filename: str
) -> bool:
    # first, search
    url = song_to_url(artist, title)
    # then, download
    return download_url(artist, title, url, output_path, filename)
