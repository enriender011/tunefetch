from __future__ import annotations

import re

from .i18n import t

# Argparse builds these messages in English no matter the language. Patterns are tried in order.
PATTERNS = (
    (r"^argument command: invalid choice: '(?P<value>.*?)' \(choose from (?P<options>.*)\)$", "err.unknown_command"),
    (r"^argument (?P<arg>.+?): invalid choice: '(?P<value>.*?)' \(choose from (?P<options>.*)\)$", "err.invalid_choice"),
    (r"^argument (?P<arg>.+?): invalid int value: '(?P<value>.*)'$", "err.invalid_number"),
    (r"^argument (?P<arg>.+?): expected (?:at least )?one argument$", "err.needs_value"),
    (r"^unrecognized arguments: (?P<value>.*)$", "err.unrecognized"),
)


def translate_parse_error(message: str) -> str:
    for pattern, key in PATTERNS:
        match = re.match(pattern, message)
        if match:
            values = match.groupdict()
            if "options" in values:
                values["options"] = values["options"].replace("'", "")
            return t(key, **values)
    return message
