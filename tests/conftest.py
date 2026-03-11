"""Root test configuration."""


def pytest_addoption(parser):
    parser.addoption(
        '--update-snapshots',
        action='store_true',
        default=False,
        help='Update snapshot files (e.g. sample.deobfuscated.js) instead of comparing against them.',
    )
