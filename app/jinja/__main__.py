from datetime import datetime, timedelta
from . import jinja

template = jinja.get_template("electricity_status_msg.md")
args = dict(
    state="UNKNOWN",
    on_emoji=":)",
    off_emoji=":(",
    last_switch=datetime.now() - timedelta(hours=1),
    next_blackout=datetime.now().replace(
        second=0, microsecond=0) + timedelta(hours=3),
    next_recovery=datetime.now().replace(minute=0, second=0) + timedelta(hours=2)
)
print(template.render(**args))
