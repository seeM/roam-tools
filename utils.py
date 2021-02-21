import re

from calendar import month_name as _MONTH_NAME
from datetime import date


# Matches Roam's date strings, for example: 'August 20th, 2020'
ROAM_DATE_PATTERN = r"([A-Z][a-z]+) ([0-9]{1,2})[a-z]+, ([0-9]{4})"

MONTH_NAME_TO_NUMBER = {
    name: number for number, name in enumerate(_MONTH_NAME)
}


def date_from_roam_string(string: str) -> date:
    """Parse a Roam date.

    Examples:
    >>> date_from_roam_string("August 20th, 2020")
    datetime.date(2020, 8, 20)
    >>> date_from_roam_string("January 3rd, 1324")
    datetime.date(1324, 1, 3)
    """
    match = re.match(f"^{ROAM_DATE_PATTERN}$", string)
    if match is None:
        raise ValueError(f"'{string}' is not a Roam date.")
    return date_from_roam_match(match)


def date_from_roam_match(match: re.Match) -> date:
    """Combine the groups of a Roam date matched with ROAM_DATE_PATTERN.

    Examples:
    >>> date_from_roam_parts("August", "20", "2020")
    datetime.date(2020, 8, 20)
    >>> date_from_roam_parts("January", "3", "1324")
    datetime.date(1324, 1, 3)
    """
    month_name, day, year = match.groups()
    month = MONTH_NAME_TO_NUMBER[month_name]
    return date(int(year), month, int(day))
