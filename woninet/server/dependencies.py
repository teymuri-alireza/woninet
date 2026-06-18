from pathlib import Path


def get_static_path() -> tuple[Path, Path]:
    """
    Return the paths to the templates and static directories.

    Returns:
        tuple[Path, Path]: A tuple containing (TEMPLATES_DIR, STATIC_DIR)
    """
    STATIC_DIR = Path(__file__).parent / "static"
    TEMPLATES_DIR = Path(__file__).parent / "templates"

    return TEMPLATES_DIR, STATIC_DIR
