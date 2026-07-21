import os
import random
import re
from pathlib import Path
from urllib.parse import quote

import requests
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("LASTFM_API_KEY")
MY_USERNAME = os.getenv("MY_USERNAME")

if not API_KEY:
    raise RuntimeError("LASTFM_API_KEY is missing. Check your .env file for LASTFM_API_KEY.")

if not MY_USERNAME:
    MY_USERNAME = ""


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------


def recommend_from_artist(artist):

    usernames = get_username_urls_from_artist(artist)

    if not usernames:
        print(f"No listeners for artist {artist}. Try a more popular artist")
        return None

    random.shuffle(usernames)

    for username_url in usernames:
        username = username_url.rsplit("/", 1)[-1]
        try:
            if username == MY_USERNAME:
                continue

            recent_tracks = get_recent_tracks(username)

            valid_tracks = select_valid_tracks(recent_tracks)

            if valid_tracks is None:
                continue

            unique_tracks = []

            for track in valid_tracks:
                if track["artist"].lower() != artist.lower():
                    unique_tracks.append(track)

            random.shuffle(unique_tracks)

            for track in unique_tracks:
                username = username_url.rsplit("/", 1)[-1]
                formatted_track = format_track(track)
                print(f"Got track [{formatted_track}] from {username}'s recent tracks")
                print(f"{formatted_track}")
                return track["artist"], track["title"]

        except Exception:
            # user profile failed, deleted account, rate limit...
            print(f"failed on user {username}")
            continue

    print("we tried literally every username, and it failed.")
    return None


def pick_random_history_track(history):
    """Returns a random track that has an artist."""

    valid = [track for track in history if track.get("artist")]

    if not valid:
        return None

    return random.choice(valid)


def get_artist(track):
    return track["artist"]


# -----------------------------------------------------------------------------
# Artist -> listeners
# -----------------------------------------------------------------------------


def get_username_urls_from_artist(artist):
    """
    Input:
        "Radiohead"

    Output:
        [
            "https://last.fm/user/alice",
            "https://last.fm/user/bob",
            ...
        ]
    """

    artist_url = quote(artist.replace(" ", "+"))

    url = f"https://www.last.fm/music/{artist_url}/+listeners"
    print(f"Trying URL: {url}")

    response = requests.get(
        url,
        headers={"User-Agent": "music-land/0.1"},
        timeout=10,
    )
    response.raise_for_status()

    # Extract usernames from href="/user/<username>"
    users = re.findall(r'href="/user/([^"/]+)', response.text)

    # Remove duplicates
    users = list(set(users))

    return users


# -----------------------------------------------------------------------------
# Recent tracks
# -----------------------------------------------------------------------------


def get_recent_tracks(username):
    """

    Get a user's recent 50 tracks.

    Normalize them into the standard track format.


    Return format:

    [
        {
            "artist": "...",
            "title": "...",
            "album": "...",
            "artist_mbid": "...",
            "album_mbid": "...",
            "track_mbid": "..."
        },
        ...
    ]
    """

    headers = {"User-Agent": "music-land/0.1"}

    url = (
        "http://ws.audioscrobbler.com/2.0/"
        f"?method=user.getrecenttracks"
        f"&user={username}"
        f"&api_key={API_KEY}"
        f"&format=json"
    )

    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()

    data = response.json()
    tracks = data.get("recenttracks", {}).get("track", [])

    history = []

    for track in tracks:
        history.append(
            {
                "artist": track.get("artist", {}).get("#text", ""),
                "title": track.get("name", ""),
                "album": track.get("album", {}).get("#text", ""),
                "artist_mbid": track.get("artist", {}).get("mbid", ""),
                "album_mbid": track.get("album", {}).get("mbid", ""),
                "track_mbid": track.get("mbid", ""),
            }
        )

    return history


# -----------------------------------------------------------------------------
# Track selection
# -----------------------------------------------------------------------------


def select_valid_tracks(tracks, history=[]):
    """
    Picks a random track that:

    - has an MBID somewhere
    - isn't already in the user's history
    """

    history_keys = {track_key(track) for track in history}

    valid = []

    for track in tracks:
        if not has_any_mbid(track):
            continue

        if track_key(track) in history_keys:
            continue

        valid.append(track)

    if not valid:
        return None

    return valid


def has_any_mbid(track):
    return any(
        [track.get("artist_mbid"), track.get("album_mbid"), track.get("track_mbid")]
    )


def track_key(track):
    """
    Used to determine if we've already listened to a song.

    Artist + Title should be good enough.
    """

    return (track["artist"].lower(), track["title"].lower())


# -----------------------------------------------------------------------------
# Output
# -----------------------------------------------------------------------------


def format_track(track):
    return f"{track['artist']} - {track['title']}"


# -----------------------------------------------------------------------------
# Test
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    pass
