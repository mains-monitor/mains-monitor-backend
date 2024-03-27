from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from .filters import get_all_filters

jinja = Environment(
    loader=FileSystemLoader(Path(__file__).parent / "templates"),
    trim_blocks=True,
    lstrip_blocks=True,
)

jinja.filters = get_all_filters()

__all__ = ["jinja"]
