"""Tests for the ApiClient class.

These tests verify the ApiClient interface without hitting the real API.
They use unittest.mock to simulate API responses.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import patch, MagicMock
from utils.api_client import ApiClient


def test_fetch_pokemon_url():
    """fetch_pokemon calls the correct URL."""
    client = ApiClient(cache_dir="data/")
    mock_response = MagicMock()
    mock_response.json.return_value = {"name": "pikachu", "id": 25}
    mock_response.raise_for_status = MagicMock()

    with patch("utils.api_client.requests.get", return_value=mock_response) as mock_get:
        result = client.fetch_pokemon("pikachu")
        mock_get.assert_called_once_with(
            "https://pokeapi.co/api/v2/pokemon/pikachu", timeout=10
        )
        assert result["name"] == "pikachu"


def test_fetch_pokemon_by_id():
    """fetch_pokemon works with numeric IDs."""
    client = ApiClient()
    mock_response = MagicMock()
    mock_response.json.return_value = {"name": "pikachu", "id": 25}
    mock_response.raise_for_status = MagicMock()

    with patch("utils.api_client.requests.get", return_value=mock_response) as mock_get:
        client.fetch_pokemon(25)
        mock_get.assert_called_once_with(
            "https://pokeapi.co/api/v2/pokemon/25", timeout=10
        )


def test_fetch_type_data():
    """fetch_type_data calls the correct URL."""
    client = ApiClient()
    mock_response = MagicMock()
    mock_response.json.return_value = {"name": "fire", "damage_relations": {}}
    mock_response.raise_for_status = MagicMock()

    with patch("utils.api_client.requests.get", return_value=mock_response) as mock_get:
        result = client.fetch_type_data("fire")
        mock_get.assert_called_once_with(
            "https://pokeapi.co/api/v2/type/fire", timeout=10
        )
        assert result["name"] == "fire"


def test_fetch_pokemon_list():
    """fetch_pokemon_list returns a list of names."""
    client = ApiClient()
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "results": [{"name": "bulbasaur", "url": "..."}, {"name": "ivysaur", "url": "..."}]
    }
    mock_response.raise_for_status = MagicMock()

    with patch("utils.api_client.requests.get", return_value=mock_response):
        result = client.fetch_pokemon_list(limit=2)
        assert len(result) == 2
        assert result[0]["name"] == "bulbasaur"


def test_download_sprite(tmp_path):
    """download_sprite saves content to file."""
    client = ApiClient()
    mock_response = MagicMock()
    mock_response.content = b"\x89PNG fake image data"
    mock_response.raise_for_status = MagicMock()

    save_path = str(tmp_path / "sprite.png")
    with patch("utils.api_client.requests.get", return_value=mock_response):
        result = client.download_sprite("https://example.com/sprite.png", save_path)
        assert result == save_path
        assert os.path.isfile(save_path)
