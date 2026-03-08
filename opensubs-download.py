import requests
import os
import time
import json
import re
import sys
import getpass
from pathlib import Path
from datetime import datetime, timedelta

class ThaiMovieDownloader:
    def __init__(self, credentials_file='open subs-api-key.txt'):
        # Read and parse credentials from file or get manual input
        self.username, self.password, self.api_key, self.language = self.get_credentials(credentials_file)
        self.token = None
        self.token_expiry = None

        self.base_url = "https://api.opensubtitles.com/api/v1"
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "ThaiMovieDownloader v1.0"
        }

        # Login to get token
        if not self.login():
            print("Failed to authenticate. Exiting...")
            sys.exit(1)

        # Create directories
        self.download_dir = Path("thai_subtitles")
        self.download_dir.mkdir(exist_ok=True)

        # Progress tracking file
        self.progress_file = self.download_dir / "download_progress.json"

        # Rate limiting
        self.last_request_time = None
        self.min_request_interval = 1.0  # seconds

        # Load previous progress
        self.progress = self.load_progress()

    def get_credentials(self, filename):
        """Get credentials from file or manual input"""
        username = password = api_key = None
        language = 'th'  # default language

        # Check if file exists and parse it
        if os.path.exists(filename):
            print(f"Found credentials file: {filename}")
            username, password, api_key, language = self.parse_credentials(filename)

            # Validate we have all three (username, password, api_key)
            if username and password and api_key:
                print("✓ All credentials loaded successfully")
                # Return everything including language
                return username, password, api_key, language
            else:
                missing = []
                if not username: missing.append("username")
                if not password: missing.append("password")
                if not api_key: missing.append("api_key")
                print(f"✗ Missing credentials in file: {', '.join(missing)}")
                print("Please re-enter your credentials.\n")

        # If we get here, need to get credentials manually
        return self.prompt_for_credentials(filename)

    def prompt_for_credentials(self, filename):
        """Prompt user for credentials with hidden password input"""
        print("\n" + "="*50)
        print("OPENSUBTITLES CREDENTIALS REQUIRED")
        print("="*50)
        print("\nYou need to provide ALL three credentials:")
        print("- Username")
        print("- Password (will be hidden)")
        print("- API Key")
        print("- Language code (optional, default 'th')")
        print("\n(You can get an API key from https://www.opensubtitles.com)")

        while True:
            print("\nPlease enter your credentials:")
            username = input("Username: ").strip()
            password = getpass.getpass("Password: ").strip()
            api_key = input("API Key: ").strip()
            language = input("Language code (default 'th'): ").strip() or 'th'

            if username and password and api_key:
                # Save for next time
                self.save_credentials(filename, username, password, api_key, language)
                return username, password, api_key, language
            else:
                print("Username, password, and API key are required!")
                retry = input("Try again? (y/n): ").strip().lower()
                if retry != 'y':
                    print("Exiting...")
                    sys.exit(0)

    def save_credentials(self, filename, username, password, api_key, language='th'):
        """Save credentials to file for future use"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("# OpenSubtitles Credentials\n")
                f.write("# All three credentials are required\n\n")
                f.write(f'username="{username}"\n')
                f.write(f'password="{password}"\n')
                f.write(f'apikey="{api_key}"\n')
                f.write(f'language="{language}"\n')
                f.write("\n# Format: username=\"...\" password=\"...\" apikey=\"...\" language=\"...\"\n")

            print(f"✓ Credentials saved to {filename}")
        except Exception as e:
            print(f"Warning: Could not save credentials: {e}")

    def parse_credentials(self, filename):
        """Parse credentials from file"""
        username = password = api_key = None
        language = 'th'  # default

        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()

                # Parse username - handle various formats
                username_match = re.search(r'username\s*[=:]\s*["\']?([^"\'\n\s]+)["\']?', content, re.IGNORECASE)
                if username_match:
                    username = username_match.group(1).strip('"\'')

                # Parse password
                password_match = re.search(r'password\s*[=:]\s*["\']?([^"\'\n\s]+)["\']?', content, re.IGNORECASE)
                if password_match:
                    password = password_match.group(1).strip('"\'')

                # Parse API key
                apikey_match = re.search(r'apikey\s*[=:]\s*["\']?([^"\'\n\s]+)["\']?', content, re.IGNORECASE)
                if apikey_match:
                    api_key = apikey_match.group(1).strip('"\'')

                # Parse language (optional)
                language_match = re.search(r'language\s*[=:]\s*["\']?([^"\'\n\s]+)["\']?', content, re.IGNORECASE)
                if language_match:
                    language = language_match.group(1).strip('"\'')

                # Also try simple colon-separated format: username:password:apikey[:language]
                if not (username and password and api_key):
                    lines = content.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            parts = line.split(':')
                            if len(parts) >= 3:
                                username = parts[0].strip()
                                password = parts[1].strip()
                                api_key = parts[2].strip()
                                if len(parts) >= 4:
                                    language = parts[3].strip()
                                break

                print(f"Debug - Parsed: username={username}, password={'*' * len(password) if password else None}, apikey={api_key[:5] + '...' if api_key else None}, language={language}")
                return username, password, api_key, language

        except Exception as e:
            print(f"Error reading credentials file: {e}")
            return None, None, None, 'th'

    def login(self):
        """Login to OpenSubtitles and get token"""
        if not all([self.username, self.password, self.api_key]):
            print("✗ Missing required credentials")
            return False

        # Set API key in headers
        self.headers["Api-Key"] = self.api_key

        try:
            print("Attempting to login...")
            login_data = {
                "username": self.username,
                "password": self.password
            }

            response = requests.post(
                f"{self.base_url}/login",
                headers=self.headers,
                json=login_data
            )

            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                self.headers["Authorization"] = f"Bearer {self.token}"

                print("✓ Login successful")

                # DEBUG TEST — verify token actually works
                test = requests.get(
                    f"{self.base_url}/infos/user",
                    headers=self.headers
                )

                print("DEBUG user check:", test.status_code)
                print("DEBUG response:", test.text[:200])

                return True
            else:
                print(f"✗ Login failed: {response.status_code}")
                print(f"Response: {response.text}")

                # If login fails, offer to re-enter credentials
                retry = input("\nWould you like to re-enter your credentials? (y/n): ").strip().lower()
                if retry == 'y':
                    # Re-prompt for credentials
                    self.username, self.password, self.api_key, self.language = self.prompt_for_credentials('open subs-api-key.txt')
                    # Update headers with new API key
                    self.headers["Api-Key"] = self.api_key
                    # Try login again
                    return self.login()
                return False

        except Exception as e:
            print(f"✗ Login error: {e}")
            return False

    def load_progress(self):
        """Load download progress from file"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_progress(self):
        """Save download progress to file"""
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2)

    def rate_limit(self):
        """Ensure we don't exceed rate limits"""
        if self.last_request_time:
            elapsed = (datetime.now() - self.last_request_time).total_seconds()
            if elapsed < self.min_request_interval:
                time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = datetime.now()

    def read_movies_from_file(self, movies_file='movies.txt'):
        """Read movie list from text file"""
        movie_list = []

        if not os.path.exists(movies_file):
            print(f"\n{movies_file} not found!")
            choice = input("Would you like to create it now? (y/n): ").strip().lower()

            if choice == 'y':
                self.create_sample_movies_file(movies_file)
                print(f"\nPlease add your movies to {movies_file} and run again.")
                sys.exit(0)
            else:
                print("Exiting...")
                sys.exit(0)

        with open(movies_file, 'r', encoding='utf-8') as f:
            for line in f:
                movie = line.strip()
                if movie and not movie.startswith('#'):
                    movie_list.append(movie)

        print(f"Found {len(movie_list)} movies in {movies_file}")
        return movie_list

    def create_sample_movies_file(self, filename):
        """Create a sample movies file"""
        sample_content = """# Thai Movies - Add one movie title per line
# Lines starting with # are ignored
# Examples:
Bad Genius (2017)
Shutter (2004)
Pee Mak (2013)
The Medium (2021)
One for the Road (2021)

# Add your movies below:
"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(sample_content)
        print(f"✓ Created {filename}")

    def search_movie_subtitle(self, movie_name, language=None):
        """Search for subtitles, using configured language if none provided."""
        if language is None:
            language = self.language  # Use language from credentials

        # Extract year if present
        year_match = re.search(r'\((\d{4})\)', movie_name)
        year = year_match.group(1) if year_match else None

        clean_name = re.sub(r'\(\d{4}\)', '', movie_name).strip()

        search_params = {
            "query": clean_name,
            "languages": language,
            "order_by": "download_count",
            "order_direction": "desc",
            "limit": 5
        }

        if year:
            search_params["year"] = year

        # DEBUG: print search parameters
        print(f"  DEBUG: Searching with params: {search_params}")

        try:
            self.rate_limit()
            response = requests.get(
                f"{self.base_url}/subtitles",
                headers=self.headers,
                params=search_params
            )

            # DEBUG: print status code
            print(f"  DEBUG: Response status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                # DEBUG: print first 500 chars of response (truncated)
                print(f"  DEBUG: Response data (first 500 chars): {json.dumps(data, indent=2)[:500]}")
                return data
            elif response.status_code == 401:
                print("  DEBUG: Token expired, re-logging...")
                if self.login():
                    return self.search_movie_subtitle(movie_name, language)
                return None
            elif response.status_code == 429:
                print("  DEBUG: Rate limited, waiting...")
                time.sleep(5)
                return self.search_movie_subtitle(movie_name, language)
            else:
                print(f"  DEBUG: Error response: {response.text[:200]}")
                print(f"  Error searching {movie_name}: {response.status_code}")
                return None

        except Exception as e:
            print(f"  DEBUG: Exception: {e}")
            print(f"  Error searching {movie_name}: {e}")
            return None

    def download_subtitle(self, file_id, movie_name, subtitle_name, attempt=1):
        """Download a specific subtitle file"""

        if movie_name in self.progress:
            print(f"  Skipping {movie_name} - already downloaded")
            return True

        download_data = {
            "file_id": file_id
        }

        try:
            self.rate_limit()
            response = requests.post(
                f"{self.base_url}/download",
                headers=self.headers,
                json=download_data
            )

            if response.status_code == 200:
                download_info = response.json()

                self.rate_limit()
                sub_response = requests.get(download_info['link'])

                if sub_response.status_code == 200:
                    safe_name = "".join(c for c in movie_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    file_path = self.download_dir / f"{safe_name}.srt"

                    with open(file_path, 'wb') as f:
                        f.write(sub_response.content)

                    self.progress[movie_name] = {
                        'downloaded': datetime.now().isoformat(),
                        'filename': safe_name,
                        'subtitle_name': subtitle_name
                    }
                    self.save_progress()

                    print(f"  ✓ Downloaded: {movie_name}")
                    return True
                else:
                    print(f"  ✗ Failed to download file: {movie_name}")
                    return False

            elif response.status_code == 401:
                if attempt < 2:
                    print("  Token expired, re-logging in...")
                    if self.login():
                        return self.download_subtitle(file_id, movie_name, subtitle_name, attempt + 1)
                return False
            elif response.status_code == 429:
                if attempt < 3:
                    wait_time = attempt * 5
                    print(f"  Rate limit hit. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                    return self.download_subtitle(file_id, movie_name, subtitle_name, attempt + 1)
                else:
                    print(f"  ✗ Rate limit exceeded for {movie_name}")
                    return False
            else:
                print(f"  ✗ Error getting download link: {response.status_code}")
                return False

        except Exception as e:
            print(f"  ✗ Error downloading {movie_name}: {e}")
            return False

    def process_movies(self, movies_file='movies.txt'):
        """Main function to process all movies from file"""

        movies = self.read_movies_from_file(movies_file)

        if not movies:
            print("No movies found in file.")
            return

        print(f"\nStarting download process for {len(movies)} movies...")
        print("Progress will be saved automatically. Press Ctrl+C to interrupt and resume later.\n")

        successful = 0
        failed = 0
        not_found = 0

        try:
            for i, movie in enumerate(movies, 1):
                print(f"[{i}/{len(movies)}] Processing: {movie}")

                if movie in self.progress:
                    print(f"  Already downloaded, skipping...")
                    successful += 1
                    continue

                result = self.search_movie_subtitle(movie)

                if result and result.get('data'):
                    subtitles = result['data']

                    downloaded = False
                    for sub in subtitles[:3]:
                        attributes = sub['attributes']
                        file_id = sub['id']
                        subtitle_name = attributes.get('release', 'Unknown')

                        print(f"  Attempting: {subtitle_name[:50]}...")

                        if self.download_subtitle(file_id, movie, subtitle_name):
                            downloaded = True
                            successful += 1
                            break
                        else:
                            time.sleep(1)

                    if not downloaded:
                        print(f"  ✗ Failed to download any subtitle for: {movie}")
                        failed += 1
                else:
                    print(f"  ✗ No subtitles found for: {movie}")
                    not_found += 1

                if i < len(movies):
                    delay = 2 + (hash(movie) % 3)
                    print(f"  Waiting {delay} seconds before next movie...")
                    time.sleep(delay)

        except KeyboardInterrupt:
            print("\n\n⚠ Download interrupted by user")
            print(f"Progress saved. {successful} movies downloaded so far.")
            print(f"Run the script again to resume from where you left off.")

        # Print summary
        print("\n" + "="*50)
        print("DOWNLOAD COMPLETE!")
        print("="*50)
        print(f"Total movies processed: {len(movies)}")
        print(f"Successfully downloaded: {successful}")
        print(f"Failed downloads: {failed}")
        print(f"No subtitles found: {not_found}")
        print(f"Previously downloaded: {len(self.progress) - successful + failed + not_found}")
        print(f"Subtitles saved in: {self.download_dir}")
        print("="*50)

def main():
    print("="*50)
    print("THAI MOVIE SUBTITLE DOWNLOADER")
    print("="*50)

    # Initialize downloader
    downloader = ThaiMovieDownloader('open-subs-api-key.txt')

    # Process movies from file
    downloader.process_movies('movies.txt')

if __name__ == "__main__":
    main()
