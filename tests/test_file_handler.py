"""Tests for the FileHandler class."""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.file_handler import FileHandler


def test_save_and_load_json(tmp_path):
    """save_json + load_json roundtrip."""
    path = str(tmp_path / "test.json")
    data = {"name": "Pikachu", "hp": 35}
    FileHandler.save_json(path, data)
    loaded = FileHandler.load_json(path)
    assert loaded == data


def test_save_creates_directories(tmp_path):
    """save_json creates parent directories if needed."""
    path = str(tmp_path / "sub" / "dir" / "test.json")
    FileHandler.save_json(path, [1, 2, 3])
    assert FileHandler.file_exists(path)


def test_file_exists_true(tmp_path):
    """file_exists returns True for existing file."""
    path = str(tmp_path / "test.json")
    FileHandler.save_json(path, {})
    assert FileHandler.file_exists(path) is True


def test_file_exists_false(tmp_path):
    """file_exists returns False for non-existing file."""
    assert FileHandler.file_exists(str(tmp_path / "nope.json")) is False


def test_load_json_list(tmp_path):
    """load_json handles list data."""
    path = str(tmp_path / "test.json")
    data = [{"name": "A"}, {"name": "B"}]
    FileHandler.save_json(path, data)
    loaded = FileHandler.load_json(path)
    assert loaded == data


def test_create_backup(tmp_path):
    """create_backup creates a timestamped copy."""
    path = str(tmp_path / "test.json")
    FileHandler.save_json(path, {"key": "value"})
    backup_path = FileHandler.create_backup(path)
    assert os.path.isfile(backup_path)
    assert "backup" in backup_path
    # Backup content matches original
    backup_data = FileHandler.load_json(backup_path)
    assert backup_data == {"key": "value"}


def test_save_json_unicode(tmp_path):
    """save_json handles unicode characters."""
    path = str(tmp_path / "test.json")
    data = {"name": "Florizarre"}
    FileHandler.save_json(path, data)
    loaded = FileHandler.load_json(path)
    assert loaded["name"] == "Florizarre"
