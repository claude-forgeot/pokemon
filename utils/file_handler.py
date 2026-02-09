"""File handler module -- generic JSON file reader/writer."""

import json
import os
import shutil
from datetime import datetime


class FileHandler:
    """Generic JSON file reader/writer with error handling.

    POO: STATIC METHODS vs INSTANCE METHODS -- this class uses @staticmethod
    because it doesn't need instance state (no 'self' parameter), but grouping
    related file operations in a class improves code organization.
    A static method belongs to the class itself, not to any particular instance.
    You call it with FileHandler.load_json(...) instead of creating an object first.
    """

    @staticmethod
    def load_json(path):
        """Load and return data from a JSON file.

        Args:
            path: Path to the JSON file.

        Returns:
            dict or list: Parsed JSON data.

        Raises:
            FileNotFoundError: If the file does not exist.
            json.JSONDecodeError: If the file is not valid JSON.
        """
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    @staticmethod
    def save_json(path, data):
        """Save data to a JSON file, creating directories if needed.

        Args:
            path: Path where the JSON file will be saved.
            data: Data to serialize (dict or list).
        """
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)

    @staticmethod
    def file_exists(path):
        """Check if a file exists at the given path.

        Args:
            path: Path to check.

        Returns:
            bool: True if the file exists, False otherwise.
        """
        return os.path.isfile(path)

    @staticmethod
    def create_backup(path):
        """Create a timestamped backup of a file.

        Args:
            path: Path to the file to back up.

        Returns:
            str: Path to the backup file.

        Raises:
            FileNotFoundError: If the original file does not exist.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base, ext = os.path.splitext(path)
        backup_path = f"{base}_backup_{timestamp}{ext}"
        shutil.copy2(path, backup_path)
        return backup_path
