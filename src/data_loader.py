"""
data_loader.py – Loads job requirements and candidate applications from JSON files.
"""

import json
import os


def load_json(filepath: str) -> list:
    """Load and return data from a JSON file.

    Args:
        filepath: Absolute or relative path to the JSON file.

    Returns:
        Parsed list of records from the JSON file.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is not valid JSON or does not contain a list.
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"Data file not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    if not isinstance(data, list):
        raise ValueError(f"Expected a JSON array in '{filepath}', got {type(data).__name__}.")

    return data


def load_jobs(filepath: str = None) -> list:
    """Load job requirements from a JSON file.

    Args:
        filepath: Path to the jobs JSON file.
                  Defaults to data/jobs.json relative to this module.

    Returns:
        List of job requirement dictionaries.
    """
    if filepath is None:
        filepath = os.path.join(os.path.dirname(__file__), "..", "data", "jobs.json")
    return load_json(filepath)


def load_applications(filepath: str = None) -> list:
    """Load candidate applications from a JSON file.

    Args:
        filepath: Path to the applications JSON file.
                  Defaults to data/applications.json relative to this module.

    Returns:
        List of candidate application dictionaries.
    """
    if filepath is None:
        filepath = os.path.join(os.path.dirname(__file__), "..", "data", "applications.json")
    return load_json(filepath)
