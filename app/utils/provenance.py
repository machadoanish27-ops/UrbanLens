NULL_MARKERS = frozenset({"", "null", "none", "nan", "na", "n/a", "not provided", "not available"})


def is_semantically_missing(value: object) -> bool:
    return value is None or str(value).strip().lower() in NULL_MARKERS