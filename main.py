"""Lab Assignment 1: Working with a Public REST API Using Python."""

import html
import os
import re
import textwrap
from pathlib import Path

import requests
from dotenv import load_dotenv

API_URL = "https://science.nasa.gov/wp-json/wp/v2/apod-basic/"


def clean_text(value):
    """Remove HTML markup sometimes included in NASA's JSON text."""
    if not value:
        return "Not available"
    without_tags = re.sub(r"<[^>]+>", " ", str(value))
    return " ".join(html.unescape(without_tags).split())


class AstronomyPicture:
    """Store the important information for one NASA astronomy picture."""

    def __init__(self, data):
        self.date = data.get("date", "Not available")
        self.title = clean_text(data.get("title"))
        self.media_type = data.get("media_type", "Not available")
        self.explanation = clean_text(data.get("explanation"))
        self.url = data.get("url", "Not available")
        self.credit = clean_text(data.get("credit") or data.get("copyright") or "NASA")

    def display_summary(self):
        """Print the image information in a clear, organized format."""
        print("=" * 65)
        print("             NASA Astronomy Picture of the Day")
        print("=" * 65)
        print(f"Date       : {self.date}")
        print(f"Title      : {self.title}")
        print(f"Media type : {self.media_type}")
        print(f"Credit     : {self.credit}")
        print(f"URL        : {self.url}")
        print("-" * 65)
        print("EXPLANATION")
        summary = textwrap.shorten(self.explanation, width=350, placeholder="...")
        print(textwrap.fill(summary, width=65))
        print("=" * 65)


def main():
    # Keep the API key in the local .env file; never commit it to GitHub.
    load_dotenv(dotenv_path=Path(__file__).with_name(".env"))
    api_key = os.getenv("NASA_API_KEY")

    if not api_key:
        print("Error: Set NASA_API_KEY in your local .env file.")
        return 1

    try:
        response = requests.get(API_URL, params={"api_key": api_key}, timeout=20)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.HTTPError:
        print(f"Error: NASA API returned HTTP {response.status_code}.")
        return 1
    except ValueError:
        print("Error: The API response is not valid JSON.")
        return 1
    except requests.exceptions.RequestException as error:
        # Do not print URLs, since query parameters contain the API key.
        print(f"Error: Could not connect to NASA API ({type(error).__name__}).")
        return 1

    # NASA's new APOD endpoint may return a list of pictures (newest first).
    if isinstance(data, list):
        data = data[0] if data else None

    if not isinstance(data, dict) or not data.get("title"):
        print("Error: NASA API returned an unexpected JSON structure.")
        return 1

    picture = AstronomyPicture(data)
    picture.display_summary()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
