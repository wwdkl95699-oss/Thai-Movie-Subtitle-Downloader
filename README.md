
```markdown
# 🎬 Thai Movie Subtitle Downloader

A Python script to bulk download Thai (or any language) subtitles from OpenSubtitles.com for your movie collection. Uses the official OpenSubtitles API v1.

[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

- 🔍 Search by movie title (with optional year) or **IMDb ID** (recommended for precision)
- 📥 Bulk download from a simple text file (`movies.txt`)
- 🌍 Configurable language (default `th` for Thai, can be changed to `eng`, `tha`, etc.)
- 💾 Progress tracking – resume interrupted downloads
- ⏱️ Built‑in rate limiting to respect API limits
- 🔐 Secure credential storage (API key, username, password)

## 📋 Prerequisites

- Python 3.6 or higher
- `requests` library (install via `pip install requests`)
- An OpenSubtitles account (free) and an API key – get one [here](https://www.opensubtitles.com/en/consumers)

## 🚀 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/thai-movie-subtitle-downloader.git
   cd thai-movie-subtitle-downloader
   ```

2. Install dependencies:
   ```bash
   pip install requests
   ```

3. Set up your credentials (see [Configuration](#configuration)).

## ⚙️ Configuration

### Credentials File: `open-subs-api-key.txt`

Create a file named `open-subs-api-key.txt` in the same directory as the script, with the following format:

```
username="your_opensubtitles_username"
password="your_password"
apikey="your_api_key"
language="th"
```

- `language` is optional – defaults to `th` (Thai). Change to `eng` for English, `tha` for three‑letter code, etc.
- You can also use a simple colon‑separated line:  
  `username:password:apikey:th`

> ⚠️ **Never commit this file to GitHub!** The provided `.gitignore` will ignore it.

### Movies List: `movies.txt`

List one movie per line. You can use:

- **Movie title only** (e.g., `Bad Genius`)
- **Title with year** (e.g., `Bad Genius (2017)`) – year will be used in search
- **IMDb ID** (e.g., `tt6788942`) – most accurate
- **Title + IMDb ID** (e.g., `Bad Genius (2017) tt6788942`) – recommended for readability

Example (`movies.txt`):

```
Bad Genius (2017) tt6788942
Shutter (2004) tt0440803
Pee Mak (2013) tt2776344
The Medium (2021) tt13446168
```

A full 40‑movie list is provided in the repository.

## ▶️ Usage

Run the script:

```bash
python opensubs-download.py
```

The script will:

1. Read your credentials and log in.
2. Load the movie list from `movies.txt`.
3. For each movie, search for subtitles in the configured language.
4. Download the most popular subtitle (if found) to the `thai_subtitles/` folder.
5. Save progress so you can interrupt (`Ctrl+C`) and resume later.

### Options

- You can change the language at any time by editing `open-subs-api-key.txt` and re‑running.
- To skip already downloaded movies, the script checks its progress file (`thai_subtitles/download_progress.json`).

## 🔧 Troubleshooting

| Problem                          | Solution                                                                 |
|----------------------------------|--------------------------------------------------------------------------|
| `No subtitles found`             | Try a different language code (`th`, `tha`, `eng`). Verify manually on [OpenSubtitles](https://www.opensubtitles.com). |
| `Login failed`                   | Check your username/password/API key. The API key must be from [your consumer page](https://www.opensubtitles.com/en/consumers). |
| `Rate limit hit`                 | The script waits automatically, but you can increase `min_request_interval` in the code if needed. |
| Movie not found by title         | Use the IMDb ID format for that movie.                                  |

## 📦 Dependencies

- `requests` – for API calls

## 📄 License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- [OpenSubtitles API](https://opensubtitles.stoplight.io/) for providing the service.
- All contributors who upload subtitles.

---

**Happy watching!** 🍿
```

---

## 🐍 2. opensubs-download.py

*(This is the full script we already provided – include it in the repository)*

[Copy the final version from the previous message](https://www.example.com) – it's the one with language config and debugging.

---

## 🎞️ 3. movies.txt

```text
Bad Genius (2017) tt6788942
Shutter (2004) tt0440803
Pee Mak (2013) tt2776344
The Medium (2021) tt13446168
One for the Road (2021) tt14936412
Hunger (2023) tt19610614
How to Make Millions Before Grandma Dies (2024) tt27501259
Friend Zone (2019) tt9794508
The Promise (2017) tt7274992
Laddaland (2011) tt2228218
4 Kings (2021) tt15560630
4 Kings 2 (2023) tt28049674
The Undertaker (2023) tt29387148
The Undertaker 2 (2025) tt32044793
Death Whisperer (2023) tt28050232
Death Whisperer 2 (2024) tt33029746
Khun Pan 3 (2023) tt28082542
The Con-Heartist (2020) tt12135140
My Boo (2024) tt27822578
You & Me & Me (2023) tt26216562
Human Resource (2026) tt32291108
Gohan (2026) tt33075490
Inherit (2026) tt32984937
50 First Dates Thai Remake (2026) tt33074694
Diva La Vie (2026) tt33116964
The Debt Collector (2026) tt32296256
My Dearest Assassin (2026) tt33105393
The Red Line (2026) tt33074842
Overacting (2026) tt33077529
A Useful Ghost (2026) tt32310654
The Evil Lawyer (2026) tt32511116
Delusion (2026) tt32419226
Untitled Taweewat Wantha Horror (2026)
Girl From Nowhere: The Reset (2026) tt32399594
Thee and Thee (2026) tt32861608
Scarlet Heart Thailand (2026) tt28049136
Wad Fun Wan Wiwa (2026) tt33075535
Panor 2 (2026) tt32295294
King Keaw (2026) tt32417744
```

---

## 🙈 4. .gitignore

```
# Credentials
open-subs-api-key.txt

# Downloaded subtitles
thai_subtitles/
*.srt

# Python cache
__pycache__/
*.pyc

# Progress file (optional)
thai_subtitles/download_progress.json

# Virtual environment
venv/
env/
.env
```

---

## 🔑 5. open-subs-api-key.txt.example

```text
# Rename this file to open-subs-api-key.txt and fill in your details
username="your_username"
password="your_password"
apikey="your_api_key"
language="th"   # optional, defaults to th
```
