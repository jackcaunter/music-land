# music land 0.1

Command line utility for non-algorithmic, audio-only music discovery.

## Setup

### 1. Install Python

If you don't already have Python 3 installed, install it first.

- **Windows**: Download Python from [python.org](https://www.python.org/downloads/), then verify the installation:
  ```
  python --version
  ```

- **Mac**: Install Python using Homebrew, then verify the installation:
  ```
  brew install python3
  python3 --version
  ```


### 2. Get the project

If you haven't downloaded the project yet, you can either:

- **Clone this repository** (recommended if you're using Git):
```
  git clone <repo-url>
```

Or download the project as a ZIP from the repository page, then extract it.

Once you have the project on your computer, open your terminal and cd into the project folder:

```
cd music-land
```

All the following steps happen inside this folder.

### 3. Create a virtual environment

**Windows**
```
python -m venv .venv
.venv\Scripts\activate
```

**Mac**
```
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install requirements

```
pip install -r requirements.txt
```

### 5. Get a Last.fm API key

Get one at [last.fm/api](https://www.last.fm/api/account/create).

Create a file called `.env` in the root of the project:

```
LASTFM_API_KEY=your_key_here
```

### 6. (Optional) Local config

Copy `config.py` to `config_local.py` to set your own options. If `config_local.py` exists, it's used instead of `config.py`.

## Usage

Each time you open a new terminal, activate the virtual environment first:

**Windows**
```
.venv\Scripts\activate
```

**Mac**
```
source .venv/bin/activate
```

Then run:

```
python main.py
```

You'll be prompted for an artist, then get a song recommendation based on that artist.

- The song won't be from the artist specified
- Even with the same artist, it's highly unlikely to get the same song twice

Pass the artist directly instead:

```
python main.py "Weezer"
```

By default, the recommended song is opened automatically. To skip that:

```
python main.py --no-open
```

After a successful run, the song and its trace `.txt` file are deposited in `/outputs`.

Enjoy!
