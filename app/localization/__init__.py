import os
from pathlib import Path
import i18n
from i18n import t
import humanize.i18n as hi18n
import pytz
from app.logger import logger

timezone = pytz.timezone(os.getenv("TIMEZONE"))

logger.info("Start init localization")

hi18n.activate('uk_UA')
i18n.set('locale', 'uk')
i18n.load_path.append((Path(__file__).parent / "translations").resolve())

logger.info("Localization got initialized")

__all__ = ["t", "timezone"]
