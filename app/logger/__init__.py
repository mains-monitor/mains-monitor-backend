import logging

root = logging.getLogger()
if root.handlers:
    for handler in root.handlers:
        root.removeHandler(handler)

logging.basicConfig(
    format='%(asctime)s %(levelname)s - %(name)s - %(message)s',
    level=logging.INFO
)

logger = root

__all__ = ["logger"]
