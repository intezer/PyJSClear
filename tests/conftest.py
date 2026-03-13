"""Root test configuration."""

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        '--update-snapshots',
        action='store_true',
        default=False,
        help='Update snapshot files (e.g. sample.deobfuscated.js) instead of comparing against them.',
    )
