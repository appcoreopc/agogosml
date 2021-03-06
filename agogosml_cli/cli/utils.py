# -*- coding: utf-8 -*-

"""Utility functions."""

import json
from pathlib import Path
from typing import Union

from jsonschema import validate


MODULE_PATH = Path(__file__).parent
SCHEMA_FILE = MODULE_PATH / 'manifest.schema.json'
TEMPLATES_FOLDER = MODULE_PATH / 'templates'


def get_template_full_filepath(file: Union[str, Path]) -> Path:
    """Get full file path for template file.
    Args:
        file (string): Name of the file in module
    """
    return TEMPLATES_FOLDER / file


def validate_manifest(manifest_json: object) -> None:
    """Validates a manifest file against
    the scheme Throws an error if invalid.
    Args:
        manifest_json (object):
    """
    with SCHEMA_FILE.open() as f:
        schema_json = json.load(f)
    validate(manifest_json, schema_json)
    return
