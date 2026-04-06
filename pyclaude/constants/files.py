"""File-related constants."""

from typing import List


# Common file extensions
CODE_EXTENSIONS = [
    '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', '.h', '.hpp',
    '.go', '.rs', '.rb', '.php', '.swift', '.kt', '.scala', '.sh', '.bash',
    '.sql', '.html', '.css', '.scss', '.sass', '.less', '.json', '.yaml', '.yml',
    '.toml', '.xml', '.md', '.rst', '.txt',
]

# Image extensions
IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.webp', '.ico']

# Binary extensions
BINARY_EXTENSIONS = ['.exe', '.dll', '.so', '.dylib', '.bin', '.dat', '.zip', '.tar', '.gz']

# Config files
CONFIG_FILES = [
    'package.json', 'Cargo.toml', 'requirements.txt', 'Pipfile', 'pyproject.toml',
    'setup.py', 'setup.cfg', 'Makefile', 'CMakeLists.txt', 'Dockerfile',
    '.gitignore', '.editorconfig', '.eslintrc', '.prettierrc', 'tsconfig.json',
]


def is_code_file(filename: str) -> bool:
    """Check if file is a code file."""
    return any(filename.endswith(ext) for ext in CODE_EXTENSIONS)


def is_image_file(filename: str) -> bool:
    """Check if file is an image."""
    return any(filename.endswith(ext) for ext in IMAGE_EXTENSIONS)


def is_binary_file(filename: str) -> bool:
    """Check if file is binary."""
    return any(filename.endswith(ext) for ext in BINARY_EXTENSIONS)


def is_config_file(filename: str) -> bool:
    """Check if file is a config file."""
    return filename in CONFIG_FILES


__all__ = [
    'CODE_EXTENSIONS',
    'IMAGE_EXTENSIONS',
    'BINARY_EXTENSIONS',
    'CONFIG_FILES',
    'is_code_file',
    'is_image_file',
    'is_binary_file',
    'is_config_file',
]