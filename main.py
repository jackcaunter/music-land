import argparse
import random
import string
import subprocess
from contextlib import redirect_stdout
from datetime import datetime, date
from io import StringIO
from pathlib import Path
from typing import Optional
import os
import platform
import shutil

from acquirer import acquire
from config_loader import CONFIG
from lastfm_crawler import recommend_from_artist

BASE_DIR = Path(__file__).resolve().parent

# -----------------------------------------------------------------------------
# Config variables
# -----------------------------------------------------------------------------

AUDIO_FORMAT_PREFERRED = CONFIG['AUDIO_FORMAT']
AUDIO_PLAYER = CONFIG['AUDIO_PLAYER']

# -----------------------------------------------------------------------------
# Run naming / output paths
# -----------------------------------------------------------------------------
def random_run_name(length=8):
    return "".join(random.choices(string.ascii_lowercase, k=length))


def get_run_name():
    timestamp = datetime.now().strftime("%H%M%S")
    return f"{timestamp}-{random_run_name()}"


def run_output_dir() -> Path:
    output_dir = BASE_DIR / "outputs" / date.today().isoformat()
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


# -----------------------------------------------------------------------------
# Core run
# -----------------------------------------------------------------------------
def execute_run(seed_artist: str, output_dir: Path, run_name: str) -> Optional[Path]:
    """Runs the recommend->acquire pipeline, capturing all stdout. Returns the
    resulting audio path, or None if no recommendation was found."""
    buffer = StringIO()
    try:
        with redirect_stdout(buffer):
            recommendation = recommend_from_artist(seed_artist)
            if recommendation is None:
                print(f"Couldn't find a recommendation for artist {seed_artist}.")
                audio_file_path = None
            else:
                artist, title = recommendation
                acquire(artist, title, output_dir, run_name)
                audio_file_path = output_dir / f"{run_name}.{AUDIO_FORMAT_PREFERRED}"
                if not audio_file_path.exists():
                    audio_file_path = None
    finally:
        write_log(output_dir, run_name, buffer.getvalue())

    return audio_file_path


def write_log(output_dir: Path, run_name: str, contents: str) -> None:
    log_path = output_dir / f"{run_name}.txt"
    log_path.write_text(contents, encoding="utf-8")


def full_run_from_artist(seed_artist: str) -> Optional[Path]:
    run_name = get_run_name()
    output_dir = run_output_dir()
    return execute_run(seed_artist, output_dir, run_name)


# -----------------------------------------------------------------------------
# Playback
# -----------------------------------------------------------------------------

def play_audio(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(path)

    system = platform.system()

    try:
        if system == "Windows":
            if AUDIO_PLAYER:
                player = shutil.which(AUDIO_PLAYER) or AUDIO_PLAYER
                subprocess.Popen([player, str(path)])
            else:
                os.startfile(str(path))

        elif system == "Darwin":
            if AUDIO_PLAYER:
                subprocess.Popen(["open", "-a", AUDIO_PLAYER, str(path)])
            else:
                subprocess.Popen(["open", str(path)])

        else:
            raise RuntimeError(f"Unsupported platform: {system}")

    except OSError as e:
        raise RuntimeError(f"Couldn't open audio file: {e}") from e
# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------
def parse_args():
    parser = argparse.ArgumentParser(description="Discover and download a track from a seed artist.")
    parser.add_argument("artist", nargs="?", help="Seed artist name (prompted if omitted)")
    parser.add_argument("--no-open", action="store_true", help="Don't open the downloaded file after download")
    return parser.parse_args()


def main():
    args = parse_args()
    artist = args.artist or input("Artist: ")

    try:
        audio_file_path = full_run_from_artist(artist)
    except Exception as e:
        print(f"it died: {e}")
        return

    if audio_file_path is None:
        print("No audio downloaded.")
        return

    print(f"Downloaded {audio_file_path}")
    if not args.no_open:
        play_audio(audio_file_path)


if __name__ == "__main__":
    main()
