"""API client module -- fetches data from PokeAPI with local caching."""

import os

import requests

from utils.file_handler import FileHandler


class ApiClient:
    """Client for PokeAPI with local caching.

    POO: This class demonstrates SINGLE RESPONSIBILITY -- it only handles
    API communication and downloading. Data transformation (turning raw API
    responses into Pokemon objects) is left to the caller.
    The constructor (__init__) stores configuration that all methods share.
    """

    BASE_URL = "https://pokeapi.co/api/v2"

    def __init__(self, cache_dir="data/"):
        """Initialize the API client.

        Args:
            cache_dir: Directory where cached JSON files are stored.
        """
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    def fetch_pokemon(self, name_or_id):
        """Fetch a single Pokemon's data from PokeAPI.

        Args:
            name_or_id: Pokemon name (str) or national dex number (int).

        Returns:
            dict: Raw API response with Pokemon data.

        Raises:
            requests.RequestException: If the API call fails.
        """
        url = f"{self.BASE_URL}/pokemon/{str(name_or_id).lower()}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()

    def fetch_type_data(self, type_name):
        """Fetch type effectiveness data for a single type.

        Args:
            type_name: Name of the type (e.g. "fire").

        Returns:
            dict: Raw API response with type damage relations.

        Raises:
            requests.RequestException: If the API call fails.
        """
        url = f"{self.BASE_URL}/type/{type_name.lower()}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()

    def download_sprite(self, url, save_path):
        """Download a sprite image from a URL and save it locally.

        Args:
            url: URL of the sprite image.
            save_path: Local file path where the image will be saved.

        Returns:
            str: The save_path if successful.

        Raises:
            requests.RequestException: If the download fails.
        """
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        with open(save_path, "wb") as file:
            file.write(response.content)
        return save_path

    def fetch_pokemon_list(self, limit=20):
        """Fetch a list of Pokemon names/URLs from PokeAPI.

        Args:
            limit: Number of Pokemon to fetch (default 20).

        Returns:
            list[dict]: List of dicts with 'name' and 'url' keys.

        Raises:
            requests.RequestException: If the API call fails.
        """
        url = f"{self.BASE_URL}/pokemon?limit={limit}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()["results"]
