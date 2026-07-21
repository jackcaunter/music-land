import random
import string
import subprocess
from contextlib import redirect_stdout
from datetime import datetime, date
from io import StringIO
from pathlib import Path

from acquirer import acquire
from lastfm_crawler import recommend_from_artist

BASE_DIR = Path(__file__).resolve().parent

# -----------------------------------------------------------------------------
# Config variables
# -----------------------------------------------------------------------------

AUDIO_FORMAT_PREFERRED = "m4a"

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------


def random_run_name(length=8):
    return "".join(random.choices(string.ascii_lowercase, k=length))

def get_run_name():
    timestamp = datetime.now().strftime("%H%M%S")
    return f"{timestamp}-{random_run_name()}"

def full_run_from_artist(seed_artist):
    run_name = get_run_name()

    output_dir = BASE_DIR / "outputs" / date.today().isoformat()
    output_dir.mkdir(parents=True, exist_ok=True)

    # Capture everything recommend() prints
    buffer = StringIO()
    try:
        with redirect_stdout(buffer):
            recommendation = recommend_from_artist(seed_artist)

            if recommendation is None:
                print(f"Couldn't find a recommendation for artist {seed_artist}.")
                return None

            artist, title = recommendation
            acquire(
                artist, title, output_dir, run_name
            )
    finally:
        full_output = buffer.getvalue()

        # Save the complete output
        log_path = output_dir / f"{run_name}.txt"
        log_path.write_text(full_output, encoding="utf-8")

    audio_file_path = output_dir / f"{run_name}.{AUDIO_FORMAT_PREFERRED}"
    if audio_file_path.exists():
        return audio_file_path
    else:
        return None


def main():
    artist = input("Artist: ")
    try:
        audio_file_path = full_run_from_artist(artist)
        print(f"Downloaded {audio_file_path}")
        subprocess.Popen(["open", "-a", "QuickTime Player", str(audio_file_path)])

    except Exception as e:
        print(e)
        print("it died. nothing downloaded")


if __name__ == "__main__":
    main()
