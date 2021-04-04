from datetime import datetime

from jinja2 import Markup


def to_local_datetime(timestamp, dt_format="llll"):
    if timestamp is None:
        return ""

    data = None
    if isinstance(timestamp, datetime):
        data = timestamp.strftime("%Y-%m-%dT%H:%M:%S Z")
    elif isinstance(timestamp, str):
        data = datetime.fromisoformat(timestamp).strftime("%Y-%m-%dT%H:%M:%S Z")
    else:
        return "MOMENT JS ERROR"
        # raise AttributeError(f"Unsupported timestamp type. {type(timestamp)}")

    return Markup('<script>\ndocument.write(moment("%s").%s);\n</script>' % (data, dt_format))


class momentjs(object):
    def __init__(self, timestamp):
        self.timestamp = timestamp

    def render(self, dt_format):
        return Markup(
            '<script>\ndocument.write(moment("%s").%s);\n</script>' % (self.timestamp, dt_format)
        )
        # self.timestamp.strftime("%Y-%m-%dT%H:%M:%S Z")

    def format(self, fmt):
        return self.render('format("%s")' % fmt)

    def calendar(self):
        return self.render("calendar()")

    def fromNow(self):
        return self.render("fromNow()")
