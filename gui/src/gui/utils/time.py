import datetime

UTC = datetime.UTC


class Date:
    """DateTime (UTC)"""

    @classmethod
    def datetime(cls):
        return datetime.datetime.now(UTC)

    @classmethod
    def date(cls):
        return datetime.datetime.now(UTC).date()

    @classmethod
    def time(cls):
        return datetime.datetime.now(UTC).time()


def to_seconds(months: int = 0, days: int = 0, hours: int = 0, minutes: int = 0) -> int:
    """
    Convert time units to total seconds.
    Note: Assumes 30 days per month for approximation.
    """
    SECONDS_PER_MINUTE = 60
    SECONDS_PER_HOUR = 60 * SECONDS_PER_MINUTE
    SECONDS_PER_DAY = 24 * SECONDS_PER_HOUR
    SECONDS_PER_MONTH = 30 * SECONDS_PER_DAY  # Approximate: 30-day month

    return (
        months * SECONDS_PER_MONTH
        + days * SECONDS_PER_DAY
        + hours * SECONDS_PER_HOUR
        + minutes * SECONDS_PER_MINUTE
    )
